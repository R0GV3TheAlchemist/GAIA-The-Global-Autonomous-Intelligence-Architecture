"""
GAIA Ontology — Relationship
Typed, confidence-weighted directed edges between entities.
Every connection in GAIA is explicit, typed, and evidence-linked.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uuid

# Canonical relationship types in the GAIA ontology
RELATIONSHIP_TYPES = {
    # Causal
    "CAUSES", "ENABLES", "INHIBITS", "CORRELATES_WITH",
    # Structural
    "PART_OF", "CONTAINS", "EXTENDS", "IS_A",
    # Epistemic
    "SUPPORTS", "CONTRADICTS", "REFINES", "SUPERSEDES",
    # Temporal
    "PRECEDES", "FOLLOWS", "CO_OCCURS_WITH",
    # Operational
    "GOVERNS", "IMPLEMENTS", "QUERIES", "UPDATES",
    # General
    "RELATED_TO",
}


class Relationship(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    from_entity: str          # Entity ID
    to_entity: str            # Entity ID
    type: str                 # Must be in RELATIONSHIP_TYPES
    confidence: float = 0.5
    source: Optional[str] = None
    attributes: Dict[str, Any] = {}

    def model_post_init(self, __context: Any) -> None:
        if self.type not in RELATIONSHIP_TYPES:
            raise ValueError(
                f"Invalid relationship type '{self.type}'. "
                f"Valid types: {sorted(RELATIONSHIP_TYPES)}"
            )

    def to_edge_attrs(self) -> Dict[str, Any]:
        """Serialise for graph edge storage."""
        return {
            "id": self.id,
            "type": self.type,
            "confidence": self.confidence,
            "source": self.source,
        }

    def __repr__(self) -> str:
        return (
            f"Relationship({self.from_entity[:8]}... "
            f"--[{self.type} @{self.confidence:.2f}]--> "
            f"{self.to_entity[:8]}...)"
        )
