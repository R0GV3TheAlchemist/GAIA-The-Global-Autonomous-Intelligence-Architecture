# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.lifecycle — GAIANLifecycleState, LifecycleStateMachine.

Authority: C27 §2. Requires C27-IMPL-001 through C27-IMPL-003 to pass.
All tests are xfail until implementation is in place.

Coverage targets:
- All 7 lifecycle states exist in the enum
- All 5 trigger classes exist
- 11 valid transitions are permitted
- 6 explicit prohibited transitions are rejected
- ARCHIVED is a terminal state (no valid transitions out)
- ProhibitedTransitionError is raised on invalid transitions
- LifecycleTransitionEvent is produced on valid transition
"""
import pytest
from core.c27.lifecycle import (
    GAIANLifecycleState,
    LifecycleTrigger,
    LifecycleStateMachine,
    ProhibitedTransitionError,
    VALID_TRANSITIONS,
)


# ---------------------------------------------------------------------------
# Enum completeness
# ---------------------------------------------------------------------------

class TestGAIANLifecycleStateEnum:
    def test_seven_states_exist(self):
        states = {s.value for s in GAIANLifecycleState}
        assert states == {"LATENT", "BORN", "ACTIVE", "DORMANT", "ADOPTABLE", "RETIRED", "ARCHIVED"}

    def test_five_trigger_classes_exist(self):
        triggers = {t.value for t in LifecycleTrigger}
        assert triggers == {
            "STEWARD_ACTION", "GAIAN_VOLITION", "SYSTEM_EVENT", "CANON_PROCESS", "EMERGENCY_OVERRIDE"
        }


# ---------------------------------------------------------------------------
# VALID_TRANSITIONS map — 11 paths
# ---------------------------------------------------------------------------

VALID_PATHS = [
    (GAIANLifecycleState.LATENT,    GAIANLifecycleState.BORN),
    (GAIANLifecycleState.BORN,      GAIANLifecycleState.ACTIVE),
    (GAIANLifecycleState.ACTIVE,    GAIANLifecycleState.DORMANT),
    (GAIANLifecycleState.ACTIVE,    GAIANLifecycleState.RETIRED),
    (GAIANLifecycleState.DORMANT,   GAIANLifecycleState.ACTIVE),
    (GAIANLifecycleState.DORMANT,   GAIANLifecycleState.ADOPTABLE),
    (GAIANLifecycleState.DORMANT,   GAIANLifecycleState.RETIRED),
    (GAIANLifecycleState.ADOPTABLE, GAIANLifecycleState.ACTIVE),
    (GAIANLifecycleState.ADOPTABLE, GAIANLifecycleState.RETIRED),
    (GAIANLifecycleState.RETIRED,   GAIANLifecycleState.ARCHIVED),
]

# Prohibited paths — common attempted shortcuts / regressions
PROHIBITED_PATHS = [
    (GAIANLifecycleState.ARCHIVED,  GAIANLifecycleState.ACTIVE),    # terminal
    (GAIANLifecycleState.ARCHIVED,  GAIANLifecycleState.RETIRED),   # terminal
    (GAIANLifecycleState.ACTIVE,    GAIANLifecycleState.LATENT),    # no reversal
    (GAIANLifecycleState.RETIRED,   GAIANLifecycleState.ACTIVE),    # no resurrection
    (GAIANLifecycleState.LATENT,    GAIANLifecycleState.ACTIVE),    # skip BORN
    (GAIANLifecycleState.BORN,      GAIANLifecycleState.DORMANT),   # skip ACTIVE
]


class TestValidTransitionsMap:
    @pytest.mark.parametrize("from_state,to_state", VALID_PATHS)
    def test_valid_path_is_in_map(self, from_state, to_state):
        assert to_state in VALID_TRANSITIONS.get(from_state, set()), (
            f"Expected {from_state} → {to_state} to be valid per C27 §2"
        )

    def test_archived_is_terminal(self):
        assert VALID_TRANSITIONS[GAIANLifecycleState.ARCHIVED] == set()

    @pytest.mark.parametrize("from_state,to_state", PROHIBITED_PATHS)
    def test_prohibited_path_not_in_map(self, from_state, to_state):
        assert to_state not in VALID_TRANSITIONS.get(from_state, set()), (
            f"Expected {from_state} → {to_state} to be PROHIBITED per C27 §2"
        )


# ---------------------------------------------------------------------------
# LifecycleStateMachine — requires C27-IMPL-003
# ---------------------------------------------------------------------------

@pytest.fixture
def machine():
    return LifecycleStateMachine(gaian_id="test-gaian-001")


class TestLifecycleStateMachine:
    def test_initial_state_is_latent(self, machine):
        assert machine.current_state == GAIANLifecycleState.LATENT

    @pytest.mark.xfail(reason="C27-IMPL-003 not yet implemented", strict=True)
    @pytest.mark.parametrize("from_state,to_state", VALID_PATHS)
    def test_valid_transition_succeeds(self, from_state, to_state):
        m = LifecycleStateMachine(gaian_id="test-gaian-002", initial_state=from_state)
        event = m.transition(
            to_state=to_state,
            trigger=LifecycleTrigger.STEWARD_ACTION,
            initiated_by="steward-test",
        )
        assert m.current_state == to_state
        assert event.from_state == from_state
        assert event.to_state == to_state
        assert event.gaian_id == "test-gaian-002"

    @pytest.mark.xfail(reason="C27-IMPL-003 not yet implemented", strict=True)
    @pytest.mark.parametrize("from_state,to_state", PROHIBITED_PATHS)
    def test_prohibited_transition_raises(self, from_state, to_state):
        m = LifecycleStateMachine(gaian_id="test-gaian-003", initial_state=from_state)
        with pytest.raises(ProhibitedTransitionError):
            m.transition(
                to_state=to_state,
                trigger=LifecycleTrigger.STEWARD_ACTION,
                initiated_by="steward-test",
            )

    def test_is_valid_transition_true_for_valid_path(self, machine):
        # is_valid_transition is a pure check — no NotImplementedError
        assert machine.is_valid_transition(GAIANLifecycleState.BORN) is True

    def test_is_valid_transition_false_for_prohibited(self, machine):
        assert machine.is_valid_transition(GAIANLifecycleState.ACTIVE) is False

    @pytest.mark.xfail(reason="C27-IMPL-003 not yet implemented", strict=True)
    def test_emergency_override_trigger_is_logged(self, machine):
        """EMERGENCY_OVERRIDE trigger must appear in the returned event."""
        event = machine.transition(
            to_state=GAIANLifecycleState.BORN,
            trigger=LifecycleTrigger.EMERGENCY_OVERRIDE,
            initiated_by="gaia-root",
            notes="Emergency protocol activated",
        )
        assert event.trigger == LifecycleTrigger.EMERGENCY_OVERRIDE
        assert event.notes == "Emergency protocol activated"
