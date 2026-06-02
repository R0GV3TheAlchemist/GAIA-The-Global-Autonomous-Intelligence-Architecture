"""
core/memory/tiers/short_term.py
SHORT_TERM memory tier — Sprint G-8

Holds the last N turns of recent context.  Entries expire after
``ttl_hours`` (default 48 h).  Backed by an in-process ordered dict;
production deployments swap this for SQLite or Redis.

TTL:         48 hours (configurable per-write via ttl_hours param)
Persistence: in-process OrderedDict (no disk I/O in this stub)
Eviction:    time-based; evict_expired() removes stale entries

Canon Ref: C34 (Presence), C01 (Sovereignty)
"""
from __future__ import annotations

import time
from collections import OrderedDict
from typing import Any

from core.memory.hierarchy import MemoryQuery, MemoryTier

_DEFAULT_TTL_HOURS = MemoryTier.SHORT_TERM.default_ttl_hours or 48.0
_DEFAULT_TTL_SECS = _DEFAULT_TTL_HOURS * 3600


class ShortTermMemoryStore:
    """Recent-context store with time-based expiry.

    Internally keyed by (gaian_id, key).  Oldest entries are at the
    front of the OrderedDict so eviction is O(n) in the number of
    expired entries, not the total store size.
    """

    def __init__(self, max_entries: int = 2048) -> None:
        self._max = max_entries
        # {(gaian_id, key): {"value": Any, "ts": float, "expires": float}}
        self._store: OrderedDict[tuple[str | None, str], dict] = OrderedDict()

    async def write(
        self,
        key: str,
        value: Any,
        gaian_id: str | None = None,
        ttl_hours: float | None = None,
    ) -> None:
        ttl_secs = (ttl_hours * 3600) if ttl_hours is not None else _DEFAULT_TTL_SECS
        now = time.time()
        k = (gaian_id, key)
        self._store[k] = {"value": value, "ts": now, "expires": now + ttl_secs}
        self._store.move_to_end(k)
        # LRU-style cap
        while len(self._store) > self._max:
            self._store.popitem(last=False)

    async def read(
        self,
        key: str,
        gaian_id: str | None = None,
    ) -> Any | None:
        entry = self._store.get((gaian_id, key))
        if entry is None:
            return None
        if time.time() > entry["expires"]:
            del self._store[(gaian_id, key)]
            return None
        return entry["value"]

    async def search(self, query: MemoryQuery) -> list[dict]:
        now = time.time()
        text = query.query_text.lower()
        results = []
        for (g, k), v in self._store.items():
            if g != query.gaian_id:
                continue
            if now > v["expires"]:
                continue
            val_str = str(v["value"]).lower()
            relevance = 0.8 if text in val_str or text in k.lower() else 0.25
            # Recency: fraction of TTL remaining (higher = fresher)
            age_secs = now - v["ts"]
            ttl_secs = v["expires"] - v["ts"] or 1.0
            recency = max(0.0, 1.0 - age_secs / ttl_secs)
            results.append({
                "key":        k,
                "value":      v["value"],
                "_relevance": relevance,
                "_recency":   recency,
                "_ts":        v["ts"],
            })
        return results

    async def evict_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v["expires"]]
        for k in expired:
            del self._store[k]
        return len(expired)
