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

__all__ = [
    # Hierarchy types
    "MemoryTier",
    "MemoryQuery",
    "MemoryStore",
    "MemoryRouter",
    # Factory
    "build_default_router",
    # High-level manager API (used by tests and runtime)
    "MemoryManager",
    "MemoryLayer",
    "MemoryTag",
    "ShadowPattern",
    "RetrievalQuery",
]
