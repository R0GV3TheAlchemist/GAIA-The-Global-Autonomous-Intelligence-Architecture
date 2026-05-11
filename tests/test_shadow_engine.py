"""
tests/test_shadow_engine.py
Integration tests for ShadowEngine using mocked stream inputs.
"""

import asyncio
import pytest
from shadow_engine.engine import ShadowEngine
from shadow_engine.types  import ACTIVATION_THRESHOLD, ShadowRecord
from shadow_engine.archetypes import ShadowInputs


def run(coro):
    # asyncio.run() creates a fresh event loop each call — safe on Python 3.10+
    # where get_event_loop() no longer auto-creates a loop outside the main thread.
    return asyncio.run(coro)


def sadness_inputs() -> ShadowInputs:
    return ShadowInputs(
        dominant_emotion="sadness",
        valence_trend=-0.7,
        mood_momentum=-0.3,
        volatility=0.1,
        is_volatile=False,
        arc_stability=0.3,
        low_energy_flag=True,
        arousal=0.2,
        decision_entropy=50.0,
        hrv_coherence=20.0,
        journaling_depth=30.0,
        focus_session_length=30.0,
        goal_completion_rate=15.0,
        emotional_arc_stability=25.0,
        days_in_stage=10,
        regression_active=False,
    )


def anger_inputs() -> ShadowInputs:
    return ShadowInputs(
        dominant_emotion="anger",
        valence_trend=-0.5,
        mood_momentum=-0.4,
        volatility=0.85,
        is_volatile=True,
        arc_stability=0.2,
        low_energy_flag=False,
        arousal=0.9,
        decision_entropy=60.0,
        hrv_coherence=30.0,
        journaling_depth=40.0,
        focus_session_length=50.0,
        goal_completion_rate=50.0,
        emotional_arc_stability=20.0,
        days_in_stage=5,
        regression_active=False,
    )


class TestEvaluateWithMockedInputs:
    def test_returns_shadow_record(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-1", override_inputs=sadness_inputs()))
        assert isinstance(record, ShadowRecord)

    def test_orphan_activates_on_sadness(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-1", override_inputs=sadness_inputs()))
        assert record.active_archetype == "Orphan"
        assert record.shadow_intensity > 0.0

    def test_warrior_activates_on_anger(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-2", override_inputs=anger_inputs()))
        assert record.active_archetype == "Warrior"

    def test_all_scores_bounded(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-3", override_inputs=sadness_inputs()))
        for score in record.archetype_scores.values():
            assert 0.0 <= score <= 1.0

    def test_intensity_bounded(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-4", override_inputs=anger_inputs()))
        assert 0.0 <= record.shadow_intensity <= 1.0

    def test_integration_starts_at_zero(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-5", override_inputs=sadness_inputs()))
        assert record.integration_progress == 0.0

    def test_days_active_zero_on_first_eval(self):
        engine = ShadowEngine()
        record = run(engine.evaluate("user-6", override_inputs=sadness_inputs()))
        assert record.days_active == 0


class TestNoneActivation:
    def test_no_archetype_when_all_scores_low(self):
        """Heavily positive, coherent, high-completion inputs should stay below threshold."""
        inp = ShadowInputs(
            dominant_emotion="joy",
            valence_trend=0.9,
            mood_momentum=0.7,
            volatility=0.0,
            is_volatile=False,
            arc_stability=0.95,
            low_energy_flag=False,
            arousal=0.6,
            decision_entropy=90.0,
            hrv_coherence=90.0,
            journaling_depth=80.0,
            focus_session_length=85.0,
            goal_completion_rate=90.0,
            emotional_arc_stability=92.0,
            days_in_stage=3,
            regression_active=False,
        )
        engine = ShadowEngine()
        record = run(engine.evaluate("user-joy", override_inputs=inp))
        # On high-coherence joy inputs, no shadow should be strongly active
        assert record.active_archetype is None or record.shadow_intensity < 0.6


class TestReflectionSession:
    def test_reflection_increases_integration(self):
        engine = ShadowEngine()
        run(engine.evaluate("user-r", override_inputs=sadness_inputs()))
        gain = engine.record_reflection_session("user-r")
        assert gain > 0.0
        record = run(engine.get_current("user-r"))
        assert record.integration_progress > 0.0


class TestGetCurrent:
    def test_returns_none_before_evaluation(self):
        engine = ShadowEngine()
        result = run(engine.get_current("unknown-user"))
        assert result is None

    def test_returns_record_after_evaluation(self):
        engine = ShadowEngine()
        run(engine.evaluate("user-cache", override_inputs=sadness_inputs()))
        record = run(engine.get_current("user-cache"))
        assert record is not None
        assert record.principal_id == "user-cache"
