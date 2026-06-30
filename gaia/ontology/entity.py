"""
GAIA Ontology — Entity
The atomic typed object in GAIA's model of reality.
Every thing that exists is an Entity with a type, name, and attributes.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import uuid

# Canonical entity types in the GAIA ontology
ENTITY_TYPES = {
    "PERSON",      # Human beings, agents with sovereignty
    "OBJECT",      # Physical or digital artifacts
    "CONCEPT",     # Abstract ideas, frameworks, principles
    "SYSTEM",      # Operational systems (AI, biological, social)
    "EVENT",       # Occurrences in time
    "PROCESS",     # Ongoing state-changing activities
    "DOMAIN",      # Fields of knowledge
    "MEASUREMENT", # Quantitative observations
}


class Entity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str                          # Must be in ENTITY_TYPES
    name: str
    attributes: Dict[str, Any] = {}
    description: Optional[str] = None
    epistemic_status: str = "unknown"  # unknown | verified | speculative | disputed
    domain: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if self.type not in ENTITY_TYPES:
            raise ValueError(
                f"Invalid entity type '{self.type}'. "
                f"Valid types: {sorted(ENTITY_TYPES)}"
            )

    def to_node_attrs(self) -> Dict[str, Any]:
        """Serialise for graph node storage."""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "epistemic_status": self.epistemic_status,
            "domain": self.domain,
            **self.attributes
        }

    def __repr__(self) -> str:
        return f"Entity(type={self.type}, name='{self.name}', status={self.epistemic_status})"
