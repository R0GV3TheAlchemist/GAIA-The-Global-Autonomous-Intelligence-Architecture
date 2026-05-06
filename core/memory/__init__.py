"""
core.memory — Phase 2A: Persistent Semantic Memory
====================================================
Public surface for GAIA-OS's long-term, cross-session memory layer.

Quick-start
-----------
    from core.memory import MemoryStore, MemoryItem, MemoryKind, MemoryTier
    from core.memory import OllamaEmbedder, MemoryPruner

    embedder = OllamaEmbedder()           # or OpenAIEmbedder(api_key=...)
    store    = MemoryStore(embedder=embedder)
    pruner   = MemoryPruner(store)

    # Remember a turn
    item_id = await store.remember(
        user_id="user_001",
        text="I prefer dark-mode interfaces and concise answers.",
        role="user",
        kind=MemoryKind.PREFERENCE,
    )

    # Recall relevant context
    hits = await store.retrieve(user_id="user_001", query="UI preferences", top_k=5)
    for hit in hits:
        print(hit.text, hit.score)
"""

from .taxonomy import MemoryKind, MemoryTier, MemoryItem
from .embedder import EmbeddingProvider, OllamaEmbedder, OpenAIEmbedder, FallbackEmbedder
from .store import MemoryStore, RetrievedMemory
from .pruner import MemoryPruner

__all__ = [
    # taxonomy
    "MemoryKind",
    "MemoryTier",
    "MemoryItem",
    # embedders
    "EmbeddingProvider",
    "OllamaEmbedder",
    "OpenAIEmbedder",
    "FallbackEmbedder",
    # store
    "MemoryStore",
    "RetrievedMemory",
    # pruner
    "MemoryPruner",
]
