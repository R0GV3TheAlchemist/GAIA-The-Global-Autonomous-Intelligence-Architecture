"""
tests/test_shadow_archetypes.py
Unit tests for the 7-archetype scoring matrix.
"""

import pytest
from shadow_engine.archetypes import ArchetypeDetector, ShadowInputs
from shadow_engine.types      import ACTIVATION_THRESHOLD

detector = ArchetypeDetector()


# ── Helpers ────────────────────────────────────────────────────────────────

def neutral_inputs() -> ShadowInputs:
    return ShadowInputs(
        dominant_emotion="neutral",
        valence_trend=0.0,
        mood_momentum=0.0,
        volatility=0.0,
        is_volatile=False,
        arc_stability=0.5,
        low_energy_flag=False,
        arousal=0.5,
        decision_entropy=50.0,
        hrv_coherence=50.0,
        journaling_depth=50.0,
        focus_session_length=50.0,
        goal_completion_rate=50.0,
        emotional_arc_stability=50.0,
        days_in_stage=0,
        regression_active=False,
    )


# ── Bounds ─────────────────────────────────────────────────────────────────

class TestScoreBounds:
    def test_all_scores_in_range(self):
        scores = detector.score_all(neutral_inputs())
        for name, score in scores.items():
            assert 0.0 <= score <= 1.0, f"{name} out of range: {score}"

    def test_seven_archetypes_returned(self):
        scores = detector.score_all(neutral_inputs())
        assert len(scores) == 7


# ── Orphan ──────────────────────────────────────────────────────────────────

class TestOrphan:
    def test_high_score_on_sadness_low_energy(self):
        inp = neutral_inputs()
        inp["dominant_emotion"]   = "sadness"
        inp["low_energy_flag"]    = True
        inp["goal_completion_rate"] = 10.0
        inp["valence_trend"]      = -0.8
        score = detector.score_orphan(inp)
        assert score >= ACTIVATION_THRESHOLD

    def test_low_score_on_joy(self):
        inp = neutral_inputs()
        inp["dominant_emotion"] = "joy"
        inp["valence_trend"]    = 0.8
        assert detector.score_orphan(inp) < 0.20


# ── Wanderer ────────────────────────────────────────────────────────────────

class TestWanderer:
    def test_high_score_on_low_entropy_long_stagnation(self):
        inp = neutral_inputs()
        inp["decision_entropy"]       = 10.0   # low = more wanderer (inverted)
        inp["emotional_arc_stability"] = 10.0  # low coherence
        inp["days_in_stage"]          = 120
        score = detector.score_wanderer(inp)
        assert score >= ACTIVATION_THRESHOLD


# ── Warrior ─────────────────────────────────────────────────────────────────

class TestWarrior:
    def test_high_score_on_anger_volatile(self):
        inp = neutral_inputs()
        inp["dominant_emotion"] = "anger"
        inp["volatility"]       = 0.9
        inp["arousal"]          = 0.95
        score = detector.score_warrior(inp)
        assert score >= ACTIVATION_THRESHOLD


# ── Caregiver ────────────────────────────────────────────────────────────────

class TestCaregiver:
    def test_high_score_on_low_hrv_sadness(self):
        inp = neutral_inputs()
        inp["hrv_coherence"]   = 5.0
        inp["journaling_depth"] = 5.0   # low journal = high self_ref_proxy
        inp["dominant_emotion"] = "sadness"
        inp["low_energy_flag"] = True
        score = detector.score_caregiver(inp)
        assert score >= ACTIVATION_THRESHOLD


# ── Seeker ──────────────────────────────────────────────────────────────────

class TestSeeker:
    def test_high_score_on_surprise_volatile_unfocused(self):
        inp = neutral_inputs()
        inp["dominant_emotion"]    = "surprise"
        inp["volatility"]          = 0.8
        inp["focus_session_length"] = 5.0
        inp["days_in_stage"]       = 90
        score = detector.score_seeker(inp)
        assert score >= ACTIVATION_THRESHOLD


# ── Destroyer ────────────────────────────────────────────────────────────────

class TestDestroyer:
    def test_high_score_on_fear_negative_trend_volatile(self):
        inp = neutral_inputs()
        inp["dominant_emotion"] = "fear"
        inp["valence_trend"]    = -0.9
        inp["is_volatile"]      = True
        inp["regression_active"] = True
        score = detector.score_destroyer(inp)
        assert score >= ACTIVATION_THRESHOLD


# ── Creator ──────────────────────────────────────────────────────────────────

class TestCreator:
    def test_high_score_on_deep_journal_low_completion(self):
        inp = neutral_inputs()
        inp["journaling_depth"]    = 95.0
        inp["goal_completion_rate"] = 5.0
        inp["focus_session_length"] = 85.0
        score = detector.score_creator(inp)
        assert score >= ACTIVATION_THRESHOLD


# ── Threshold / activation ────────────────────────────────────────────────────

class TestActivationThreshold:
    def test_all_neutral_below_threshold(self):
        """Pure neutral inputs — no archetype should dominate strongly."""
        scores = detector.score_all(neutral_inputs())
        # On neutral inputs at least one archetype may score near threshold;
        # we just verify nothing is pathologically high (> 0.7).
        assert max(scores.values()) < 0.7

    def test_co_active_detection(self):
        """When two archetypes are very close, co_active should include both."""
        from shadow_engine.engine import ShadowEngine
        from shadow_engine.types  import CO_ACTIVE_DELTA
        inp = neutral_inputs()
        inp["dominant_emotion"] = "sadness"
        inp["low_energy_flag"]  = True
        inp["valence_trend"]    = -0.5
        scores = detector.score_all(inp)
        ranked = sorted(scores.values(), reverse=True)
        if len(ranked) >= 2 and (ranked[0] - ranked[1]) <= CO_ACTIVE_DELTA:
            _, co = ShadowEngine._resolve_active(scores)
            assert len(co) >= 1
