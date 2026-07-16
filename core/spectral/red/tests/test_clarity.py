# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
Tests for core/spectral/red/clarity.py
"""

from __future__ import annotations

from core.spectral.red.clarity import (
    assess_integration_level,
    classify_red_fire,
    detect_sacred_wound,
    distinguish_anger_passion,
    map_warrior_archetype,
)


# ---------------------------------------------------------------------------
# distinguish_anger_passion
# ---------------------------------------------------------------------------

class TestDistinguishAngerPassion:
    def test_pure_passion_features(self):
        assert distinguish_anger_passion(
            {"features": ["life_force", "vitality", "joy_adjacent"]}
        ) == "passion"

    def test_pure_anger_features(self):
        assert distinguish_anger_passion(
            {"features": ["reactivity", "defensiveness", "blame_projection"]}
        ) == "anger"

    def test_tie_defaults_to_anger(self):
        assert distinguish_anger_passion(
            {"features": ["life_force", "reactivity"]}
        ) == "anger"

    def test_empty_features(self):
        assert distinguish_anger_passion({"features": []}) == "anger"

    def test_empty_signal(self):
        assert distinguish_anger_passion({}) == "anger"

    def test_none_signal(self):
        assert distinguish_anger_passion(None) == "anger"


# ---------------------------------------------------------------------------
# detect_sacred_wound
# ---------------------------------------------------------------------------

class TestDetectSacredWound:
    def test_wound_resonance_flag(self):
        result = detect_sacred_wound({"wound_resonance": True})
        assert result["wound_present"] is True
        assert result["stage"] == "metabolizing"

    def test_historical_trigger_flag(self):
        result = detect_sacred_wound({"historical_trigger": True})
        assert result["wound_present"] is True

    def test_no_wound(self):
        result = detect_sacred_wound({"some_key": "value"})
        assert result["wound_present"] is False
        assert result["stage"] == "unacknowledged"

    def test_explicit_stage_respected(self):
        result = detect_sacred_wound(
            {"wound_resonance": True, "wound_stage": "integrated"}
        )
        assert result["stage"] == "integrated"

    def test_invalid_stage_overridden(self):
        result = detect_sacred_wound(
            {"wound_resonance": True, "wound_stage": "not_a_real_stage"}
        )
        assert result["stage"] == "metabolizing"

    def test_estimated_origin_passed_through(self):
        result = detect_sacred_wound(
            {"wound_resonance": True, "estimated_origin": "childhood"}
        )
        assert result["estimated_origin"] == "childhood"

    def test_empty_signal(self):
        result = detect_sacred_wound({})
        assert result["wound_present"] is False

    def test_none_signal(self):
        result = detect_sacred_wound(None)
        assert result["wound_present"] is False


# ---------------------------------------------------------------------------
# classify_red_fire
# ---------------------------------------------------------------------------

class TestClassifyRedFire:
    def test_reactive_override(self):
        assert classify_red_fire({"reactive": True}) == "reactive"

    def test_completion_override_generative(self):
        assert classify_red_fire({"completion": True}) == "generative"

    def test_living_flame_override_generative(self):
        assert classify_red_fire({"living_flame": True}) == "generative"

    def test_passion_features_generative(self):
        assert classify_red_fire({"features": ["life_force", "vitality"]}) == "generative"

    def test_passion_with_boundary_protective(self):
        assert classify_red_fire(
            {"features": ["life_force", "boundary"]}
        ) == "protective"

    def test_anger_features_reactive(self):
        assert classify_red_fire({"features": ["reactivity", "blame_projection"]}) == "reactive"

    def test_anger_with_boundary_protective(self):
        assert classify_red_fire(
            {"features": ["reactivity", "boundary"]}
        ) == "protective"

    def test_empty_features_reactive(self):
        assert classify_red_fire({"features": []}) == "reactive"

    def test_empty_signal(self):
        assert classify_red_fire({}) == "reactive"

    def test_none_signal(self):
        assert classify_red_fire(None) == "reactive"


# ---------------------------------------------------------------------------
# assess_integration_level
# ---------------------------------------------------------------------------

class TestAssessIntegrationLevel:
    def test_no_history_returns_baseline(self):
        assert assess_integration_level("entity_1", []) == 0.5

    def test_generative_signals_raise_score(self):
        history = [{"classification": "generative"} for _ in range(4)]
        score = assess_integration_level("e", history)
        assert score > 0.5

    def test_reactive_signals_lower_score(self):
        history = [{"classification": "reactive"} for _ in range(4)]
        score = assess_integration_level("e", history)
        assert score < 0.5

    def test_integrated_wound_adds_bonus(self):
        history = [{"classification": "generative", "wound_stage": "integrated"}]
        score = assess_integration_level("e", history)
        assert score > 0.65

    def test_score_bounded_to_one(self):
        history = [{"classification": "generative", "wound_stage": "integrated"} for _ in range(20)]
        assert assess_integration_level("e", history) == 1.0

    def test_score_bounded_to_zero(self):
        history = [{"classification": "reactive"} for _ in range(20)]
        assert assess_integration_level("e", history) == 0.0


# ---------------------------------------------------------------------------
# map_warrior_archetype
# ---------------------------------------------------------------------------

class TestMapWarriorArchetype:
    def test_explicit_athena_archetype(self):
        assert map_warrior_archetype({"archetype": "athena"}) == "athena"

    def test_explicit_ares_archetype(self):
        assert map_warrior_archetype({"archetype": "ares"}) == "ares"

    def test_generative_fire_maps_to_athena(self):
        assert map_warrior_archetype({"completion": True}) == "athena"

    def test_reactive_fire_maps_to_ares(self):
        assert map_warrior_archetype({"reactive": True}) == "ares"

    def test_empty_signal(self):
        assert map_warrior_archetype({}) == "ares"

    def test_none_signal(self):
        assert map_warrior_archetype(None) == "ares"
