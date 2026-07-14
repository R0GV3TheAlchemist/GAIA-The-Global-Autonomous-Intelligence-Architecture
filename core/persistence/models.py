"""Domain models for the GAIA OS persistence layer.

These dataclasses are the canonical data-transfer objects shared between
the abstract repository interfaces (repositories.py) and all concrete
implementations (postgres_repositories.py, sqlite, in-memory, etc.).

All fields use Python stdlib types only — no ORM, no Pydantic dependency.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MemoryType(str, Enum):
    """Categorises the nature of a stored memory fragment."""
    EPISODIC = "episodic"       # a specific experienced event
    SEMANTIC = "semantic"       # general factual knowledge
    PROCEDURAL = "procedural"   # how-to / skill knowledge
    WORKING = "working"         # short-lived in-session context
    EMOTIONAL = "emotional"     # affective / value-laden memory


class MemoryStatus(str, Enum):
    """Lifecycle state of a memory record."""
    ACTIVE = "active"           # available for retrieval
    ARCHIVED = "archived"       # retained but deprioritised
    DELETED = "deleted"         # soft-deleted, not returned by default


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Memory:
    """A single memory fragment owned by one GAIAN.

    ``id`` is None before the record is persisted; the repository
    implementation assigns a UUID on first save.
    """
    user_id: str
    content: str
    memory_type: MemoryType = MemoryType.SEMANTIC
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    confidence: float = 1.0
    source: str | None = None
    status: MemoryStatus = MemoryStatus.ACTIVE
    id: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass
class SearchResult:
    """Audit record of a single search interaction.

    ``id`` is None before the record is persisted.
    """
    user_id: str
    query: str
    results: list[dict[str, Any]] = field(default_factory=list)
    total_found: int = 0
    search_time_ms: int = 0
    id: str | None = None
    created_at: datetime | None = None


__all__ = [
    "Memory",
    "MemoryStatus",
    "MemoryType",
    "SearchResult",
]
