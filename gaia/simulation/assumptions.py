"""
GAIA Simulation Assumptions Layer
The most important architectural recommendation in Phase 8.

Every simulation must explicitly record:
  - Assumptions (what we are taking as given)
  - Unknowns (what we cannot model)
  - Constraints (boundaries on validity)
  - Evidence base (what the assumptions rest on)
  - Confidence (how strongly we hold each assumption)

This prevents GAIA from presenting hypothetical outcomes as established facts.
A simulation without explicit assumptions is epistemically dishonest.

This is not optional infrastructure — it is the boundary between
'what is true' and 'what follows if we assume X'.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid


class Assumption(BaseModel):
    id: str = Field(default_factory=lambda: f"asm_{str(uuid.uuid4())[:6]}")
    statement: str
    confidence: float = 0.7         # how strongly we hold this assumption [0–1]
    evidence_sources: List[str] = []
    domain: Optional[str] = None
    flagged: bool = False           # True if this assumption is contested

    def __repr__(self) -> str:
        flag = " [CONTESTED]" if self.flagged else ""
        return f"Assumption('{self.statement[:60]}' @{self.confidence:.2f}{flag})"


class Unknown(BaseModel):
    id: str = Field(default_factory=lambda: f"unk_{str(uuid.uuid4())[:6]}")
    description: str
    impact_level: str = "medium"   # low | medium | high | critical
    domain: Optional[str] = None

    def __repr__(self) -> str:
        return f"Unknown('[{self.impact_level.upper()}] {self.description[:60]}')"


class Constraint(BaseModel):
    description: str
    type: str = "boundary"         # boundary | validity | scope | temporal


class AssumptionSet:
    """
    The complete assumptions context for a single simulation.
    Must be attached to every simulation before it can be evaluated.
    A simulation without assumptions is not a valid GAIA simulation.

    Example:
        asm_set = AssumptionSet(simulation_id="sim_abc123")
        asm_set.add_assumption(
            "Battery costs continue declining",
            confidence=0.80,
            evidence_sources=["IEA_2025", "BloombergNEF"]
        )
        asm_set.add_unknown(
            "Fusion breakthrough timeline",
            impact_level="critical"
        )
    """

    def __init__(self, simulation_id: str, title: str = ""):
        self.simulation_id = simulation_id
        self.title         = title
        self.assumptions:  List[Assumption] = []
        self.unknowns:     List[Unknown]    = []
        self.constraints:  List[Constraint] = []

    def add_assumption(
        self,
        statement: str,
        confidence: float = 0.7,
        evidence_sources: Optional[List[str]] = None,
        domain: Optional[str] = None,
        flagged: bool = False
    ) -> Assumption:
        asm = Assumption(
            statement=statement,
            confidence=confidence,
            evidence_sources=evidence_sources or [],
            domain=domain,
            flagged=flagged
        )
        self.assumptions.append(asm)
        return asm

    def add_unknown(
        self,
        description: str,
        impact_level: str = "medium",
        domain: Optional[str] = None
    ) -> Unknown:
        unk = Unknown(
            description=description,
            impact_level=impact_level,
            domain=domain
        )
        self.unknowns.append(unk)
        return unk

    def add_constraint(self, description: str, ctype: str = "boundary") -> None:
        self.constraints.append(Constraint(description=description, type=ctype))

    def is_valid(self) -> bool:
        """A simulation must have at least one assumption to be epistemically honest."""
        return len(self.assumptions) > 0

    def aggregate_confidence(self) -> float:
        """Product of all assumption confidences — overall assumption reliability."""
        if not self.assumptions:
            return 0.0
        result = 1.0
        for a in self.assumptions:
            result *= a.confidence
        return round(result, 4)

    def critical_unknowns(self) -> List[Unknown]:
        return [u for u in self.unknowns if u.impact_level == "critical"]

    def contested_assumptions(self) -> List[Assumption]:
        return [a for a in self.assumptions if a.flagged]

    def summary(self) -> Dict[str, Any]:
        return {
            "simulation_id":        self.simulation_id,
            "title":                self.title,
            "assumption_count":     len(self.assumptions),
            "unknown_count":        len(self.unknowns),
            "constraint_count":     len(self.constraints),
            "aggregate_confidence": self.aggregate_confidence(),
            "critical_unknowns":    len(self.critical_unknowns()),
            "contested_assumptions": len(self.contested_assumptions()),
            "is_valid":             self.is_valid(),
            "assumptions":  [a.model_dump() for a in self.assumptions],
            "unknowns":     [u.model_dump() for u in self.unknowns],
            "constraints":  [c.model_dump() for c in self.constraints]
        }

    def __repr__(self) -> str:
        return (
            f"AssumptionSet(sim={self.simulation_id}, "
            f"assumptions={len(self.assumptions)}, "
            f"unknowns={len(self.unknowns)}, "
            f"agg_confidence={self.aggregate_confidence():.3f})"
        )


from typing import Optional  # noqa
