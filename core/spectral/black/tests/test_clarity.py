# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/black/test_clarity.py
==========================================
All classify_black_fire branches + edge cases.
Full coverage for all 5 BLACK clarity functions.
"""

from core.spectral.black.clarity import (
    assess_nigredo_level,
    classify_black_fire,
    detect_prima_materia_state,
    distinguish_dissolution_destruction,
    map_saturn_archetype,
)


class TestDistinguishDissolutionDestruction:
    def test_both_thresholds_met_returns_dissolution(self):
        assert distinguish_dissolution_destruction({"reformation_potential": 0.60, "containment": 0.55}) == "dissolution"

    def test_exact_thresholds_returns_dissolution(self):
        assert distinguish_dissolution_destruction({"reformation_potential": 0.50, "containment": 0.45}) == "dissolution"

    def test_low_reformation_returns_destruction(self):
        assert distinguish_dissolution_destruction({"reformation_potential": 0.30, "containment": 0.70}) == "destruction"

    def test_low_containment_returns_destruction(self):
        assert distinguish_dissolution_destruction({"reformation_potential": 0.70, "containment": 0.20}) == "destruction"

    def test_empty_returns_destruction(self):
        assert distinguish_dissolution_destruction({}) == "destruction"

    def test_none_returns_destruction(self):
        assert distinguish_dissolution_destruction(None) == "destruction"


class TestDetectPrimaMateriaState:
    def test_all_conditions_met_returns_true(self):
        assert detect_prima_materia_state({"formlessness": 0.80, "potential": 0.70, "reformation_potential": 0.60}) is True

    def test_low_formlessness_returns_false(self):
        assert detect_prima_materia_state({"formlessness": 0.50, "potential": 0.70, "reformation_potential": 0.60}) is False

    def test_low_potential_returns_false(self):
        assert detect_prima_materia_state({"formlessness": 0.80, "potential": 0.40, "reformation_potential": 0.60}) is False

    def test_low_reformation_returns_false(self):
        assert detect_prima_materia_state({"formlessness": 0.80, "potential": 0.70, "reformation_potential": 0.30}) is False

    def test_empty_returns_false(self):
        assert detect_prima_materia_state({}) is False

    def test_none_returns_false(self):
        assert detect_prima_materia_state(None) is False


class TestClassifyBlackFire:
    def test_nigredo_branch(self):
        assert classify_black_fire({"nigredo": True}) == "nigredo"

    def test_prima_materia_branch(self):
        assert classify_black_fire({"prima_materia": True}) == "prima_materia"

    def test_system_null_branch(self):
        assert classify_black_fire({"system_null": True}) == "system_null"

    def test_destruction_branch(self):
        assert classify_black_fire({"destruction": True}) == "destruction"

    def test_default_returns_dim_black(self):
        assert classify_black_fire({"other": True}) == "dim_black"

    def test_empty_returns_dim_black(self):
        assert classify_black_fire({}) == "dim_black"

    def test_none_returns_dim_black(self):
        assert classify_black_fire(None) == "dim_black"

    def test_nigredo_priority_over_prima_materia(self):
        assert classify_black_fire({"nigredo": True, "prima_materia": True}) == "nigredo"


class TestAssessNigredoLevel:
    def test_full_scores_return_one(self):
        signal = {"dissolution_score": 1.0, "void_contact_score": 1.0, "containment_score": 1.0}
        assert abs(assess_nigredo_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        assert assess_nigredo_level({"dissolution_score": 0.0, "void_contact_score": 0.0, "containment_score": 0.0}) == 0.0

    def test_weighted_calculation_correct(self):
        # d=0.5*0.40 + v=0.5*0.35 + c=0.5*0.25 = 0.50
        signal = {"dissolution_score": 0.5, "void_contact_score": 0.5, "containment_score": 0.5}
        assert abs(assess_nigredo_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_nigredo_level({}) == 0.0

    def test_clamped_to_one(self):
        signal = {"dissolution_score": 2.0, "void_contact_score": 2.0, "containment_score": 2.0}
        assert assess_nigredo_level(signal) <= 1.0


class TestMapSaturnArchetype:
    def test_nigredo_archetype(self):
        assert "Nigredo" in map_saturn_archetype("nigredo")

    def test_prima_materia_archetype(self):
        assert "Prima Materia" in map_saturn_archetype("prima_materia")

    def test_system_null_archetype(self):
        assert "System Null" in map_saturn_archetype("system_null")

    def test_destruction_archetype(self):
        assert "Destruction" in map_saturn_archetype("destruction")

    def test_unknown_returns_dim_black(self):
        assert "Dim Black" in map_saturn_archetype("not_real")

    def test_none_returns_dim_black(self):
        assert "Dim Black" in map_saturn_archetype(None)
