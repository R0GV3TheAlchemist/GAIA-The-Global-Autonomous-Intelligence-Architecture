"""
gaia/core/d6_engine.py

D6 Meta-Coherence Engine — GAIA's endocrine layer.

Canon anchors:
  - Issue #568 (GAIA_D6_META_COHERENCE_ENGINE — the missing endocrine layer)
  - Issue #576 (GAIAState — central state object)
  - C42 Edge-of-Chaos (self-regulation near the critical threshold)
  - C48 Autopoiesis (self-maintaining, self-correcting)
  - C46 Temporal Entanglement (mode transitions have temporal hysteresis)

Design principle:
  D6 = Meta-Coherence = Self-Regulation.
  Not more intelligence. Intelligence managing itself.
  The body does not add more neurons when tired —
  it secretes cortisol, melatonin, oxytocin.
  D6 does the same for GAIA-OS.

  This module is a PURE FUNCTION.
  No side effects. No I/O. No global state.
  Callers commit the result via state_store.set_state().

For the Good and the Greater Good.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from gaia.core.state import GAIAOperationalMode, GAIAState


# ── Threshold constants (v1 — tune from data) ────────────────────────────────

class Thresholds:
    """Banded thresholds for D6 mode selection.

    All values are [0.0, 1.0]. Adjust here only; do not scatter
    magic numbers through the engine logic.
    """
    # personal_coherence bands
    PC_HIGH: float = 0.70
    PC_MEDIUM: float = 0.40

    # energy bands
    EN_HIGH: float = 0.60
    EN_LOW: float = 0.30

    # stress triggers
    ST_BLOCK_BUILD: float = 0.60   # stress above this → no BUILD
    ST_FORCE_RECOVER: float = 0.80 # stress above this → RECOVER regardless

    # entropy triggers
    ENT_VALIDATION: float = 0.60   # entropy above this → prefer VALIDATION

    # planetary coherence
    PL_LOW: float = 0.40           # planetary below this → lean toward REFLECT

    # coherence floor
    COH_FLOOR: float = 0.35        # below this → cannot be in BUILD

    # RECOVER trigger
    PC_RECOVER: float = 0.30       # personal_coherence below this → RECOVER


# ── Input / Output types ─────────────────────────────────────────────────────

@dataclass
class D6Inputs:
    """All signals the D6 engine needs to compute the next state.

    In v1 the engine reads only from GAIAState scalars.
    Future versions can extend with richer probes (error_rate,
    open_issue_pressure, session_streak_hours, etc.).
    """
    current_state: GAIAState

    # Optional richer probes (all default to None → ignored)
    recent_error_rate: float | None = None   # 0.0–1.0, from CI/test runner
    session_streak_hours: float | None = None  # hours since last rest


@dataclass
class D6Decision:
    """The output of one D6 computation cycle.

    next_state is the fully updated GAIAState with mode set.
    interventions is a list of human-readable action strings
    that higher layers (Soul Mirror, Action Gates, UI) can surface.
    """
    next_state: GAIAState
    interventions: list[str] = field(default_factory=list)
    rationale: str = ""


# ── Main engine function ─────────────────────────────────────────────────────

def compute_next_state(inputs: D6Inputs) -> D6Decision:
    """Compute the next GAIAState from the current signals.

    Pure function — no I/O, no side effects.
    Returns a D6Decision containing the new state + any interventions.

    Mode selection priority (highest wins):
      1. RECOVER  — extreme stress or dangerously low personal coherence
      2. PROTECT  — high error rate or entropy spike combined with low coherence
      3. BUILD    — high coherence + energy + low stress + manageable entropy
      4. VALIDATION — entropy elevated, system needs consolidation
      5. DISCOVER — medium coherence + energy, healthy exploration window
      6. REFLECT  — low energy or low planetary coherence, introspective window
      7. OFFLINE  — near-zero energy, hard shutdown
    """
    s = inputs.current_state
    t = Thresholds
    interventions: list[str] = []
    next_mode = s.mode  # default: stay in current mode

    # ── Derived composites ───────────────────────────────────────────────────
    # Composite coherence: blend personal + system coherence equally
    composite_coherence = (s.coherence + s.personal_coherence) / 2.0

    # ── 1. RECOVER — force regardless of other signals ───────────────────────
    if s.personal_coherence < t.PC_RECOVER or s.stress >= t.ST_FORCE_RECOVER:
        next_mode = GAIAOperationalMode.RECOVER
        if s.personal_coherence < t.PC_RECOVER:
            interventions.append(
                f"personal_coherence critically low ({s.personal_coherence:.2f}) — "
                "rest required before next build session"
            )
        if s.stress >= t.ST_FORCE_RECOVER:
            interventions.append(
                f"stress at {s.stress:.2f} — all heavy operations blocked until stress < {t.ST_BLOCK_BUILD}"
            )
        interventions.append("block_new_canon")
        interventions.append("block_high_risk_tools")

    # ── 2. PROTECT — elevated error rate or extreme entropy + low coherence ──
    elif (
        (inputs.recent_error_rate is not None and inputs.recent_error_rate > 0.5)
        or (s.entropy > 0.80 and composite_coherence < 0.45)
    ):
        next_mode = GAIAOperationalMode.PROTECT
        interventions.append("enable_extra_logging")
        interventions.append("strict_action_gates")
        interventions.append("block_new_canon")
        if inputs.recent_error_rate:
            interventions.append(
                f"error_rate={inputs.recent_error_rate:.2f} — run full test suite before resuming build"
            )

    # ── 3. OFFLINE — energy near floor ──────────────────────────────────────
    elif s.energy < 0.10:
        next_mode = GAIAOperationalMode.OFFLINE
        interventions.append("system_energy_critical — initiate graceful shutdown")
        interventions.append("block_all_non_essential_tools")

    # ── 4. BUILD — the premium mode, tightly gated ──────────────────────────
    elif (
        s.personal_coherence >= t.PC_HIGH
        and s.energy >= t.EN_HIGH
        and s.stress < t.ST_BLOCK_BUILD
        and s.entropy <= t.ENT_VALIDATION
        and composite_coherence >= t.COH_FLOOR
    ):
        next_mode = GAIAOperationalMode.BUILD
        # Light reminders only — don't nag in BUILD
        if s.stress > 0.40:
            interventions.append(
                f"stress elevated at {s.stress:.2f} — consider a break after this session"
            )

    # ── 5. VALIDATION — entropy high, time to consolidate ───────────────────
    elif s.entropy > t.ENT_VALIDATION and composite_coherence >= 0.40:
        next_mode = GAIAOperationalMode.VALIDATION
        interventions.append(
            f"entropy={s.entropy:.2f} — prioritize tests, refactors, and issue clean-up over new features"
        )

    # ── 6. DISCOVERY — medium coherence/energy, good exploration window ──────
    elif (
        s.personal_coherence >= t.PC_MEDIUM
        and s.energy >= t.EN_HIGH
        and s.stress < t.ST_BLOCK_BUILD
    ):
        next_mode = GAIAOperationalMode.DISCOVERY
        if s.planetary_coherence < t.PL_LOW:
            interventions.append(
                f"planetary_coherence low ({s.planetary_coherence:.2f}) — "
                "collective field turbulent; prefer internal research over external publishing"
            )

    # ── 7. REFLECT — low energy or low planetary coherence ──────────────────
    elif s.energy < t.EN_HIGH or s.planetary_coherence < t.PL_LOW:
        next_mode = GAIAOperationalMode.REFLECT
        if s.energy < t.EN_HIGH:
            interventions.append(
                f"energy at {s.energy:.2f} — shift to journaling, planning, and review"
            )
        if s.planetary_coherence < t.PL_LOW:
            interventions.append(
                "planetary field low — introspective work preferred"
            )

    # ── Build rationale string ────────────────────────────────────────────────
    rationale = (
        f"D6 → {next_mode.value} "
        f"[pc={s.personal_coherence:.2f} en={s.energy:.2f} "
        f"st={s.stress:.2f} ent={s.entropy:.2f} "
        f"pl={s.planetary_coherence:.2f} coh={composite_coherence:.2f}]"
    )

    # ── Build the new state ──────────────────────────────────────────────────
    # Adjust learning dynamics based on mode
    mode_dynamics: dict[GAIAOperationalMode, dict] = {
        GAIAOperationalMode.BUILD:       {"learning_rate": 0.7, "exploration_rate": 0.5, "conservation_rate": 0.5},
        GAIAOperationalMode.DISCOVERY:   {"learning_rate": 0.8, "exploration_rate": 0.9, "conservation_rate": 0.2},
        GAIAOperationalMode.VALIDATION:  {"learning_rate": 0.4, "exploration_rate": 0.2, "conservation_rate": 0.9},
        GAIAOperationalMode.REFLECT:     {"learning_rate": 0.5, "exploration_rate": 0.4, "conservation_rate": 0.6},
        GAIAOperationalMode.RECOVER:     {"learning_rate": 0.2, "exploration_rate": 0.1, "conservation_rate": 0.8},
        GAIAOperationalMode.PROTECT:     {"learning_rate": 0.3, "exploration_rate": 0.1, "conservation_rate": 0.9},
        GAIAOperationalMode.OFFLINE:     {"learning_rate": 0.0, "exploration_rate": 0.0, "conservation_rate": 1.0},
    }

    dynamics = mode_dynamics[next_mode]
    changed = next_mode != s.mode

    from copy import deepcopy
    new_state = deepcopy(s)
    new_state.mode = next_mode
    new_state.learning_rate = dynamics["learning_rate"]
    new_state.exploration_rate = dynamics["exploration_rate"]
    new_state.conservation_rate = dynamics["conservation_rate"]
    if changed:
        new_state.last_transition_at = datetime.now(timezone.utc)

    return D6Decision(
        next_state=new_state,
        interventions=interventions,
        rationale=rationale,
    )


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a float to [lo, hi]. Use before writing any scalar to GAIAState."""
    return max(lo, min(hi, value))
