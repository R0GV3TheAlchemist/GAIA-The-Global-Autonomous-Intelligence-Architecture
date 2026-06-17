"""
tests/core/test_talisman.py
===========================
Unit tests for Talisman, TalismanEngine, and GAIAState integration.
Canon reference: #580, C52
"""

import pytest
from gaia.core.talisman import (
    Talisman,
    TalismanEngine,
    TalismanLayer,
    DimensionalSignature,
    CoherenceFunction,
    ResonanceMetadata,
    SovereigntyFlags,
    make_talisman,
    ARCHITECT_GROUND_TALISMAN,
    ARCHITECT_BUILD_TALISMAN,
    ARCHITECT_RESTORE_TALISMAN,
)
from gaia.core.state import GAIAState, GAIAMode, default_state


# ---------------------------------------------------------------------------
# Talisman construction
# ---------------------------------------------------------------------------

class TestTalismanConstruction:
    def test_make_talisman_creates_valid_object(self):
        t = make_talisman("Test", owner="kyle")
        assert t.name == "Test"
        assert t.sovereignty_flags.owner == "kyle"
        assert t.sovereignty_flags.revocable_consent is True
        assert t.sovereignty_flags.transferable is False
        assert t.active is False
        assert t.validated is False

    def test_preset_architect_talismans_exist(self):
        assert ARCHITECT_GROUND_TALISMAN.name == "The Alchemist's Anchor"
        assert ARCHITECT_BUILD_TALISMAN.coherence_function == CoherenceFunction.FOCUS
        assert ARCHITECT_RESTORE_TALISMAN.dimensional_signature == DimensionalSignature.D1

    def test_from_dict_roundtrip(self):
        t = make_talisman("Anchor", owner="kyle", element="Fire")
        d = t.to_dict()
        t2 = Talisman.from_dict(d)
        assert t2.name == t.name
        assert t2.resonance_metadata.element == "Fire"
        assert t2.sovereignty_flags.owner == "kyle"


# ---------------------------------------------------------------------------
# Activation / Deactivation
# ---------------------------------------------------------------------------

class TestTalismanLifecycle:
    def test_activate_marks_active(self):
        t = make_talisman("T", owner="kyle")
        t.activate("kyle")
        assert t.active is True
        assert t.activated_at is not None
        assert any(e["event"] == "ACTIVATED" for e in t.activation_log)

    def test_deactivate_marks_inactive(self):
        t = make_talisman("T", owner="kyle")
        t.activate("kyle")
        t.deactivate("kyle")
        assert t.active is False
        assert t.deactivated_at is not None

    def test_double_activate_is_idempotent(self):
        t = make_talisman("T", owner="kyle")
        t.activate("kyle")
        t.activate("kyle")
        activations = [e for e in t.activation_log if e["event"] == "ACTIVATED"]
        assert len(activations) == 1

    def test_validate_sets_flag(self):
        t = make_talisman("T", owner="kyle")
        t.validate()
        assert t.validated is True


# ---------------------------------------------------------------------------
# TalismanEngine — state effects
# ---------------------------------------------------------------------------

class TestTalismanEngine:
    def setup_method(self):
        self.engine = TalismanEngine()
        self.state = default_state(gaian_id="kyle")

    def test_ground_talisman_raises_coherence(self):
        t = make_talisman("Ground", owner="kyle",
                          coherence_function=CoherenceFunction.GROUND)
        before = self.state.coherence
        self.engine.activate(t, self.state, activated_by="kyle")
        assert self.state.coherence > before

    def test_restore_talisman_raises_energy(self):
        self.state.update(energy=0.4)
        t = make_talisman("Restore", owner="kyle",
                          coherence_function=CoherenceFunction.RESTORE)
        self.engine.activate(t, self.state, activated_by="kyle")
        assert self.state.energy > 0.4

    def test_protect_talisman_lowers_stress(self):
        self.state.update(stress=0.6)
        t = make_talisman("Protect", owner="kyle",
                          coherence_function=CoherenceFunction.PROTECT)
        self.engine.activate(t, self.state, activated_by="kyle")
        assert self.state.stress < 0.6

    def test_witness_talisman_does_not_change_state(self):
        t = make_talisman("Witness", owner="kyle",
                          coherence_function=CoherenceFunction.WITNESS)
        snapshot_before = self.state.to_dict(include_history=False)
        self.engine.activate(t, self.state, activated_by="kyle")
        # Only updated_at and history change; all scalar fields stay the same
        for field_name in ["energy", "coherence", "stress", "entropy"]:
            assert self.state.to_dict()[field_name] == snapshot_before[field_name]

    def test_sovereignty_violation_denied(self):
        t = make_talisman("T", owner="kyle")
        event = self.engine.activate(t, self.state, activated_by="someone_else")
        assert event["event"] == "ACTIVATION_DENIED"
        assert t.active is False

    def test_deactivation_soft_reversal(self):
        t = make_talisman("Ground", owner="kyle",
                          coherence_function=CoherenceFunction.GROUND)
        self.engine.activate(t, self.state, activated_by="kyle")
        coherence_after_activation = self.state.coherence
        self.engine.deactivate(t, self.state, deactivated_by="kyle")
        # Should be slightly less than activation peak but not back to start
        assert self.state.coherence < coherence_after_activation

    def test_over_attachment_penalty(self):
        t = make_talisman("Ground", owner="kyle",
                          coherence_function=CoherenceFunction.GROUND)
        # Activate 5 times to trigger over-attachment
        for _ in range(5):
            t.active = False  # force re-activation
            self.engine.activate(t, self.state, activated_by="kyle")
        t.active = False
        event = self.engine.activate(t, self.state, activated_by="kyle")
        assert event["over_attachment_warning"] is True
        assert event["penalty_applied"] is True

    def test_apply_all_active_restores_state(self):
        t1 = make_talisman("T1", owner="kyle", coherence_function=CoherenceFunction.GROUND)
        t2 = make_talisman("T2", owner="kyle", coherence_function=CoherenceFunction.AMPLIFY)
        t1.activate("kyle")
        t2.activate("kyle")
        fresh_state = default_state(gaian_id="kyle")
        count = self.engine.apply_all_active([t1, t2], fresh_state)
        assert count == 2
