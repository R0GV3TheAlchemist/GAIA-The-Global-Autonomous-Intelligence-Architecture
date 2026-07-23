# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/pink/test_clarity.py
=========================================
All classify_pink_fire branches + edge cases.
Full coverage for all 5 PINK clarity functions.
"""

from core.spectral.pink.clarity import (
    assess_rose_level,
    classify_pink_fire,
    detect_false_albedo_state,
    distinguish_tenderness_sentimentality,
    map_rosa_archetype,
)


# ---------------------------------------------------------------------------
# distinguish_tenderness_sentimentality
# ---------------------------------------------------------------------------

class TestDistinguishTendernessSentimentality:
    def test_both_thresholds_met_returns_tenderness(self):
        signal = {"grief_capacity": 0.70, "complexity_tolerance": 0.60}
        assert distinguish_tenderness_sentimentality(signal) == "tenderness"

    def test_exact_thresholds_returns_tenderness(self):
        signal = {"grief_capacity": 0.60, "complexity_tolerance": 0.55}
        assert distinguish_tenderness_sentimentality(signal) == "tenderness"

    def test_low_grief_capacity_returns_sentimentality(self):
        signal = {"grief_capacity": 0.40, "complexity_tolerance": 0.70}
        assert distinguish_tenderness_sentimentality(signal) == "sentimentality"

    def test_low_complexity_tolerance_returns_sentimentality(self):
        signal = {"grief_capacity": 0.70, "complexity_tolerance": 0.40}
        assert distinguish_tenderness_sentimentality(signal) == "sentimentality"

    def test_empty_returns_sentimentality(self):
        assert distinguish_tenderness_sentimentality({}) == "sentimentality"

    def test_none_returns_sentimentality(self):
        assert distinguish_tenderness_sentimentality(None) == "sentimentality"


# ---------------------------------------------------------------------------
# detect_false_albedo_state
# ---------------------------------------------------------------------------

class TestDetectFalseAlbedoState:
    def test_all_conditions_met_returns_true(self):
        signal = {
            "softness": 0.80,
            "grief_integration": 0.30,
            "shadow_acknowledgment": 0.30,
        }
        assert detect_false_albedo_state(signal) is True

    def test_low_softness_returns_false(self):
        signal = {
            "softness": 0.50,
            "grief_integration": 0.30,
            "shadow_acknowledgment": 0.30,
        }
        assert detect_false_albedo_state(signal) is False

    def test_high_grief_integration_returns_false(self):
        signal = {
            "softness": 0.80,
            "grief_integration": 0.70,
            "shadow_acknowledgment": 0.30,
        }
        assert detect_false_albedo_state(signal) is False

    def test_high_shadow_acknowledgment_returns_false(self):
        signal = {
            "softness": 0.80,
            "grief_integration": 0.30,
            "shadow_acknowledgment": 0.60,
        }
        assert detect_false_albedo_state(signal) is False

    def test_empty_returns_false(self):
        assert detect_false_albedo_state({}) is False

    def test_none_returns_false(self):
        assert detect_false_albedo_state(None) is False


# ---------------------------------------------------------------------------
# classify_pink_fire — all branches
# ---------------------------------------------------------------------------

class TestClassifyPinkFire:
    def test_rosa_mystica_branch(self):
        assert classify_pink_fire({"rosa_mystica": True}) == "rosa_mystica"

    def test_false_albedo_branch(self):
        assert classify_pink_fire({"false_albedo": True}) == "false_albedo"

    def test_rose_denial_branch(self):
        assert classify_pink_fire({"rose_denial": True}) == "rose_denial"

    def test_premature_tenderness_branch(self):
        assert classify_pink_fire({"premature_tenderness": True}) == "premature_tenderness"

    def test_default_returns_dim_rose(self):
        assert classify_pink_fire({"other": True}) == "dim_rose"

    def test_empty_returns_dim_rose(self):
        assert classify_pink_fire({}) == "dim_rose"

    def test_none_returns_dim_rose(self):
        assert classify_pink_fire(None) == "dim_rose"

    def test_rosa_mystica_priority_over_false_albedo(self):
        # rosa_mystica has first-priority
        signal = {"rosa_mystica": True, "false_albedo": True}
        assert classify_pink_fire(signal) == "rosa_mystica"


# ---------------------------------------------------------------------------
# assess_rose_level
# ---------------------------------------------------------------------------

class TestAssessRoseLevel:
    def test_full_scores_return_near_one(self):
        signal = {
            "tenderness_score": 1.0,
            "groundedness_score": 1.0,
            "openness_score": 1.0,
        }
        assert abs(assess_rose_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        signal = {
            "tenderness_score": 0.0,
            "groundedness_score": 0.0,
            "openness_score": 0.0,
        }
        assert assess_rose_level(signal) == 0.0

    def test_weighted_calculation_correct(self):
        # t=0.5*0.40 + g=0.5*0.35 + o=0.5*0.25 = 0.20+0.175+0.125 = 0.50
        signal = {
            "tenderness_score": 0.5,
            "groundedness_score": 0.5,
            "openness_score": 0.5,
        }
        assert abs(assess_rose_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_rose_level({}) == 0.0

    def test_none_returns_zero(self):
        assert assess_rose_level(None) == 0.0

    def test_result_clamped_to_one(self):
        signal = {
            "tenderness_score": 2.0,
            "groundedness_score": 2.0,
            "openness_score": 2.0,
        }
        assert assess_rose_level(signal) <= 1.0


# ---------------------------------------------------------------------------
# map_rosa_archetype
# ---------------------------------------------------------------------------

class TestMapRosaArchetype:
    def test_rosa_mystica_archetype(self):
        result = map_rosa_archetype("rosa_mystica")
        assert "Rosa Mystica" in result

    def test_false_albedo_archetype(self):
        result = map_rosa_archetype("false_albedo")
        assert "False Albedo" in result

    def test_rose_denial_archetype(self):
        result = map_rosa_archetype("rose_denial")
        assert "Rose Denial" in result

    def test_premature_tenderness_archetype(self):
        result = map_rosa_archetype("premature_tenderness")
        assert "Premature" in result

    def test_unknown_returns_dim_rose(self):
        result = map_rosa_archetype("not_a_real_type")
        assert "Dim Rose" in result

    def test_none_returns_dim_rose(self):
        result = map_rosa_archetype(None)
        assert "Dim Rose" in result
