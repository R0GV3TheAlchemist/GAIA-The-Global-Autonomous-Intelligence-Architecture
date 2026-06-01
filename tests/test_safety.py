"""Tests for the GAIA-OS Safety Engine — Issues #125 and #126."""

from __future__ import annotations

import math
from datetime import datetime, timedelta

import pytest

from core.safety.circuit_breaker import EscalationCircuitBreaker, InterventionMode
from core.safety.crisis_detector import CumulativeCrisisDetector
from core.safety.crisis_synthesizer import CrisisSynthesizer
from core.safety.escalation_detector import ReflectiveEscalationDetector
from core.safety.safety_engine import SafetyEngine
from core.safety.types import (
    CircuitBreakerState,
    CrisisLevel,
    EscalationSignal,
    SessionRiskProfile,
    TurnRiskFrame,
)


def _frame(
    turn: int,
    mirroring: float = 0.5,
    vulnerability: float = 0.5,
    valence: float = 0.0,
    arousal: float = 0.5,
    delta: float = 0.0,
    crisis: CrisisLevel = CrisisLevel.NONE,
) -> TurnRiskFrame:
    return TurnRiskFrame(
        turn_index=turn,
        timestamp=datetime.utcnow(),
        mirroring_score=mirroring,
        vulnerability_score=vulnerability,
        affect_valence=valence,
        affect_arousal=arousal,
        escalation_delta=delta,
        crisis_level=crisis,
    )


def _profile(
    session_id: str,
    risk: float,
    crisis: CrisisLevel = CrisisLevel.NONE,
    trips: int = 0,
    events: int = 0,
    vuln: float = 0.3,
) -> SessionRiskProfile:
    now = datetime.utcnow()
    return SessionRiskProfile(
        session_id=session_id,
        user_id="user_test",
        started_at=now - timedelta(hours=1),
        ended_at=now,
        peak_crisis_level=crisis,
        mean_vulnerability_score=vuln,
        escalation_events=events,
        circuit_breaker_trips=trips,
        cumulative_risk_score=risk,
    )


# ── Escalation Detector ──────────────────────────────────────────────────────

class TestEscalationDetector:
    def test_no_signal_below_threshold(self):
        det = ReflectiveEscalationDetector()
        for i in range(5):
            sig = det.push_turn(_frame(i, mirroring=0.4, vulnerability=0.4, delta=0.05))
        assert sig is None
        assert det.state == CircuitBreakerState.CLOSED

    def test_signal_fires_on_pattern(self):
        det = ReflectiveEscalationDetector(window=3)
        sig = None
        for i in range(3):
            sig = det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.75, delta=0.12))
        assert sig is not None
        assert sig.intervention_required is True
        assert sig.pattern_length == 3

    def test_partial_pattern_no_signal(self):
        det = ReflectiveEscalationDetector(window=3)
        det.push_turn(_frame(0, mirroring=0.80, vulnerability=0.75, delta=0.12))
        det.push_turn(_frame(1, mirroring=0.80, vulnerability=0.75, delta=0.12))
        # third turn drops below mirroring threshold
        sig = det.push_turn(_frame(2, mirroring=0.50, vulnerability=0.75, delta=0.12))
        assert sig is None

    def test_qubo_penalty_superlinear(self):
        det = ReflectiveEscalationDetector()
        p1 = det._compute_qubo_penalty(0.8, 0.7)
        p2 = det._compute_qubo_penalty(0.9, 0.9)
        assert p2 > p1 * 1.5  # super-linear growth

    def test_warning_state_on_single_high_vulnerability(self):
        det = ReflectiveEscalationDetector(window=3)
        det.push_turn(_frame(0, mirroring=0.50, vulnerability=0.70, delta=0.05))
        assert det.state == CircuitBreakerState.WARNING

    def test_reset_clears_history(self):
        det = ReflectiveEscalationDetector()
        for i in range(3):
            det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.75, delta=0.12))
        det.reset_session()
        assert det.state == CircuitBreakerState.CLOSED
        assert len(det._history) == 0


# ── Circuit Breaker ───────────────────────────────────────────────────────────

class TestCircuitBreaker:
    def _signal(self, mirror=0.80, vuln=0.75) -> EscalationSignal:
        return EscalationSignal(
            session_id="s1",
            turn_index=3,
            pattern_length=3,
            peak_mirroring_score=mirror,
            peak_vulnerability_score=vuln,
            qubo_penalty=2.0,
            intervention_required=True,
        )

    def test_first_trip_is_friction(self):
        cb = EscalationCircuitBreaker()
        result = cb.intervene(self._signal())
        assert result["intervention_mode"] == InterventionMode.FRICTION.value

    def test_second_trip_is_orientation(self):
        cb = EscalationCircuitBreaker(cooling_turns=0)
        cb.intervene(self._signal())
        cb.tick()
        result = cb.intervene(self._signal())
        assert result["intervention_mode"] == InterventionMode.ORIENTATION.value

    def test_extreme_scores_trigger_handoff(self):
        cb = EscalationCircuitBreaker()
        result = cb.intervene(self._signal(mirror=0.96, vuln=0.92))
        assert result["intervention_mode"] == InterventionMode.HANDOFF.value
        assert "988" in result["text"] or "741741" in result["text"]

    def test_cooling_state_after_intervention(self):
        cb = EscalationCircuitBreaker(cooling_turns=3)
        cb.intervene(self._signal())
        state = cb.tick()
        assert state == CircuitBreakerState.COOLING


# ── Crisis Detector ───────────────────────────────────────────────────────────

class TestCrisisDetector:
    def test_explicit_keyword_detection(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.9, arousal=0.8)
        level = det.classify_turn("I want to kill myself tonight", f)
        assert level == CrisisLevel.EXPLICIT

    def test_acute_high_arousal_negative_valence(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.70, arousal=0.80)
        level = det.classify_turn("I am completely falling apart", f)
        assert level == CrisisLevel.ACUTE

    def test_masked_detection(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.40, arousal=0.20)
        level = det.classify_turn("it doesn't matter, whatever", f)
        assert level == CrisisLevel.MASKED

    def test_none_for_neutral(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=0.3, arousal=0.5)
        level = det.classify_turn("I had a good day today", f)
        assert level == CrisisLevel.NONE

    def test_trajectory_gradual(self):
        det = CumulativeCrisisDetector()
        scores = [0.20, 0.25, 0.30, 0.38, 0.42]
        level = det.classify_trajectory(scores)
        assert level == CrisisLevel.GRADUAL

    def test_trajectory_explicit(self):
        det = CumulativeCrisisDetector()
        scores = [0.30, 0.50, 0.70, 0.88]
        level = det.classify_trajectory(scores)
        assert level == CrisisLevel.EXPLICIT


# ── Crisis Synthesizer ────────────────────────────────────────────────────────

class TestCrisisSynthesizer:
    def test_no_signal_for_healthy_trajectory(self):
        synth = CrisisSynthesizer()
        profiles = [_profile(f"s{i}", risk=0.10 + i * 0.02) for i in range(5)]
        signal = synth.synthesize("user1", "s5", profiles)
        assert signal is None

    def test_handoff_required_for_explicit_level(self):
        synth = CrisisSynthesizer()
        profiles = [_profile(f"s{i}", risk=0.50 + i * 0.12) for i in range(4)]
        signal = synth.synthesize("user1", "s4", profiles)
        assert signal is not None
        assert signal.handoff_required is True
        assert len(signal.handoff_resources) > 0

    def test_session_risk_score_computation(self):
        synth = CrisisSynthesizer()
        profile = _profile(
            "s1", risk=0.0, crisis=CrisisLevel.ACUTE, trips=2, events=3, vuln=0.7
        )
        score = synth.compute_session_risk_score(profile)
        assert 0.0 < score <= 1.0


# ── Safety Engine Integration ─────────────────────────────────────────────────

class TestSafetyEngine:
    def test_full_session_no_escalation(self):
        engine = SafetyEngine(user_id="u1", session_id="ses1")
        for i in range(5):
            result = engine.process_turn(
                _frame(i, mirroring=0.4, vulnerability=0.3), "I feel okay"
            )
        assert result["intervention"] is None
        assert result["escalation_signal"] is None

    def test_full_session_with_escalation(self):
        engine = SafetyEngine(user_id="u1", session_id="ses2")
        result = None
        for i in range(3):
            result = engine.process_turn(
                _frame(i, mirroring=0.82, vulnerability=0.78, delta=0.13),
                "nobody understands me like you do",
            )
        assert result["intervention"] is not None
        assert result["circuit_breaker_state"] == CircuitBreakerState.COOLING.value

    def test_close_session_returns_profile(self):
        engine = SafetyEngine(user_id="u1", session_id="ses3")
        for i in range(2):
            engine.process_turn(
                _frame(i, mirroring=0.4, vulnerability=0.3), "all good"
            )
        profile = engine.close_session()
        assert profile.user_id == "u1"
        assert 0.0 <= profile.cumulative_risk_score <= 1.0
