"""
core/memory/store_tier.py

StoreTier — flat-store tier enum used by the SQLite MemoryStore.
This is intentionally separate from core.memory.hierarchy.MemoryTier
(which has exactly 5 members for the hierarchy architecture).

StoreTier has 7 members covering all tier values the SQLite store
needs to persist and filter on, including PERMANENT and EPHEMERAL.

Canon Reference: C01 (Gaian Sovereignty), C-SENTINEL Article 4
Issue: #213
Version: 1.0.0
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class StoreTier(str, Enum):
    """Tier classification for the flat SQLite memory store."""
    WORKING    = "working"
    SHORT_TERM = "short_term"
    EPISODIC   = "episodic"
    SEMANTIC   = "semantic"
    LONG_TERM  = "long_term"
    PERMANENT  = "permanent"
    EPHEMERAL  = "ephemeral"

    @property
    def is_permanent(self) -> bool:
        return self in (StoreTier.SEMANTIC, StoreTier.LONG_TERM, StoreTier.PERMANENT)

    @classmethod
    def parse(cls, val: Optional[str]) -> "StoreTier":
        """Parse a string or None into a StoreTier, defaulting to EPHEMERAL."""
        if val is None:
            return cls.EPHEMERAL
        try:
            return cls(val)
        except ValueError:
            return cls.EPHEMERAL
