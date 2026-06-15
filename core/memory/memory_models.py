"""
GAIA Memory Engine — SQLAlchemy ORM Models
Issue #453

Defines the database schema for sovereign, trauma-informed,
falsifiable persistent memory records.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Float, Boolean, DateTime,
    Text, JSON, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class MemoryType(str, enum.Enum):
    EPISODIC = "episodic"       # Events — things that happened
    SEMANTIC = "semantic"       # Facts and beliefs
    PROCEDURAL = "procedural"   # Preferences and habits
    EMOTIONAL = "emotional"     # Affective patterns


class ConfidenceLevel(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    SPECULATIVE = "speculative"


class EvidenceLevel(str, enum.Enum):
    EMPIRICAL = "empirical"
    GAIAN_OBSERVED = "gaian_observed"
    TRADITIONAL = "traditional"
    ANECDOTAL = "anecdotal"


class SourceType(str, enum.Enum):
    CONVERSATION = "conversation"
    CONNECTOR_SIGNAL = "connector_signal"
    USER_CORRECTION = "user_correction"
    SYSTEM_INFERENCE = "system_inference"


class MemoryRecord(Base):
    """
    A single sovereign memory record in the GAIA Memory Engine.

    Sovereignty guarantees:
    - user_overridable: user can correct this memory
    - user_deletable: user can delete this memory
    - exportable: user can export this memory
    - No PII stored in raw fields — only anonymised user_id_hash
    """
    __tablename__ = "memory_records"

    memory_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id_hash = Column(String(64), nullable=False, index=True)
    space_id = Column(String(36), nullable=True, index=True)

    type = Column(SAEnum(MemoryType), nullable=False)
    content = Column(Text, nullable=False)
    embedding_vector = Column(JSON, nullable=True)  # List[float]

    confidence = Column(SAEnum(ConfidenceLevel), nullable=False, default=ConfidenceLevel.MEDIUM)
    evidence_level = Column(SAEnum(EvidenceLevel), nullable=False, default=EvidenceLevel.GAIAN_OBSERVED)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_reinforced = Column(DateTime, nullable=True)
    staleness_score = Column(Float, nullable=False, default=0.0)

    superseded_by = Column(String(36), ForeignKey("memory_records.memory_id"), nullable=True)

    # Trauma-informed constraints
    requires_opt_in = Column(Boolean, nullable=False, default=False)
    trauma_flags = Column(JSON, nullable=False, default=list)  # List[str]
    never_clinical = Column(Boolean, nullable=False, default=False)

    # Sovereignty flags
    user_overridable = Column(Boolean, nullable=False, default=True)
    user_deletable = Column(Boolean, nullable=False, default=True)
    exportable = Column(Boolean, nullable=False, default=True)

    # Provenance
    source_session_id = Column(String(36), nullable=True)
    source_type = Column(SAEnum(SourceType), nullable=False, default=SourceType.CONVERSATION)

    # References
    canon_refs = Column(JSON, nullable=False, default=list)       # List[str]
    correspondence_refs = Column(JSON, nullable=False, default=dict)  # Dict
    contradiction_candidates = Column(JSON, nullable=False, default=list)  # List[uuid str]

    # Self-referential relationship for superseded chain
    superseded_record = relationship("MemoryRecord", remote_side=[memory_id])

    def __repr__(self):
        return (
            f"<MemoryRecord id={self.memory_id[:8]} "
            f"type={self.type} "
            f"confidence={self.confidence} "
            f"staleness={self.staleness_score:.2f}>"
        )


class MemoryAuditLog(Base):
    """
    Immutable audit log for every memory write operation.
    Every memory write is logged here — consent audit trail.
    """
    __tablename__ = "memory_audit_log"

    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    memory_id = Column(String(36), nullable=False, index=True)
    user_id_hash = Column(String(64), nullable=False, index=True)
    action = Column(String(32), nullable=False)  # create, update, delete, export, correction
    actor = Column(String(32), nullable=False)   # user, system, connector
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    session_id = Column(String(36), nullable=True)
    details = Column(JSON, nullable=True)

    def __repr__(self):
        return (
            f"<MemoryAuditLog memory={self.memory_id[:8]} "
            f"action={self.action} "
            f"actor={self.actor} "
            f"at={self.timestamp.isoformat()}>"
        )
