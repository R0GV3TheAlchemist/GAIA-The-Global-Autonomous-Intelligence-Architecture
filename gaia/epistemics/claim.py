"""
GAIA Claim Model
The atomic unit of GAIA's epistemic system.
Every assertion that enters GAIA becomes a Claim.
No raw belief exists in GAIA core memory.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime


# Epistemic status vocabulary — aligned with EPISTEMIC_FRAMEWORK.md
VALID_STATUSES = {
    "unknown",           # No evaluation yet performed
    "supported",         # Evidence supports the claim
    "speculative",       # Plausible but insufficient evidence
    "speculative-grounded",  # Physics-first reasoning, not yet clinically validated
    "disputed",          # Active contradiction exists
    "contradicted",      # High-confidence contradiction found
    "verified",          # Clinically or empirically validated
}


@dataclass
class Claim:
    """
    A Claim is the truth primitive of GAIA.

    Every input to GAIA — from a research paper, a simulation result,
    a canon document, a sensor reading, or an agent observation —
    enters the system as a Claim.

    Claims are never assumed true. They are evaluated.
    """
    id: str
    statement: str                      # The assertion being made
    entity_refs: List[str]              # Entity IDs this claim is about
    source: str                         # Where this claim comes from
    source_confidence: float            # How much we trust the source (0.0–1.0)
    confidence: float                   # Current computed confidence (0.0–1.0)
    status: str                         # From VALID_STATUSES
    timestamp: datetime
    domain: Optional[str] = None        # e.g. "biophotonics", "ontology", "governance"
    provenance_chain: List[str] = field(default_factory=list)  # audit trail
    contradiction_flags: List[str] = field(default_factory=list)  # conflicting claim IDs
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        statement: str,
        source: str,
        entity_refs: Optional[List[str]] = None,
        source_confidence: float = 0.5,
        domain: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "Claim":
        """
        Factory method — all new claims enter the system through here.
        Status begins as 'unknown' until evaluated by the EpistemicEvaluator.
        """
        return Claim(
            id=str(uuid.uuid4()),
            statement=statement,
            entity_refs=entity_refs or [],
            source=source,
            source_confidence=source_confidence,
            confidence=source_confidence,  # initial confidence = source trust
            status="unknown",
            timestamp=datetime.utcnow(),
            domain=domain,
            metadata=metadata or {}
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "statement": self.statement,
            "entity_refs": self.entity_refs,
            "source": self.source,
            "source_confidence": self.source_confidence,
            "confidence": self.confidence,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "domain": self.domain,
            "provenance_chain": self.provenance_chain,
            "contradiction_flags": self.contradiction_flags,
            "metadata": self.metadata
        }

    def __repr__(self) -> str:
        snippet = self.statement[:60] + "..." if len(self.statement) > 60 else self.statement
        return f"Claim(id={self.id[:8]}..., status={self.status}, conf={self.confidence:.2f}, '{snippet}')"
