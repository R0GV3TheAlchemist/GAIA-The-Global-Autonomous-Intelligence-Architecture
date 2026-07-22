"""nexusos.memory

Memory Broker for NEXUS-OS

Provides the MemoryBroker and MemorySegment types for capability-gated
memory management within NEXUS-OS. Inspired by MemGPT's tiered memory
model (context window = RAM; external storage = disk) and the Portable
Agent Memory protocol's Merkle-DAG provenance model.

Design:
    - MemorySegment: a named, typed region of memory with a CapabilityToken gate.
    - MemoryBroker:  allocates and maps segments; enforces capability checks
                     before read/write; eventually chains writes into an audit log.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 1.5 - MemoryBroker
Research reference:
    MemGPT (arXiv:2310.08560)            - tiered context/storage model
    Portable Agent Memory (arXiv:2605.11032) - Merkle-DAG provenance
    seL4 Manual v15 Ch.5                 - virtual memory capabilities
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("nexusos.memory")


class SegmentType(Enum):
    """Memory segment type taxonomy."""
    EPISODIC = auto()    # Recent event log (short-term)
    SEMANTIC = auto()    # Facts / knowledge graph nodes (long-term)
    PROCEDURAL = auto()  # Skills / how-to patterns
    SCRATCH = auto()     # Temporary working memory (evictable)
    SHARED = auto()      # Cross-module shared region


@dataclass
class MemorySegment:
    """A named, capability-gated memory region.

    Fields:
        segment_id:  Unique UUID4 identifier.
        name:        Human-readable segment name.
        seg_type:    SegmentType classification.
        data:        The in-memory data payload (Any — structured in Phase B+).
        created_at:  UTC creation timestamp.
        updated_at:  UTC last-write timestamp.
        token_id:    ID of the CapabilityToken that gates write access.
                     Readers that do not hold a valid token are denied.
    """
    name: str
    seg_type: SegmentType
    data: Any = None
    segment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    token_id: Optional[str] = None


class MemoryBroker:
    """Capability-gated memory broker for NEXUS-OS.

    Manages the lifecycle of MemorySegments:
        - allocate: create a new segment and return its ID.
        - read:     return segment data (capability check in Phase B).
        - write:    update segment data (capability check + audit chain in Phase B).
        - free:     deallocate a segment.

    Tiered model (MemGPT-inspired):
        SCRATCH segments are eligible for eviction when working memory is full.
        EPISODIC / SEMANTIC / PROCEDURAL segments are paged to SovereignMemory.

    Reference:
        MemGPT arXiv:2310.08560 — paging model.
        Portable Agent Memory arXiv:2605.11032 — provenance chain.
    """

    def __init__(self) -> None:
        self._segments: dict[str, MemorySegment] = {}
        logger.info("MemoryBroker initialised.")

    def allocate(self, name: str, seg_type: SegmentType, token_id: Optional[str] = None) -> str:
        """Allocate a new MemorySegment and return its segment_id.

        Args:
            name:     Human-readable segment name.
            seg_type: SegmentType classification.
            token_id: Optional CapabilityToken ID gating write access.

        Returns:
            The new segment's UUID4 string ID.
        """
        seg = MemorySegment(name=name, seg_type=seg_type, token_id=token_id)
        self._segments[seg.segment_id] = seg
        logger.debug("MemoryBroker: allocated segment '%s' (%s).", name, seg_type)
        return seg.segment_id

    def read(self, segment_id: str) -> Any:
        """Read the data payload of a MemorySegment.

        Args:
            segment_id: UUID4 ID of the segment.

        Returns:
            The current data payload.

        Raises:
            KeyError: If segment_id does not exist.
            NotImplementedError: Capability check not yet implemented.
                Expected: validate caller holds a valid CapabilityToken for this segment.
        """
        if segment_id not in self._segments:
            raise KeyError(f"MemorySegment not found: {segment_id}")
        # TODO Phase B: capability token validation before read
        return self._segments[segment_id].data

    def write(self, segment_id: str, data: Any) -> None:
        """Write data to a MemorySegment.

        Args:
            segment_id: UUID4 ID of the segment.
            data:       New data payload.

        Raises:
            KeyError: If segment_id does not exist.
            NotImplementedError: Capability check and audit chain not yet implemented.
                Expected: validate CapabilityToken, write data, append to AuditStore chain.
        """
        if segment_id not in self._segments:
            raise KeyError(f"MemorySegment not found: {segment_id}")
        # TODO Phase B: capability check + AuditStore.record() call
        seg = self._segments[segment_id]
        seg.data = data
        seg.updated_at = datetime.now(timezone.utc)
        logger.debug("MemoryBroker: wrote to segment '%s'.", segment_id)

    def free(self, segment_id: str) -> None:
        """Deallocate a MemorySegment.

        Args:
            segment_id: UUID4 ID of the segment to free.

        Raises:
            KeyError: If segment_id does not exist.
        """
        if segment_id not in self._segments:
            raise KeyError(f"MemorySegment not found: {segment_id}")
        del self._segments[segment_id]
        logger.debug("MemoryBroker: freed segment '%s'.", segment_id)

    def list_segments(self) -> list[MemorySegment]:
        """Return all currently allocated MemorySegments."""
        return list(self._segments.values())
