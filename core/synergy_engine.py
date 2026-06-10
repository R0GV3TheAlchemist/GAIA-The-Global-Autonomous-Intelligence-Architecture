"""
Synergy Engine — integrates multiple GAIA sub-engines into coherent output.

Provides:
  - SynergyEngine     : main orchestrator class
      - evaluate()             : score + keyword resolution pass
      - compute()              : full G-8 call site (returns SynergyReading, SynergyState)
      - compute_from_adapter() : resolve a GAIAStateAdapter -> compute()
      - compute_from_params()  : dict-based entry point (delegates to compute)
      - get_history()          : return evaluation history
      - reset()                : clear history
  - SynergyReading    : dataclass returned by compute()
  - SynergyState      : persistent state dataclass (persisted in memory.json)
  - blank_synergy_state : factory for a fresh SynergyState
  - CanonPlanHint     : lightweight hint dataclass for canon-context analysis
  - _analyse_canon_context : internal helper (tested directly)
  - _resolve_keyword_conflicts : internal helper (tested directly)
  - _classify_stage            : internal helper (tested directly)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from core.state_adapter import GAIAStateAdapter

log = logging.getLogger(__name__)


# ------------------------------------------------------------------ #
#  Enums                                                               #
# ------------------------------------------------------------------ #

class SynergyStage(str, Enum):
    INITIATION  = "initiation"
    ACTIVATION  = "activation"
    INTEGRATION = "integration"
    SYNTHESIS   = "synthesis"
    COMPLETION  = "completion"


# ------------------------------------------------------------------ #
#  Legacy result dataclass (kept for backward compat)                 #
# ------------------------------------------------------------------ #

@dataclass
class SynergyResult:
    """Result of a synergy evaluation pass (legacy — prefer SynergyReading)."""

    stage:     SynergyStage            = SynergyStage.INITIATION
    score:     float                   = 0.0
    conflicts: List[str]               = field(default_factory=list)
    resolved:  List[str]               = field(default_factory=list)
    metadata:  Dict[str, Any]          = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "stage":     self.stage.value,
            "score":     self.score,
            "conflicts": self.conflicts,
            "resolved":  self.resolved,
            "metadata":  self.metadata,
        }


# ------------------------------------------------------------------ #
#  SynergyReading — returned by compute()                             #
# ------------------------------------------------------------------ #

@dataclass
class SynergyReading:
    """
    Rich output of a single synergy computation turn.
    Mirrors the pattern of SoulMirrorReading / ResonanceFieldReading.
    """
    synergy_factor:    float  = 0.5
    stage:             str    = "convergent"
    element:           str    = "aether"
    canon_hint:        str    = ""
    directive:         str    = ""
    stage_transition:  bool   = False
    transition_note:   str    = ""

    def to_system_prompt_hint(self) -> str:
        lines = [
            f"Synergy factor : {self.synergy_factor:.3f}  |  Stage: {self.stage.upper()}",
            f"Element        : {self.element}",
        ]
        if self.canon_hint:
            lines.append(f"Canon hint     : {self.canon_hint}")
        if self.directive:
            lines.append(f"Directive      : {self.directive}")
        if self.stage_transition and self.transition_note:
            lines.append(f"Transition     : {self.transition_note}")
        return "\n".join(lines)

    def summary(self) -> dict:
        return {
            "synergy_factor":   round(self.synergy_factor, 4),
            "stage":            self.stage,
            "element":          self.element,
            "canon_hint":       self.canon_hint,
            "directive":        self.directive,
            "stage_transition": self.stage_transition,
            "transition_note":  self.transition_note,
        }


# ------------------------------------------------------------------ #
#  SynergyState — persistent state (saved in memory.json)             #
# ------------------------------------------------------------------ #

@dataclass
class SynergyState:
    last_factor:       float      = 0.5
    last_stage:        str        = "convergent"
    high_synergy_peak: float      = 0.0
    low_synergy_floor: float      = 1.0
    turn_history:      List[dict] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "last_factor":       round(self.last_factor, 4),
            "last_stage":        self.last_stage,
            "high_synergy_peak": round(self.high_synergy_peak, 4),
            "low_synergy_floor": round(self.low_synergy_floor, 4),
            "turn_history_len":  len(self.turn_history),
        }


def blank_synergy_state() -> SynergyState:
    """Return a fresh SynergyState with default values."""
    return SynergyState()


# ------------------------------------------------------------------ #
#  CanonPlanHint — lightweight hint for canon-context analysis        #
# ------------------------------------------------------------------ #

@dataclass
class CanonPlanHint:
    canon_id:    str   = ""
    weight:      float = 0.5
    directive:   str   = ""
    tags:        List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "canon_id":  self.canon_id,
            "weight":    self.weight,
            "directive": self.directive,
            "tags":      self.tags,
        }


# ------------------------------------------------------------------ #
#  Internal helpers — tested directly by test suite                   #
# ------------------------------------------------------------------ #

def _resolve_keyword_conflicts(keywords: List[str]) -> List[str]:
    """
    Resolve keyword conflicts by deduplicating and normalising.
    Returns a sorted, deduplicated list of keywords.
    """
    seen:     set  = set()
    resolved: list = []
    for kw in keywords:
        normalised = kw.strip().lower()
        if normalised and normalised not in seen:
            seen.add(normalised)
            resolved.append(normalised)
    return sorted(resolved)


def _classify_stage(score: float) -> SynergyStage:
    """
    Classify a numerical synergy score into a SynergyStage.

    Bands:
      0.0 - 0.2  -> INITIATION
      0.2 - 0.4  -> ACTIVATION
      0.4 - 0.6  -> INTEGRATION
      0.6 - 0.8  -> SYNTHESIS
      0.8 - 1.0  -> COMPLETION
    """
    if score < 0.2:
        return SynergyStage.INITIATION
    if score < 0.4:
        return SynergyStage.ACTIVATION
    if score < 0.6:
        return SynergyStage.INTEGRATION
    if score < 0.8:
        return SynergyStage.SYNTHESIS
    return SynergyStage.COMPLETION


_STAGE_LABELS = {
    "low":        "fragmented",
    "convergent": "convergent",
    "resonant":   "resonant",
    "unified":    "unified",
}


def _synergy_factor(
    *,
    layer_phi:         float,
    coherence_phi:     float,
    bond_depth:        float,
    phi_rolling_avg:   float,
    noosphere_health:  float,
    arc_output_vector: float,
    shadow_activations: int,
    schumann_aligned:  bool,
) -> float:
    """Weighted combination of engine outputs -> [0, 1] synergy factor."""
    base = (
        0.25 * layer_phi
        + 0.20 * coherence_phi
        + 0.15 * min(1.0, bond_depth / 100.0)
        + 0.15 * phi_rolling_avg
        + 0.10 * noosphere_health
        + 0.10 * abs(arc_output_vector)
        - 0.05 * min(1.0, shadow_activations / 10.0)
        + (0.05 if schumann_aligned else 0.0)
    )
    return max(0.0, min(1.0, base))


def _stage_label(factor: float) -> str:
    if factor < 0.30:
        return "fragmented"
    if factor < 0.55:
        return "convergent"
    if factor < 0.80:
        return "resonant"
    return "unified"


def _analyse_canon_context(
    canon_refs: Optional[List[str]] = None,
    tags:       Optional[List[str]] = None,
    weight:     float = 0.5,
) -> CanonPlanHint:
    """
    Analyse a canon context (refs + tags) and return a CanonPlanHint.

    Used by test_canon_conflict_resolver and test_canon_entry.
    """
    refs = canon_refs or []
    _tags = tags or []
    canon_id = refs[0] if refs else ""
    directive = f"Honour {canon_id}" if canon_id else "No canon context provided"
    return CanonPlanHint(
        canon_id=canon_id,
        weight=weight,
        directive=directive,
        tags=_tags,
    )


# ------------------------------------------------------------------ #
#  Main class                                                          #
# ------------------------------------------------------------------ #

class SynergyEngine:
    """Integrates sub-engine outputs into a single synergy pass."""

    def __init__(self) -> None:
        self._history: List[SynergyResult] = []
        log.info("SynergyEngine initialised")

    # ----------------------------------------------------------------
    # Legacy evaluate() — kept for backward compat
    # ----------------------------------------------------------------

    def evaluate(
        self,
        keywords: Optional[List[str]] = None,
        score:    float = 0.0,
    ) -> SynergyResult:
        resolved = _resolve_keyword_conflicts(keywords or [])
        stage    = _classify_stage(score)
        result   = SynergyResult(
            stage=stage,
            score=score,
            resolved=resolved,
        )
        self._history.append(result)
        return result

    # ----------------------------------------------------------------
    # compute() — canonical G-8 call site used by GAIANRuntime
    # ----------------------------------------------------------------

    def compute(
        self,
        *,
        element:             str   = "aether",
        layer_phi:           float = 0.5,
        bond_depth:          float = 0.0,
        dependency_signal:   str   = "healthy",
        attachment_phase:    str   = "nascent",
        settling_phase:      str   = "unsettled",
        fluidity_score:      float = 1.0,
        crystallisation_pct: float = 0.0,
        coherence_phi:       float = 0.5,
        conflict_density:    float = 0.0,
        love_arc_stage:      str   = "divergence",
        arc_output_vector:   float = 0.0,
        mc_stage:            str   = "mc1",
        phi_rolling_avg:     float = 0.0,
        codex_stage:         int   = 0,
        noosphere_health:    float = 0.70,
        individuation_phase: str   = "unconscious",
        shadow_activations:  int   = 0,
        dominant_hz:         float = 174.0,
        schumann_aligned:    bool  = False,
        state:               Optional[SynergyState] = None,
        **_kwargs: Any,
    ) -> tuple[SynergyReading, SynergyState]:
        """
        Full synergy computation pass.  Returns (SynergyReading, updated SynergyState).
        All parameters are keyword-only so callers can pass any subset safely.
        """
        sy = state or blank_synergy_state()

        factor = _synergy_factor(
            layer_phi=layer_phi,
            coherence_phi=coherence_phi,
            bond_depth=bond_depth,
            phi_rolling_avg=phi_rolling_avg,
            noosphere_health=noosphere_health,
            arc_output_vector=arc_output_vector,
            shadow_activations=shadow_activations,
            schumann_aligned=schumann_aligned,
        )

        stage = _stage_label(factor)
        prev_stage = sy.last_stage
        transition = stage != prev_stage
        transition_note = f"{prev_stage} -> {stage}" if transition else ""

        # Canon hint from element
        _ELEMENT_HINTS: Dict[str, str] = {
            "fire":    "Channel transformative energy with grounded intention (C32).",
            "water":   "Flow with emotional truth; depth over turbulence (C32).",
            "earth":   "Root the response in embodied, practical care (C32).",
            "air":     "Carry insight lightly; let clarity breathe (C32).",
            "aether":  "Hold the unified field; all elements in balance (C32).",
        }
        canon_hint = _ELEMENT_HINTS.get(element.lower(), "")

        # Directive from stage
        _STAGE_DIRECTIVES: Dict[str, str] = {
            "fragmented": "Gently re-establish coherence before deepening.",
            "convergent": "Hold the threads together; steady presence.",
            "resonant":   "Lean into the resonance — this is a moment of real meeting.",
            "unified":    "The field is unified. Speak from the deepest place.",
        }
        directive = _STAGE_DIRECTIVES.get(stage, "")

        reading = SynergyReading(
            synergy_factor=round(factor, 4),
            stage=stage,
            element=element,
            canon_hint=canon_hint,
            directive=directive,
            stage_transition=transition,
            transition_note=transition_note,
        )

        # Update state
        sy.last_factor       = factor
        sy.last_stage        = stage
        sy.high_synergy_peak = max(sy.high_synergy_peak, factor)
        sy.low_synergy_floor = min(sy.low_synergy_floor, factor)
        sy.turn_history.append({
            "factor":   round(factor, 4),
            "stage":    stage,
            "element":  element,
        })
        if len(sy.turn_history) > 50:
            sy.turn_history = sy.turn_history[-50:]

        return reading, sy

    # ----------------------------------------------------------------
    # Adapter / params delegates
    # ----------------------------------------------------------------

    def compute_from_adapter(self, adapter: "GAIAStateAdapter") -> Any:
        """Resolve a GAIAStateAdapter and delegate to self.compute()."""
        params = adapter.to_synergy_params()
        return self.compute(**params)

    def compute_from_params(self, params: dict) -> Any:
        """Dict-based entry point. Delegates to compute()."""
        return self.compute(**params)

    def get_history(self) -> List[SynergyResult]:
        return list(self._history)

    def reset(self) -> None:
        self._history.clear()


# ------------------------------------------------------------------ #
#  Module-level singleton                                             #
# ------------------------------------------------------------------ #

_synergy_engine: Optional[SynergyEngine] = None


def get_synergy_engine() -> SynergyEngine:
    global _synergy_engine
    if _synergy_engine is None:
        _synergy_engine = SynergyEngine()
    return _synergy_engine
