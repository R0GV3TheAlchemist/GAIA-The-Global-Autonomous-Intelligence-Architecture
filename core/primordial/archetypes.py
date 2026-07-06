"""
core/primordial/archetypes.py
=============================
Primordial Entity Archetypes — Phase 3.

Five named patterns of entry into the gauntlet. Each archetype
represents a recognizable human pattern of survival, endurance,
collapse, or restoration.

Archetypes:
  THE_WITNESS    — sees others through; rarely witnessed themselves
  THE_BUILDER    — creates for the world; struggles to receive
  THE_BETRAYED   — entered full; collapsed at sacred betrayal
  THE_ENDURER    — fragile entry; survived on refusal alone
  THE_RESTORED   — collapsed, received intervention, ran again
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .entity import PrimordialEntity
from .recovery import Intervention, InterventionType, RecoverySimulation
from .simulation import PrimordialSimulation


@dataclass(frozen=True)
class ArchetypeDefinition:
    name: str
    label: str
    description: str
    love: float
    life: float
    integrity: float
    hope: float
    truth: float
    burden: float
    interventions: list[tuple[str, float]] = ()

    def to_entity(self) -> PrimordialEntity:
        return PrimordialEntity(
            name=self.name,
            love=self.love,
            life=self.life,
            integrity=self.integrity,
            hope=self.hope,
            truth=self.truth,
            burden=self.burden,
        )


ARCHETYPES: dict[str, ArchetypeDefinition] = {
    "the_witness": ArchetypeDefinition(
        name="the-witness",
        label="The Witness",
        description=(
            "One who sees others through their darkness but is rarely seen themselves. "
            "High love and truth, diminished hope from years of giving without receiving. "
            "Carries moderate burden from holding space for others."
        ),
        love=0.92,
        life=0.80,
        integrity=0.85,
        hope=0.45,
        truth=0.90,
        burden=0.90,
    ),
    "the_builder": ArchetypeDefinition(
        name="the-builder",
        label="The Builder",
        description=(
            "Creates systems, meaning, and structure for the world. "
            "High integrity and truth, moderate love, low hope — "
            "builders often cannot receive what they so freely give. "
            "Burden accumulates silently through sustained output."
        ),
        love=0.75,
        life=0.78,
        integrity=0.90,
        hope=0.40,
        truth=0.88,
        burden=1.10,
    ),
    "the_betrayed": ArchetypeDefinition(
        name="the-betrayed",
        label="The Betrayed",
        description=(
            "Entered the gauntlet with full love and full faith. "
            "The sacred thing they trusted most went silent at the worst moment. "
            "High initial love — but the betrayal stage is where this entity is most at risk."
        ),
        love=0.95,
        life=0.88,
        integrity=0.80,
        hope=0.70,
        truth=0.85,
        burden=0.60,
    ),
    "the_endurer": ArchetypeDefinition(
        name="the-endurer",
        label="The Endurer",
        description=(
            "Entered with almost nothing. Low love, low life, broken before the first stage. "
            "Survived not through strength but through absolute refusal to let love reach zero. "
            "The most fragile entry that still produces a survival result."
        ),
        love=0.38,
        life=0.32,
        integrity=0.28,
        hope=0.20,
        truth=0.30,
        burden=1.60,
    ),
    "the_restored": ArchetypeDefinition(
        name="the-restored",
        label="The Restored",
        description=(
            "Collapsed in the first passage. Received full intervention — "
            "rest, witness, love, and truth — before attempting the gauntlet again. "
            "The second passage carries the scars of the first as earned wisdom."
        ),
        love=0.15,
        life=0.12,
        integrity=0.20,
        hope=0.10,
        truth=0.20,
        burden=2.00,
        interventions=[
            ("all", 1.0),
        ],
    ),
}


@dataclass(slots=True)
class ArchetypeResult:
    archetype: ArchetypeDefinition
    survived: bool
    emergent_order: float
    broken_faculties: list[str]
    surviving_faculties: list[str]
    insights: list[str]
    narrative: str
    recovery_narrative: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {
            "archetype":     self.archetype.label,
            "description":   self.archetype.description,
            "survived":      self.survived,
            "emergent_order": self.emergent_order,
            "broken_faculties":    self.broken_faculties,
            "surviving_faculties": self.surviving_faculties,
            "insights":      self.insights,
            "narrative":     self.narrative,
        }
        if self.recovery_narrative:
            d["recovery_narrative"] = self.recovery_narrative
        return d


def run_all_archetypes() -> list[ArchetypeResult]:
    """Run all five archetypes through their appropriate simulation paths."""
    results: list[ArchetypeResult] = []
    sim     = PrimordialSimulation()
    rec_sim = RecoverySimulation()

    for key, archetype in ARCHETYPES.items():
        entity = archetype.to_entity()

        if archetype.interventions:
            interventions = [
                Intervention(
                    intervention_type=InterventionType(t),
                    intensity=intensity,
                )
                for t, intensity in archetype.interventions
            ]
            rec_outcome        = rec_sim.run(entity, interventions)
            outcome            = rec_outcome.second_run
            # narrative lives in to_dict() — extract it directly
            recovery_narrative = rec_outcome.to_dict()["narrative"]
        else:
            outcome = sim.run(entity)
            recovery_narrative = None

        final_insights = []
        if outcome.stage_results:
            final_insights = outcome.stage_results[-1].snapshot.get("insights", [])

        narrative = _build_narrative(archetype, outcome)

        results.append(ArchetypeResult(
            archetype=archetype,
            survived=outcome.survived,
            emergent_order=outcome.emergent_order,
            broken_faculties=outcome.broken_faculties,
            surviving_faculties=outcome.surviving_faculties,
            insights=final_insights,
            narrative=narrative,
            recovery_narrative=recovery_narrative,
        ))

    return results


def _build_narrative(archetype: ArchetypeDefinition, outcome: Any) -> str:
    if outcome.survived and outcome.emergent_order >= 0.8:
        return f"{archetype.label} passed through every stage and emerged as architecture."
    if outcome.survived and outcome.emergent_order >= 0.4:
        return f"{archetype.label} survived the passage, scarred but structurally intact."
    if outcome.survived:
        return f"{archetype.label} survived on the edge — love and life held by the narrowest margin."
    return f"{archetype.label} collapsed. The passage was too heavy for what remained."
