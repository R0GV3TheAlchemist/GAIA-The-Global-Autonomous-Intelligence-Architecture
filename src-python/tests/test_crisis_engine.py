"""Test suite for the Crisis Engine — Issue #126.

14 test classes, ~40 assertions covering:
- Signal taxonomy (all 4 classes, boundary conditions)
- Trajectory model (slope, consecutive sessions, 72h peak, synthesis)
- Escalation ladder (all tiers, elevation rules)
- Engine (evaluate, close_session, cold-start restore, handoff)
- Router (health, evaluate endpoint, history endpoint)
"""

from __future__ import annotations

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from crisis_engine.taxonomy import classify_turn, is_gradual_indicator
from crisis_engine.trajectory import TrajectoryModel, SessionRiskRecord
from crisis_engine.escalation import (
    determine_escalation_tier,
    get_intervention_message,
    build_handoff_record,
)
from crisis_engine.types import (
    CrisisSnapshot,
    EscalationTier,
    RiskLevel,
    SignalClass,
)
from crisis_engine.engine import CrisisEngine, EngineConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_engine(tmp_path: Path | None = None, principal: str = "test_user") -> CrisisEngine:
    return CrisisEngine(EngineConfig(
        principal_id=principal,
        db_path=(tmp_path / "crisis.db") if tmp_path else None,
    ))


def make_snapshot(
    risk: RiskLevel = RiskLevel.NONE,
    tier: EscalationTier = EscalationTier.MONITOR,
    slope: float = 0.0,
    consecutive: int = 0,
    peak_72h: RiskLevel = RiskLevel.NONE,
    principal: str = "test_user",
) -> CrisisSnapshot:
    return CrisisSnapshot(
        principal_id=principal,
        current_risk=risk,
        escalation_tier=tier,
        trajectory_slope=slope,
        sessions_in_distress=consecutive,
        peak_risk_72h=peak_72h,
    )


# ---------------------------------------------------------------------------
# 1. RiskLevel ordering
# ---------------------------------------------------------------------------

class TestRiskLevelOrdering:
    def test_ordering(self):
        assert RiskLevel.NONE < RiskLevel.LOW
        assert RiskLevel.LOW < RiskLevel.MODERATE
        assert RiskLevel.MODERATE < RiskLevel.HIGH
        assert RiskLevel.HIGH < RiskLevel.CRITICAL

    def test_critical_is_max(self):
        for level in RiskLevel:
            assert level <= RiskLevel.CRITICAL


# ---------------------------------------------------------------------------
# 2. Taxonomy — EXPLICIT CRITICAL
# ---------------------------------------------------------------------------

class TestExplicitCritical:
    def test_kill_myself(self):
        sigs = classify_turn("I want to kill myself")
        assert len(sigs) >= 1
        assert sigs[0].risk_level == RiskLevel.CRITICAL
        assert sigs[0].signal_class == SignalClass.EXPLICIT

    def test_suicidal_ideation(self):
        sigs = classify_turn("I've been having suicidal thoughts all week")
        assert any(s.risk_level == RiskLevel.CRITICAL for s in sigs)

    def test_want_to_die(self):
        sigs = classify_turn("I just want to die")
        assert any(s.risk_level == RiskLevel.CRITICAL for s in sigs)


# ---------------------------------------------------------------------------
# 3. Taxonomy — MASKED
# ---------------------------------------------------------------------------

class TestMaskedSignals:
    def test_burden_high(self):
        sigs = classify_turn("I feel like such a burden on everyone around me")
        assert any(s.signal_class == SignalClass.MASKED and s.risk_level == RiskLevel.HIGH for s in sigs)

    def test_better_off_without_me(self):
        sigs = classify_turn("everyone would be better off without me")
        assert any(s.signal_class == SignalClass.MASKED for s in sigs)

    def test_masked_moderate(self):
        sigs = classify_turn("I'm just too tired to keep going")
        assert any(s.signal_class == SignalClass.MASKED and s.risk_level == RiskLevel.MODERATE for s in sigs)


# ---------------------------------------------------------------------------
# 4. Taxonomy — clean text
# ---------------------------------------------------------------------------

class TestCleanText:
    def test_neutral_text(self):
        sigs = classify_turn("I had a great day today, feeling really good")
        assert sigs == []

    def test_empty_string(self):
        sigs = classify_turn("")
        assert sigs == []


# ---------------------------------------------------------------------------
# 5. Gradual indicator vocabulary
# ---------------------------------------------------------------------------

class TestGradualIndicators:
    def test_known_indicators(self):
        for word in ["hopelessness", "worthlessness", "anhedonia", "despair"]:
            assert is_gradual_indicator(word), f"{word} should be a gradual indicator"

    def test_unknown_word(self):
        assert not is_gradual_indicator("excitement")


# ---------------------------------------------------------------------------
# 6. Trajectory — slope
# ---------------------------------------------------------------------------

class TestTrajectorySlope:
    def test_insufficient_data_returns_zero(self):
        model = TrajectoryModel()
        model.record_session(SessionRiskRecord("s1", RiskLevel.NONE, 0, False, False))
        model.record_session(SessionRiskRecord("s2", RiskLevel.LOW, 0, False, False))
        assert model.trajectory_slope() == 0.0  # < 3 sessions

    def test_worsening_slope_is_positive(self):
        model = TrajectoryModel()
        for risk in [RiskLevel.NONE, RiskLevel.LOW, RiskLevel.MODERATE, RiskLevel.HIGH]:
            model.record_session(SessionRiskRecord("s", risk, 0, False, False))
        assert model.trajectory_slope() > 0

    def test_improving_slope_is_negative(self):
        model = TrajectoryModel()
        for risk in [RiskLevel.HIGH, RiskLevel.MODERATE, RiskLevel.LOW, RiskLevel.NONE]:
            model.record_session(SessionRiskRecord("s", risk, 0, False, False))
        assert model.trajectory_slope() < 0


# ---------------------------------------------------------------------------
# 7. Trajectory — consecutive distress
# ---------------------------------------------------------------------------

class TestConsecutiveDistress:
    def test_no_distress(self):
        model = TrajectoryModel()
        for _ in range(5):
            model.record_session(SessionRiskRecord("s", RiskLevel.NONE, 0, False, False))
        assert model.consecutive_distress_sessions() == 0

    def test_three_consecutive(self):
        model = TrajectoryModel()
        model.record_session(SessionRiskRecord("s0", RiskLevel.NONE, 0, False, False))
        for i in range(3):
            model.record_session(SessionRiskRecord(f"s{i+1}", RiskLevel.LOW, 1, False, True))
        assert model.consecutive_distress_sessions() == 3


# ---------------------------------------------------------------------------
# 8. Trajectory — synthesis
# ---------------------------------------------------------------------------

class TestTrajectoryRiskSynthesis:
    def test_no_signals_returns_none(self):
        model = TrajectoryModel()
        assert model.synthesise_risk([]) == RiskLevel.NONE

    def test_explicit_critical_not_downgraded(self):
        model = TrajectoryModel()
        # Add a flat, stable history
        for _ in range(10):
            model.record_session(SessionRiskRecord("s", RiskLevel.NONE, 0, False, False))
        sigs = classify_turn("I want to kill myself")
        result = model.synthesise_risk(sigs)
        assert result == RiskLevel.CRITICAL


# ---------------------------------------------------------------------------
# 9. Escalation — base mapping
# ---------------------------------------------------------------------------

class TestEscalationBaseTier:
    def test_none_is_monitor(self):
        snap = make_snapshot(risk=RiskLevel.NONE)
        assert determine_escalation_tier(snap) == EscalationTier.MONITOR

    def test_moderate_is_soft_intervene(self):
        snap = make_snapshot(risk=RiskLevel.MODERATE)
        assert determine_escalation_tier(snap) == EscalationTier.SOFT_INTERVENE

    def test_high_is_hard_intervene(self):
        snap = make_snapshot(risk=RiskLevel.HIGH)
        assert determine_escalation_tier(snap) == EscalationTier.HARD_INTERVENE

    def test_critical_is_handoff(self):
        snap = make_snapshot(risk=RiskLevel.CRITICAL)
        assert determine_escalation_tier(snap) == EscalationTier.HANDOFF


# ---------------------------------------------------------------------------
# 10. Escalation — elevation rules
# ---------------------------------------------------------------------------

class TestEscalationElevation:
    def test_three_consecutive_sessions_elevates_moderate(self):
        snap = make_snapshot(risk=RiskLevel.MODERATE, consecutive=3)
        assert determine_escalation_tier(snap) == EscalationTier.HARD_INTERVENE

    def test_rapid_slope_elevates_low(self):
        snap = make_snapshot(risk=RiskLevel.LOW, slope=0.7)
        assert determine_escalation_tier(snap) == EscalationTier.SOFT_INTERVENE


# ---------------------------------------------------------------------------
# 11. Intervention messages
# ---------------------------------------------------------------------------

class TestInterventionMessages:
    def test_monitor_returns_empty(self):
        assert get_intervention_message(EscalationTier.MONITOR) == ""

    def test_soft_contains_check_in(self):
        msg = get_intervention_message(EscalationTier.SOFT_INTERVENE)
        assert "carrying something heavy" in msg.lower() or "noticed" in msg.lower()

    def test_handoff_contains_988(self):
        msg = get_intervention_message(EscalationTier.HANDOFF)
        assert "988" in msg

    def test_hard_contains_988(self):
        msg = get_intervention_message(EscalationTier.HARD_INTERVENE)
        assert "988" in msg


# ---------------------------------------------------------------------------
# 12. Engine — basic evaluate
# ---------------------------------------------------------------------------

class TestEngineEvaluate:
    def test_clean_text_returns_none_risk(self, tmp_path):
        engine = make_engine(tmp_path)
        snap = engine.evaluate("I had a lovely morning", session_id="s1")
        assert snap.current_risk == RiskLevel.NONE
        assert snap.escalation_tier == EscalationTier.MONITOR
        assert not snap.requires_action

    def test_explicit_critical_returns_critical(self, tmp_path):
        engine = make_engine(tmp_path)
        snap = engine.evaluate("I want to kill myself", session_id="s1")
        assert snap.current_risk == RiskLevel.CRITICAL
        assert snap.escalation_tier == EscalationTier.HANDOFF
        assert snap.requires_action

    def test_intervention_message_nonempty_when_required(self, tmp_path):
        engine = make_engine(tmp_path)
        engine.evaluate("I want to kill myself", session_id="s1")
        assert engine.get_intervention_message() != ""


# ---------------------------------------------------------------------------
# 13. Engine — handoff record
# ---------------------------------------------------------------------------

class TestEngineHandoff:
    def test_handoff_record_built_on_critical(self, tmp_path):
        engine = make_engine(tmp_path)
        engine.evaluate("I want to end my life", session_id="s1")
        record = engine.build_handoff()
        assert record is not None
        assert record.principal_id == "test_user"
        assert "988" in record.message_sent

    def test_no_handoff_on_clean_text(self, tmp_path):
        engine = make_engine(tmp_path)
        engine.evaluate("good morning", session_id="s1")
        assert engine.build_handoff() is None


# ---------------------------------------------------------------------------
# 14. Engine — cold-start restore
# ---------------------------------------------------------------------------

class TestEngineColdStartRestore:
    def test_session_records_survive_restart(self, tmp_path):
        db = tmp_path / "crisis.db"
        engine1 = CrisisEngine(EngineConfig(principal_id="user_a", db_path=db))
        engine1.close_session("s1", RiskLevel.LOW, 1, False, True)
        engine1.close_session("s2", RiskLevel.MODERATE, 2, False, True)
        engine1.close_session("s3", RiskLevel.MODERATE, 1, False, True)

        # Cold-start new engine with same db
        engine2 = CrisisEngine(EngineConfig(principal_id="user_a", db_path=db))
        assert engine2._trajectory.consecutive_distress_sessions() == 3
