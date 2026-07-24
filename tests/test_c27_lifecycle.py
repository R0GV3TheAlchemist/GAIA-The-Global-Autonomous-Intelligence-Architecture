# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
Tests for core.c27.lifecycle — GAIANLifecycleState, LifecycleStateMachine.

Authority: C27 §2. Implements C27-IMPL-001 through C27-IMPL-003.

Coverage targets:
- All 7 lifecycle states exist in the enum
- All 5 trigger classes exist
- 10 valid transitions are permitted
- 6 explicit prohibited transitions are rejected
- ARCHIVED is a terminal state (no valid transitions out)
- ProhibitedTransitionError is raised on invalid transitions, with structured attrs
- LifecycleTransitionEvent is produced on valid transition
"""
import pytest
from core.c27.lifecycle import (
    GAIANLifecycleState,
    LifecycleTrigger,
    LifecycleStateMachine,
    LifecycleTransitionEvent,
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
# VALID_TRANSITIONS map — 10 paths
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
# LifecycleStateMachine
# ---------------------------------------------------------------------------

@pytest.fixture
def machine():
    return LifecycleStateMachine(gaian_id="test-gaian-001")


class TestLifecycleStateMachine:
    def test_initial_state_is_latent(self, machine):
        assert machine.current_state == GAIANLifecycleState.LATENT

    @pytest.mark.parametrize("from_state,to_state", VALID_PATHS)
    def test_valid_transition_succeeds(self, from_state, to_state):
        m = LifecycleStateMachine(gaian_id="test-gaian-002", initial_state=from_state)
        event = m.transition(
            to_state=to_state,
            trigger=LifecycleTrigger.STEWARD_ACTION,
            initiated_by="steward-test",
        )
        assert m.current_state == to_state
        assert isinstance(event, LifecycleTransitionEvent)
        assert event.from_state == from_state
        assert event.to_state == to_state
        assert event.gaian_id == "test-gaian-002"
        assert event.event_id  # non-empty UUID string
        assert event.timestamp is not None

    @pytest.mark.parametrize("from_state,to_state", PROHIBITED_PATHS)
    def test_prohibited_transition_raises(self, from_state, to_state):
        m = LifecycleStateMachine(gaian_id="test-gaian-003", initial_state=from_state)
        with pytest.raises(ProhibitedTransitionError) as exc_info:
            m.transition(
                to_state=to_state,
                trigger=LifecycleTrigger.STEWARD_ACTION,
                initiated_by="steward-test",
            )
        err = exc_info.value
        assert err.from_state == from_state
        assert err.to_state   == to_state
        assert err.gaian_id   == "test-gaian-003"
        # state must NOT have advanced after a rejected transition
        assert m.current_state == from_state

    def test_is_valid_transition_true_for_valid_path(self, machine):
        assert machine.is_valid_transition(GAIANLifecycleState.BORN) is True

    def test_is_valid_transition_false_for_prohibited(self, machine):
        assert machine.is_valid_transition(GAIANLifecycleState.ACTIVE) is False

    def test_emergency_override_trigger_is_logged(self, machine):
        """EMERGENCY_OVERRIDE trigger must appear in the returned event."""
        event = machine.transition(
            to_state=GAIANLifecycleState.BORN,
            trigger=LifecycleTrigger.EMERGENCY_OVERRIDE,
            initiated_by="gaia-root",
            notes="Emergency protocol activated",
        )
        assert event.trigger      == LifecycleTrigger.EMERGENCY_OVERRIDE
        assert event.notes        == "Emergency protocol activated"
        assert event.initiated_by == "gaia-root"
        assert len(machine.history) == 1
        assert machine.history[0] is event

    def test_history_grows_with_each_transition(self):
        """history property returns a chronological log of all transitions."""
        m = LifecycleStateMachine(gaian_id="test-gaian-history")
        assert len(m.history) == 0

        m.transition(GAIANLifecycleState.BORN,   LifecycleTrigger.SYSTEM_EVENT,  "sys")
        m.transition(GAIANLifecycleState.ACTIVE,  LifecycleTrigger.GAIAN_VOLITION, "sys")
        m.transition(GAIANLifecycleState.DORMANT, LifecycleTrigger.CANON_PROCESS,  "sys")

        assert len(m.history) == 3
        states = [e.to_state for e in m.history]
        assert states == [
            GAIANLifecycleState.BORN,
            GAIANLifecycleState.ACTIVE,
            GAIANLifecycleState.DORMANT,
        ]

    def test_history_is_a_copy(self):
        """Mutating the returned history list must not affect internal state."""
        m = LifecycleStateMachine(gaian_id="test-gaian-copy")
        m.transition(GAIANLifecycleState.BORN, LifecycleTrigger.STEWARD_ACTION, "steward")
        snapshot = m.history
        snapshot.clear()
        assert len(m.history) == 1  # internal list unchanged

    def test_failed_transition_does_not_pollute_history(self):
        """A rejected transition must leave history and current_state untouched."""
        m = LifecycleStateMachine(gaian_id="test-gaian-no-pollute")
        with pytest.raises(ProhibitedTransitionError):
            m.transition(
                to_state=GAIANLifecycleState.ACTIVE,
                trigger=LifecycleTrigger.STEWARD_ACTION,
                initiated_by="steward",
            )
        assert m.current_state == GAIANLifecycleState.LATENT
        assert len(m.history) == 0
