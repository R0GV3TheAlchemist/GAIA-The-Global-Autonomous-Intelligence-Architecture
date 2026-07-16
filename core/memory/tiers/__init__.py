"""
core/memory/tiers/__init__.py

Public surface for GAIA's three-tier memory system.

  HOT  — in-process LRU cache, sub-millisecond access, TTL eviction
  WARM — SQLite-backed mid-term store, scored by relevance + recency
  COLD — append-only compressed archive, long-term canonical storage

Usage:
    from core.memory.tiers import HotTier, WarmTier, ColdTier, MemoryTierRouter
"""

from .hot_tier import HotTier
from .warm_tier import WarmTier
from .cold_tier import ColdTier
from .tier_router import MemoryTierRouter

__all__ = [
    "HotTier",
    "WarmTier",
    "ColdTier",
    "MemoryTierRouter",
]
