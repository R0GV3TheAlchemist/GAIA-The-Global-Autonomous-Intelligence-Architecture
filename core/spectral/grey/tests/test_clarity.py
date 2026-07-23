# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/grey/test_clarity.py
=========================================
All classify_grey_fire branches + edge cases.
Full coverage for all 5 GREY clarity functions.
"""

from core.spectral.grey.clarity import (
    assess_cauda_pavonis_level,
    classify_grey_fire,
    detect_permanent_threshold,
    distinguish_transition_stasis,
    map_mercury_threshold_archetype,
)


class TestDistinguishTransitionStasis:
    def test_both_thresholds_met_returns_transition(self):
        assert distinguish_transition_stasis({"directionality": 0.65, "momentum": 0.60}) == "transition"

    def test_exact_thresholds_returns_transition(self):
        assert distinguish_transition_stasis({"directionality": 0.55, "momentum": 0.50}) == "transition"

    def test_low_directionality_returns_stasis(self):
        assert distinguish_transition_stasis({"directionality": 0.30, "momentum": 0.70}) == "stasis"

    def test_low_momentum_returns_stasis(self):
        assert distinguish_transition_stasis({"directionality": 0.70, "momentum": 0.20}) == "stasis"

    def test_empty_returns_stasis(self):
        assert distinguish_transition_stasis({}) == "stasis"

    def test_none_returns_stasis(self):
        assert distinguish_transition_stasis(None) == "stasis"


class TestDetectPermanentThreshold:
    def test_all_conditions_met_returns_true(self):
        assert detect_permanent_threshold({"iridescence": 0.80, "directionality": 0.20, "momentum": 0.20}) is True

    def test_low_iridescence_returns_false(self):
        assert detect_permanent_threshold({"iridescence": 0.50, "directionality": 0.20, "momentum": 0.20}) is False

    def test_high_directionality_returns_false(self):
        assert detect_permanent_threshold({"iridescence": 0.80, "directionality": 0.60, "momentum": 0.20}) is False

    def test_high_momentum_returns_false(self):
        assert detect_permanent_threshold({"iridescence": 0.80, "directionality": 0.20, "momentum": 0.60}) is False

    def test_empty_returns_false(self):
        assert detect_permanent_threshold({}) is False

    def test_none_returns_false(self):
        assert detect_permanent_threshold(None) is False


class TestClassifyGreyFire:
    def test_cauda_pavonis_branch(self):
        assert classify_grey_fire({"cauda_pavonis": True}) == "cauda_pavonis"

    def test_permanent_threshold_branch(self):
        assert classify_grey_fire({"permanent_threshold": True}) == "permanent_threshold"

    def test_twilight_branch(self):
        assert classify_grey_fire({"twilight": True}) == "twilight"

    def test_liminal_branch(self):
        assert classify_grey_fire({"liminal": True}) == "liminal"

    def test_default_returns_dim_grey(self):
        assert classify_grey_fire({"other": True}) == "dim_grey"

    def test_empty_returns_dim_grey(self):
        assert classify_grey_fire({}) == "dim_grey"

    def test_none_returns_dim_grey(self):
        assert classify_grey_fire(None) == "dim_grey"

    def test_cauda_pavonis_priority_over_permanent_threshold(self):
        assert classify_grey_fire({"cauda_pavonis": True, "permanent_threshold": True}) == "cauda_pavonis"


class TestAssessCaudaPavonisLevel:
    def test_full_scores_return_one(self):
        signal = {"transition_momentum_score": 1.0, "iridescence_score": 1.0, "directionality_score": 1.0}
        assert abs(assess_cauda_pavonis_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        assert assess_cauda_pavonis_level({
            "transition_momentum_score": 0.0, "iridescence_score": 0.0, "directionality_score": 0.0
        }) == 0.0

    def test_weighted_calculation_correct(self):
        # t=0.5*0.40 + i=0.5*0.35 + d=0.5*0.25 = 0.50
        signal = {"transition_momentum_score": 0.5, "iridescence_score": 0.5, "directionality_score": 0.5}
        assert abs(assess_cauda_pavonis_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_cauda_pavonis_level({}) == 0.0

    def test_clamped_to_one(self):
        signal = {"transition_momentum_score": 2.0, "iridescence_score": 2.0, "directionality_score": 2.0}
        assert assess_cauda_pavonis_level(signal) <= 1.0


class TestMapMercuryThresholdArchetype:
    def test_cauda_pavonis_archetype(self):
        assert "Cauda Pavonis" in map_mercury_threshold_archetype("cauda_pavonis")

    def test_permanent_threshold_archetype(self):
        assert "Permanent Threshold" in map_mercury_threshold_archetype("permanent_threshold")

    def test_twilight_archetype(self):
        assert "Twilight" in map_mercury_threshold_archetype("twilight")

    def test_liminal_archetype(self):
        assert "Liminal" in map_mercury_threshold_archetype("liminal")

    def test_unknown_returns_dim_grey(self):
        assert "Dim Grey" in map_mercury_threshold_archetype("not_real")

    def test_none_returns_dim_grey(self):
        assert "Dim Grey" in map_mercury_threshold_archetype(None)
