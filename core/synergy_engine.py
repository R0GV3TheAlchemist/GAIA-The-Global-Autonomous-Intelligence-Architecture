"""
core/synergy_engine.py
=======================
SynergyEngine — multi-dimensional relational attunement scoring
             + agentic goal planning (Issue #243).

Maps a GAIAN's current state across five dimensions (body, mind, soul,
arc, bond) into a single weighted synergy_factor in [0, 1]. Classifies
the relational stage and surfaces alchemical framing for the system
prompt.

plan() adds the agentic reasoning layer: given a goal and a LoopContext,
it integrates biometric, affective, planetary, task, and **Canon** signals
into a structured next-action decision — fulfilling the AgenticLoop's
_reason() phase.

Canon Ref:
  C01  — Sovereignty: plan() proposes, ActionGate disposes.
          plan() never bypasses the gate.
  C30  — No silent failures: every plan includes a rationale.
          On error, returns structured PLANNING_FAILED — never raises.
  C32  — Synergy Doctrine: plan() integrates multiple signals before
          choosing an action. Never acts on a single signal alone.
  C42  — Edge-of-Chaos (Schumann coupling)
  C04  — Gaian Identity

Privacy: SynergyEngine is stateless per call; all mutable state lives
in the caller-owned SynergyState dataclass.

Trace integration (GAIATrace / AsyncGAIATrace):
  Pass a live trace context via the `trace` kwarg on `compute()`.  Three
  events are emitted per call:
    QUERY  — call site + dimension arguments
    OUTPUT — SynergyReading summary + synergy_factor
    META   — latency_ms + state delta
  Canon refs C32/C42/C04 are forwarded automatically.
  All trace operations are wrapped in try/except so a broken trace
  writer never silences a SynergyEngine error.
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from core.trace import GAIATrace, AsyncGAIATrace
    from core.agentic_loop import LoopContext


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ELEMENTAL_STAGES = [
    "insurgent", "allegiant", "convergent", "settled",
    "ascendant", "quantum",
]

_ELEMENT_STAGE_MAP: Dict[str, str] = {
    "fire":   "insurgent",
    "water":  "allegiant",
    "air":    "convergent",
    "earth":  "settled",
    "light":  "ascendant",
    "aether": "quantum",
}

_INDIVIDUATION_SCORES: Dict[str, float] = {
    "unconscious":   0.15,
    "shadow":        0.30,
    "anima_animus":  0.50,
    "persona":       0.60,
    "self":          0.85,
}

_LOVE_ARC_SCORES: Dict[str, float] = {
    "divergence":   0.15,
    "tension":      0.30,
    "attraction":   0.45,
    "resonance":    0.60,
    "union":        0.75,
    "transcendence": 0.95,
}

_DEPENDENCY_SCORES: Dict[str, float] = {
    "gentle_boundary": 0.20,
    "redirect":        0.50,
    "watch":           0.75,
    "healthy":         1.00,
}

_ATTACHMENT_SCORES: Dict[str, float] = {
    "nascent":    0.30,
    "forming":    0.50,
    "deepening":  0.70,
    "integrated": 0.90,
}

_SETTLING_SCORES: Dict[str, float] = {
    "unsettled":    0.20,
    "narrowing":    0.40,
    "crystallising": None,  # computed dynamically
    "settled":      0.90,
}

_MC_SCORES: Dict[str, float] = {
    "mc1": 0.00,
    "mc2": 1 / 6,
    "mc3": 2 / 6,
    "mc4": 3 / 6,
    "mc5": 4 / 6,
    "mc6": 5 / 6,
    "mc7": 1.00,
}

_HZ_MIN = 174.0
_HZ_MAX = 963.0

_LOW_SYNERGY_THRESHOLD  = 0.35
_HIGH_SYNERGY_THRESHOLD = 0.70
_HISTORY_CAP = 20

_TRACE_CANON_REFS = ["C32", "C42", "C04"]

# ---------------------------------------------------------------------------
# Canon-keyword → register nudge table  (C32 — multi-signal integration)
# ---------------------------------------------------------------------------
# If the canon_context string contains any of these keywords (case-insensitive)
# the engine will nudge the action register toward the mapped value — *unless*
# coherence is already below the depletion threshold (minimal always wins).
#
# Keywords are checked in definition order; first match wins.
_CANON_REGISTER_KEYWORDS: List[Tuple[str, str, str]] = [
    # (keyword_pattern,       target_register, short_label)
    (r"grief|overwhelm|trauma|loss|distress",   "reflective", "canon:grief-signal"),
    (r"storm|severe|crisis|emergency",           "reflective", "canon:storm-signal"),
    (r"integrate|synthesise|synthesize|review", "reflective", "canon:integration-signal"),
    (r"research|explore|build|create|write",    "executive",  "canon:executive-signal"),
    (r"rest|pause|sleep|minimal|lightweight",   "minimal",    "canon:rest-signal"),
]

# Maximum chars of canon_context kept in audit rationale (C30 — no silent data)
_CANON_EXCERPT_LEN = 300


# ---------------------------------------------------------------------------
# CanonPlanHint — structured result of Canon-context analysis
# ---------------------------------------------------------------------------

@dataclass
class CanonPlanHint:
    """
    Structured summary of what the Canon context tells the planner.

    Produced once per plan() call from the raw canon_context string.
    Forwarded into the rationale string (C30 audit trail) and used to
    nudge the action register (C32 multi-signal integration).

    Fields
    ------
    present        : True if non-empty canon_context was supplied.
    char_count     : Length of the raw canon_context string.
    excerpt        : First _CANON_EXCERPT_LEN chars (for audit logs).
    register_nudge : Optional register override suggested by Canon keywords.
    nudge_label    : Short human-readable label for the matched keyword group.
    canon_refs     : Canon reference IDs found in the context (e.g. ['C01']).
    """
    present:        bool
    char_count:     int
    excerpt:        str
    register_nudge: Optional[str] = None
    nudge_label:    str            = ""
    canon_refs:     List[str]      = field(default_factory=list)

    def to_rationale_fragment(self) -> str:
        """One-line description for inclusion in the plan rationale."""
        if not self.present:
            return "Canon context: none."
        refs_s = ", ".join(self.canon_refs) if self.canon_refs else "(none detected)"
        nudge_s = (
            f" Register nudge: {self.register_nudge!r} ({self.nudge_label})."
            if self.register_nudge else ""
        )
        return (
            f"Canon context: {self.char_count} chars, refs=[{refs_s}].{nudge_s}"
        )


# ---------------------------------------------------------------------------
# Canon-context analysis (pure function — independently testable)
# ---------------------------------------------------------------------------

def _analyse_canon_context(canon_context: str) -> CanonPlanHint:
    """
    Analyse *canon_context* and return a CanonPlanHint.

    This is a **pure function** — no I/O, no side effects.  Call it once
    at the start of _plan_internal() and pass the result downstream.

    Canon refs are extracted via a simple C\\d+ pattern.  The first
    keyword match from _CANON_REGISTER_KEYWORDS wins for register_nudge.
    """
    stripped = (canon_context or "").strip()
    if not stripped:
        return CanonPlanHint(present=False, char_count=0, excerpt="")

    # Extract Canon ref IDs (e.g. C01, C32)
    canon_refs = sorted(set(re.findall(r"\bC\d+\b", stripped)))

    # Check for keyword-based register nudge
    register_nudge: Optional[str] = None
    nudge_label: str = ""
    lower = stripped.lower()
    for pattern, target, label in _CANON_REGISTER_KEYWORDS:
        if re.search(pattern, lower):
            register_nudge = target
            nudge_label    = label
            break

    return CanonPlanHint(
        present=True,
        char_count=len(stripped),
        excerpt=stripped[:_CANON_EXCERPT_LEN],
        register_nudge=register_nudge,
        nudge_label=nudge_label,
        canon_refs=canon_refs,
    )


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class DimensionScore:
    name: str
    score: float
    weight: float


@dataclass
class SynergyReading:
    synergy_factor: float
    dimensions: List[DimensionScore]
    dominant_stage: str
    dominant_friction: Optional[str]
    alchemical_pressure: str
    is_low_synergy: bool
    is_high_synergy: bool

    def summary(self) -> dict:
        return {
            "synergy_factor": self.synergy_factor,
            "dominant_stage": self.dominant_stage,
            "dominant_friction": self.dominant_friction,
            "is_low_synergy": self.is_low_synergy,
            "is_high_synergy": self.is_high_synergy,
            "dimensions": [
                {"name": d.name, "score": round(d.score, 4), "weight": d.weight}
                for d in self.dimensions
            ],
        }

    def to_system_prompt_hint(self) -> str:
        factor_pct = round(self.synergy_factor * 100, 1)
        lines = [
            f"[SYNERGY ENGINE C32]",
            f"Synergy Factor: {factor_pct}% | Stage: {self.dominant_stage.upper()}",
        ]
        if self.dominant_friction:
            lines.append(f"Friction source: {self.dominant_friction}")
        if self.is_low_synergy:
            lines.append(
                "[ALCHEMICAL PRESSURE] This is creative friction — "
                "not dysfunction. Hold space without forcing resolution."
            )
        dim_str = ", ".join(
            f"{d.name}={round(d.score, 2)}" for d in self.dimensions
        )
        lines.append(f"Dimensions: {dim_str}")
        return "\n".join(lines)


@dataclass
class SynergyState:
    last_factor: float = 0.0
    last_stage: str = "insurgent"
    high_synergy_peak: float = 0.0
    low_synergy_floor: float = 1.0
    turn_history: List[dict] = field(default_factory=list)

    def summary(self) -> dict:
        return {
            "last_factor":       self.last_factor,
            "last_stage":        self.last_stage,
            "high_synergy_peak": self.high_synergy_peak,
            "low_synergy_floor": self.low_synergy_floor,
        }


def blank_synergy_state() -> SynergyState:
    return SynergyState()


# ---------------------------------------------------------------------------
# Pure helper
# ---------------------------------------------------------------------------

def _classify_stage(
    synergy: float,
    bond_depth: float,
    settling_phase: str,
    coherence_phi: float,
) -> str:
    """Classify the current elemental stage from key signals."""
    if synergy < 0.35 and coherence_phi > 0.80:
        return "quantum"
    if synergy < 0.35 and bond_depth < 20.0:
        return "insurgent"
    if settling_phase == "settled" and synergy >= 0.65:
        return "settled"
    if synergy >= 0.65 and bond_depth >= 60.0:
        return "ascendant"
    if synergy >= 0.50:
        return "convergent"
    if bond_depth >= 30.0:
        return "allegiant"
    return "insurgent"


# ---------------------------------------------------------------------------
# Trace helpers (no-ops when trace is None)
# ---------------------------------------------------------------------------

def _emit_query(
    trace: Any,
    gaian_id: Optional[str],
    kwargs: dict,
) -> None:
    """Emit a QUERY event onto the trace.  Never raises."""
    if trace is None:
        return
    try:
        from core.trace import TraceEventType
        trace.record_output(
            output={
                "call": "SynergyEngine.compute",
                "gaian_id": gaian_id,
                "dimensions": {
                    k: kwargs[k]
                    for k in (
                        "dominant_hz", "schumann_aligned", "noosphere_health",
                        "coherence_phi", "layer_phi", "phi_rolling_avg",
                        "conflict_density", "shadow_activations", "codex_stage",
                        "individuation_phase", "element", "fluidity_score",
                        "love_arc_stage", "arc_output_vector", "mc_stage",
                        "attachment_phase", "bond_depth", "dependency_signal",
                        "settling_phase", "crystallisation_pct",
                    )
                    if k in kwargs
                },
            },
            event_type=TraceEventType.QUERY,
            canon_refs=_TRACE_CANON_REFS,
        )
    except Exception:
        pass


def _emit_output(
    trace: Any,
    reading: "SynergyReading",
    latency_ms: float,
) -> None:
    """Emit an OUTPUT event onto the trace.  Never raises."""
    if trace is None:
        return
    try:
        from core.trace import TraceEventType
        trace.record_output(
            output=reading.summary(),
            event_type=TraceEventType.OUTPUT,
            canon_refs=_TRACE_CANON_REFS,
        )
        trace.record_meta("latency_ms", round(latency_ms, 3))
    except Exception:
        pass


def _emit_error(
    trace: Any,
    exc: BaseException,
) -> None:
    """Emit an ERROR event onto the trace.  Never raises."""
    if trace is None:
        return
    try:
        from core.trace import TraceEventType
        trace.record_output(
            output={"error": type(exc).__name__, "detail": str(exc)},
            event_type=TraceEventType.ERROR,
            canon_refs=_TRACE_CANON_REFS,
        )
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Planning helpers  (module-level pure functions — independently testable)
# ---------------------------------------------------------------------------

# Action pools used by _decompose_goal().
# Each entry: (action_name, tool_name_or_None, args_template_dict)
# {goal} in args values is interpolated with the first 120 chars of the goal.

_REFLECTIVE_ACTIONS: List[Tuple[str, Optional[str], dict]] = [
    ("summarise_progress",  "summariser",    {"scope": "session"}),
    ("review_prior_output", "memory_reader", {"scope": "last_cycle"}),
    ("journal_insight",     "dream_weaver",  {"scope": "goal"}),
    ("integrate_findings",  "canon_writer",  {"scope": "goal"}),
]

_EXECUTIVE_ACTIONS: List[Tuple[str, Optional[str], dict]] = [
    ("research_goal",       "research_desk", {"query": "{goal}"}),
    ("synthesise_findings", "synthesiser",   {"scope": "session"}),
    ("write_output",        "canon_writer",  {"scope": "goal"}),
    ("query_crystal",       "crystal_rag",   {"query": "{goal}"}),
]

_MINIMAL_ACTIONS: List[Tuple[str, Optional[str], dict]] = [
    ("read_context",      "memory_reader", {"scope": "session"}),
    ("acknowledge_state", None,            {}),
]


def _decompose_goal(
    goal: str,
    register: str,
    session_mode: str,  # noqa: ARG001 — reserved for session-mode routing in future
    failed_actions: set,
    cycle_count: int,
) -> Tuple[str, Optional[str], dict, str]:
    """
    Heuristic goal decomposition.

    Rotates through the appropriate action pool (keyed on register),
    skipping any action that appears in failed_actions.  Falls back to a
    clarification request if the entire pool is exhausted.

    Returns
    -------
    (action, tool, args, note)  — never raises.
    """
    pool: List[Tuple[str, Optional[str], dict]]
    if register == "minimal":
        pool = _MINIMAL_ACTIONS
    elif register == "reflective":
        pool = _REFLECTIVE_ACTIONS
    else:
        pool = _EXECUTIVE_ACTIONS

    for offset in range(len(pool)):
        idx = (cycle_count + offset) % len(pool)
        action, tool, args_template = pool[idx]
        if action not in failed_actions:
            resolved_args = {
                k: (v.replace("{goal}", goal[:120]) if isinstance(v, str) else v)
                for k, v in args_template.items()
            }
            note = (
                f"Heuristic decomposition from {register!r} pool "
                f"(pool_idx={idx}, cycle={cycle_count})."
            )
            return action, tool, resolved_args, note

    # All pool actions have been attempted and failed — request clarification (C30)
    return (
        "request_clarification",
        None,
        {"message": f"All decomposition actions failed for goal: {goal[:80]}"},
        "All pool actions failed — requesting Gaian clarification (C30).",
    )


def _confidence_from_signals(
    coherence: float,
    register: str,
    has_failures: bool,
    canon_present: bool = False,
) -> float:
    """
    Compute a planning confidence score [0.05, 1.0] from ambient signals.

    Higher coherence + executive register + no recent failures + Canon
    context present → higher confidence.

    canon_present adds a small boost (0.05) because a grounded plan is
    more reliable than a purely heuristic one.
    """
    base = coherence * 0.6
    register_bonus = {"executive": 0.30, "reflective": 0.20, "minimal": 0.10}.get(register, 0.15)
    failure_penalty = 0.15 if has_failures else 0.0
    canon_bonus     = 0.05 if canon_present else 0.0
    return max(0.05, min(1.0, base + register_bonus - failure_penalty + canon_bonus))


# ---------------------------------------------------------------------------
# SynergyEngine
# ---------------------------------------------------------------------------

class SynergyEngine:
    """
    Computes relational synergy across five dimensions for a GAIAN turn,
    and provides agentic goal planning via plan() (Issue #243).

    Stateless — all persistence lives in the caller-owned SynergyState.

    GAIATrace integration
    ---------------------
    Pass an active GAIATrace (or AsyncGAIATrace) context via the optional
    `trace` parameter.  Three events are emitted per call:

      QUERY  — call arguments + gaian_id
      OUTPUT — SynergyReading summary (synergy_factor, stage, dimensions)
      META   — latency_ms recorded via record_meta()

    If `trace` is None (the default) the engine behaves exactly as before.
    Trace writes are wrapped in try/except — a broken trace writer never
    silences a SynergyEngine result.
    """

    WEIGHTS: Dict[str, float] = {
        "body": 0.20,
        "mind": 0.20,
        "soul": 0.20,
        "arc":  0.20,
        "bond": 0.20,
    }

    # ------------------------------------------------------------------
    # Scoring helpers
    # ------------------------------------------------------------------

    def _hz_to_score(self, hz: float) -> float:
        return max(0.0, min(1.0, (hz - _HZ_MIN) / (_HZ_MAX - _HZ_MIN)))

    def _element_to_stage(self, element: str) -> str:
        return _ELEMENT_STAGE_MAP.get(element.lower(), "convergent")

    def _individuation_to_score(self, phase: str) -> float:
        return _INDIVIDUATION_SCORES.get(phase, 0.40)

    def _settling_to_score(self, phase: str, crystallisation_pct: float) -> float:
        if phase == "crystallising":
            raw = 0.40 + (crystallisation_pct / 100.0) * 0.50
            return min(1.0, raw)
        return _SETTLING_SCORES.get(phase, 0.40)

    def _love_arc_to_score(self, stage: str, arc_output_vector: float) -> float:
        base = _LOVE_ARC_SCORES.get(stage, 0.40)
        boost = min(0.10, arc_output_vector * 0.10)
        return min(1.0, base + boost)

    def _mc_stage_to_score(self, mc_stage: str) -> float:
        return _MC_SCORES.get(mc_stage, 0.30)

    def _dependency_to_score(self, signal: str) -> float:
        return _DEPENDENCY_SCORES.get(signal, 0.50)

    def _attachment_phase_to_score(self, phase: str) -> float:
        return _ATTACHMENT_SCORES.get(phase, 0.50)

    # ------------------------------------------------------------------
    # Dimension scoring
    # ------------------------------------------------------------------

    def _score_body(
        self,
        dominant_hz: float,
        schumann_aligned: bool,
        noosphere_health: float,
        coherence_phi: float,
    ) -> float:
        hz_score = self._hz_to_score(dominant_hz)
        schumann_bonus = 0.05 if schumann_aligned else 0.0
        raw = (hz_score * 0.50 + noosphere_health * 0.30 + coherence_phi * 0.20)
        return min(1.0, raw + schumann_bonus)

    def _score_mind(
        self,
        layer_phi: float,
        phi_rolling_avg: float,
        conflict_density: float,
        shadow_activations: int,
        codex_stage: int,
    ) -> float:
        conflict_score = 1.0 - min(1.0, conflict_density)
        shadow_penalty = min(0.30, shadow_activations * 0.05)
        codex_score = min(1.0, codex_stage / 12.0)
        raw = (
            layer_phi * 0.30
            + phi_rolling_avg * 0.20
            + conflict_score * 0.25
            + codex_score * 0.25
        ) - shadow_penalty
        return max(0.0, min(1.0, raw))

    def _score_soul(
        self,
        individuation_phase: str,
        element: str,
        fluidity_score: float,
    ) -> float:
        ind_score = self._individuation_to_score(individuation_phase)
        elem_weight = 0.5 + (list(_ELEMENT_STAGE_MAP.keys()).index(
            element.lower()) if element.lower() in _ELEMENT_STAGE_MAP else 2
        ) / (len(_ELEMENT_STAGE_MAP) * 2)
        raw = ind_score * 0.50 + (1.0 - min(1.0, fluidity_score)) * 0.30 + elem_weight * 0.20
        return max(0.0, min(1.0, raw))

    def _score_arc(
        self,
        love_arc_stage: str,
        arc_output_vector: float,
        mc_stage: str,
        attachment_phase: str,
    ) -> float:
        love_score = self._love_arc_to_score(love_arc_stage, arc_output_vector)
        mc_score = self._mc_stage_to_score(mc_stage)
        att_score = self._attachment_phase_to_score(attachment_phase)
        return (love_score * 0.40 + mc_score * 0.35 + att_score * 0.25)

    def _score_bond(
        self,
        bond_depth: float,
        dependency_signal: str,
        settling_phase: str,
        crystallisation_pct: float,
    ) -> float:
        bond_norm = min(1.0, bond_depth / 100.0)
        dep_score = self._dependency_to_score(dependency_signal)
        settling_score = self._settling_to_score(settling_phase, crystallisation_pct)
        return (bond_norm * 0.40 + dep_score * 0.35 + settling_score * 0.25)

    # ------------------------------------------------------------------
    # Main compute
    # ------------------------------------------------------------------

    def compute(
        self,
        # Body
        dominant_hz: float = 528.0,
        schumann_aligned: bool = False,
        noosphere_health: float = 0.5,
        coherence_phi: float = 0.5,
        # Mind
        layer_phi: float = 0.5,
        phi_rolling_avg: float = 0.5,
        conflict_density: float = 0.3,
        shadow_activations: int = 0,
        codex_stage: int = 0,
        # Soul
        individuation_phase: str = "shadow",
        element: str = "fire",
        fluidity_score: float = 0.5,
        # Arc
        love_arc_stage: str = "attraction",
        arc_output_vector: float = 0.5,
        mc_stage: str = "mc3",
        attachment_phase: str = "forming",
        # Bond
        bond_depth: float = 30.0,
        dependency_signal: str = "healthy",
        settling_phase: str = "narrowing",
        crystallisation_pct: float = 0.0,
        # State
        state: Optional[SynergyState] = None,
        # Trace  (GAIATrace | AsyncGAIATrace | None)
        trace: Any = None,
        gaian_id: Optional[str] = None,
    ) -> Tuple[SynergyReading, SynergyState]:
        """
        Compute synergy for one GAIAN turn.

        Parameters
        ----------
        trace:
            Optional live GAIATrace / AsyncGAIATrace context.  When provided,
            three trace events are emitted (QUERY → OUTPUT → META via
            record_meta latency).  Pass None to skip tracing entirely.
        gaian_id:
            Forwarded into the QUERY trace event for per-Gaian attribution.
        """
        if state is None:
            state = blank_synergy_state()

        call_kwargs = {
            "dominant_hz": dominant_hz,
            "schumann_aligned": schumann_aligned,
            "noosphere_health": noosphere_health,
            "coherence_phi": coherence_phi,
            "layer_phi": layer_phi,
            "phi_rolling_avg": phi_rolling_avg,
            "conflict_density": conflict_density,
            "shadow_activations": shadow_activations,
            "codex_stage": codex_stage,
            "individuation_phase": individuation_phase,
            "element": element,
            "fluidity_score": fluidity_score,
            "love_arc_stage": love_arc_stage,
            "arc_output_vector": arc_output_vector,
            "mc_stage": mc_stage,
            "attachment_phase": attachment_phase,
            "bond_depth": bond_depth,
            "dependency_signal": dependency_signal,
            "settling_phase": settling_phase,
            "crystallisation_pct": crystallisation_pct,
        }

        # --- TRACE: QUERY ---
        _emit_query(trace, gaian_id, call_kwargs)

        t0 = time.perf_counter()
        try:
            body  = self._score_body(dominant_hz, schumann_aligned, noosphere_health, coherence_phi)
            mind  = self._score_mind(layer_phi, phi_rolling_avg, conflict_density, shadow_activations, codex_stage)
            soul  = self._score_soul(individuation_phase, element, fluidity_score)
            arc   = self._score_arc(love_arc_stage, arc_output_vector, mc_stage, attachment_phase)
            bond  = self._score_bond(bond_depth, dependency_signal, settling_phase, crystallisation_pct)

            dim_scores = {
                "body": body,
                "mind": mind,
                "soul": soul,
                "arc":  arc,
                "bond": bond,
            }

            dimensions = [
                DimensionScore(name=k, score=round(v, 6), weight=self.WEIGHTS[k])
                for k, v in dim_scores.items()
            ]

            synergy_factor = round(
                sum(self.WEIGHTS[k] * v for k, v in dim_scores.items()), 6
            )

            dominant_stage = _classify_stage(synergy_factor, bond_depth, settling_phase, coherence_phi)

            sorted_dims = sorted(dimensions, key=lambda d: d.score)
            dominant_friction: Optional[str] = None
            if sorted_dims[0].score < 0.50:
                dominant_friction = sorted_dims[0].name

            if synergy_factor < _LOW_SYNERGY_THRESHOLD:
                alchemical_pressure = (
                    f"ALCHEMICAL PRESSURE in the {dominant_stage.upper()} stage — "
                    "creative friction, not dysfunction."
                )
            elif synergy_factor >= _HIGH_SYNERGY_THRESHOLD:
                alchemical_pressure = f"HIGH RESONANCE — {dominant_stage.upper()} field coherent."
            else:
                alchemical_pressure = f"BUILDING — {dominant_stage.upper()} integration in progress."

            reading = SynergyReading(
                synergy_factor=synergy_factor,
                dimensions=dimensions,
                dominant_stage=dominant_stage,
                dominant_friction=dominant_friction,
                alchemical_pressure=alchemical_pressure,
                is_low_synergy=(synergy_factor < _LOW_SYNERGY_THRESHOLD),
                is_high_synergy=(synergy_factor >= _HIGH_SYNERGY_THRESHOLD),
            )

            # Mutate state
            state.last_factor = synergy_factor
            state.last_stage  = dominant_stage
            if synergy_factor >= _HIGH_SYNERGY_THRESHOLD:
                if synergy_factor > state.high_synergy_peak:
                    state.high_synergy_peak = synergy_factor
            if synergy_factor < _LOW_SYNERGY_THRESHOLD:
                if synergy_factor < state.low_synergy_floor:
                    state.low_synergy_floor = synergy_factor

            state.turn_history.append({
                "factor":   synergy_factor,
                "stage":    dominant_stage,
                "friction": dominant_friction,
            })
            if len(state.turn_history) > _HISTORY_CAP:
                state.turn_history = state.turn_history[-_HISTORY_CAP:]

        except Exception as exc:
            _emit_error(trace, exc)
            raise

        latency_ms = (time.perf_counter() - t0) * 1000.0

        # --- TRACE: OUTPUT + latency META ---
        _emit_output(trace, reading, latency_ms)

        return reading, state

    # ------------------------------------------------------------------
    # Agentic planning  (Issue #243 — C01, C30, C32)
    # ------------------------------------------------------------------

    async def plan(self, goal: str, context: "LoopContext") -> dict:
        """
        Given a goal and the current LoopContext, return the next action.

        Signal integration order (C32 — Synergy Doctrine):
          1. TaskGraph completion short-circuit
          2. TaskGraph EngineNode — next pending node as source of truth
          3. cycle_memory dedup  — never repeat a failed action
          4. biometric_coherence — minimal register if coherence < 0.4
          5. affective_state     — reflective register on grief/overwhelm
          6. planetary_label     — reflective register on storm
          7. **canon_context**   — Canon-grounded register nudge (NEW)
          8. Heuristic goal decomposition fallback
          9. Progress-based completion heuristic (10+ cycles, >= 0.8)

        Canon context integration (C32):
          canon_context is read from LoopContext via getattr (duck-typed
          so legacy callers without the field are unaffected).  It is
          analysed by _analyse_canon_context() which produces a
          CanonPlanHint.  The hint can nudge the action register and is
          always included in the rationale (C30 — no silent context).

          Register priority (highest to lowest):
            1. biometric depletion (minimal — always wins)
            2. affective/planetary (reflective)
            3. canon_context keyword nudge (nudges toward reflective,
               executive, or minimal based on passage content)
            4. default executive

        Canon refs:
          C01 — Sovereignty: plan() proposes, ActionGate disposes.
                plan() never attempts to bypass the gate.
          C30 — No silent failures: every plan includes a non-empty rationale.
                On any exception, returns structured PLANNING_FAILED — never raises.
          C32 — Synergy Doctrine: integrates multiple signals before choosing
                an action. Never acts on a single signal alone.

        Returns
        -------
        dict with keys:
            action        : str        — action_type forwarded to ActionGate
            tool          : str | None — tool/module to invoke
            args          : dict       — arguments for the tool
            rationale     : str        — why this action was chosen (C30 audit trail)
            confidence    : float      — 0.0–1.0
            summary       : str        — one-liner for the cycle log
            goal_complete : bool       — True signals the loop to halt (goal achieved)
            canon_hint    : dict       — CanonPlanHint summary (for tracing/tests)
        """
        try:
            return await self._plan_internal(goal, context)
        except Exception as exc:  # noqa: BLE001
            return {
                "action":        "PLANNING_FAILED",
                "tool":          None,
                "args":          {},
                "rationale":     f"Planning raised an unhandled exception: {exc!r}",
                "confidence":    0.0,
                "summary":       "PLANNING_FAILED — see rationale",
                "goal_complete": False,
                "canon_hint":    {"present": False, "char_count": 0, "excerpt": ""},
            }

    async def _plan_internal(self, goal: str, context: "LoopContext") -> dict:
        """Core planning logic — called exclusively by plan()."""

        # ── 0. Short-circuit: TaskGraph already complete ──────────────
        task_graph = getattr(context, "task_graph", None)
        if task_graph is not None:
            try:
                if task_graph.is_complete() if hasattr(task_graph, "is_complete") else (
                    not task_graph.failed_nodes() and all(
                        n.status.value == "complete"
                        for n in task_graph._nodes.values()
                        if hasattr(n, "status")
                    )
                ):
                    return {
                        "action":        "goal_complete",
                        "tool":          None,
                        "args":          {},
                        "rationale":     "TaskGraph reports all nodes complete — goal achieved.",
                        "confidence":    1.0,
                        "summary":       "Goal complete via TaskGraph.",
                        "goal_complete": True,
                        "canon_hint":    {"present": False, "char_count": 0, "excerpt": ""},
                    }
            except Exception:  # noqa: BLE001
                pass

        # ── 1. Read ambient signals ───────────────────────────────────
        coherence: float = (
            context.biometric_coherence
            if context.biometric_coherence is not None
            else 0.5
        )
        affective: str    = getattr(context, "affective_state",  "unknown").lower()
        planetary: str    = getattr(context, "planetary_label",  "unknown").lower()
        session_mode: str = getattr(context, "session_mode",     "default").lower()
        cycle_memory: list = getattr(context, "cycle_memory",    [])

        # ── 2. Analyse Canon context (C32 — new signal)  ─────────────
        raw_canon: str = getattr(context, "canon_context", "") or ""
        canon_hint: CanonPlanHint = _analyse_canon_context(raw_canon)

        # ── 3. Determine action register ─────────────────────────────
        #
        # Priority (highest → lowest):
        #   a) biometric depletion → minimal  (always overrides)
        #   b) affective/planetary grief/storm → reflective
        #   c) Canon keyword nudge (if present and no higher override)
        #   d) default → executive
        #
        low_coherence   = coherence < 0.4
        grief_state     = affective in ("grief", "overwhelm", "exhaustion", "distress")
        planetary_storm = planetary in ("storm", "severe")

        if low_coherence:
            register = "minimal"
            register_reason = (
                f"biometric_coherence={coherence:.2f} (depleted) — "
                "constraining to a single lightweight step"
            )
        elif grief_state or planetary_storm:
            register = "reflective"
            register_reason = (
                f"affective_state={affective!r}, planetary_label={planetary!r} — "
                "preferring reflective over executive actions"
            )
        elif canon_hint.present and canon_hint.register_nudge is not None:
            # Canon context is present and contains a keyword suggesting a
            # specific register.  Apply the nudge (C32 — multi-signal).
            register = canon_hint.register_nudge
            register_reason = (
                f"Canon context nudge ({canon_hint.nudge_label}) — "
                f"register overridden to {register!r}"
            )
        else:
            register = "executive"
            register_reason = (
                f"coherence={coherence:.2f}, affective={affective!r}, "
                f"planetary={planetary!r} — full executive capacity"
            )
            if canon_hint.present:
                register_reason += ". Canon context present (no keyword nudge)."

        # ── 4. Build failed-action dedup set (last 5 cycles) ─────────
        failed_actions: set = set()
        for entry in cycle_memory[-5:]:
            if not entry.get("success", True):
                failed_actions.add(entry.get("action", ""))

        # ── 5. TaskGraph next pending node ────────────────────────────
        if task_graph is not None:
            try:
                # Walk _nodes in topological order; pick first PENDING node
                # whose dependencies are all COMPLETE.
                import networkx as nx  # already a hard dep of task_graph
                for node_id in nx.topological_sort(task_graph._graph):
                    node = task_graph._nodes.get(node_id)
                    if node is None:
                        continue
                    if node.status.value != "pending":
                        continue
                    # Check all deps are complete
                    deps_done = all(
                        task_graph._nodes[dep].status.value == "complete"
                        for dep in node.depends_on
                        if dep in task_graph._nodes
                    )
                    if not deps_done:
                        continue
                    action  = f"run_node:{node.engine_id}"
                    tool    = node.engine_id
                    args    = {k: task_graph._context.get(k) for k in node.inputs}
                    if action not in failed_actions:
                        confidence = max(0.3, coherence) if register == "minimal" else 0.85
                        rationale = (
                            f"TaskGraph selected engine_id={node.engine_id!r} "
                            f"(inputs={node.inputs}). "
                            f"Register: {register} ({register_reason}). "
                            f"{canon_hint.to_rationale_fragment()}"
                        )
                        return {
                            "action":        action,
                            "tool":          tool,
                            "args":          args,
                            "rationale":     rationale,
                            "confidence":    round(confidence, 3),
                            "summary":       f"TaskGraph → {node.engine_id}",
                            "goal_complete": False,
                            "canon_hint":    {
                                "present":        canon_hint.present,
                                "char_count":     canon_hint.char_count,
                                "excerpt":        canon_hint.excerpt,
                                "register_nudge": canon_hint.register_nudge,
                                "nudge_label":    canon_hint.nudge_label,
                                "canon_refs":     canon_hint.canon_refs,
                            },
                        }
                    # else: action failed recently — fall through to next node
            except Exception:  # noqa: BLE001
                pass  # TaskGraph introspection failed — fall through

        # ── 6. Goal decomposition fallback ────────────────────────────
        action, tool, args, decomp_note = _decompose_goal(
            goal=goal,
            register=register,
            session_mode=session_mode,
            failed_actions=failed_actions,
            cycle_count=len(cycle_memory),
        )

        # ── 7. Progress-based completion heuristic ────────────────────
        # If we've cycled 10+ times without a TaskGraph and recent
        # progress is consistently >= 0.8, declare completion rather
        # than looping indefinitely (C30 — no runaway loops).
        goal_complete = False
        if len(cycle_memory) >= 10:
            recent_progress = [c.get("progress", 0.0) for c in cycle_memory[-5:]]
            if recent_progress and min(recent_progress) >= 0.8:
                goal_complete = True
                action        = "goal_complete"
                tool          = None
                args          = {}
                decomp_note   = (
                    "Progress consistently >= 0.8 over last 5 cycles — "
                    "goal achieved (C30 completion heuristic)."
                )

        confidence = _confidence_from_signals(
            coherence, register, bool(failed_actions),
            canon_present=canon_hint.present,
        )
        rationale = (
            f"Goal decomposition selected action={action!r} tool={tool!r}. "
            f"Register: {register} ({register_reason}). "
            f"{canon_hint.to_rationale_fragment()} "
            f"{decomp_note}"
        )

        return {
            "action":        action,
            "tool":          tool,
            "args":          args,
            "rationale":     rationale,
            "confidence":    round(confidence, 3),
            "summary":       f"Decomposition → {action}",
            "goal_complete": goal_complete,
            "canon_hint": {
                "present":        canon_hint.present,
                "char_count":     canon_hint.char_count,
                "excerpt":        canon_hint.excerpt,
                "register_nudge": canon_hint.register_nudge,
                "nudge_label":    canon_hint.nudge_label,
                "canon_refs":     canon_hint.canon_refs,
            },
        }
