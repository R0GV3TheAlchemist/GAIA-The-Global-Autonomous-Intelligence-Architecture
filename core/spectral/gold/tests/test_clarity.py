# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/gold/test_clarity.py
=========================================
All classify_gold_fire branches + edge cases.
Full coverage for all 5 GOLD clarity functions.
"""

from core.spectral.gold.clarity import (
    assess_aurum_level,
    classify_gold_fire,
    detect_canon_calcification,
    distinguish_completion_ossification,
    map_solar_archetype,
)


class TestDistinguishCompletionOssification:
    def test_both_thresholds_met_returns_completion(self):
        assert distinguish_completion_ossification({"vitality": 0.70, "receptivity": 0.60}) == "completion"

    def test_exact_thresholds_returns_completion(self):
        assert distinguish_completion_ossification({"vitality": 0.60, "receptivity": 0.50}) == "completion"

    def test_low_vitality_returns_ossification(self):
        assert distinguish_completion_ossification({"vitality": 0.40, "receptivity": 0.70}) == "ossification"

    def test_low_receptivity_returns_ossification(self):
        assert distinguish_completion_ossification({"vitality": 0.70, "receptivity": 0.30}) == "ossification"

    def test_empty_returns_ossification(self):
        assert distinguish_completion_ossification({}) == "ossification"

    def test_none_returns_ossification(self):
        assert distinguish_completion_ossification(None) == "ossification"


class TestDetectCanonCalcification:
    def test_all_conditions_met_returns_true(self):
        assert detect_canon_calcification({"completion": 0.90, "vitality": 0.20, "receptivity": 0.20}) is True

    def test_low_completion_returns_false(self):
        assert detect_canon_calcification({"completion": 0.60, "vitality": 0.20, "receptivity": 0.20}) is False

    def test_high_vitality_returns_false(self):
        assert detect_canon_calcification({"completion": 0.90, "vitality": 0.60, "receptivity": 0.20}) is False

    def test_high_receptivity_returns_false(self):
        assert detect_canon_calcification({"completion": 0.90, "vitality": 0.20, "receptivity": 0.60}) is False

    def test_empty_returns_false(self):
        assert detect_canon_calcification({}) is False

    def test_none_returns_false(self):
        assert detect_canon_calcification(None) is False


class TestClassifyGoldFire:
    def test_aurum_branch(self):
        assert classify_gold_fire({"aurum": True}) == "aurum"

    def test_ossification_branch(self):
        assert classify_gold_fire({"ossification": True}) == "ossification"

    def test_false_completion_branch(self):
        assert classify_gold_fire({"false_completion": True}) == "false_completion"

    def test_monument_branch(self):
        assert classify_gold_fire({"monument": True}) == "monument"

    def test_default_returns_dim_gold(self):
        assert classify_gold_fire({"other": True}) == "dim_gold"

    def test_empty_returns_dim_gold(self):
        assert classify_gold_fire({}) == "dim_gold"

    def test_none_returns_dim_gold(self):
        assert classify_gold_fire(None) == "dim_gold"

    def test_aurum_priority_over_ossification(self):
        assert classify_gold_fire({"aurum": True, "ossification": True}) == "aurum"


class TestAssessAurumLevel:
    def test_full_scores_return_one(self):
        signal = {"completion_score": 1.0, "vitality_score": 1.0, "receptivity_score": 1.0}
        assert abs(assess_aurum_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        signal = {"completion_score": 0.0, "vitality_score": 0.0, "receptivity_score": 0.0}
        assert assess_aurum_level(signal) == 0.0

    def test_weighted_calculation_correct(self):
        # c=0.5*0.40 + v=0.5*0.35 + r=0.5*0.25 = 0.20+0.175+0.125 = 0.50
        signal = {"completion_score": 0.5, "vitality_score": 0.5, "receptivity_score": 0.5}
        assert abs(assess_aurum_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_aurum_level({}) == 0.0

    def test_clamped_to_one(self):
        signal = {"completion_score": 2.0, "vitality_score": 2.0, "receptivity_score": 2.0}
        assert assess_aurum_level(signal) <= 1.0


class TestMapSolarArchetype:
    def test_aurum_archetype(self):
        assert "Aurum" in map_solar_archetype("aurum")

    def test_ossification_archetype(self):
        assert "Ossification" in map_solar_archetype("ossification")

    def test_false_completion_archetype(self):
        assert "False Completion" in map_solar_archetype("false_completion")

    def test_monument_archetype(self):
        assert "Monument" in map_solar_archetype("monument")

    def test_unknown_returns_dim_gold(self):
        assert "Dim Gold" in map_solar_archetype("not_real")

    def test_none_returns_dim_gold(self):
        assert "Dim Gold" in map_solar_archetype(None)
