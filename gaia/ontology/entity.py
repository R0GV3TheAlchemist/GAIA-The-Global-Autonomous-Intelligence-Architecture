"""
GAIA Entity Model
The atomic unit of the GAIA ontology.
Every thing that exists in GAIA's world model is an Entity.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import uuid
from datetime import datetime


@dataclass
class Entity:
    """
    An entity is any object, system, agent, concept, or phenomenon
    that GAIA tracks in its world model.

    Examples:
        - A human being (type: "Person")
        - A canon document (type: "KnowledgeNode")
        - A biophotonic coherence measurement (type: "Measurement")
        - A causal relationship claim (type: "CausalClaim")
        - A GAIA agent (type: "Agent")
    """
    id: str
    type: str
    name: str
    attributes: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    provenance: Optional[str] = None  # source of this entity's entry into the world model
    epistemic_status: str = "unknown"  # unknown | verified | speculative | disputed

    @staticmethod
    def create(
        type: str,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        provenance: Optional[str] = None,
        epistemic_status: str = "unknown"
    ) -> "Entity":
        """
        Factory method — creates a new entity with a UUID and UTC timestamps.
        All entities enter the world model through this method.
        """
        now = datetime.utcnow()
        return Entity(
            id=str(uuid.uuid4()),
            type=type,
            name=name,
            attributes=attributes or {},
            created_at=now,
            updated_at=now,
            provenance=provenance,
            epistemic_status=epistemic_status
        )

    def update_attributes(self, new_attributes: Dict[str, Any]) -> None:
        """Update entity attributes and refresh the updated_at timestamp."""
        self.attributes.update(new_attributes)
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serialise entity to dictionary for storage or transport."""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "attributes": self.attributes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "provenance": self.provenance,
            "epistemic_status": self.epistemic_status
        }

    def __repr__(self) -> str:
        return f"Entity(id={self.id[:8]}..., type={self.type}, name={self.name}, status={self.epistemic_status})"
