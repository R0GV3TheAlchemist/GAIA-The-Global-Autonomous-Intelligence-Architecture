"""sovereignmemory

NEXUS Sovereign Memory Module

Provides GAIA's sovereign, capability-gated, bi-temporal memory store.
Encodes episodic, semantic, and procedural memory in a graph-native
structure compatible with Zep/Graphiti and neo4j-agent-memory.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 3 - Sovereign Memory
Research reference:
    Zep/Graphiti arXiv:2501.13956   - bi-temporal graph memory
    Portable Agent Memory arXiv:2605.11032 - Merkle-DAG provenance
    MemGPT arXiv:2310.08560         - tiered paging model
"""
from __future__ import annotations

from sovereignmemory.engine import SovereignMemory
from sovereignmemory.router import memory_router, init_memory

__all__ = ["SovereignMemory", "memory_router", "init_memory"]
