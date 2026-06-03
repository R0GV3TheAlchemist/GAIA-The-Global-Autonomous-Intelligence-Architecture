"""Shared types for Sovereign Memory (Issue #66).

All public types that cross module boundaries live here to avoid
circular imports between __init__.py, vec_search.py, crypto.py, etc.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ---------------------------------------------------------------------------
# Memory tier enumeration
# ---------------------------------------------------------------------------

class MemoryTier(str, Enum):
    """Tiers in GAIA's sovereign memory hierarchy.

    Used by the memory router to decide which store to consult
    and in which order, and by tests to assert tier registration.
    """
    WORKING   = "working"    # Short-lived, in-process scratchpad
    SEMANTIC  = "semantic"   # Distilled patterns via sentence-transformers
    LONG_TERM = "long_term"  # Persistent episodic + semantic SQLite store
    BIOMETRIC = "biometric"  # Physiological signals (HRV, GSR, …)
    ARCHIVAL  = "archival"   # Cold compressed store for older episodes


# ---------------------------------------------------------------------------
# Core record types
# ---------------------------------------------------------------------------

@dataclass
class EpisodeRecord:
    episode_id   : str
    principal_id : str
    content      : str
    type         : str
    tags         : List[str]
    created_at   : int           # Unix ms
    deleted      : bool = False


@dataclass
class SemanticPattern:
    pattern_id   : str
    principal_id : str
    pattern      : str
    episode_ids  : List[str]
    confidence   : float
    tags         : List[str]
    created_at   : int


@dataclass
class BiometricSample:
    principal_id : str
    signal_type  : str
    value        : float
    source       : str
    timestamp    : int   # Unix ms


@dataclass
class SearchResult:
    episode_id   : str
    principal_id : str
    content      : str
    score        : float
    tier         : MemoryTier = MemoryTier.SEMANTIC
    tags         : List[str] = field(default_factory=list)
