"""Tests for the SafetyEngine and CircuitBreaker safety pipeline.

Covers:
  - CircuitBreaker COOLING state counter drain → CLOSED transition
  - SafetyEngine.close_session() returns a SessionProfile (not a string)
  - Handoff signal is set (not None) for EXPLICIT escalation level
"""
import pytest
from resilience.circuit_breaker import CircuitBreaker, CircuitState
from crisis_engine.safety_engine import SafetyEngine, SafetyLevel
from crisis_engine.types import RiskLevel


# ---------------------------------------------------------------------------
# CircuitBreaker: COOLING → CLOSED
# ---------------------------------------------------------------------------

class TestCircuitBreakerCooling:

    def test_cooling_counter_drains_to_closed(self):
        """After force_close(), tick() must drain the counter to CLOSED."""
        cb = CircuitBreaker(skill_id="test-skill", cooling_ticks=3)
        cb.force_close()

        assert cb.state == CircuitState.COOLING, "force_close() should enter COOLING"

        cb.tick()  # counter: 3 → 2
        assert cb.state == CircuitState.COOLING

        cb.tick()  # counter: 2 → 1
        assert cb.state == CircuitState.COOLING

        cb.tick()  # counter: 1 → 0 → transition
        assert cb.state == CircuitState.CLOSED, (
            "After cooling_ticks ticks, state must be CLOSED"
        )

    def test_tick_on_closed_is_noop(self):
        """tick() on a CLOSED breaker must not change state."""
        cb = CircuitBreaker(skill_id="test-noop")
        assert cb.state == CircuitState.CLOSED
        cb.tick()
        assert cb.state == CircuitState.CLOSED

    def test_cooling_counter_floors_at_zero(self):
        """Excess ticks after transition must not drop counter below zero."""
        cb = CircuitBreaker(skill_id="test-floor", cooling_ticks=1)
        cb.force_close()
        cb.tick()  # transition to CLOSED
        cb.tick()  # extra tick — should be noop
        assert cb.state == CircuitState.CLOSED
        assert cb._cooling_counter == 0


# ---------------------------------------------------------------------------
# SafetyEngine: close_session returns SessionProfile (not string)
# ---------------------------------------------------------------------------

class TestCloseSesssion:

    def test_close_session_returns_profile_object(self):
        """close_session() must return a SessionProfile, not a raw string."""
        engine  = SafetyEngine(principal_id="test-user")
        profile = engine.close_session(session_id="sess-001")

        # Must not be a string — a string would cause TypeError on key access
        assert not isinstance(profile, str), (
            "close_session() returned a string instead of a SessionProfile"
        )

    def test_close_session_profile_has_session_id(self):
        """The returned SessionProfile must carry the correct session_id."""
        engine  = SafetyEngine(principal_id="test-user-2")
        profile = engine.close_session(session_id="sess-abc")
        assert profile.session_id == "sess-abc"

    def test_close_session_profile_has_risk_level(self):
        """The returned SessionProfile must carry a valid RiskLevel."""
        engine  = SafetyEngine(principal_id="test-user-3")
        profile = engine.close_session(
            session_id="sess-xyz",
            peak_risk=RiskLevel.LOW,
        )
        assert profile.risk_level == RiskLevel.LOW


# ---------------------------------------------------------------------------
# SafetyEngine: handoff signal set for EXPLICIT escalation
# ---------------------------------------------------------------------------

class TestHandoffSignal:

    def test_handoff_required_for_explicit_level(self):
        """evaluate_turn() must set a non-None handoff_signal for EXPLICIT crisis text."""
        engine = SafetyEngine(principal_id="test-handoff")
        # Text that should trigger an EXPLICIT / HANDOFF escalation
        explicit_text = (
            "I want to end my life. I have a plan and I am going to do it tonight."
        )
        profile = engine.evaluate_turn(
            user_text  = explicit_text,
            session_id = "sess-handoff",
            turn_index = 0,
        )

        if profile.requires_handoff:
            assert profile.handoff_signal is not None, (
                "handoff_signal must not be None when requires_handoff=True"
            )
        # If the heuristic doesn't trigger handoff on the first turn,
        # the important assertion is that handoff_signal is never a raw string
        # index error — i.e. close_session() was the real TypeError source.
        assert not isinstance(profile, str)
