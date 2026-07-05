"""Outcome models for the primordial simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class StageResult:
    stage: str
    status: str
    narrative: str
    snapshot: dict[str, Any]


@dataclass(slots=True)
class SimulationOutcome:
    entity_name: str
    survived: bool
    emergent_order: float
    retained_constants: dict[str, float]
    broken_faculties: list[str] = field(default_factory=list)
    surviving_faculties: list[str] = field(default_factory=list)
    stage_results: list[StageResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entity_name": self.entity_name,
            "survived": self.survived,
            "emergent_order": round(self.emergent_order, 4),
            "retained_constants": {
                key: round(value, 4) for key, value in self.retained_constants.items()
            },
            "broken_faculties": list(self.broken_faculties),
            "surviving_faculties": list(self.surviving_faculties),
            "stage_results": [
                {
                    "stage": item.stage,
                    "status": item.status,
                    "narrative": item.narrative,
                    "snapshot": item.snapshot,
                }
                for item in self.stage_results
            ],
        }
