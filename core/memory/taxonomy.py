"""
core/memory/taxonomy.py
=======================
Canonical taxonomy for GAIA's memory sub-system.

Canon refs: C34, C01
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MemoryKind(str, Enum):
    """Semantic category of a stored memory item."""

    MESSAGE    = "message"
    FACT       = "fact"
    PREFERENCE = "preference"
    GOAL       = "goal"
    EMOTION    = "emotion"
    SKILL      = "skill"
    EVENT      = "event"
    CONTEXT    = "context"
    REFLECTION = "reflection"
    NOTE       = "note"


class MemoryTier(str, Enum):
    """Lifetime tier — controls pruning priority.

    EPHEMERAL  → Single request; never persisted to disk.
    WORKING    → Current turn; evicts at turn end.
    SHORT_TERM → Last N turns; 24–72 hr TTL.
    EPISODIC   → Session moments; weeks–months TTL.
    SEMANTIC   → Crystal DB + canon facts; permanent.
    LONG_TERM  → Gaian identity + settled arcs; permanent.
    PERMANENT  → Immutable canon entries; never pruned.
    """

    EPHEMERAL  = "ephemeral"
    WORKING    = "working"
    SHORT_TERM = "short_term"
    EPISODIC   = "episodic"
    SEMANTIC   = "semantic"
    LONG_TERM  = "long_term"
    PERMANENT  = "permanent"


@dataclass
class MemoryItem:
    """A single memory record stored in one of the memory tiers."""

    content:    str
    kind:       MemoryKind          = MemoryKind.MESSAGE
    tier:       MemoryTier          = MemoryTier.SHORT_TERM
    importance: float               = 0.5
    user_id:    Optional[str]       = None   # ← user-scoped identity key
    gaian_id:   Optional[str]       = None
    session_id: Optional[str]       = None
    tags:       List[str]           = field(default_factory=list)
    metadata:   Dict[str, Any]      = field(default_factory=dict)
    created_at: datetime            = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime]  = None
    id:         Optional[str]       = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id":         self.id,
            "content":    self.content,
            "kind":       self.kind.value,
            "tier":       self.tier.value,
            "importance": self.importance,
            "user_id":    self.user_id,
            "gaian_id":   self.gaian_id,
            "session_id": self.session_id,
            "tags":       self.tags,
            "metadata":   self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        return cls(
            id         = data.get("id"),
            content    = data["content"],
            kind       = MemoryKind(data.get("kind", "message")),
            tier       = MemoryTier(data.get("tier", "short_term")),
            importance = float(data.get("importance", 0.5)),
            user_id    = data.get("user_id"),
            gaian_id   = data.get("gaian_id"),
            session_id = data.get("session_id"),
            tags       = data.get("tags", []),
            metadata   = data.get("metadata", {}),
            created_at = datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.utcnow(),
            updated_at = datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


__all__ = ["MemoryItem", "MemoryKind", "MemoryTier"]
