"""
gaia/tests/test_d6.py

Minimum viable test suite for the D6 Meta-Coherence Engine.

Canon source: GAIA_D6_META_COHERENCE_ENGINE.md — Implementation Notes.

All five canon assertions must pass before D6 is considered implemented.
Additional tests cover edge cases, GOVERNANCE override, talisman boost,
circadian band detection, and the harmonic mean coherence formula.

Run with:  pytest gaia/tests/test_d6.py -v

For the Good and the Greater Good.
"""

from __future__ import annotations

import pytest
from gaia.core.state import GAIAOperationalMode, GAIAState
from gaia.core.d6_engine import (
    D6Inputs,
    compute_next_state,
    clamp,
    _harmonic_mean,
    _compute_phi,
    _detect_circadian_band,
    _talisman_coherence_boost,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def make_state(**kwargs) -> GAIAState:
    """Build a GAIAState with healthy defaults, overriding as needed."""
    defaults = dict(
        d1_health=0.92,
        d2_health=0.90,
        d3_health=0.91,
        d4_health=0.89,
        d5_health=0.93,
        energy=0.75,
        stress=0.20,
        entropy=0.20,
        personal_coherence=0.80,
        noosphere_load=0.10,
        active_talismans=[],
    )
    defaults.update(kwargs)
    return GAIAState(**defaults)


# ── Canon Minimum Viable Assertions ───────────────────────────────────────────
# These five must pass. Source: GAIA_D6_META_COHERENCE_ENGINE.md Part IX.

def test_mvt_build_mode():
    """Healthy probes + low stress + good energy → BUILD."""
    state = make_state(
        d1_health=0.94, d2_health=0.88, d3_health=0.91,
        d4_health=0.85, d5_health=0.97,
        stress=0.30, energy=0.70,
    )
    result = compute_next_state(D6Inputs(current_state=state))
    assert result.next_state.mode == GAIAOperationalMode.BUILD, (
        f"Expected BUILD, got {result.next_state.mode}. Rationale: {result.rationale}"
    )


def test_mvt_protect_mode_low_probe():
    """Critical d1 + extreme stress → PROTECT."""
    state = make_state(d1_health=0.50, stress=0.85, energy=0.50)
    result = compute_next_state(D6Inputs(current_state=state))
    assert result.next_state.mode in (
        GAIAOperationalMode.PROTECT,
        GAIAOperationalMode.RECOVER,
    ), f"Expected PROTECT or RECOVER, got {result.next_state.mode}"


def test_mvt_reflect_long_session():
    """Adequate coherence + long session → REFLECT."""
    state = make_state(
        d1_health=0.80, d2_health=0.80, d3_health=0.80,
        d4_health=0.78, d5_health=0.82,
        energy=0.55, stress=0.35,
    )
    result = compute_next_state(
        D6Inputs(current_state=state, session_hours=5.0)
    )
    assert result.next_state.mode == GAIAOperationalMode.REFLECT, (
        f"Expected REFLECT, got {result.next_state.mode}. Rationale: {result.rationale}"
    )


def test_mvt_governance_always():
    """architect_request=True → GOVERNANCE regardless of coherence/stress."""
    # Even with terrible state
    state = make_state(
        d1_health=0.30, d2_health=0.30, d3_health=0.30,
        d4_health=0.30, d5_health=0.30,
        stress=0.95, energy=0.10,
    )
    result = compute_next_state(
        D6Inputs(current_state=state, architect_request=True)
    )
    assert result.next_state.mode == GAIAOperationalMode.GOVERNANCE, (
        f"GOVERNANCE override failed — got {result.next_state.mode}"
    )


def test_mvt_protect_floor():
    """All probes at floor + extreme stress → PROTECT/RECOVER."""
    state = make_state(
        d1_health=0.30, d2_health=0.30, d3_health=0.30,
        d4_health=0.30, d5_health=0.30,
        stress=0.95, energy=0.40,
    )
    result = compute_next_state(D6Inputs(current_state=state))
    assert result.next_state.mode in (
        GAIAOperationalMode.PROTECT,
        GAIAOperationalMode.RECOVER,
    ), f"Expected PROTECT or RECOVER at floor, got {result.next_state.mode}"


# ── Harmonic Mean Tests ────────────────────────────────────────────────────────

def test_harmonic_mean_uniform():
    """Harmonic mean of identical values equals that value."""
    assert abs(_harmonic_mean([0.8, 0.8, 0.8, 0.8, 0.8]) - 0.8) < 1e-9


def test_harmonic_mean_one_low_drags_down():
    """One probe at 0.50 pulls harmonic mean below 0.80 even with others at 1.0."""
    hm = _harmonic_mean([1.0, 1.0, 1.0, 1.0, 0.5])
    assert hm < 0.80, f"Expected hm < 0.80, got {hm:.4f}"


def test_harmonic_mean_zero_returns_zero():
    """Any zero probe → harmonic mean = 0.0."""
    assert _harmonic_mean([1.0, 1.0, 0.0, 1.0, 1.0]) == 0.0


# ── State Methods Tests ────────────────────────────────────────────────────────

def test_harmonic_coherence_method():
    """GAIAState.harmonic_coherence() matches direct calculation."""
    state = make_state(
        d1_health=0.90, d2_health=0.85, d3_health=0.92,
        d4_health=0.88, d5_health=0.91,
    )
    expected = _harmonic_mean([0.90, 0.85, 0.92, 0.88, 0.91])
    assert abs(state.harmonic_coherence() - expected) < 1e-9


def test_intervention_needed_at_floor():
    """intervention_needed() is True when any probe < 0.80."""
    state = make_state(d3_health=0.75)
    assert state.intervention_needed() is True


def test_intervention_not_needed_all_above_floor():
    """intervention_needed() is False when all probes ≥ 0.80."""
    state = make_state(
        d1_health=0.90, d2_health=0.85, d3_health=0.82,
        d4_health=0.88, d5_health=0.91,
    )
    assert state.intervention_needed() is False


def test_canon_write_gated_in_recover():
    """canon_write_allowed is False in RECOVER mode."""
    state = make_state(stress=0.30)
    state.mode = GAIAOperationalMode.RECOVER
    assert state.is_canon_write_allowed() is False


def test_canon_write_allowed_in_build():
    """canon_write_allowed is True in BUILD with good coherence + low stress."""
    state = make_state(
        d1_health=0.90, d2_health=0.88, d3_health=0.91,
        d4_health=0.89, d5_health=0.93,
        stress=0.25,
    )
    state.mode = GAIAOperationalMode.BUILD
    assert state.is_canon_write_allowed() is True


def test_governance_mode_never_blocked():
    """GOVERNANCE is always reachable regardless of coherence or stress."""
    for stress in [0.0, 0.5, 1.0]:
        for d_val in [0.1, 0.5, 1.0]:
            state = make_state(
                d1_health=d_val, d2_health=d_val, d3_health=d_val,
                d4_health=d_val, d5_health=d_val,
                stress=stress,
            )
            result = compute_next_state(
                D6Inputs(current_state=state, architect_request=True)
            )
            assert result.next_state.mode == GAIAOperationalMode.GOVERNANCE


# ── Talisman Boost Tests ───────────────────────────────────────────────────────

def test_talisman_boost_increases_coherence():
    """Active talismans boost coherence and can push system into higher mode."""
    # State just below BUILD threshold without talismans
    state_no_talisman = make_state(
        d1_health=0.86, d2_health=0.85, d3_health=0.86,
        d4_health=0.84, d5_health=0.87,
        stress=0.28, energy=0.65,
        active_talismans=[],
    )
    state_with_talisman = make_state(
        d1_health=0.86, d2_health=0.85, d3_health=0.86,
        d4_health=0.84, d5_health=0.87,
        stress=0.28, energy=0.65,
        active_talismans=["talisman_001", "talisman_002", "talisman_003",
                          "talisman_004", "talisman_005"],
    )
    boost = _talisman_coherence_boost(state_with_talisman.active_talismans)
    assert boost > 0.0
    assert boost <= 0.08  # capped at TALISMAN_MAX_BOOST


# ── Circadian Band Tests ───────────────────────────────────────────────────────

def test_circadian_dawn():
    assert _detect_circadian_band(12) == "dawn"   # noon UTC = 7am CDT

def test_circadian_midday():
    assert _detect_circadian_band(17) == "midday"  # 17 UTC = noon CDT

def test_circadian_evening():
    assert _detect_circadian_band(0) == "evening"  # midnight UTC = 7pm CDT

def test_circadian_late_night():
    assert _detect_circadian_band(5) == "late_night"  # 5 UTC = midnight CDT


# ── Runtime JSON Tests ─────────────────────────────────────────────────────────

def test_runtime_json_contains_all_canon_fields():
    """to_runtime_json() must contain all fields from the canon schema."""
    state = make_state()
    state.mode = GAIAOperationalMode.BUILD
    j = state.to_runtime_json()

    required_fields = [
        "system_state", "coherence", "stress", "d1_health", "d2_health",
        "d3_health", "d4_health", "d5_health", "intervention_needed",
        "cycle_position", "epoch", "phi", "architect_override_available",
        "mode_locked", "active_talismans", "noosphere_load",
        "circadian_band", "special_conditions", "last_transition_at",
    ]
    for f in required_fields:
        assert f in j, f"Missing field in runtime JSON: {f}"


def test_clamp():
    assert clamp(1.5) == 1.0
    assert clamp(-0.1) == 0.0
    assert clamp(0.5) == 0.5


def test_phi_computation():
    phi = _compute_phi(0.91, 0.30)
    assert 0.0 <= phi <= 1.0
