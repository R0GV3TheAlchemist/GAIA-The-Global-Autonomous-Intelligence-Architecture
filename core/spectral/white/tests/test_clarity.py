# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/white/test_clarity.py
==========================================
All classify_white_fire branches + edge cases.
Full coverage for all 5 WHITE clarity functions.
"""

from core.spectral.white.clarity import (
    assess_albedo_level,
    classify_white_fire,
    detect_bleaching_state,
    distinguish_purification_erasure,
    map_lunar_archetype,
)


class TestDistinguishPurificationErasure:
    def test_both_thresholds_met_returns_purification(self):
        assert distinguish_purification_erasure({"texture": 0.60, "contrast": 0.50}) == "purification"

    def test_exact_thresholds_returns_purification(self):
        assert distinguish_purification_erasure({"texture": 0.50, "contrast": 0.40}) == "purification"

    def test_low_texture_returns_erasure(self):
        assert distinguish_purification_erasure({"texture": 0.30, "contrast": 0.60}) == "erasure"

    def test_low_contrast_returns_erasure(self):
        assert distinguish_purification_erasure({"texture": 0.70, "contrast": 0.20}) == "erasure"

    def test_empty_returns_erasure(self):
        assert distinguish_purification_erasure({}) == "erasure"

    def test_none_returns_erasure(self):
        assert distinguish_purification_erasure(None) == "erasure"


class TestDetectBleachingState:
    def test_all_conditions_met_returns_true(self):
        assert detect_bleaching_state({"purification": 0.95, "texture": 0.10, "contrast": 0.10}) is True

    def test_exact_thresholds_returns_true(self):
        assert detect_bleaching_state({"purification": 0.90, "texture": 0.29, "contrast": 0.24}) is True

    def test_low_purification_returns_false(self):
        assert detect_bleaching_state({"purification": 0.70, "texture": 0.10, "contrast": 0.10}) is False

    def test_high_texture_returns_false(self):
        assert detect_bleaching_state({"purification": 0.95, "texture": 0.60, "contrast": 0.10}) is False

    def test_high_contrast_returns_false(self):
        assert detect_bleaching_state({"purification": 0.95, "texture": 0.10, "contrast": 0.60}) is False

    def test_empty_returns_false(self):
        assert detect_bleaching_state({}) is False

    def test_none_returns_false(self):
        assert detect_bleaching_state(None) is False


class TestClassifyWhiteFire:
    def test_albedo_branch(self):
        assert classify_white_fire({"albedo": True}) == "albedo"

    def test_bleaching_branch(self):
        assert classify_white_fire({"bleaching": True}) == "bleaching"

    def test_overexposed_branch(self):
        assert classify_white_fire({"overexposed": True}) == "overexposed"

    def test_pale_branch(self):
        assert classify_white_fire({"pale": True}) == "pale"

    def test_default_returns_dim_white(self):
        assert classify_white_fire({"other": True}) == "dim_white"

    def test_empty_returns_dim_white(self):
        assert classify_white_fire({}) == "dim_white"

    def test_none_returns_dim_white(self):
        assert classify_white_fire(None) == "dim_white"

    def test_albedo_priority_over_bleaching(self):
        assert classify_white_fire({"albedo": True, "bleaching": True}) == "albedo"


class TestAssessAlbedoLevel:
    def test_full_scores_return_one(self):
        signal = {"purification_score": 1.0, "reflection_score": 1.0, "texture_score": 1.0}
        assert abs(assess_albedo_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        assert assess_albedo_level({"purification_score": 0.0, "reflection_score": 0.0, "texture_score": 0.0}) == 0.0

    def test_weighted_calculation_correct(self):
        # p=0.5*0.40 + r=0.5*0.35 + t=0.5*0.25 = 0.50
        signal = {"purification_score": 0.5, "reflection_score": 0.5, "texture_score": 0.5}
        assert abs(assess_albedo_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_albedo_level({}) == 0.0

    def test_clamped_to_one(self):
        signal = {"purification_score": 2.0, "reflection_score": 2.0, "texture_score": 2.0}
        assert assess_albedo_level(signal) <= 1.0


class TestMapLunarArchetype:
    def test_albedo_archetype(self):
        assert "Albedo" in map_lunar_archetype("albedo")

    def test_bleaching_archetype(self):
        assert "Bleaching" in map_lunar_archetype("bleaching")

    def test_overexposed_archetype(self):
        assert "Overexposed" in map_lunar_archetype("overexposed")

    def test_pale_archetype(self):
        assert "Pale" in map_lunar_archetype("pale")

    def test_unknown_returns_dim_white(self):
        assert "Dim White" in map_lunar_archetype("not_real")

    def test_none_returns_dim_white(self):
        assert "Dim White" in map_lunar_archetype(None)
