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
                       (taxonomy.MemoryTier — used for flat store pruning)
  RetrievedMemory    — (item, score) result wrapper

Legacy hierarchy API (Sprint G-8) also re-exported for back-compat:
  MemoryQuery, MemoryRouter, WorkingMemoryStore, ShortTermMemoryStore,
  EpisodicMemoryStore, SemanticMemoryStore, LongTermMemoryStore

Important: Two MemoryTier enums exist in this codebase
  ───────────────────────────────────────────────
  core.memory.taxonomy.MemoryTier  — str enum (ephemeral → permanent)
      Used for flat MemoryItem tier labelling + pruning.
      This is what `from core.memory import MemoryTier` exports.

  core.memory.hierarchy.MemoryTier  — auto() int enum (WORKING → LONG_TERM)
      Used exclusively by MemoryRouter store mapping.
      build_default_router() uses this enum internally via the
      _HierarchyTier alias below.  Tests that import MemoryRouter and call
      router.registered_tiers() receive hierarchy.MemoryTier members.

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
from .hierarchy import MemoryTier as _HierarchyTier   # int-enum for MemoryRouter
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

    IMPORTANT: uses hierarchy.MemoryTier (_HierarchyTier) as the dict keys
    because MemoryRouter.__init__() validates against that enum.  The public
    `MemoryTier` export (taxonomy.MemoryTier) is a separate str-enum used
    only for MemoryItem tier labelling; mixing the two causes silent key-miss
    lookups and tier-registration test failures.

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
        _HierarchyTier.WORKING:    WorkingMemoryStore(),
        _HierarchyTier.SHORT_TERM: ShortTermMemoryStore(db_path=db_path),
        _HierarchyTier.EPISODIC:   EpisodicMemoryStore(),
        _HierarchyTier.SEMANTIC:   semantic_store  if semantic_store  is not None else SemanticMemoryStore(),
        _HierarchyTier.LONG_TERM:  long_term_store if long_term_store is not None else LongTermMemoryStore(),
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
