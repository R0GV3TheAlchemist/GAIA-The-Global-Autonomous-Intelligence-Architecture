"""
core/memory/tiers/hot_tier.py

HOT TIER — in-process LRU cache with TTL eviction.

Design:
- Backed by an OrderedDict for O(1) LRU operations.
- Each entry carries an expiry timestamp; stale entries are lazily
  evicted on read and eagerly evicted by a background sweep.
- Thread-safe via a reentrant lock.
- No disk I/O — data lives only for the lifetime of the process.
  Promotion from warm tier happens externally via MemoryTierRouter.

Typical TTL: 300 s (5 min). Max capacity: 2 048 entries.
"""

from __future__ import annotations

import threading
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class HotEntry:
    key: str
    value: Any
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    expires_at: Optional[float] = None  # None = no expiry

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def touch(self) -> None:
        self.accessed_at = time.time()
        self.access_count += 1


# ---------------------------------------------------------------------------
# HotTier
# ---------------------------------------------------------------------------

class HotTier:
    """
    In-process LRU cache with optional per-entry TTL.

    Parameters
    ----------
    max_size : int
        Maximum number of entries before LRU eviction kicks in.
    default_ttl : float | None
        Seconds until an entry expires.  None disables expiry.
    sweep_interval : float
        Seconds between background expiry sweeps.  0 disables sweeping.
    """

    def __init__(
        self,
        max_size: int = 2048,
        default_ttl: Optional[float] = 300.0,
        sweep_interval: float = 60.0,
    ) -> None:
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, HotEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "expirations": 0}

        if sweep_interval > 0:
            self._sweeper = threading.Thread(
                target=self._sweep_loop,
                args=(sweep_interval,),
                daemon=True,
                name="HotTier-sweeper",
            )
            self._sweeper.start()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def put(
        self,
        key: str,
        value: Any,
        *,
        tags: Optional[List[str]] = None,
        ttl: Optional[float] = ...,  # type: ignore[assignment]
    ) -> HotEntry:
        """Insert or overwrite an entry.  Returns the stored HotEntry."""
        if ttl is ...:
            ttl = self.default_ttl
        expires_at = (time.time() + ttl) if ttl is not None else None
        entry = HotEntry(
            key=key,
            value=value,
            tags=tags or [],
            expires_at=expires_at,
        )
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            self._cache[key] = entry
            self._evict_if_full()
        return entry

    def get(self, key: str) -> Optional[Any]:
        """Return the value for *key*, or None if absent / expired."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._stats["misses"] += 1
                return None
            if entry.is_expired():
                del self._cache[key]
                self._stats["expirations"] += 1
                self._stats["misses"] += 1
                return None
            # Move to end (most-recently-used position)
            self._cache.move_to_end(key)
            entry.touch()
            self._stats["hits"] += 1
            return entry.value

    def get_entry(self, key: str) -> Optional[HotEntry]:
        """Return the full HotEntry, or None."""
        with self._lock:
            entry = self._cache.get(key)
            if entry is None or entry.is_expired():
                return None
            self._cache.move_to_end(key)
            entry.touch()
            return entry

    def delete(self, key: str) -> bool:
        """Remove an entry.  Returns True if it existed."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def invalidate_by_tag(self, tag: str) -> int:
        """Remove all entries carrying *tag*.  Returns count removed."""
        with self._lock:
            victims = [k for k, e in self._cache.items() if tag in e.tags]
            for k in victims:
                del self._cache[k]
            return len(victims)

    def clear(self) -> None:
        """Wipe all entries."""
        with self._lock:
            self._cache.clear()

    def contains(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            return entry is not None and not entry.is_expired()

    def keys(self) -> List[str]:
        with self._lock:
            return [
                k for k, e in self._cache.items() if not e.is_expired()
            ]

    def __len__(self) -> int:
        with self._lock:
            return sum(1 for e in self._cache.values() if not e.is_expired())

    def __iter__(self) -> Iterator[str]:
        return iter(self.keys())

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                **self._stats,
                "size": len(self._cache),
                "max_size": self.max_size,
                "hit_rate": (
                    self._stats["hits"]
                    / max(1, self._stats["hits"] + self._stats["misses"])
                ),
            }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _evict_if_full(self) -> None:
        """Evict LRU entries until we're under max_size."""
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)  # oldest
            self._stats["evictions"] += 1

    def _sweep_expired(self) -> int:
        """Remove all expired entries.  Returns count removed."""
        with self._lock:
            victims = [k for k, e in self._cache.items() if e.is_expired()]
            for k in victims:
                del self._cache[k]
                self._stats["expirations"] += 1
            return len(victims)

    def _sweep_loop(self, interval: float) -> None:
        while True:
            time.sleep(interval)
            self._sweep_expired()
