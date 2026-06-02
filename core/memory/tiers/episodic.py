"""
core/memory/tiers/episodic.py
EPISODIC memory tier — Sprint G-8

Stores significant session moments that persist weeks to months.
Designed for narrative retrieval: "what happened last Tuesday with Luna".

TTL:         720 hours / 30 days (configurable per-write)
Persistence: in-process list (production backend: ArcadeDB / graph DB)
Search:      linear keyword scan + recency scoring (embedding search added later)

Canon Ref: C34 (Presence — GAIA remembers significant moments)
"""
from __future__ import annotations

import time
from typing import Any

from core.memory.hierarchy import MemoryQuery, MemoryTier

_DEFAULT_TTL_SECS = (MemoryTier.EPISODIC.default_ttl_hours or 720.0) * 3600


class EpisodicMemoryStore:
    """Session-moment store with long TTL and keyword-based search.

    Each write appends an episode record.  Episodes are not deduplicated;
    the same key may appear multiple times (each write is a new moment).
    Retrieval returns the most recent matching episodes.
    """

    def __init__(self) -> None:
        # List of {"gaian_id", "key", "value", "ts", "expires"}
        self._episodes: list[dict] = []
        # Latest-write index for keyed reads: {(gaian_id, key): index}
        self._latest: dict[tuple[str | None, str], int] = {}

    async def write(
        self,
        key: str,
        value: Any,
        gaian_id: str | None = None,
        ttl_hours: float | None = None,
    ) -> None:
        now = time.time()
        ttl_secs = (ttl_hours * 3600) if ttl_hours is not None else _DEFAULT_TTL_SECS
        idx = len(self._episodes)
        self._episodes.append({
            "gaian_id": gaian_id,
            "key":      key,
            "value":    value,
            "ts":       now,
            "expires":  now + ttl_secs,
        })
        self._latest[(gaian_id, key)] = idx

    async def read(
        self,
        key: str,
        gaian_id: str | None = None,
    ) -> Any | None:
        idx = self._latest.get((gaian_id, key))
        if idx is None:
            return None
        ep = self._episodes[idx]
        if time.time() > ep["expires"]:
            return None
        return ep["value"]

    async def search(self, query: MemoryQuery) -> list[dict]:
        now = time.time()
        text = query.query_text.lower()
        ts_vals = [ep["ts"] for ep in self._episodes
                   if ep["gaian_id"] == query.gaian_id and now <= ep["expires"]]
        ts_min = min(ts_vals) if ts_vals else 0.0
        ts_max = max(ts_vals) if ts_vals else 1.0
        ts_range = ts_max - ts_min or 1.0

        results = []
        for ep in self._episodes:
            if ep["gaian_id"] != query.gaian_id:
                continue
            if now > ep["expires"]:
                continue
            val_str = str(ep["value"]).lower()
            relevance = 0.75 if text in val_str or text in ep["key"].lower() else 0.2
            recency = (ep["ts"] - ts_min) / ts_range
            results.append({
                "key":        ep["key"],
                "value":      ep["value"],
                "_relevance": relevance,
                "_recency":   recency,
                "_ts":        ep["ts"],
            })
        return results

    async def evict_expired(self) -> int:
        now = time.time()
        before = len(self._episodes)
        self._episodes = [ep for ep in self._episodes if now <= ep["expires"]]
        # Rebuild latest index
        self._latest = {}
        for idx, ep in enumerate(self._episodes):
            self._latest[(ep["gaian_id"], ep["key"])] = idx
        return before - len(self._episodes)
