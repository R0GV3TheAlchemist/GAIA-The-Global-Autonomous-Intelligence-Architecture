"""
GAIA Node
The atomic unit of the distributed GAIA network.
Each node is a semi-autonomous epistemic processor:
  - maintains its own local world state
  - evaluates claims independently
  - proposes updates to the network
  - syncs with peers to form consensus
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime


class GAIANode(BaseModel):
    """
    A single node in the GAIA distributed network.

    In v0.4 this is the data model.
    In v0.5+ each node will run as an independent process / microservice.
    """
    id: str = Field(default_factory=lambda: f"node_{str(uuid.uuid4())[:8]}")
    name: str = "unnamed-node"
    local_world_state: Dict[str, Any] = {}
    ontology_fragment: Dict[str, Any] = {}  # this node's slice of the ontology
    peers: List[str] = []                   # peer node IDs or endpoint URLs
    trust_score: float = 1.0               # 0.0–1.0; used in weighted consensus
    domain_specialisation: Optional[str] = None  # e.g. "biophotonics", "architecture"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_sync: Optional[datetime] = None
    sync_count: int = 0

    def update_state(self, claim_id: str, entry: Dict[str, Any]) -> None:
        """Update this node's local world state with a new claim entry."""
        self.local_world_state[claim_id] = {
            **entry,
            "node_id": self.id,
            "node_trust": self.trust_score
        }

    def get_state_snapshot(self) -> Dict[str, Any]:
        return {
            "node_id":    self.id,
            "name":       self.name,
            "trust":      self.trust_score,
            "domain":     self.domain_specialisation,
            "state":      dict(self.local_world_state),
            "claim_count": len(self.local_world_state),
            "snapshot_at": datetime.utcnow().isoformat()
        }

    def record_sync(self) -> None:
        self.last_sync = datetime.utcnow()
        self.sync_count += 1

    def __repr__(self) -> str:
        return (
            f"GAIANode(id={self.id}, name={self.name}, "
            f"claims={len(self.local_world_state)}, "
            f"trust={self.trust_score:.2f}, "
            f"domain={self.domain_specialisation})"
        )
