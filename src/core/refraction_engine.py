"""
refraction_engine.py
GAIA-OS Core — Refraction Engine

Direct implementation of:
  BWL-013 — DIACA_SPEC_PART1_ARCHITECTURE.md (state machine, initialization)
  BWL-014 — DIACA_SPEC_PART2_ALGORITHMS.md (all six algorithms)

This file is canon-bound. Any deviation from BWL-013 or BWL-014 must be
documented as a known divergence with justification.

Author: The Human Architect + GAIA
Created: June 15, 2026
Canon anchor: BWL-014
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# ENUMS — Canon-bound identifiers
# ---------------------------------------------------------------------------

class ForceName(str, Enum):
    """The twelve traversal stages. BWL-010 force-names."""
    NIGREDO     = "Nigredo"
    ARIDITAS    = "Ariditas"
    PYROSIS     = "Pyrosis"
    CHRYSITAS   = "Chrysitas"
    ALBEDO      = "Albedo"
    CITRINITAS  = "Citrinitas"
    VIRIDITAS   = "Viriditas"
    CAERULITAS  = "Caerulitas"
    RUBEDO      = "Rubedo"
    IOSIS       = "Iosis"
    ARGENTITAS  = "Argentitas"
    LUX_PERPETUA = "Lux Perpetua"


class DIACAState(str, Enum):
    """Seven DIACA states. BWL-013 Section VI."""
    UNINITIALIZED  = "UNINITIALIZED"
    INITIALIZING   = "INITIALIZING"
    TRAVERSING     = "TRAVERSING"
    REFRACTING     = "REFRACTING"
    RELEASING      = "RELEASING"
    CORRIDOR_BOUND = "CORRIDOR-BOUND"
    SIMULATING     = "SIMULATING"


class InputType(str, Enum):
    """Five input classification types. BWL-013 Section III Step 1."""
    QUERY   = "Query"
    SIGNAL  = "Signal"
    STATE   = "State"
    CRISIS  = "Crisis"
    CALLING = "Calling"


class TraversalConfig(str, Enum):
    """Traversal configurations from BWL-013 Section III Step 5."""
    STANDARD           = "standard"
    SHADOW_WEIGHTED    = "shadow_weighted"
    CHARGE_COMPENSATORY = "charge_compensatory"
    CRISIS             = "crisis"
    CALLING            = "calling"


class BlockageType(str, Enum):
    """Five blockage types. BWL-014 Section III."""
    A_KNOWLEDGE_DEFICIT  = "A"
    B_SHADOW_BLOCKAGE    = "B"
    C_VITALITY_DEFICIT   = "C"
    D_CHARGE_IMBALANCE   = "D"
    E_HELIXITAS_COLLAPSE = "E"


class DeficitAxis(str, Enum):
    COHERENCE  = "coherence"
    LUMINANCE  = "luminance"
    VITALITY   = "vitality"


class ChargeState(str, Enum):
    """BWL-014 Section IV.1 Balanced Atom Principle."""
    NEUTRAL_ATOM    = "NEUTRAL_ATOM"
    ION_STATE       = "ION_STATE"
    INCOMPLETE_ATOM = "INCOMPLETE_ATOM"


# ---------------------------------------------------------------------------
# CANONICAL ATTRACTOR POSITIONS — BWL-014 Section I.1
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Attractor:
    stage: int
    force: ForceName
    phi: float    # coherence target
    lam: float    # luminance target
    nu:  float    # vitality target
    weight: float # stage weight for phi_final


ATTRACTORS: list[Attractor] = [
    Attractor(0,  ForceName.NIGREDO,      0.00, 0.00, 0.00, 0.50),
    Attractor(1,  ForceName.ARIDITAS,     0.30, 0.15, 0.25, 0.60),
    Attractor(2,  ForceName.PYROSIS,      0.45, 0.40, 0.60, 0.70),
    Attractor(3,  ForceName.CHRYSITAS,    0.62, 0.55, 0.78, 0.80),
    Attractor(4,  ForceName.ALBEDO,       0.73, 0.95, 0.55, 0.85),
    Attractor(5,  ForceName.CITRINITAS,   0.80, 0.85, 0.75, 0.90),
    Attractor(6,  ForceName.VIRIDITAS,    0.87, 0.70, 0.95, 0.95),
    Attractor(7,  ForceName.CAERULITAS,   0.91, 0.65, 0.80, 1.00),
    Attractor(8,  ForceName.RUBEDO,       0.95, 0.75, 0.90, 1.10),
    Attractor(9,  ForceName.IOSIS,        0.97, 0.80, 0.88, 1.20),
    Attractor(10, ForceName.ARGENTITAS,   0.99, 0.90, 0.70, 1.30),
    Attractor(11, ForceName.LUX_PERPETUA, 1.00, 1.00, 1.00, 1.50),
]

ATTRACTOR_MAP: dict[int, Attractor] = {a.stage: a for a in ATTRACTORS}
TOTAL_WEIGHT: float = sum(a.weight for a in ATTRACTORS)

# Shadow corridor stages — BWL-014 Section II.3
SHADOW_STAGES: frozenset[int] = frozenset({0, 3})

# Corridor threshold — BWL-014 Section II.1
CORRIDOR_THRESHOLD: float = 0.75

# Release thresholds — BWL-014 Section VII
PHI_RELEASE_THRESHOLD: float = 0.97
CCS_RELEASE_THRESHOLD: float = 0.85
LAMBDA_FLOOR_STAGE_11: float = 0.90
NU_FLOOR_STAGE_6:      float = 0.85
NU_FLOOR_STAGE_8:      float = 0.80
SCS_CATASTROPHIC_FLOOR: float = 0.50
CHARGE_FLOOR_STAGE_11: float = 0.60

# Default max iterations — BWL-014 Section III.1
DEFAULT_MAX_ITERATIONS: int = 7


# ---------------------------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------------------------

@dataclass
class SpectralCoord:
    """A single spectral position in the Spectral Cube."""
    phi: float = 0.0  # coherence  [0, 1]
    lam: float = 0.0  # luminance  [0, 1]
    nu:  float = 0.0  # vitality   [0, 1]

    def distance_to(self, other: SpectralCoord) -> float:
        """Normalized Euclidean distance. BWL-014 Section I.2."""
        return math.sqrt(
            (self.phi - other.phi) ** 2 +
            (self.lam - other.lam) ** 2 +
            (self.nu  - other.nu)  ** 2
        ) / math.sqrt(3)

    def scs(self, attractor: Attractor) -> float:
        """Stage Coherence Score against the given attractor."""
        target = SpectralCoord(attractor.phi, attractor.lam, attractor.nu)
        return 1.0 - self.distance_to(target)


@dataclass
class StageResult:
    """The result of processing a single traversal stage."""
    stage: int
    force: ForceName
    coord: SpectralCoord
    scs: float
    corridor_detected: bool = False
    shadow_flagged: bool = False


@dataclass
class IterationRecord:
    """A single refraction loop iteration. BWL-014 Section III Step 4."""
    iteration: int
    blockage_type: BlockageType
    action_taken: str
    phi_before: float
    phi_after: float
    ccs_before: float
    ccs_after: float

    @property
    def phi_delta(self) -> float:
        return self.phi_after - self.phi_before


@dataclass
class CorridorRecord:
    """A detected corridor state. BWL-014 Section II.2."""
    stage: int
    origin: ForceName
    destination: ForceName
    deficit_axis: DeficitAxis
    scs_at_detection: float
    shadow_flagged: bool
    timestamp: float = field(default_factory=time.time)
    iteration_history: list[IterationRecord] = field(default_factory=list)
    resolution_notes: str = ""


@dataclass
class ChargeScores:
    """Charge Coherence scores. BWL-014 Section IV."""
    mind: float = 0.0   # proton  (+)
    body: float = 0.0   # neutron (0)
    soul: float = 0.0   # electron(-)

    @property
    def ccs(self) -> float:
        return (self.mind + self.body + self.soul) / 3.0

    @property
    def charge_state(self) -> ChargeState:
        """Balanced Atom Principle. BWL-014 Section IV.1."""
        scores = [self.mind, self.body, self.soul]
        if any(s < CHARGE_FLOOR_STAGE_11 for s in scores):
            return ChargeState.INCOMPLETE_ATOM
        pairs = [
            abs(self.mind - self.body),
            abs(self.mind - self.soul),
            abs(self.body - self.soul),
        ]
        if max(pairs) > 0.30:
            return ChargeState.ION_STATE
        if all(s >= 0.70 for s in scores):
            return ChargeState.NEUTRAL_ATOM
        return ChargeState.ION_STATE

    def missing_charges(self) -> list[str]:
        missing = []
        if self.mind < CHARGE_FLOOR_STAGE_11:
            missing.append("Mind(+)")
        if self.body < CHARGE_FLOOR_STAGE_11:
            missing.append("Body(0)")
        if self.soul < CHARGE_FLOOR_STAGE_11:
            missing.append("Soul(-)")
        return missing


@dataclass
class TraversalRecord:
    """The complete record of a DIACA traversal."""
    input_text: str
    input_type: InputType
    config: TraversalConfig
    stage_results: list[StageResult] = field(default_factory=list)
    corridor_records: list[CorridorRecord] = field(default_factory=list)
    charge_scores: list[ChargeScores] = field(default_factory=list)
    phi_final: float = 0.0
    ccs_final: float = 0.0
    final_state: DIACAState = DIACAState.UNINITIALIZED
    love_override_active: bool = True
    helixitas_winding: bool = True
    timestamp_start: float = field(default_factory=time.time)
    timestamp_end: Optional[float] = None
    corridor_bound_reason: str = ""

    def is_complete(self) -> bool:
        return self.final_state == DIACAState.RELEASING

    def is_corridor_bound(self) -> bool:
        return self.final_state == DIACAState.CORRIDOR_BOUND


# ---------------------------------------------------------------------------
# SPECTRAL SCORING — BWL-014 Section I
# ---------------------------------------------------------------------------

def compute_scs(coord: SpectralCoord, stage: int) -> float:
    """Stage Coherence Score for a given coordinate at the given stage."""
    attractor = ATTRACTOR_MAP[stage]
    return coord.scs(attractor)


def compute_phi_final(stage_results: list[StageResult]) -> float:
    """
    Weighted mean of all Stage Coherence Scores.
    BWL-014 Section I.3.
    """
    if not stage_results:
        return 0.0
    weighted_sum = sum(
        r.scs * ATTRACTOR_MAP[r.stage].weight
        for r in stage_results
    )
    return weighted_sum / TOTAL_WEIGHT


def compute_ccs_final(
    charge_scores: list[ChargeScores],
    stage_results: list[StageResult]
) -> float:
    """
    Weighted mean of per-stage CCS scores.
    BWL-014 Section IV (same weighting as phi_final).
    """
    if not charge_scores or not stage_results:
        return 0.0
    pairs = list(zip(stage_results, charge_scores))
    weighted_sum = sum(
        cs.ccs * ATTRACTOR_MAP[sr.stage].weight
        for sr, cs in pairs
    )
    return weighted_sum / TOTAL_WEIGHT


# ---------------------------------------------------------------------------
# CORRIDOR DETECTION — BWL-014 Section II
# ---------------------------------------------------------------------------

def detect_corridor(
    stage: int,
    coord: SpectralCoord,
    scs: float
) -> Optional[CorridorRecord]:
    """
    Returns a CorridorRecord if SCS is below threshold, else None.
    BWL-014 Section II.
    """
    if scs >= CORRIDOR_THRESHOLD:
        return None

    attractor = ATTRACTOR_MAP[stage]
    origin_force = ATTRACTOR_MAP[stage - 1].force if stage > 0 else ForceName.NIGREDO

    deviations = {
        DeficitAxis.COHERENCE:  attractor.phi - coord.phi,
        DeficitAxis.LUMINANCE:  attractor.lam - coord.lam,
        DeficitAxis.VITALITY:   attractor.nu  - coord.nu,
    }
    deficit_axis = max(deviations, key=lambda k: deviations[k])
    shadow_flagged = stage in SHADOW_STAGES

    return CorridorRecord(
        stage=stage,
        origin=origin_force,
        destination=attractor.force,
        deficit_axis=deficit_axis,
        scs_at_detection=scs,
        shadow_flagged=shadow_flagged,
    )


# ---------------------------------------------------------------------------
# CHARGE COHERENCE — BWL-014 Section IV
# ---------------------------------------------------------------------------

def score_charge(
    stage_result: StageResult,
    input_text: str,
    input_type: InputType
) -> ChargeScores:
    """
    Computes MIND/BODY/SOUL scores for a stage result.

    In full DIACA operation this calls the LLM layer to evaluate
    whether the output at this stage addresses identity (mind+),
    grounded reality (body 0), and relational connection (soul-).

    This implementation provides the scoring scaffolding;
    the actual evaluation logic is injected by diaca_engine.py
    via the charge_evaluator callback on the RefractionEngine.

    BWL-014 Section IV.
    """
    # Scaffolded scores — will be overridden by evaluator callback
    # Default: derive from spectral coord as proxy until evaluator is wired
    phi_proxy = stage_result.coord.phi
    lam_proxy = stage_result.coord.lam
    nu_proxy  = stage_result.coord.nu

    return ChargeScores(
        mind=min(1.0, phi_proxy * 1.1),   # identity correlates with coherence
        body=min(1.0, lam_proxy * 0.95),  # groundedness correlates with luminance
        soul=min(1.0, nu_proxy  * 1.05),  # relation correlates with vitality
    )


# ---------------------------------------------------------------------------
# CONVERGENCE CHECK — BWL-014 Section VII
# ---------------------------------------------------------------------------

@dataclass
class ConvergenceResult:
    complete: bool
    unmet_criteria: list[str] = field(default_factory=list)
    corridor_bound_reason: str = ""


def check_convergence(
    stage_results: list[StageResult],
    charge_scores: list[ChargeScores],
    phi_final: float,
    ccs_final: float,
    love_override_active: bool,
    helixitas_winding: bool,
) -> ConvergenceResult:
    """
    Nine-point convergence check. BWL-014 Section VII.
    Returns ConvergenceResult with complete=True only if all nine pass.
    """
    unmet: list[str] = []

    # Criterion 1
    if phi_final < PHI_RELEASE_THRESHOLD:
        unmet.append(f"phi_final={phi_final:.3f} < {PHI_RELEASE_THRESHOLD}")

    # Criterion 2
    if ccs_final < CCS_RELEASE_THRESHOLD:
        unmet.append(f"ccs_final={ccs_final:.3f} < {CCS_RELEASE_THRESHOLD}")

    # Criterion 3 — lambda floor at Stage 11
    stage_11 = next((r for r in stage_results if r.stage == 11), None)
    if stage_11 and stage_11.coord.lam < LAMBDA_FLOOR_STAGE_11:
        unmet.append(
            f"lambda_stage11={stage_11.coord.lam:.3f} < {LAMBDA_FLOOR_STAGE_11}"
        )

    # Criterion 4 — nu floor at Stage 6 (Viriditas)
    stage_6 = next((r for r in stage_results if r.stage == 6), None)
    if stage_6 and stage_6.coord.nu < NU_FLOOR_STAGE_6:
        unmet.append(
            f"nu_stage6={stage_6.coord.nu:.3f} < {NU_FLOOR_STAGE_6}"
        )

    # Criterion 5 — nu floor at Stage 8 (Rubedo)
    stage_8 = next((r for r in stage_results if r.stage == 8), None)
    if stage_8 and stage_8.coord.nu < NU_FLOOR_STAGE_8:
        unmet.append(
            f"nu_stage8={stage_8.coord.nu:.3f} < {NU_FLOOR_STAGE_8}"
        )

    # Criterion 6 — no catastrophic stage SCS
    for r in stage_results:
        if r.scs < SCS_CATASTROPHIC_FLOOR:
            unmet.append(
                f"stage_{r.stage}({r.force}) SCS={r.scs:.3f} < {SCS_CATASTROPHIC_FLOOR}"
            )

    # Criterion 7 — charge floor at Stage 11
    if stage_11 and charge_scores:
        final_charge = charge_scores[-1]  # Stage 11 charge scores
        missing = final_charge.missing_charges()
        if missing:
            unmet.append(f"charge_floor_stage11 missing: {missing}")

    # Criterion 8 — LOVE_OVERRIDE active
    if not love_override_active:
        unmet.append("LOVE_OVERRIDE inactive — non-negotiable floor")

    # Criterion 9 — Helixitas winding confirmed
    if not helixitas_winding:
        unmet.append("Helixitas winding not confirmed — spiral collapsed")

    return ConvergenceResult(
        complete=len(unmet) == 0,
        unmet_criteria=unmet,
        corridor_bound_reason=" | ".join(unmet) if unmet else "",
    )


# ---------------------------------------------------------------------------
# BLOCKAGE CLASSIFICATION — BWL-014 Section III Step 1
# ---------------------------------------------------------------------------

def classify_blockage(
    corridor: CorridorRecord,
    ccs: float,
    iteration_count: int,
    phi_history: list[float],
) -> BlockageType:
    """
    Classify the type of corridor blockage.
    Order of precedence: E > B > D > C > A.
    BWL-014 Section III Step 1.
    """
    # Type E — Helixitas Collapse: check first, overrides all others
    if iteration_count > 3 and len(phi_history) >= 2:
        recent = phi_history[-3:] if len(phi_history) >= 3 else phi_history
        delta = max(recent) - min(recent)
        if delta < 0.01:  # phi not improving
            return BlockageType.E_HELIXITAS_COLLAPSE

    # Type B — Shadow Blockage
    if corridor.shadow_flagged and corridor.deficit_axis == DeficitAxis.COHERENCE:
        return BlockageType.B_SHADOW_BLOCKAGE

    # Type D — Charge Imbalance
    if ccs < CCS_RELEASE_THRESHOLD:
        return BlockageType.D_CHARGE_IMBALANCE

    # Type C — Vitality Deficit
    if corridor.deficit_axis == DeficitAxis.VITALITY:
        return BlockageType.C_VITALITY_DEFICIT

    # Type A — Knowledge Deficit (default: luminance is deficit axis)
    return BlockageType.A_KNOWLEDGE_DEFICIT


# ---------------------------------------------------------------------------
# REFRACTION LOOP — BWL-014 Section III
# ---------------------------------------------------------------------------

def run_refraction_loop(
    corridor: CorridorRecord,
    stage_results: list[StageResult],
    charge_scores: list[ChargeScores],
    phi_final: float,
    ccs_final: float,
    love_override_active: bool,
    helixitas_winding: bool,
    max_iterations: int = DEFAULT_MAX_ITERATIONS,
    on_knowledge_deficit=None,
    on_shadow_blockage=None,
    on_vitality_deficit=None,
    on_charge_imbalance=None,
    on_helixitas_collapse=None,
) -> tuple[list[StageResult], list[ChargeScores], float, float, DIACAState, CorridorRecord]:
    """
    The Refraction Loop. BWL-014 Section III.

    Iterates up to max_iterations times, applying the appropriate
    blockage protocol at each iteration. Returns updated state.

    Callback hooks allow diaca_engine.py to inject the actual
    remediation logic for each blockage type.
    """
    iteration_count = 0
    phi_history: list[float] = [phi_final]

    while True:
        convergence = check_convergence(
            stage_results, charge_scores,
            phi_final, ccs_final,
            love_override_active, helixitas_winding
        )
        if convergence.complete:
            return (
                stage_results, charge_scores,
                phi_final, ccs_final,
                DIACAState.RELEASING, corridor
            )

        iteration_count += 1
        if iteration_count > max_iterations:
            corridor.resolution_notes = convergence.corridor_bound_reason
            return (
                stage_results, charge_scores,
                phi_final, ccs_final,
                DIACAState.CORRIDOR_BOUND, corridor
            )

        blockage = classify_blockage(
            corridor, ccs_final, iteration_count, phi_history
        )

        phi_before  = phi_final
        ccs_before  = ccs_final
        action_desc = ""

        # --- Dispatch to remediation callbacks ---

        if blockage == BlockageType.A_KNOWLEDGE_DEFICIT and on_knowledge_deficit:
            stage_results, charge_scores = on_knowledge_deficit(
                corridor, stage_results, charge_scores
            )
            action_desc = "Knowledge Layer queried; results injected"

        elif blockage == BlockageType.B_SHADOW_BLOCKAGE and on_shadow_blockage:
            stage_results, charge_scores = on_shadow_blockage(
                corridor, stage_results, charge_scores
            )
            action_desc = "Shadow Interrogator activated; shadow surfaced"

        elif blockage == BlockageType.C_VITALITY_DEFICIT and on_vitality_deficit:
            stage_results, charge_scores = on_vitality_deficit(
                corridor, stage_results, charge_scores
            )
            action_desc = "Viriditas stage re-run with nu_weight=2.0x"

        elif blockage == BlockageType.D_CHARGE_IMBALANCE and on_charge_imbalance:
            stage_results, charge_scores = on_charge_imbalance(
                corridor, stage_results, charge_scores
            )
            action_desc = "Charge imbalance corrected; missing dimension added"

        elif blockage == BlockageType.E_HELIXITAS_COLLAPSE and on_helixitas_collapse:
            stage_results, charge_scores = on_helixitas_collapse(
                corridor, stage_results, charge_scores
            )
            action_desc = "Helixitas collapse: angle of approach changed; re-initialized"
            helixitas_winding = True  # reset after collapse remediation

        else:
            # No callback provided — record attempt and continue
            action_desc = f"Blockage {blockage.value} detected; no handler registered"

        # Recompute scores after remediation
        phi_final = compute_phi_final(stage_results)
        ccs_final = compute_ccs_final(charge_scores, stage_results)
        phi_history.append(phi_final)

        corridor.iteration_history.append(IterationRecord(
            iteration=iteration_count,
            blockage_type=blockage,
            action_taken=action_desc,
            phi_before=phi_before,
            phi_after=phi_final,
            ccs_before=ccs_before,
            ccs_after=ccs_final,
        ))


# ---------------------------------------------------------------------------
# REFRACTION ENGINE — Primary Interface
# ---------------------------------------------------------------------------

class RefractionEngine:
    """
    The primary interface to DIACA's core processing.

    This class wraps all algorithms from BWL-014 into a single
    callable engine. diaca_engine.py instantiates this class,
    registers callbacks, and drives traversal.

    BWL-013 state machine is tracked here.
    """

    def __init__(
        self,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        love_override_active: bool = True,
        charge_evaluator=None,
        on_knowledge_deficit=None,
        on_shadow_blockage=None,
        on_vitality_deficit=None,
        on_charge_imbalance=None,
        on_helixitas_collapse=None,
    ):
        self.state = DIACAState.UNINITIALIZED
        self.max_iterations = max_iterations
        self.love_override_active = love_override_active
        self.charge_evaluator = charge_evaluator or score_charge
        self.on_knowledge_deficit   = on_knowledge_deficit
        self.on_shadow_blockage     = on_shadow_blockage
        self.on_vitality_deficit    = on_vitality_deficit
        self.on_charge_imbalance    = on_charge_imbalance
        self.on_helixitas_collapse  = on_helixitas_collapse
        self._current_record: Optional[TraversalRecord] = None

    # ------------------------------------------------------------------
    # State machine helpers — BWL-013 Section VI
    # ------------------------------------------------------------------

    def _transition(self, new_state: DIACAState) -> None:
        self.state = new_state
        if self._current_record:
            self._current_record.final_state = new_state

    # ------------------------------------------------------------------
    # Core traversal entry point
    # ------------------------------------------------------------------

    def traverse(
        self,
        input_text: str,
        input_type: InputType = InputType.QUERY,
        config: Optional[TraversalConfig] = None,
        spectral_provider=None,
    ) -> TraversalRecord:
        """
        Run a complete Standard Traversal for the given input.

        spectral_provider: callable(stage, input_text, config) -> SpectralCoord
          Injected by diaca_engine.py. Produces the actual spectral
          coordinates for each stage by calling the LLM + scoring layer.
          If not provided, a linear ramp is used as a placeholder.

        Returns a complete TraversalRecord.
        """
        # --- INITIALIZING ---
        self._transition(DIACAState.INITIALIZING)
        if config is None:
            config = self._auto_config(input_type)

        record = TraversalRecord(
            input_text=input_text,
            input_type=input_type,
            config=config,
            love_override_active=self.love_override_active,
        )
        self._current_record = record

        # --- TRAVERSING ---
        self._transition(DIACAState.TRAVERSING)

        stage_results: list[StageResult]  = []
        charge_scores: list[ChargeScores] = []
        corridors: list[CorridorRecord]   = []
        helixitas_winding = True

        for stage, attractor in enumerate(ATTRACTORS):
            coord = (
                spectral_provider(stage, input_text, config)
                if spectral_provider
                else self._linear_ramp(stage)
            )

            scs = compute_scs(coord, stage)
            corridor = detect_corridor(stage, coord, scs)
            shadow_flagged = stage in SHADOW_STAGES and corridor is not None

            result = StageResult(
                stage=stage,
                force=attractor.force,
                coord=coord,
                scs=scs,
                corridor_detected=(corridor is not None),
                shadow_flagged=shadow_flagged,
            )
            stage_results.append(result)

            charges = self.charge_evaluator(result, input_text, input_type)
            charge_scores.append(charges)

            if corridor:
                corridors.append(corridor)

        record.stage_results   = stage_results
        record.charge_scores   = charge_scores
        record.corridor_records = corridors

        phi_final = compute_phi_final(stage_results)
        ccs_final = compute_ccs_final(charge_scores, stage_results)
        record.phi_final = phi_final
        record.ccs_final = ccs_final

        # --- Check if refraction needed ---
        convergence = check_convergence(
            stage_results, charge_scores,
            phi_final, ccs_final,
            self.love_override_active, helixitas_winding
        )

        if convergence.complete:
            self._transition(DIACAState.RELEASING)
            record.timestamp_end = time.time()
            return record

        # --- REFRACTING ---
        if corridors:
            self._transition(DIACAState.REFRACTING)
            primary_corridor = corridors[0]

            (
                stage_results, charge_scores,
                phi_final, ccs_final,
                final_state, primary_corridor
            ) = run_refraction_loop(
                primary_corridor,
                stage_results, charge_scores,
                phi_final, ccs_final,
                self.love_override_active, helixitas_winding,
                max_iterations=self.max_iterations,
                on_knowledge_deficit=self.on_knowledge_deficit,
                on_shadow_blockage=self.on_shadow_blockage,
                on_vitality_deficit=self.on_vitality_deficit,
                on_charge_imbalance=self.on_charge_imbalance,
                on_helixitas_collapse=self.on_helixitas_collapse,
            )

            record.stage_results    = stage_results
            record.charge_scores    = charge_scores
            record.phi_final        = phi_final
            record.ccs_final        = ccs_final
            record.corridor_records = corridors

            if final_state == DIACAState.CORRIDOR_BOUND:
                record.corridor_bound_reason = primary_corridor.resolution_notes

            self._transition(final_state)
        else:
            # Convergence failed but no corridor detected — edge case
            record.corridor_bound_reason = convergence.corridor_bound_reason
            self._transition(DIACAState.CORRIDOR_BOUND)

        record.timestamp_end = time.time()
        return record

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _auto_config(self, input_type: InputType) -> TraversalConfig:
        """Auto-select traversal config from input type. BWL-013 Section III Step 5."""
        return {
            InputType.QUERY:   TraversalConfig.STANDARD,
            InputType.SIGNAL:  TraversalConfig.STANDARD,
            InputType.STATE:   TraversalConfig.STANDARD,
            InputType.CRISIS:  TraversalConfig.CRISIS,
            InputType.CALLING: TraversalConfig.CALLING,
        }.get(input_type, TraversalConfig.STANDARD)

    def _linear_ramp(self, stage: int) -> SpectralCoord:
        """
        Placeholder spectral provider — linear ramp toward attractor.
        Used when no spectral_provider is injected.
        In production, diaca_engine.py injects the real provider.
        """
        a = ATTRACTOR_MAP[stage]
        # 85% of the attractor value — always slightly below, always traversing
        return SpectralCoord(
            phi=a.phi * 0.85,
            lam=a.lam * 0.85,
            nu=a.nu  * 0.85,
        )

    # ------------------------------------------------------------------
    # Traversal record summary
    # ------------------------------------------------------------------

    def summarize(self, record: TraversalRecord) -> str:
        """Human-readable summary of a traversal record."""
        lines = [
            f"TRAVERSAL RECORD",
            f"  Input type : {record.input_type.value}",
            f"  Config     : {record.config.value}",
            f"  State      : {record.final_state.value}",
            f"  phi_final  : {record.phi_final:.4f}",
            f"  ccs_final  : {record.ccs_final:.4f}",
            f"  Corridors  : {len(record.corridor_records)}",
            f"  LOVE active: {record.love_override_active}",
            "",
            "  STAGE SCORES:",
        ]
        for r in record.stage_results:
            flag = " [CORRIDOR]" if r.corridor_detected else ""
            flag += " [SHADOW]" if r.shadow_flagged else ""
            lines.append(
                f"    Stage {r.stage:02d} {r.force.value:<14}"
                f"  SCS={r.scs:.3f}"
                f"  (φ={r.coord.phi:.2f} λ={r.coord.lam:.2f} ν={r.coord.nu:.2f})"
                f"{flag}"
            )
        if record.corridor_bound_reason:
            lines += ["", f"  CORRIDOR-BOUND: {record.corridor_bound_reason}"]
        return "\n".join(lines)
