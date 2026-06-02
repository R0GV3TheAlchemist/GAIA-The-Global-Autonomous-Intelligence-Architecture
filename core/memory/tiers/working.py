"""
core/memory/tiers/working.py
WORKING memory tier — Sprint G-8

The most volatile tier. Holds the current-turn scratch-pad only.
All entries are stored in a plain dict and evicted at turn end via
evict_expired() (which clears everything) or explicit key deletion.

TTL: 0 hours — everything expires immediately when evict_expired() is called.
Persistence: none (in-process dict).
Concurrency: not thread-safe; designed for single-coroutine turn loops.

Canon Ref: C34 (Presence — GAIA knows what tier a moment belongs to)
"""
from __future__ import annotations

import time
from typing import Any

from core.memory.hierarchy import MemoryQuery


class WorkingMemoryStore:
    """In-process working memory.  Keys live until evict_expired() is called
    (i.e. at turn end) or until overwritten.  There is no per-key TTL because
    the entire working context is considered stale once the turn completes.
    """

    def __init__(self) -> None:
        # {(gaian_id_or_None, key): {"value": Any, "ts": float}}
        self._store: dict[tuple[str | None, str], dict] = {}

    async def write(
        self,
        key: str,
        value: Any,
        gaian_id: str | None = None,
        ttl_hours: float | None = None,  # ignored — working tier always evicts at turn end
    ) -> None:
        self._store[(gaian_id, key)] = {"value": value, "ts": time.time()}

    async def read(
        self,
        key: str,
        gaian_id: str | None = None,
    ) -> Any | None:
        entry = self._store.get((gaian_id, key))
        return entry["value"] if entry else None

    async def search(self, query: MemoryQuery) -> list[dict]:
        """Linear scan of all working-memory entries for this gaian.
        Returns results with _relevance=0.9 (high — working context is
        always fresh) and _recency normalised to [0, 1].
        """
        now = time.time()
        entries = [
            (k, v)
            for (g, k), v in self._store.items()
            if g == query.gaian_id
        ]
        if not entries:
            return []

        ts_vals = [v["ts"] for _, v in entries]
        ts_min, ts_max = min(ts_vals), max(ts_vals)
        ts_range = ts_max - ts_min or 1.0

        results = []
        text = query.query_text.lower()
        for k, v in entries:
            raw_val = v["value"]
            val_str = str(raw_val).lower()
            relevance = 0.9 if text in val_str or text in k.lower() else 0.3
            recency = (v["ts"] - ts_min) / ts_range
            results.append({
                "key":        k,
                "value":      raw_val,
                "_relevance": relevance,
                "_recency":   recency,
                "_ts":        v["ts"],
            })
        return results

    async def evict_expired(self) -> int:
        """Clear ALL working-memory entries (called at turn end).
        Returns count of evicted entries.
        """
        count = len(self._store)
        self._store.clear()
        return count
