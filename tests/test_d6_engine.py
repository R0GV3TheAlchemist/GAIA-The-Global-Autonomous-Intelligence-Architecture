"""
tests/test_d6_engine.py

Unit tests for the D6 Meta-Coherence Engine.

Philosophy:
  These tests are the first line of proof that D6 is sane.
  Before any other queue depends on GAIAState, these must be green.
  Each test case maps to a real scenario the Architect or system will face.

Canon anchors:
  - Issue #576 (GAIAState)
  - Issue #568 (D6 Meta-Coherence Engine)
  - Issue #578 (Architect Protocol — the human comes first)

For the Good and the Greater Good.
"""

from __future__ import annotations

import pytest

from gaia.core.state import GAIAOperationalMode, GAIAState
from gaia.core.d6_engine import D6Inputs, compute_next_state


def make_state(**kwargs) -> GAIAState:
    """Helper: build a GAIAState with safe defaults, overriding only what the test needs."""
    defaults = dict(
        coherence=0.7,
        energy=0.7,
        stress=0.3,
        entropy=0.3,
        personal_coherence=0.7,
        planetary_coherence=0.6,
    )
    defaults.update(kwargs)
    return GAIAState(**defaults)


# ── Case 1: Prime BUILD conditions ────────────────────────────────────────────
def test_build_mode_when_conditions_prime():
    """High coherence + energy + low stress + low entropy → BUILD."""
    state = make_state(personal_coherence=0.82, energy=0.80, stress=0.20, entropy=0.25)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.BUILD
    assert decision.next_state.is_high_risk_allowed()
    assert decision.next_state.is_canon_write_allowed()


# ── Case 2: High entropy forces VALIDATION ────────────────────────────────────
def test_validation_mode_when_entropy_high():
    """High entropy, decent coherence → VALIDATION (consolidate before building)."""
    state = make_state(personal_coherence=0.65, energy=0.70, stress=0.30, entropy=0.75)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.VALIDATION
    assert any("entropy" in i for i in decision.interventions)
    assert not decision.next_state.is_canon_write_allowed()  # conservation_rate should be high


# ── Case 3: Stress spike blocks BUILD → RECOVER ───────────────────────────────
def test_recover_mode_on_stress_spike():
    """Stress ≥ 0.80 → RECOVER regardless of coherence. Architect Protocol: human comes first."""
    state = make_state(personal_coherence=0.75, energy=0.65, stress=0.85, entropy=0.30)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.RECOVER
    assert "block_new_canon" in decision.interventions
    assert "block_high_risk_tools" in decision.interventions
    assert not decision.next_state.is_high_risk_allowed()


# ── Case 4: Low personal coherence forces RECOVER ─────────────────────────────
def test_recover_mode_on_low_personal_coherence():
    """personal_coherence < 0.30 → RECOVER. The body is speaking. Listen."""
    state = make_state(personal_coherence=0.22, energy=0.80, stress=0.40, entropy=0.20)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.RECOVER
    assert any("personal_coherence" in i for i in decision.interventions)
    assert not decision.next_state.is_high_risk_allowed()


# ── Case 5: Low energy → REFLECT ─────────────────────────────────────────────
def test_reflect_mode_on_low_energy():
    """Medium coherence + low energy → REFLECT. Not BUILD. Rest before the next sprint."""
    state = make_state(personal_coherence=0.55, energy=0.35, stress=0.40, entropy=0.30)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.REFLECT
    assert any("energy" in i for i in decision.interventions)


# ── Case 6: Medium coherence + high energy → DISCOVERY ───────────────────────
def test_discovery_mode_medium_coherence_high_energy():
    """Medium coherence + good energy + low stress → DISCOVERY (not BUILD)."""
    state = make_state(personal_coherence=0.55, energy=0.75, stress=0.25, entropy=0.30)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.DISCOVERY
    assert decision.next_state.exploration_rate > 0.5


# ── Case 7: High error rate → PROTECT ────────────────────────────────────────
def test_protect_mode_on_high_error_rate():
    """Even with decent coherence, high CI error rate → PROTECT."""
    state = make_state(personal_coherence=0.65, energy=0.70, stress=0.35, entropy=0.45)
    decision = compute_next_state(
        D6Inputs(current_state=state, recent_error_rate=0.65)
    )
    assert decision.next_state.mode == GAIAOperationalMode.PROTECT
    assert "enable_extra_logging" in decision.interventions
    assert "block_new_canon" in decision.interventions
    assert not decision.next_state.is_canon_write_allowed()


# ── Case 8: Learning dynamics are correct per mode ───────────────────────────
def test_learning_dynamics_set_correctly_for_discovery():
    """In DISCOVERY mode, exploration_rate should be high (0.9), conservation low (0.2)."""
    state = make_state(personal_coherence=0.55, energy=0.75, stress=0.25, entropy=0.30)
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.next_state.mode == GAIAOperationalMode.DISCOVERY
    assert decision.next_state.exploration_rate == 0.9
    assert decision.next_state.conservation_rate == 0.2
    assert decision.next_state.learning_rate == 0.8


# ── Case 9: Rationale string is populated ────────────────────────────────────
def test_rationale_string_populated():
    """D6 must always explain its decision — for the Architect, and for audit."""
    state = make_state()
    decision = compute_next_state(D6Inputs(current_state=state))
    assert decision.rationale.startswith("D6 →")
    assert "pc=" in decision.rationale
    assert "en=" in decision.rationale
