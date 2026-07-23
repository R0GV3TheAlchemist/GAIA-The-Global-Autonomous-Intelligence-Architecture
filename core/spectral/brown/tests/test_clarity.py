# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/brown/test_clarity.py
==========================================
All classify_brown_fire branches + edge cases.
Full coverage for all 5 BROWN clarity functions.
"""

from core.spectral.brown.clarity import (
    assess_humus_level,
    classify_brown_fire,
    detect_compaction_state,
    distinguish_fertility_inertia,
    map_earth_archetype,
)


class TestDistinguishFertilityInertia:
    def test_both_thresholds_met_returns_fertility(self):
        assert distinguish_fertility_inertia({"porosity": 0.65, "decomposition_rate": 0.55}) == "fertility"

    def test_exact_thresholds_returns_fertility(self):
        assert distinguish_fertility_inertia({"porosity": 0.55, "decomposition_rate": 0.45}) == "fertility"

    def test_low_porosity_returns_inertia(self):
        assert distinguish_fertility_inertia({"porosity": 0.30, "decomposition_rate": 0.60}) == "inertia"

    def test_low_decomposition_rate_returns_inertia(self):
        assert distinguish_fertility_inertia({"porosity": 0.70, "decomposition_rate": 0.20}) == "inertia"

    def test_empty_returns_inertia(self):
        assert distinguish_fertility_inertia({}) == "inertia"

    def test_none_returns_inertia(self):
        assert distinguish_fertility_inertia(None) == "inertia"


class TestDetectCompactionState:
    def test_all_conditions_met_returns_true(self):
        assert detect_compaction_state({
            "groundedness": 0.90, "porosity": 0.10, "decomposition_rate": 0.10
        }) is True

    def test_low_groundedness_returns_false(self):
        assert detect_compaction_state({
            "groundedness": 0.60, "porosity": 0.10, "decomposition_rate": 0.10
        }) is False

    def test_high_porosity_returns_false(self):
        assert detect_compaction_state({
            "groundedness": 0.90, "porosity": 0.60, "decomposition_rate": 0.10
        }) is False

    def test_high_decomposition_rate_returns_false(self):
        assert detect_compaction_state({
            "groundedness": 0.90, "porosity": 0.10, "decomposition_rate": 0.60
        }) is False

    def test_empty_returns_false(self):
        assert detect_compaction_state({}) is False

    def test_none_returns_false(self):
        assert detect_compaction_state(None) is False


class TestClassifyBrownFire:
    def test_humus_branch(self):
        assert classify_brown_fire({"humus": True}) == "humus"

    def test_compaction_branch(self):
        assert classify_brown_fire({"compaction": True}) == "compaction"

    def test_sediment_branch(self):
        assert classify_brown_fire({"sediment": True}) == "sediment"

    def test_clay_branch(self):
        assert classify_brown_fire({"clay": True}) == "clay"

    def test_default_returns_dim_brown(self):
        assert classify_brown_fire({"other": True}) == "dim_brown"

    def test_empty_returns_dim_brown(self):
        assert classify_brown_fire({}) == "dim_brown"

    def test_none_returns_dim_brown(self):
        assert classify_brown_fire(None) == "dim_brown"

    def test_humus_priority_over_compaction(self):
        assert classify_brown_fire({"humus": True, "compaction": True}) == "humus"


class TestAssessHumusLevel:
    def test_full_scores_return_one(self):
        signal = {"fertility_score": 1.0, "groundedness_score": 1.0, "porosity_score": 1.0}
        assert abs(assess_humus_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        assert assess_humus_level({
            "fertility_score": 0.0, "groundedness_score": 0.0, "porosity_score": 0.0
        }) == 0.0

    def test_weighted_calculation_correct(self):
        # f=0.5*0.40 + g=0.5*0.35 + p=0.5*0.25 = 0.50
        signal = {"fertility_score": 0.5, "groundedness_score": 0.5, "porosity_score": 0.5}
        assert abs(assess_humus_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_humus_level({}) == 0.0

    def test_clamped_to_one(self):
        signal = {"fertility_score": 2.0, "groundedness_score": 2.0, "porosity_score": 2.0}
        assert assess_humus_level(signal) <= 1.0


class TestMapEarthArchetype:
    def test_humus_archetype(self):
        assert "Humus" in map_earth_archetype("humus")

    def test_compaction_archetype(self):
        assert "Compaction" in map_earth_archetype("compaction")

    def test_sediment_archetype(self):
        assert "Sediment" in map_earth_archetype("sediment")

    def test_clay_archetype(self):
        assert "Clay" in map_earth_archetype("clay")

    def test_unknown_returns_dim_brown(self):
        assert "Dim Brown" in map_earth_archetype("not_real")

    def test_none_returns_dim_brown(self):
        assert "Dim Brown" in map_earth_archetype(None)
