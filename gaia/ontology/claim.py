"""
GAIA Ontology — Claim (Ontology-Aware)
The truth primitive of GAIA — now bound to ontology entities.
Every assertion is typed, entity-linked, evidence-weighted, and versioned.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

VALID_STATUSES = {
    "unknown",
    "speculative",
    "speculative-grounded",
    "supported",
    "verified",
    "disputed",
    "contradicted",
}


class Claim(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statement: str

    # Ontology bindings — what this claim is about
    entities: List[str] = []           # Entity IDs this claim references
    context: str = "global"            # Scope of truth (global | domain | local)
    domain: Optional[str] = None

    # Evidence
    sources: List[str] = []
    source_confidence: float = 0.5

    # Epistemic state
    confidence: float = 0.5
    status: str = "unknown"

    # Audit
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    contradiction_ids: List[str] = []
    provenance: List[str] = []
    metadata: Dict[str, Any] = {}

    def summary(self) -> str:
        snippet = self.statement[:72] + "..." if len(self.statement) > 72 else self.statement
        return (
            f"[{self.status.upper()} @{self.confidence:.2f}] "
            f"entities={len(self.entities)} '{snippet}'"
        )

    def __repr__(self) -> str:
        return self.summary()
