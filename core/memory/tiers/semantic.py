"""
core/memory/tiers/semantic.py
SEMANTIC memory tier — Sprint G-8

Permanent, fact-oriented knowledge.  Backs the Crystal Knowledge Graph
and canon-derived facts.  Entries never auto-expire.

TTL:         None (permanent)
Persistence: in-process dict (production backend: Crystal DB / graph store)
Search:      keyword match + static relevance scoring

Canon Ref: C34 (Presence — GAIA knows established facts about the world)
           C01 (Sovereignty — facts are explicit, not hallucinated)
"""
from __future__ import annotations

import time
from typing import Any

from core.memory.hierarchy import MemoryQuery


class SemanticMemoryStore:
    """Permanent fact store.  Writes overwrite the previous value for the
    same (gaian_id, key).  Nothing ever expires.
    """

    def __init__(self) -> None:
        # {(gaian_id, key): {"value": Any, "ts": float}}
        self._store: dict[tuple[str | None, str], dict] = {}

    async def write(
        self,
        key: str,
        value: Any,
        gaian_id: str | None = None,
        ttl_hours: float | None = None,  # ignored — semantic is permanent
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
        text = query.query_text.lower()
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
        for k, v in entries:
            val_str = str(v["value"]).lower()
            relevance = 0.85 if text in val_str or text in k.lower() else 0.15
            recency = (v["ts"] - ts_min) / ts_range
            results.append({
                "key":        k,
                "value":      v["value"],
                "_relevance": relevance,
                "_recency":   recency,
                "_ts":        v["ts"],
            })
        return results

    async def evict_expired(self) -> int:
        """No-op — semantic memory is permanent.  Always returns 0."""
        return 0
