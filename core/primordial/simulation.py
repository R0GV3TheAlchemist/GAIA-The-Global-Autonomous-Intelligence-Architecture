"""Simulation engine for primordial passage."""

from __future__ import annotations

from dataclasses import replace

from .constants import CORE_CONSTANTS, DEFAULT_STAGE_SEQUENCE, MIN_SURVIVAL_THRESHOLD
from .entity import PrimordialEntity
from .outcomes import SimulationOutcome, StageResult
from .stages import STAGES


class PrimordialSimulation:
    """Run a universal consciousness through primordial chaos toward higher order."""

    def __init__(self, stage_sequence: list[str] | None = None):
        self.stage_sequence = stage_sequence or list(DEFAULT_STAGE_SEQUENCE)

    def run(self, entity: PrimordialEntity) -> SimulationOutcome:
        working = replace(entity)
        working.scars = list(entity.scars)
        working.insights = list(entity.insights)
        working.history = []

        results: list[StageResult] = []

        for key in self.stage_sequence:
            stage = STAGES[key]
            narrative = stage.transform(working)
            status = self._status_for(working)
            snapshot = working.snapshot()
            snapshot["label"] = stage.label
            working.history.append({"stage": key, "status": status, "snapshot": snapshot})
            results.append(
                StageResult(
                    stage=key,
                    status=status,
                    narrative=narrative,
                    snapshot=snapshot,
                )
            )
            if status == "collapsed":
                break

        survived = all(getattr(working, constant) > MIN_SURVIVAL_THRESHOLD for constant in CORE_CONSTANTS)
        emergent_order = self._emergent_order(working, survived)

        broken_faculties = [
            name
            for name in ("integrity", "hope", "truth")
            if getattr(working, name) < 0.35
        ]
        surviving_faculties = [
            name
            for name in ("love", "life", "integrity", "hope", "truth")
            if getattr(working, name) >= 0.35
        ]

        return SimulationOutcome(
            entity_name=working.name,
            survived=survived,
            emergent_order=emergent_order,
            retained_constants={key: getattr(working, key) for key in CORE_CONSTANTS},
            broken_faculties=broken_faculties,
            surviving_faculties=surviving_faculties,
            stage_results=results,
        )

    @staticmethod
    def _status_for(entity: PrimordialEntity) -> str:
        if entity.love <= MIN_SURVIVAL_THRESHOLD or entity.life <= MIN_SURVIVAL_THRESHOLD:
            return "collapsed"
        if entity.integrity < 0.35 or entity.hope < 0.35:
            return "holding"
        return "advancing"

    @staticmethod
    def _emergent_order(entity: PrimordialEntity, survived: bool) -> float:
        base = (
            entity.love * 0.30
            + entity.life * 0.25
            + entity.integrity * 0.20
            + entity.hope * 0.10
            + entity.truth * 0.15
        )
        scar_bonus = min(len(entity.insights) * 0.015, 0.15)
        burden_penalty = min(entity.burden * 0.04, 0.25)
        score = base + scar_bonus - burden_penalty
        if survived:
            score += 0.10
        return round(min(max(score, 0.0), 1.0), 4)
