"""
core/memory/hierarchy.py
GAIA Memory Hierarchy — Sprint G-8

Formalizes five cognitive memory tiers and a routing layer that directs
retrieval queries to the correct tier(s) rather than searching everything.
This makes memory retrieval cost-predictable and retrieval logic testable.

Canon Ref: C34 (Presence — GAIA knows what tier of memory a moment belongs to)
           C01 (Sovereignty — memory routing is explicit, not opaque)
"""
from __future__ import annotations

from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from core.trace import TraceEventType  # noqa: F401

__all__ = [
    "MemoryTier",
    "MemoryQuery",
    "MemoryStore",
    "MemoryRouter",
]


# ---------------------------------------------------------------------------
# Memory tiers
# ---------------------------------------------------------------------------

class MemoryTier(Enum):
    """The five cognitive memory tiers in GAIA-OS.

    Each tier has a different storage backend, TTL, and retrieval cost:

    WORKING    — Current turn context; evicts at turn end (in-memory dict).
    SHORT_TERM — Last N turns; 24-72 hr TTL (SQLite/Redis).
    EPISODIC   — Session moments; weeks-months TTL (ArcadeDB / graph DB).
    SEMANTIC   — Crystal Knowledge Graph facts; permanent.
    LONG_TERM  — Gaian identity and settled personality arcs; permanent.
    """
    WORKING    = auto()
    SHORT_TERM = auto()
    EPISODIC   = auto()
    SEMANTIC   = auto()
    LONG_TERM  = auto()

    def to_trace_event(self, *, write: bool = False) -> str:
        """Return the ``TraceEventType`` string value appropriate for this tier.

        Using the string value directly (rather than importing TraceEventType
        at module level) avoids a circular import while remaining mypy-safe
        under ``TYPE_CHECKING``.

        Parameters
        ----------
        write:
            If ``True``, return the write-side event (``memory_write``);
            otherwise return the read-side event (``memory_recall``).
        """
        return "memory_write" if write else "memory_recall"


# ---------------------------------------------------------------------------
# MemoryQuery — describes what is being sought
# ---------------------------------------------------------------------------

class MemoryQuery:
    """Describes what kind of memory is being sought.

    Parameters
    ----------
    query_text:
        The natural-language or embedding query string.
    intent:
        Routing hint — one of ``"context"``, ``"recall"``, ``"fact"``,
        ``"identity"``, or ``"full"``.  Controls which tiers are searched
        when ``tiers`` is ``None``.
    gaian_id:
        Optional scoping to a specific Gaian persona.
    tiers:
        Explicit tier list; overrides intent-based routing when provided.
    max_results:
        Maximum number of results to return across all searched tiers.
    recency_weight:
        Float in [0.0, 1.0].  Higher values rank recent memories first;
        lower values rank by relevance.
    """

    VALID_INTENTS = frozenset({"context", "recall", "fact", "identity", "full"})

    def __init__(
        self,
        query_text: str,
        intent: str,
        gaian_id: str | None = None,
        tiers: list[MemoryTier] | None = None,
        max_results: int = 10,
        recency_weight: float = 0.5,
    ) -> None:
        if intent not in self.VALID_INTENTS:
            raise ValueError(f"intent must be one of {self.VALID_INTENTS!r}, got {intent!r}")
        self.query_text    = query_text
        self.intent        = intent
        self.gaian_id      = gaian_id
        self.tiers         = tiers
        self.max_results   = max_results
        self.recency_weight = recency_weight


# ---------------------------------------------------------------------------
# MemoryStore — protocol for tier-specific backends
# ---------------------------------------------------------------------------

@runtime_checkable
class MemoryStore(Protocol):
    """Protocol every tier-specific memory store must satisfy.

    Implementations are injected into ``MemoryRouter`` at construction time.
    This protocol is defined here (not in ``memory/store.py``) so that
    ``MemoryRouter`` can depend on it without importing the concrete
    implementation, avoiding import cycles.

    ``memory/store.py`` contains the concrete ``GaianMemoryStore`` class
    that implements this protocol — do **not** re-export this Protocol from
    ``memory/store.py`` or a shadowing collision will occur.
    """

    async def write(
        self,
        key: str,
        value: Any,
        gaian_id: str | None = None,
    ) -> None: ...

    async def read(
        self,
        key: str,
        gaian_id: str | None = None,
    ) -> Any | None: ...

    async def search(self, query: "MemoryQuery") -> list[dict]: ...

    async def evict_expired(self) -> int:
        """Evict expired entries; return the number evicted."""
        ...


# ---------------------------------------------------------------------------
# MemoryRouter
# ---------------------------------------------------------------------------

class MemoryRouter:
    """
    Routes ``MemoryQuery`` objects to the appropriate tier(s).
    Merges and ranks results when multiple tiers are searched.

    Intent-to-tier routing rules
    ----------------------------
    ``"context"``  → WORKING + SHORT_TERM
    ``"recall"``   → SHORT_TERM + EPISODIC
    ``"fact"``     → SEMANTIC
    ``"identity"`` → LONG_TERM
    ``"full"``     → all tiers (expensive; only for explicit full-context requests)

    Trace integration
    -----------------
    ``MemoryRouter.search`` and ``MemoryRouter.write`` emit trace events
    using ``MemoryTier.to_trace_event()``, which returns the string value
    of ``TraceEventType.MEMORY_RECALL`` or ``TraceEventType.MEMORY_WRITE``
    without importing ``core.trace`` at module level (avoids circular dep).
    Callers that want to wrap these calls in a ``GAIATrace`` context manager
    should do so in their own code; ``MemoryRouter`` does not own traces.
    """

    _INTENT_MAP: dict[str, list[MemoryTier]] = {
        "context":  [MemoryTier.WORKING,    MemoryTier.SHORT_TERM],
        "recall":   [MemoryTier.SHORT_TERM, MemoryTier.EPISODIC],
        "fact":     [MemoryTier.SEMANTIC],
        "identity": [MemoryTier.LONG_TERM],
        "full":     list(MemoryTier),
    }

    def __init__(self, stores: dict[MemoryTier, MemoryStore]) -> None:
        self._stores = stores

    async def search(self, query: MemoryQuery) -> list[dict]:
        """Search the appropriate tier(s) and return ranked results.

        Each result dict gains a ``_tier`` key (the tier name string) and
        a ``_trace_event`` key (the corresponding TraceEventType string)
        so callers can emit a correctly-typed trace record.
        """
        tiers = query.tiers or self._INTENT_MAP.get(query.intent, list(MemoryTier))
        results: list[dict] = []
        for tier in tiers:
            store = self._stores.get(tier)
            if store is None:
                continue
            tier_results = await store.search(query)
            for r in tier_results:
                r["_tier"] = tier.name
                r["_trace_event"] = tier.to_trace_event(write=False)
            results.extend(tier_results)
        return self._rank(results, query)

    async def write(
        self,
        tier: MemoryTier,
        key: str,
        value: Any,
        gaian_id: str | None = None,
    ) -> None:
        """Write a value to a specific memory tier.

        Raises ``KeyError`` if no store is registered for *tier*.
        """
        store = self._stores[tier]
        await store.write(key, value, gaian_id=gaian_id)

    async def read(
        self,
        tier: MemoryTier,
        key: str,
        gaian_id: str | None = None,
    ) -> Any | None:
        """Read a value from a specific memory tier.

        Returns ``None`` if the key does not exist or no store is registered.
        """
        store = self._stores.get(tier)
        if store is None:
            return None
        return await store.read(key, gaian_id=gaian_id)

    def _rank(self, results: list[dict], query: MemoryQuery) -> list[dict]:
        """Combine recency and relevance scores, weighted by ``query.recency_weight``.

        Each result is expected to carry:
        - ``_score`` (float, 0.0–1.0): semantic relevance from the store.
        - ``_ts``    (float, Unix timestamp): creation/update time.

        Missing fields default to 0.0 so partial results still sort cleanly.
        Results are truncated to ``query.max_results``.
        """
        if not results:
            return results

        timestamps = [r.get("_ts", 0.0) for r in results]
        ts_min, ts_max = min(timestamps), max(timestamps)
        ts_range = ts_max - ts_min or 1.0

        rw = max(0.0, min(1.0, query.recency_weight))
        rel_w = 1.0 - rw

        for r in results:
            recency_score = (r.get("_ts", 0.0) - ts_min) / ts_range
            relevance_score = float(r.get("_score", 0.0))
            r["_combined_score"] = rw * recency_score + rel_w * relevance_score

        results.sort(key=lambda r: r["_combined_score"], reverse=True)
        return results[: query.max_results]
