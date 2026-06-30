"""
core/memory/__init__.py

Public surface for the GAIA memory subsystem.

Exports the factory function used by tests and production code:
    build_default_router() -> MemoryRouter

Also re-exports the core hierarchy types and high-level manager API
for convenience.

Canon: C01 (GAIA as orchestration layer), C34 (Memory Sovereignty)
Issue: #213
"""
from __future__ import annotations

from core.memory.hierarchy import (
    MemoryTier,
    MemoryQuery,
    MemoryStore,
    MemoryRouter,
    build_default_router,
)
from core.memory.manager import MemoryManager
from core.memory.layers import MemoryLayer, MemoryTag
from core.memory.shadow_registry import ShadowPattern
from core.memory.retrieval import RetrievalQuery
from core.memory.connectivity_graph import ConnectivityGraph, ConnectivityNode
from core.memory.relevance_scorer import RelevanceScorer, RelevanceBreakdown
from core.memory.persistent_memory import PersistentMemoryModule, PersistentMemoryRecord

__all__ = [
    "MemoryTier",
    "MemoryQuery",
    "MemoryStore",
    "MemoryRouter",
    "build_default_router",
    "MemoryManager",
    "MemoryLayer",
    "MemoryTag",
    "ShadowPattern",
    "RetrievalQuery",
    "ConnectivityGraph",
    "ConnectivityNode",
    "RelevanceScorer",
    "RelevanceBreakdown",
    "PersistentMemoryModule",
    "PersistentMemoryRecord",
]
