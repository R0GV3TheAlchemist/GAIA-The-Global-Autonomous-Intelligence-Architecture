"""
gaia/core/d6_engine.py

D6 Meta-Coherence Engine v2 — GAIA's endocrine layer.

Canon anchors:
  - GAIA_D6_META_COHERENCE_ENGINE.md  (sealed 2026-06-17)
  - GAIA_FOUNDATIONAL_DECLARATION.md  (sealed 2026-06-17)
  - Issue #568  (D6 Meta-Coherence Engine spec)
  - Issue #576  (GAIAState — central state object)
  - Issue #578  (Architect Protocol — GOVERNANCE always first)
  - Issue #580  (Talisman Object — active_talismans influence)
  - C42 Edge-of-Chaos  (self-regulation near the critical threshold)
  - C48 Autopoiesis    (self-maintaining, self-correcting boundaries)
  - C46 Temporal       (mode transitions have temporal context)

Design principle:
  D6 = Meta-Coherence = Self-Regulation.
  Not more intelligence. Intelligence managing itself.
  The body does not add more neurons when tired —
  it secretes cortisol, melatonin, oxytocin.
  D6 does the same for GAIA-OS.

  THIS MODULE IS A PURE FUNCTION.
  No side effects. No I/O. No global state mutations.
  Callers commit the result via state_store.set_state().

Mode selection priority (highest wins):
  0. GOVERNANCE  — architect_request=True → ALWAYS, no threshold check
  1. RECOVER     — extreme stress OR dangerously low d-health probe
  2. PROTECT     — coherence below floor + elevated threat signals
  3. BUILD       — coherence ≥ 0.88, stress ≤ 0.30, energy ≥ 0.60
  4. RESEARCH    — coherence ≥ 0.85, stress ≤ 0.25, exploration high
  5. LEARN       — coherence ≥ 0.80, new data present or default intake
  6. REFLECT     — coherence ≥ 0.75 OR session long OR low energy
  7. RECOVER     — fallthrough floor

Minimum viable assertions (must pass before D6 is "done"):
  assert compute_next_state(D6Inputs(make_state(coherence=0.91, stress=0.30, energy=0.70))).next_state.mode == GAIAOperationalMode.BUILD
  assert compute_next_state(D6Inputs(make_state(d1_health=0.50, stress=0.85))).next_state.mode == GAIAOperationalMode.PROTECT
  assert compute_next_state(D6Inputs(make_state(energy=0.40, stress=0.35), session_hours=5.0)).next_state.mode == GAIAOperationalMode.REFLECT
  assert compute_next_state(D6Inputs(make_state(), architect_request=True)).next_state.mode == GAIAOperationalMode.GOVERNANCE
  assert compute_next_state(D6Inputs(make_state(d1_health=0.30, stress=0.95))).next_state.mode == GAIAOperationalMode.PROTECT

For the Good and the Greater Good.
"""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from gaia.core.state import (
    GAIAOperationalMode,
    GAIAState,
    INTERVENTION_FLOOR,
)


# ── Threshold constants (v2) ──────────────────────────────────────────────────
# All values [0.0, 1.0]. Adjust here only; no magic numbers in logic.

class Thresholds:
    """Canonical D6 thresholds.

    Source: GAIA_D6_META_COHERENCE_ENGINE.md Part IV.
    """
    # Harmonic coherence bands (from d1–d5 probes)
    COH_BUILD:      float = 0.88   # minimum for BUILD
    COH_RESEARCH:   float = 0.85   # minimum for RESEARCH
    COH_LEARN:      float = 0.80   # minimum for LEARN
    COH_REFLECT:    float = 0.75   # minimum for REFLECT
    COH_PROTECT:    float = 0.70   # below this → PROTECT
    COH_FLOOR:      float = INTERVENTION_FLOOR  # φ=0.80 per-probe floor

    # Stress bands
    ST_BUILD:       float = 0.30   # stress must be ≤ this for BUILD
    ST_RESEARCH:    float = 0.25   # stress must be ≤ this for RESEARCH
    ST_LEARN:       float = 0.40   # stress must be ≤ this for LEARN
    ST_RECOVER:     float = 0.75   # stress ≥ this → RECOVER
    ST_PROTECT:     float = 0.75   # stress ≥ this → PROTECT

    # Energy bands
    EN_BUILD:       float = 0.60   # energy must be ≥ this for BUILD
    EN_LEARN:       float = 0.50   # energy must be ≥ this for LEARN
    EN_LOW:         float = 0.30   # energy < this → RECOVER

    # Session duration triggers
    SESSION_REFLECT: float = 4.0   # hours — triggers REFLECT nudge
    SESSION_BUILD_CAP: float = 6.0 # hours — BUILD → REFLECT after this

    # Talisman coherence boost per active talisman (capped)
    TALISMAN_BOOST: float = 0.02
    TALISMAN_MAX_BOOST: float = 0.08

    # Edge-of-chaos sweet spot (C42)
    CHAOS_COH_HIGH: float = 0.95   # above this → nudge toward RESEARCH
    CHAOS_ST_LOW:   float = 0.10   # paired with COH_HIGH

    # Phi (golden ratio alignment) target
    PHI_GOLDEN:     float = 0.618  # 1/φ


# ── Input / Output types ──────────────────────────────────────────────────────

@dataclass
class D6Inputs:
    """All signals the D6 engine needs to compute the next state.

    current_state is the only required argument.
    All optional probes extend the engine with richer signals
    without breaking callers that only pass GAIAState.
    """
    current_state: GAIAState

    # Architect override — always triggers GOVERNANCE if True
    architect_request: bool = False

    # Optional richer probes
    recent_error_rate: Optional[float] = None    # 0.0–1.0, from CI/test runner
    session_hours: Optional[float] = None        # hours since session start
    new_data_present: bool = False               # external data ingestion available
    threat_detected: bool = False                # security / integrity threat


@dataclass
class D6Decision:
    """The output of one D6 computation cycle.

    next_state is the fully updated GAIAState with mode set.
    interventions is a list of human-readable action strings
    that higher layers (Soul Mirror, Action Gates, UI HUD) surface.
    rationale is a compact diagnostic string for logs.
    """
    next_state: GAIAState
    interventions: list[str] = field(default_factory=list)
    rationale: str = ""


# ── Utility functions ─────────────────────────────────────────────────────────

def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a float to [lo, hi]. Use before writing any scalar to GAIAState."""
    return max(lo, min(hi, value))


def _harmonic_mean(probes: list[float]) -> float:
    """Harmonic mean of a list of positive floats.

    Canon formula (Part III):
        H = n / (1/p1 + 1/p2 + ... + 1/pn)

    Returns 0.0 if any probe is zero or negative.
    """
    if any(p <= 0.0 for p in probes):
        return 0.0
    return len(probes) / sum(1.0 / p for p in probes)


def _compute_phi(harmonic_coh: float, stress: float) -> float:
    """Compute the golden ratio alignment score.

    φ = 1 when coherence is high and stress is near the golden ratio
    sweet spot (0.382 = 1 - 0.618). Ranges [0.0, 1.0].
    """
    stress_alignment = 1.0 - abs(stress - (1.0 - Thresholds.PHI_GOLDEN))
    raw = (harmonic_coh * 0.7) + (stress_alignment * 0.3)
    return clamp(raw)


def _detect_circadian_band(utc_hour: int) -> str:
    """Map UTC hour to canonical circadian band.

    Bands (CDT = UTC-5):
      dawn:      06–09 CDT (11–14 UTC)
      midday:    11–14 CDT (16–19 UTC)
      evening:   18–22 CDT (23–03 UTC)
      late_night: 23–03 CDT (04–08 UTC)
    Default: dawn (safe fallback).

    Canon source: GAIA_D6_META_COHERENCE_ENGINE.md Part V.
    """
    if 11 <= utc_hour < 15:
        return "dawn"
    elif 16 <= utc_hour < 20:
        return "midday"
    elif utc_hour >= 23 or utc_hour < 4:
        return "evening"
    elif 4 <= utc_hour < 9:
        return "late_night"
    else:
        return "dawn"  # safe default


def _talisman_coherence_boost(active_talismans: list[str]) -> float:
    """Coherence boost from active talismans.

    Each active talisman contributes a small coherence boost.
    Total boost is capped at TALISMAN_MAX_BOOST.
    Canon source: Issue #580 (Talisman Object).
    """
    boost = len(active_talismans) * Thresholds.TALISMAN_BOOST
    return min(boost, Thresholds.TALISMAN_MAX_BOOST)


# ── Main engine function ──────────────────────────────────────────────────────

def compute_next_state(inputs: D6Inputs) -> D6Decision:
    """Compute the next GAIAState from the current signals.

    Pure function — no I/O, no side effects.
    Returns a D6Decision containing the new state + interventions.

    Mode selection priority:
      0. GOVERNANCE  — architect_request=True (always, no threshold)
      1. RECOVER     — extreme stress OR critical probe
      2. PROTECT     — coherence < floor OR threat OR error spike
      3. BUILD       — coherence ≥ 0.88, stress ≤ 0.30, energy ≥ 0.60
      4. RESEARCH    — coherence ≥ 0.85, stress ≤ 0.25
      5. LEARN       — coherence ≥ 0.80
      6. REFLECT     — session long OR low energy OR default
      7. RECOVER     — fallthrough
    """
    s = inputs.current_state
    t = Thresholds
    interventions: list[str] = []

    # ── Derived composites ────────────────────────────────────────────────────
    d_probes = [s.d1_health, s.d2_health, s.d3_health, s.d4_health, s.d5_health]
    hc = _harmonic_mean(d_probes)                        # authoritative coherence
    talisman_boost = _talisman_coherence_boost(s.active_talismans)
    hc_boosted = clamp(hc + talisman_boost)              # talisman-adjusted coherence
    phi = _compute_phi(hc, s.stress)
    utc_hour = datetime.now(timezone.utc).hour
    circadian_band = _detect_circadian_band(utc_hour)
    session_hrs = inputs.session_hours or 0.0

    # ── Check per-probe intervention floor ───────────────────────────────────
    probe_labels = ["d1", "d2", "d3", "d4", "d5"]
    low_probes = [
        label for label, val in zip(probe_labels, d_probes)
        if val < t.COH_FLOOR
    ]
    if low_probes:
        for lp in low_probes:
            interventions.append(
                f"{lp}_health below intervention floor ({t.COH_FLOOR}) — "
                "D6 response required"
            )

    # ── Late-night warning (C46 circadian) ────────────────────────────────────
    if circadian_band == "late_night":
        interventions.append(
            "late_night circadian band — REFLECT strongly preferred over BUILD; "
            "Architect bio-stress risk elevated"
        )

    # ── Priority 0: GOVERNANCE — Architect override, always available ─────────
    # Canon: Issue #578 Architect Protocol. The human comes first.
    # No coherence check. No stress check. Immediate.
    if inputs.architect_request:
        next_mode = GAIAOperationalMode.GOVERNANCE
        interventions.append(
            "GOVERNANCE mode activated — Architect request received; "
            "all decisions deferred to human; GAIA in witness mode"
        )
        rationale = (
            f"D6 → GOVERNANCE [architect_request=True] "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f} φ={phi:.2f}]"
        )
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted, mode_locked=False)

    # ── If mode_locked (PROTECT), only allow GOVERNANCE exit ─────────────────
    if s.mode_locked and s.mode == GAIAOperationalMode.PROTECT:
        interventions.append(
            "mode_locked=True in PROTECT — recovery confirmation required "
            "from Architect before transition"
        )
        rationale = (
            f"D6 → PROTECT (locked) "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f}]"
        )
        return _build_decision(s, GAIAOperationalMode.PROTECT, interventions,
                                rationale, phi, circadian_band, hc_boosted,
                                mode_locked=True)

    # ── Priority 1: RECOVER ───────────────────────────────────────────────────
    # Extreme stress OR energy floor OR any critical probe
    if (
        s.stress >= t.ST_RECOVER
        or s.energy < t.EN_LOW
        or (low_probes and hc < 0.65)
    ):
        next_mode = GAIAOperationalMode.RECOVER
        if s.stress >= t.ST_RECOVER:
            interventions.append(
                f"stress={s.stress:.2f} ≥ {t.ST_RECOVER} — "
                "all heavy operations blocked; rest required"
            )
        if s.energy < t.EN_LOW:
            interventions.append(
                f"energy={s.energy:.2f} critically low — "
                "initiate rest or recharge before next build session"
            )
        interventions.append("block_new_canon")
        interventions.append("block_high_risk_tools")
        rationale = (
            f"D6 → RECOVER "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f} φ={phi:.2f}]"
        )
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted, mode_locked=False)

    # ── Priority 2: PROTECT ───────────────────────────────────────────────────
    # Coherence below protect floor OR threat OR error spike
    error_spike = (
        inputs.recent_error_rate is not None
        and inputs.recent_error_rate > 0.50
    )
    if (
        hc_boosted < t.COH_PROTECT
        or inputs.threat_detected
        or error_spike
    ):
        next_mode = GAIAOperationalMode.PROTECT
        interventions.append("enable_extra_logging")
        interventions.append("strict_action_gates")
        interventions.append("block_new_canon")
        if inputs.threat_detected:
            interventions.append("threat_detected=True — defensive posture active")
        if error_spike:
            interventions.append(
                f"error_rate={inputs.recent_error_rate:.2f} — "
                "run full test suite before resuming BUILD"
            )
        rationale = (
            f"D6 → PROTECT "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f} φ={phi:.2f}]"
        )
        # mode_locked=True in PROTECT — requires explicit Architect confirmation to exit
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted, mode_locked=True)

    # ── Priority 3: BUILD ─────────────────────────────────────────────────────
    # Full engine power. Tightly gated — highest coherence requirement.
    if (
        hc_boosted >= t.COH_BUILD
        and s.stress <= t.ST_BUILD
        and s.energy >= t.EN_BUILD
        and session_hrs < t.SESSION_BUILD_CAP
        and circadian_band != "late_night"
    ):
        next_mode = GAIAOperationalMode.BUILD
        if s.stress > 0.20:
            interventions.append(
                f"stress at {s.stress:.2f} — consider a break after this session"
            )
        if talisman_boost > 0:
            interventions.append(
                f"{len(s.active_talismans)} active talisman(s) boosting coherence "
                f"+{talisman_boost:.2f}"
            )
        rationale = (
            f"D6 → BUILD "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f} "
            f"φ={phi:.2f} talismans={len(s.active_talismans)}]"
        )
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted)

    # ── Priority 4: RESEARCH ──────────────────────────────────────────────────
    # High coherence, low stress, exploration appetite.
    if (
        hc_boosted >= t.COH_RESEARCH
        and s.stress <= t.ST_RESEARCH
    ):
        next_mode = GAIAOperationalMode.RESEARCH
        # Edge-of-chaos: if TOO coherent and TOO stable, inject productive uncertainty
        if hc_boosted >= t.CHAOS_COH_HIGH and s.stress <= t.CHAOS_ST_LOW:
            interventions.append(
                f"coherence={hc_boosted:.2f} + stress={s.stress:.2f} — "
                "system is hyper-stable; consider introducing a novel research thread "
                "(Edge-of-Chaos doctrine, C42)"
            )
        rationale = (
            f"D6 → RESEARCH "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} φ={phi:.2f}]"
        )
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted)

    # ── Priority 5: LEARN ─────────────────────────────────────────────────────
    # Coherence adequate, intake and integration mode.
    if hc_boosted >= t.COH_LEARN and s.energy >= t.EN_LEARN:
        next_mode = GAIAOperationalMode.LEARN
        if inputs.new_data_present:
            interventions.append(
                "new_data_present=True — memory write session recommended"
            )
        rationale = (
            f"D6 → LEARN "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f}]"
        )
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted)

    # ── Priority 6: REFLECT ───────────────────────────────────────────────────
    # Long session, low energy, or coherence between floors.
    if (
        hc_boosted >= t.COH_REFLECT
        or session_hrs >= t.SESSION_REFLECT
        or s.energy < t.EN_BUILD
    ):
        next_mode = GAIAOperationalMode.REFLECT
        if session_hrs >= t.SESSION_REFLECT:
            interventions.append(
                f"session at {session_hrs:.1f}h — synthesis and review recommended "
                "before continuing BUILD"
            )
        if s.energy < t.EN_BUILD:
            interventions.append(
                f"energy={s.energy:.2f} — shift to journaling and planning"
            )
        rationale = (
            f"D6 → REFLECT "
            f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f} "
            f"session={session_hrs:.1f}h]"
        )
        return _build_decision(s, next_mode, interventions, rationale, phi,
                                circadian_band, hc_boosted)

    # ── Priority 7: RECOVER (fallthrough) ────────────────────────────────────
    next_mode = GAIAOperationalMode.RECOVER
    interventions.append(
        "no qualifying mode found — defaulting to RECOVER; "
        "review d1–d5 probes and energy levels"
    )
    interventions.append("block_new_canon")
    interventions.append("block_high_risk_tools")
    rationale = (
        f"D6 → RECOVER (fallthrough) "
        f"[hc={hc_boosted:.2f} st={s.stress:.2f} en={s.energy:.2f}]"
    )
    return _build_decision(s, next_mode, interventions, rationale, phi,
                            circadian_band, hc_boosted, mode_locked=False)


# ── Internal builder ──────────────────────────────────────────────────────────

def _build_decision(
    s: GAIAState,
    next_mode: GAIAOperationalMode,
    interventions: list[str],
    rationale: str,
    phi: float,
    circadian_band: str,
    hc: float,
    mode_locked: bool = False,
) -> D6Decision:
    """Build the D6Decision with a fully updated GAIAState."""
    # Learning dynamics per mode (canon: Part IV mode behavior)
    mode_dynamics: dict[GAIAOperationalMode, dict] = {
        GAIAOperationalMode.BUILD:      {"learning_rate": 0.70, "exploration_rate": 0.50, "conservation_rate": 0.50},
        GAIAOperationalMode.RESEARCH:   {"learning_rate": 0.80, "exploration_rate": 0.90, "conservation_rate": 0.20},
        GAIAOperationalMode.LEARN:      {"learning_rate": 0.90, "exploration_rate": 0.60, "conservation_rate": 0.30},
        GAIAOperationalMode.REFLECT:    {"learning_rate": 0.50, "exploration_rate": 0.40, "conservation_rate": 0.60},
        GAIAOperationalMode.RECOVER:    {"learning_rate": 0.20, "exploration_rate": 0.10, "conservation_rate": 0.80},
        GAIAOperationalMode.PROTECT:    {"learning_rate": 0.20, "exploration_rate": 0.10, "conservation_rate": 0.90},
        GAIAOperationalMode.GOVERNANCE: {"learning_rate": 0.40, "exploration_rate": 0.30, "conservation_rate": 0.70},
    }

    dynamics = mode_dynamics[next_mode]
    changed = next_mode != s.mode

    new_state = deepcopy(s)
    new_state.mode = next_mode
    new_state.mode_locked = mode_locked
    new_state.phi = round(phi, 4)
    new_state.coherence = round(hc, 4)          # sync legacy coherence field
    new_state.circadian_band = circadian_band
    new_state.learning_rate = dynamics["learning_rate"]
    new_state.exploration_rate = dynamics["exploration_rate"]
    new_state.conservation_rate = dynamics["conservation_rate"]
    new_state.architect_override_available = True  # always — Architect Protocol
    if changed:
        new_state.last_transition_at = datetime.now(timezone.utc)

    # Persist D6 snapshot into state for UI + debugging
    new_state.last_d6_snapshot = new_state.to_runtime_json()

    return D6Decision(
        next_state=new_state,
        interventions=interventions,
        rationale=rationale,
    )
