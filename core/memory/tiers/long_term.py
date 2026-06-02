"""
core/memory/tiers/long_term.py
LONG_TERM memory tier — Sprint G-8

The most permanent tier.  Holds Gaian identity, settled personality
arcs, and cross-session biographical facts.  Entries never auto-expire
and are never evicted without explicit deliberate action.

TTL:         None (permanent)
Persistence: in-process dict (production backend: Tauri Store / SQLite)
Search:      keyword match — identity facts are few and highly specific

Canon Ref: C34 (Presence — GAIA holds a stable sense of each Gaian's identity)
           C01 (Sovereignty — identity is explicit, not inferred ad-hoc)
"""
from __future__ import annotations

import time
from typing import Any

from core.memory.hierarchy import MemoryQuery


class LongTermMemoryStore:
    """Permanent identity + settled-arc store.  Semantically identical
    to SemanticMemoryStore but kept separate so routing and eviction
    policies can diverge without a breaking change.
    """

    def __init__(self) -> None:
        # {(gaian_id, key): {"value": Any, "ts": float}}
        self._store: dict[tuple[str | None, str], dict] = {}

    async def write(
        self,
        key: str,
        value: Any,
        gaian_id: str | None = None,
        ttl_hours: float | None = None,  # ignored — long-term is permanent
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
            # Identity facts are highly specific — weight relevance strongly
            relevance = 0.95 if text in val_str or text in k.lower() else 0.1
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
        """No-op — long-term memory is permanent.  Always returns 0."""
        return 0
