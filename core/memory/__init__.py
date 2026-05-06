"""
core.memory — Phase 2A: Persistent Semantic Memory
====================================================
Public surface for GAIA-OS's long-term, cross-session memory layer.

Quick-start (offline / sovereign)
----------------------------------
    from core.memory import MemoryStore, MemoryItem, MemoryKind, MemoryTier
    from core.memory import SentenceTransformerEmbedder, MemoryPruner

    embedder = SentenceTransformerEmbedder()  # downloads ~80 MB on first use
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
        print(hit.item.text, hit.score)

Alternative backends
--------------------
    from core.memory import OllamaEmbedder   # local Ollama daemon
    from core.memory import OpenAIEmbedder   # OpenAI API
    from core.memory import FallbackEmbedder # hash-based, tests only
"""

from .taxonomy import MemoryKind, MemoryTier, MemoryItem
from .embedder import (
    EmbeddingProvider,
    SentenceTransformerEmbedder,
    OllamaEmbedder,
    OpenAIEmbedder,
    FallbackEmbedder,
)
from .store import MemoryStore, RetrievedMemory
from .pruner import MemoryPruner

__all__ = [
    # taxonomy
    "MemoryKind",
    "MemoryTier",
    "MemoryItem",
    # embedders
    "EmbeddingProvider",
    "SentenceTransformerEmbedder",
    "OllamaEmbedder",
    "OpenAIEmbedder",
    "FallbackEmbedder",
    # store
    "MemoryStore",
    "RetrievedMemory",
    # pruner
    "MemoryPruner",
]
