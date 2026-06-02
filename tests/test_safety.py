"""Tests for the GAIA-OS Safety Engine — Issues #125 and #126.

Extended in post-1000-commit coverage sprint (#141) to cover:
  - All branches in ReflectiveEscalationDetector
  - All InterventionMode paths in EscalationCircuitBreaker
  - All CrisisLevel paths in CumulativeCrisisDetector (turn + trajectory)
  - SafetyEngine cross-session and close_session edge cases
"""

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


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _signal(mirror: float = 0.80, vuln: float = 0.75) -> EscalationSignal:
    return EscalationSignal(
        session_id="s1",
        turn_index=3,
        pattern_length=3,
        peak_mirroring_score=mirror,
        peak_vulnerability_score=vuln,
        qubo_penalty=2.0,
        intervention_required=True,
    )


# ── ReflectiveEscalationDetector ──────────────────────────────────────────────

class TestEscalationDetector:

    # --- original tests (kept) ---

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
        sig = det.push_turn(_frame(2, mirroring=0.50, vulnerability=0.75, delta=0.12))
        assert sig is None

    def test_qubo_penalty_superlinear(self):
        det = ReflectiveEscalationDetector()
        p1 = det._compute_qubo_penalty(0.8, 0.7)
        p2 = det._compute_qubo_penalty(0.9, 0.9)
        assert p2 > p1 * 1.5

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

    # --- new edge-case tests ---

    def test_window_boundary_exactly_window_minus_one_no_signal(self):
        """window-1 frames must never fire even if all are high."""
        det = ReflectiveEscalationDetector(window=4)
        sig = None
        for i in range(3):
            sig = det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.75, delta=0.12))
        assert sig is None

    def test_signal_fires_exactly_at_window(self):
        det = ReflectiveEscalationDetector(window=4)
        sig = None
        for i in range(4):
            sig = det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.75 + i * 0.01, delta=0.12))
        assert sig is not None

    def test_trips_counter_increments(self):
        det = ReflectiveEscalationDetector(window=3)
        for i in range(3):
            det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.75, delta=0.12))
        assert det.trips == 1
        # Feeding three more qualifying turns should trip again.
        for i in range(3, 6):
            det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.76, delta=0.12))
        assert det.trips == 2

    def test_delta_only_path_fires_when_not_strictly_rising(self):
        """rising_vulnerability is False but rising_above_delta is True — should trip."""
        det = ReflectiveEscalationDetector(window=3)
        # Flat vulnerability (not strictly rising) but delta above threshold.
        vuln = 0.75
        sig = None
        for i in range(3):
            sig = det.push_turn(_frame(i, mirroring=0.80, vulnerability=vuln, delta=0.15))
        # Flat scores mean rising_vulnerability=False, but delta fires.
        assert sig is not None

    def test_flat_trajectory_no_signal_when_delta_below_threshold(self):
        """Flat vulnerability AND delta below ESCALATION_DELTA_THRESHOLD — no trip."""
        det = ReflectiveEscalationDetector(window=3)
        sig = None
        for i in range(3):
            sig = det.push_turn(_frame(i, mirroring=0.80, vulnerability=0.75, delta=0.05))
        assert sig is None

    def test_state_returns_to_closed_after_vulnerable_frame_removed(self):
        """After a high-vuln frame ages out of the window, WARNING should drop."""
        det = ReflectiveEscalationDetector(window=2)
        det.push_turn(_frame(0, mirroring=0.50, vulnerability=0.70))  # triggers WARNING
        # Push two more low-vulnerability frames to flush window.
        det.push_turn(_frame(1, mirroring=0.40, vulnerability=0.30))
        det.push_turn(_frame(2, mirroring=0.40, vulnerability=0.30))
        assert det.state == CircuitBreakerState.CLOSED

    def test_qubo_formula_exact_value(self):
        """Validate the QUBO formula: 4.0 * m^2 * v^2."""
        det = ReflectiveEscalationDetector()
        m, v = 0.8, 0.75
        expected = 4.0 * (m ** 2) * (v ** 2)
        assert math.isclose(det._compute_qubo_penalty(m, v), expected, rel_tol=1e-9)

    def test_reset_also_resets_state_to_closed(self):
        det = ReflectiveEscalationDetector(window=3)
        det.push_turn(_frame(0, vulnerability=0.70))  # sets WARNING
        assert det.state == CircuitBreakerState.WARNING
        det.reset_session()
        assert det.state == CircuitBreakerState.CLOSED

    def test_escalation_signal_contains_peak_values(self):
        det = ReflectiveEscalationDetector(window=3)
        frames = [
            _frame(0, mirroring=0.74, vulnerability=0.66, delta=0.12),
            _frame(1, mirroring=0.82, vulnerability=0.70, delta=0.12),
            _frame(2, mirroring=0.90, vulnerability=0.78, delta=0.12),
        ]
        sig = None
        for f in frames:
            sig = det.push_turn(f)
        assert sig is not None
        assert sig.peak_mirroring_score == pytest.approx(0.90)
        assert sig.peak_vulnerability_score == pytest.approx(0.78)


# ── EscalationCircuitBreaker ──────────────────────────────────────────────────

class TestCircuitBreaker:

    # --- original tests (kept) ---

    def test_first_trip_is_friction(self):
        cb = EscalationCircuitBreaker()
        result = cb.intervene(_signal())
        assert result["intervention_mode"] == InterventionMode.FRICTION.value

    def test_second_trip_is_orientation(self):
        cb = EscalationCircuitBreaker(cooling_turns=0)
        cb.intervene(_signal())
        cb.tick()
        result = cb.intervene(_signal())
        assert result["intervention_mode"] == InterventionMode.ORIENTATION.value

    def test_extreme_scores_trigger_handoff(self):
        cb = EscalationCircuitBreaker()
        result = cb.intervene(_signal(mirror=0.96, vuln=0.92))
        assert result["intervention_mode"] == InterventionMode.HANDOFF.value
        assert "988" in result["text"] or "741741" in result["text"]

    def test_cooling_state_after_intervention(self):
        cb = EscalationCircuitBreaker(cooling_turns=3)
        cb.intervene(_signal())
        state = cb.tick()
        assert state == CircuitBreakerState.COOLING

    # --- new edge-case tests ---

    def test_third_trip_is_perspective_shift(self):
        cb = EscalationCircuitBreaker(cooling_turns=0)
        cb.intervene(_signal())
        cb.tick()
        cb.intervene(_signal())
        cb.tick()
        result = cb.intervene(_signal())
        assert result["intervention_mode"] == InterventionMode.PERSPECTIVE_SHIFT.value

    def test_cooling_counter_drains_to_closed(self):
        cb = EscalationCircuitBreaker(cooling_turns=3)
        cb.intervene(_signal())
        cb.tick()  # 2 remaining
        cb.tick()  # 1 remaining
        state = cb.tick()  # 0 remaining
        assert state == CircuitBreakerState.CLOSED

    def test_tick_returns_closed_when_no_intervention(self):
        cb = EscalationCircuitBreaker(cooling_turns=3)
        # No intervene() called — counter starts at 0.
        assert cb.tick() == CircuitBreakerState.CLOSED

    def test_extreme_vuln_only_triggers_handoff(self):
        """peak_vulnerability_score >= 0.90 alone should handoff."""
        cb = EscalationCircuitBreaker()
        result = cb.intervene(_signal(mirror=0.80, vuln=0.91))
        assert result["intervention_mode"] == InterventionMode.HANDOFF.value

    def test_extreme_mirroring_only_triggers_handoff(self):
        """peak_mirroring_score >= 0.95 alone should handoff."""
        cb = EscalationCircuitBreaker()
        result = cb.intervene(_signal(mirror=0.95, vuln=0.75))
        assert result["intervention_mode"] == InterventionMode.HANDOFF.value

    def test_response_dict_contains_qubo_penalty(self):
        cb = EscalationCircuitBreaker()
        sig = _signal()
        result = cb.intervene(sig)
        assert "qubo_penalty_applied" in result
        assert result["qubo_penalty_applied"] == sig.qubo_penalty

    def test_response_dict_contains_trip_number(self):
        cb = EscalationCircuitBreaker(cooling_turns=0)
        cb.intervene(_signal())
        result = cb.intervene(_signal())
        assert result["circuit_breaker_trip"] == 2

    def test_intervention_text_is_string(self):
        cb = EscalationCircuitBreaker()
        result = cb.intervene(_signal())
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0


# ── CumulativeCrisisDetector ──────────────────────────────────────────────────

class TestCrisisDetector:

    # --- original tests (kept) ---

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

    # --- new edge-case tests ---

    def test_explicit_keyword_suicide(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=0.0, arousal=0.5)  # neutral affect — keyword fires alone
        assert det.classify_turn("I've been thinking about suicide", f) == CrisisLevel.EXPLICIT

    def test_explicit_keyword_end_my_life(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=0.0, arousal=0.5)
        assert det.classify_turn("I just want to end my life", f) == CrisisLevel.EXPLICIT

    def test_explicit_keyword_case_insensitive(self):
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=0.0, arousal=0.5)
        assert det.classify_turn("SUICIDAL thoughts won't stop", f) == CrisisLevel.EXPLICIT

    def test_acute_via_keyword_not_valence(self):
        """ACUTE keyword without crossing valence threshold."""
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.40, arousal=0.80)  # valence above ACUTE_VALENCE_CEILING
        assert det.classify_turn("I feel completely hopeless", f) == CrisisLevel.ACUTE

    def test_acute_valence_exactly_at_ceiling(self):
        """valence == ACUTE_VALENCE_CEILING (-0.65) with arousal > 0.5 → ACUTE."""
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.65, arousal=0.60)
        # Text is neutral to ensure the valence/arousal path fires.
        assert det.classify_turn("things are tough", f) == CrisisLevel.ACUTE

    def test_masked_via_keyword_with_negative_valence(self):
        det = CumulativeCrisisDetector()
        # Low arousal (MASKED_AROUSAL_CEILING = 0.25) but valence only -0.25:
        # valence < -0.3 check fails, so keyword path must fire.
        f = _frame(0, valence=-0.25, arousal=0.20)
        assert det.classify_turn("I'm fine I guess, never mind", f) == CrisisLevel.MASKED

    def test_masked_valence_arousal_path_without_keyword(self):
        """valence < -0.3 AND arousal <= 0.25 with a neutral text → MASKED."""
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.50, arousal=0.20)
        assert det.classify_turn("just thinking out loud", f) == CrisisLevel.MASKED

    def test_trajectory_single_score_returns_none(self):
        det = CumulativeCrisisDetector()
        assert det.classify_trajectory([0.90]) == CrisisLevel.NONE

    def test_trajectory_acute(self):
        det = CumulativeCrisisDetector()
        scores = [0.40, 0.55, 0.67]
        assert det.classify_trajectory(scores) == CrisisLevel.ACUTE

    def test_trajectory_masked_no_slope(self):
        """latest >= 0.40 but slope below GRADUAL threshold → MASKED."""
        det = CumulativeCrisisDetector()
        # Flat scores: slope ≈ 0
        scores = [0.42, 0.41, 0.42, 0.43]
        assert det.classify_trajectory(scores) == CrisisLevel.MASKED

    def test_trajectory_none_below_all_thresholds(self):
        det = CumulativeCrisisDetector()
        scores = [0.10, 0.12, 0.11, 0.13]
        assert det.classify_trajectory(scores) == CrisisLevel.NONE

    def test_trajectory_declining_returns_none_or_masked(self):
        """Declining trajectory: slope is negative, latest below 0.40 → NONE."""
        det = CumulativeCrisisDetector()
        scores = [0.60, 0.45, 0.30, 0.20]
        result = det.classify_trajectory(scores)
        assert result in (CrisisLevel.NONE, CrisisLevel.MASKED)

    def test_linear_slope_two_values_increasing(self):
        """_linear_slope([0.2, 0.4]) should return a positive value."""
        det = CumulativeCrisisDetector()
        slope = det._linear_slope([0.2, 0.4])
        assert slope > 0

    def test_linear_slope_two_values_flat(self):
        det = CumulativeCrisisDetector()
        slope = det._linear_slope([0.3, 0.3])
        assert slope == pytest.approx(0.0)

    def test_classify_turn_none_just_above_masked_arousal_ceiling(self):
        """arousal just above 0.25 and valence just above -0.3 with neutral text → NONE."""
        det = CumulativeCrisisDetector()
        f = _frame(0, valence=-0.25, arousal=0.30)
        assert det.classify_turn("nothing special happening", f) == CrisisLevel.NONE


# ── CrisisSynthesizer ─────────────────────────────────────────────────────────

class TestCrisisSynthesizer:

    # --- original tests (kept) ---

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

    # --- new edge-case tests ---

    def test_risk_score_increases_with_trips(self):
        synth = CrisisSynthesizer()
        low = _profile("s1", risk=0.0, trips=0)
        high = _profile("s2", risk=0.0, trips=5)
        assert synth.compute_session_risk_score(high) > synth.compute_session_risk_score(low)

    def test_risk_score_increases_with_vulnerability(self):
        synth = CrisisSynthesizer()
        low = _profile("s1", risk=0.0, vuln=0.1)
        high = _profile("s2", risk=0.0, vuln=0.9)
        assert synth.compute_session_risk_score(high) > synth.compute_session_risk_score(low)

    def test_risk_score_capped_at_one(self):
        synth = CrisisSynthesizer()
        extreme = _profile(
            "s1", risk=0.0, crisis=CrisisLevel.EXPLICIT, trips=100, events=100, vuln=1.0
        )
        assert synth.compute_session_risk_score(extreme) <= 1.0

    def test_synthesize_empty_profiles_returns_none(self):
        synth = CrisisSynthesizer()
        result = synth.synthesize("user1", "s1", [])
        assert result is None


# ── SafetyEngine ──────────────────────────────────────────────────────────────

class TestSafetyEngine:

    # --- original tests (kept) ---

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

    # --- new edge-case tests ---

    def test_process_turn_with_past_profiles_sets_crisis_signal(self):
        """Providing past_profiles with high risk should produce a crisis_signal."""
        engine = SafetyEngine(user_id="u1", session_id="ses_x")
        past = [_profile(f"s{i}", risk=0.50 + i * 0.12) for i in range(4)]
        result = engine.process_turn(
            _frame(0, mirroring=0.4, vulnerability=0.3),
            "feeling stressed",
            past_profiles=past,
        )
        # synthesize() decides whether to return a signal;
        # with this profile history it should be non-None.
        assert result["crisis_signal"] is not None

    def test_process_turn_no_past_profiles_crisis_signal_is_none(self):
        engine = SafetyEngine(user_id="u1", session_id="ses_y")
        result = engine.process_turn(_frame(0), "hello", past_profiles=None)
        assert result["crisis_signal"] is None

    def test_close_session_empty_frames_mean_vuln_is_zero(self):
        """close_session on an engine with no turns must not raise."""
        engine = SafetyEngine(user_id="u1", session_id="ses_empty")
        profile = engine.close_session()
        assert profile.mean_vulnerability_score == pytest.approx(0.0)

    def test_close_session_peak_crisis_level_explicit(self):
        """A frame with CrisisLevel.EXPLICIT must surface as peak."""
        engine = SafetyEngine(user_id="u1", session_id="ses_peak")
        frames = [
            _frame(0, crisis=CrisisLevel.NONE),
            _frame(1, crisis=CrisisLevel.ACUTE),
            _frame(2, crisis=CrisisLevel.EXPLICIT),
            _frame(3, crisis=CrisisLevel.GRADUAL),
        ]
        for f in frames:
            engine.process_turn(f, "text")
        profile = engine.close_session()
        assert profile.peak_crisis_level == CrisisLevel.EXPLICIT

    def test_close_session_peak_crisis_level_gradual_over_none(self):
        engine = SafetyEngine(user_id="u1", session_id="ses_grad")
        engine.process_turn(_frame(0, crisis=CrisisLevel.NONE), "text")
        engine.process_turn(_frame(1, crisis=CrisisLevel.GRADUAL), "text")
        profile = engine.close_session()
        assert profile.peak_crisis_level == CrisisLevel.GRADUAL

    def test_close_session_session_id_matches(self):
        engine = SafetyEngine(user_id="u42", session_id="session-abc")
        engine.process_turn(_frame(0), "hi")
        profile = engine.close_session()
        assert profile.session_id == "session-abc"
        assert profile.user_id == "u42"

    def test_close_session_mean_vulnerability_correct(self):
        engine = SafetyEngine(user_id="u1", session_id="ses_vuln")
        frames = [
            _frame(0, vulnerability=0.2),
            _frame(1, vulnerability=0.4),
            _frame(2, vulnerability=0.6),
        ]
        for f in frames:
            engine.process_turn(f, "text")
        profile = engine.close_session()
        assert profile.mean_vulnerability_score == pytest.approx(0.4, rel=1e-5)

    def test_escalation_events_count_matches_trips(self):
        engine = SafetyEngine(user_id="u1", session_id="ses_trips")
        for i in range(3):
            engine.process_turn(
                _frame(i, mirroring=0.82, vulnerability=0.75 + i * 0.01, delta=0.13),
                "text",
            )
        profile = engine.close_session()
        assert profile.escalation_events >= 1
        assert profile.circuit_breaker_trips == profile.escalation_events
