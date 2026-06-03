"""
core/memory/__init__.py
GAIA Memory Package

Public surface (flat API — used by tests and all GAIA modules):
  FallbackEmbedder   — hash-based embedder (no network required)
  MemoryItem         — canonical memory row dataclass
  MemoryKind         — enum: message / fact / preference / …
  MemoryPruner       — capacity + TTL enforcement
  MemoryStore        — SQLite-backed semantic memory store
  MemoryTier         — enum: ephemeral / short_term / long_term / permanent
  RetrievedMemory    — (item, score) result wrapper

Legacy hierarchy API (Sprint G-8) also re-exported for back-compat:
  MemoryQuery, MemoryRouter, WorkingMemoryStore, ShortTermMemoryStore,
  EpisodicMemoryStore, SemanticMemoryStore, LongTermMemoryStore

Canon refs: C34 (Presence), C01 (Sovereignty)
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Flat API (new — used by test_memory_store.py and all new modules)
# ---------------------------------------------------------------------------
from .embedder import EmbeddingProvider, FallbackEmbedder
from .taxonomy import MemoryItem, MemoryKind, MemoryTier
from .store import MemoryStore, RetrievedMemory
from .pruner import MemoryPruner

# ---------------------------------------------------------------------------
# Legacy hierarchy API (Sprint G-8 — kept for back-compat)
# ---------------------------------------------------------------------------
from .hierarchy import MemoryQuery, MemoryRouter
from .tiers import (
    WorkingMemoryStore,
    ShortTermMemoryStore,
    EpisodicMemoryStore,
    SemanticMemoryStore,
    LongTermMemoryStore,
)


def build_default_router(
    *,
    db_path: str = ":memory:",
    semantic_store: SemanticMemoryStore | None = None,
    long_term_store: LongTermMemoryStore | None = None,
) -> MemoryRouter:
    """Return a MemoryRouter wired with all five tier stores.

    Parameters
    ----------
    db_path:
        SQLite database path for ShortTermMemoryStore.
        Defaults to ':memory:' (in-process, no persistence).
    semantic_store:
        Optional pre-built SemanticMemoryStore to inject.
    long_term_store:
        Optional pre-built LongTermMemoryStore to inject.

    Canon refs: C34, C01
    """
    return MemoryRouter({
        MemoryTier.WORKING:    WorkingMemoryStore(),
        MemoryTier.SHORT_TERM: ShortTermMemoryStore(db_path=db_path),
        MemoryTier.EPISODIC:   EpisodicMemoryStore(),
        MemoryTier.SEMANTIC:   semantic_store  if semantic_store  is not None else SemanticMemoryStore(),
        MemoryTier.LONG_TERM:  long_term_store if long_term_store is not None else LongTermMemoryStore(),
    })


__all__ = [
    # Flat API
    "EmbeddingProvider",
    "FallbackEmbedder",
    "MemoryItem",
    "MemoryKind",
    "MemoryPruner",
    "MemoryStore",
    "MemoryTier",
    "RetrievedMemory",
    # Legacy hierarchy
    "MemoryQuery",
    "MemoryRouter",
    "WorkingMemoryStore",
    "ShortTermMemoryStore",
    "EpisodicMemoryStore",
    "SemanticMemoryStore",
    "LongTermMemoryStore",
    # Factory
    "build_default_router",
]
