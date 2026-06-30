"""
GAIA Relationship Model
Typed, confidence-weighted connections between entities in the world model.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import uuid
from datetime import datetime


# Canonical relationship types in the GAIA ontology
RELATIONSHIP_TYPES = {
    # Causal
    "CAUSES",
    "ENABLES",
    "INHIBITS",
    "CORRELATES_WITH",

    # Hierarchical
    "IS_A",
    "PART_OF",
    "CONTAINS",
    "EXTENDS",

    # Epistemic
    "SUPPORTS",
    "CONTRADICTS",
    "REFINES",
    "SUPERSEDES",

    # Temporal
    "PRECEDES",
    "FOLLOWS",
    "CO_OCCURS_WITH",

    # Operational
    "GOVERNS",
    "IMPLEMENTS",
    "QUERIES",
    "UPDATES",
}


@dataclass
class Relationship:
    """
    A typed, confidence-weighted directed edge between two entities.
    Every relationship in GAIA is explicit, typed, and evidence-linked.
    """
    id: str
    from_entity_id: str
    to_entity_id: str
    type: str                       # Must be in RELATIONSHIP_TYPES
    confidence: float               # 0.0 – 1.0
    source: Optional[str] = None   # provenance of this relationship
    attributes: Dict[str, Any] = None
    created_at: datetime = None

    @staticmethod
    def create(
        from_entity_id: str,
        to_entity_id: str,
        rel_type: str,
        confidence: float = 0.5,
        source: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> "Relationship":
        if rel_type not in RELATIONSHIP_TYPES:
            raise ValueError(f"Unknown relationship type: {rel_type}. "
                             f"Valid types: {RELATIONSHIP_TYPES}")
        return Relationship(
            id=str(uuid.uuid4()),
            from_entity_id=from_entity_id,
            to_entity_id=to_entity_id,
            type=rel_type,
            confidence=confidence,
            source=source,
            attributes=attributes or {},
            created_at=datetime.utcnow()
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from": self.from_entity_id,
            "to": self.to_entity_id,
            "type": self.type,
            "confidence": self.confidence,
            "source": self.source,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self) -> str:
        return (f"Relationship({self.from_entity_id[:8]}... "
                f"--[{self.type} @{self.confidence:.2f}]--> "
                f"{self.to_entity_id[:8]}...)")
