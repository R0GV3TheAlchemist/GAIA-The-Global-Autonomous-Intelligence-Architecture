"""
tests/core/test_state.py
========================
Unit tests for GAIAState and D6 Meta-Coherence Engine.
Canon reference: C52 Part VI, GAIA_D6_META_COHERENCE_ENGINE.md
Issues: #571, #576
"""

import pytest
from gaia.core.state import (
    GAIAState,
    GAIAMode,
    default_state,
    depleted_state,
    integrate_state,
)


# ---------------------------------------------------------------------------
# Construction and validation
# ---------------------------------------------------------------------------

class TestGAIAStateConstruction:
    def test_default_state_is_valid(self):
        s = default_state()
        assert 0.0 <= s.energy <= 1.0
        assert 0.0 <= s.coherence <= 1.0
        assert 0.0 <= s.stress <= 1.0
        assert s.mode == GAIAMode.BUILD

    def test_invalid_field_raises(self):
        with pytest.raises(ValueError):
            GAIAState(energy=1.5)   # out of bounds

    def test_negative_field_raises(self):
        with pytest.raises(ValueError):
            GAIAState(stress=-0.1)

    def test_from_dict_roundtrip(self):
        s = default_state(gaian_id="kyle", session_id="sess-001")
        d = s.to_dict()
        s2 = GAIAState.from_dict(d)
        assert s2.energy == s.energy
        assert s2.mode == s.mode
        assert s2.gaian_id == "kyle"


# ---------------------------------------------------------------------------
# Dimensional health flags (C52 §6.2)
# ---------------------------------------------------------------------------

class TestDimensionalHealth:
    def test_d1_critical_when_energy_low(self):
        s = GAIAState(energy=0.10)
        assert s.d1_critical is True

    def test_d1_not_critical_when_energy_ok(self):
        s = GAIAState(energy=0.5)
        assert s.d1_critical is False

    def test_d2_distress_when_stress_high(self):
        s = GAIAState(stress=0.80)
        assert s.d2_distress is True

    def test_d3_saturated_requires_both_conditions(self):
        # High entropy alone is not enough
        s = GAIAState(entropy=0.75, energy=0.6)
        assert s.d3_saturated is False
        # High entropy + low energy = saturated
        s2 = GAIAState(entropy=0.75, energy=0.25)
        assert s2.d3_saturated is True

    def test_d4_isolated_when_conservation_high(self):
        s = GAIAState(conservation_rate=0.90)
        assert s.d4_isolated is True

    def test_d6_approaching_requires_all_conditions(self):
        # Missing INTEGRATE mode
        s = GAIAState(coherence=0.90, stress=0.10, entropy=0.10, mode=GAIAMode.BUILD)
        assert s.d6_approaching is False
        # All conditions met
        s2 = GAIAState(coherence=0.90, stress=0.10, entropy=0.10, mode=GAIAMode.INTEGRATE)
        assert s2.d6_approaching is True


# ---------------------------------------------------------------------------
# D6 Mode recommendations (GAIA_D6_META_COHERENCE_ENGINE.md)
# ---------------------------------------------------------------------------

class TestRecommendedMode:
    def test_d1_critical_recommends_rest(self):
        s = GAIAState(energy=0.10, stress=0.3)
        assert s.recommended_mode() == GAIAMode.REST

    def test_high_stress_low_energy_recommends_recover(self):
        s = GAIAState(stress=0.85, energy=0.30)
        assert s.recommended_mode() == GAIAMode.RECOVER

    def test_high_stress_moderate_energy_recommends_protect(self):
        s = GAIAState(stress=0.85, energy=0.60)
        assert s.recommended_mode() == GAIAMode.PROTECT

    def test_high_entropy_recommends_reflect(self):
        s = GAIAState(entropy=0.80, energy=0.5, stress=0.3)
        assert s.recommended_mode() == GAIAMode.REFLECT

    def test_healthy_low_exploration_recommends_build(self):
        s = GAIAState(
            energy=0.8, coherence=0.8, stress=0.2,
            entropy=0.2, exploration_rate=0.4
        )
        assert s.recommended_mode() == GAIAMode.BUILD

    def test_healthy_high_exploration_recommends_create(self):
        s = GAIAState(
            energy=0.8, coherence=0.8, stress=0.2,
            entropy=0.2, exploration_rate=0.70
        )
        assert s.recommended_mode() == GAIAMode.CREATE

    def test_d6_approaching_recommends_integrate(self):
        s = GAIAState(
            coherence=0.92, stress=0.08, entropy=0.08,
            energy=0.9, mode=GAIAMode.INTEGRATE
        )
        assert s.recommended_mode() == GAIAMode.INTEGRATE

    def test_high_learning_recommends_research(self):
        s = GAIAState(
            learning_rate=0.8, exploration_rate=0.75,
            energy=0.5, coherence=0.6, stress=0.4, entropy=0.4
        )
        assert s.recommended_mode() == GAIAMode.RESEARCH


# ---------------------------------------------------------------------------
# Priority dimension cascade (C52 §2.2)
# ---------------------------------------------------------------------------

class TestPriorityDimension:
    def test_d1_critical_overrides_all(self):
        # Even if stress is also high, D1 wins
        s = GAIAState(energy=0.05, stress=0.9)
        assert s.priority_dimension == "D1_PHYSICAL_CRITICAL"

    def test_d2_distress_when_d1_ok(self):
        s = GAIAState(energy=0.6, stress=0.85)
        assert s.priority_dimension == "D2_EMOTIONAL_DISTRESS"

    def test_default_is_d3_operational(self):
        s = default_state()
        assert s.priority_dimension == "D3_OPERATIONAL"


# ---------------------------------------------------------------------------
# Update + history
# ---------------------------------------------------------------------------

class TestStateUpdate:
    def test_update_records_history(self):
        s = default_state()
        original_energy = s.energy
        s.update(energy=0.5)
        assert s.energy == 0.5
        assert len(s.history) == 1
        assert s.history[0]["snapshot"]["energy"] == original_energy

    def test_update_invalid_field_raises(self):
        s = default_state()
        with pytest.raises(AttributeError):
            s.update(nonexistent_field=0.5)

    def test_update_out_of_bounds_raises(self):
        s = default_state()
        with pytest.raises(ValueError):
            s.update(energy=1.5)

    def test_apply_recommended_mode_switches_mode(self):
        # Force conditions that should trigger REST
        s = GAIAState(energy=0.10, mode=GAIAMode.BUILD)
        s.apply_recommended_mode()
        assert s.mode == GAIAMode.REST

    def test_apply_recommended_mode_no_change_when_correct(self):
        s = default_state()  # BUILD mode, healthy fields
        original_mode = s.mode
        s.apply_recommended_mode()
        # Should stay BUILD
        assert s.mode == original_mode


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

class TestConvenienceConstructors:
    def test_depleted_state_is_d1_critical(self):
        s = depleted_state()
        assert s.d1_critical is True
        assert s.recommended_mode() == GAIAMode.REST

    def test_integrate_state_is_d6_approaching(self):
        s = integrate_state()
        assert s.d6_approaching is True

    def test_repr_does_not_raise(self):
        s = default_state()
        r = repr(s)
        assert "GAIAState" in r
        assert "BUILD" in r
