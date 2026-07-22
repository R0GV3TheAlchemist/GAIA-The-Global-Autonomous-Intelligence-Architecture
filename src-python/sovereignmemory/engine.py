"""sovereignmemory.engine

Sovereign Memory Engine for NEXUS-GAIA

Stores and retrieves GAIA's memories with capability-gated access,
bi-temporal indexing (event-time + ingest-time), and provenance
chaining. Backed by Zep/Graphiti in Phase B+ implementations.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 3
Research reference:
    Zep arXiv:2501.13956   - bi-temporal memory, 18.5x accuracy
    neo4j-agent-memory     - graph-native Python memory layer
    Portable Agent Memory  - Merkle-DAG provenance chain
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("sovereignmemory.engine")


class MemoryLayer(Enum):
    """Sovereign memory layer taxonomy."""
    EPISODIC = auto()
    SEMANTIC = auto()
    PROCEDURAL = auto()
    WORKING = auto()


@dataclass
class MemoryRecord:
    """A single memory record with bi-temporal metadata.

    Fields:
        record_id:   UUID4 unique identifier.
        layer:       MemoryLayer classification.
        content:     The memory payload (str, dict, or structured object).
        event_time:  When the event happened in the world (fact time).
        ingest_time: When this record was written to the store.
        tags:        Arbitrary string tags for retrieval.
        provenance:  Optional hash or ID of the source event/capability.
    """
    layer: MemoryLayer
    content: Any
    event_time: Optional[datetime] = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    ingest_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    tags: list[str] = field(default_factory=list)
    provenance: Optional[str] = None


class SovereignMemory:
    """GAIA's sovereign memory store.

    Phase A: in-memory list backing store.
    Phase B: swap to Zep/Graphiti + neo4j-agent-memory.

    Reference:
        GAIA_LAWS.md Law I  - Sovereignty of Self.
        ETHICS.md Commitment 5 - Memory Integrity.
    """

    def __init__(self) -> None:
        self._records: list[MemoryRecord] = []
        logger.info("SovereignMemory initialised.")

    def store(self, record: MemoryRecord) -> str:
        """Store a MemoryRecord and return its record_id."""
        self._records.append(record)
        logger.debug("SovereignMemory: stored record %s (%s).", record.record_id, record.layer)
        return record.record_id

    def recall(
        self,
        layer: Optional[MemoryLayer] = None,
        tag: Optional[str] = None,
        limit: int = 50,
    ) -> list[MemoryRecord]:
        """Recall memory records filtered by layer and/or tag.

        Args:
            layer:  Optional MemoryLayer filter.
            tag:    Optional tag substring filter.
            limit:  Maximum number of records to return.

        Returns:
            List of matching MemoryRecord instances (most recent first).
        """
        results = list(reversed(self._records))
        if layer is not None:
            results = [r for r in results if r.layer == layer]
        if tag:
            results = [r for r in results if any(tag in t for t in r.tags)]
        return results[:limit]

    def forget(self, record_id: str) -> bool:
        """Remove a MemoryRecord by ID (consent-driven deletion).

        Args:
            record_id: UUID4 ID of the record to remove.

        Returns:
            True if removed, False if not found.

        Note:
            Deletion is governed by GAIAN_LAWS.md Law II (Right to Forget).
            Phase B will add audit log entry before deletion.
        """
        before = len(self._records)
        self._records = [r for r in self._records if r.record_id != record_id]
        return len(self._records) < before

    def count(self) -> int:
        """Return the total number of stored records."""
        return len(self._records)
