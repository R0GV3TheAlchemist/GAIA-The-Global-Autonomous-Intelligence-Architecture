# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
"""
Tests for core/spectral/orange/clarity.py
"""
import pytest
from core.spectral.orange.clarity import (
    distinguish_ambition_creativity,
    detect_solar_wound,
    classify_orange_fire,
    assess_solar_integration,
    map_solar_archetype,
)


class TestDistinguishAmbitionCreativity:
    def test_ambition_only(self):
        assert distinguish_ambition_creativity({"goal": "build empire"}) == "ambition"

    def test_creativity_only(self):
        assert distinguish_ambition_creativity({"play": True}) == "creativity"

    def test_integrated(self):
        assert distinguish_ambition_creativity({"goal": "x", "expression": "y"}) == "integrated"

    def test_undifferentiated(self):
        assert distinguish_ambition_creativity({}) == "undifferentiated"


class TestDetectSolarWound:
    def test_shame_detected(self):
        result = detect_solar_wound({"shame": True})
        assert result["wound_detected"] is True
        assert result["severity"] == "severe"

    def test_no_wound(self):
        result = detect_solar_wound({"grounded": True})
        assert result["wound_detected"] is False

    def test_self_doubt_mild(self):
        result = detect_solar_wound({"self_doubt": True})
        assert result["severity"] == "mild"


class TestClassifyOrangeFire:
    def test_dormant_when_blocked(self):
        assert classify_orange_fire({"blocked": True, "intensity": 0.8}) == "dormant"

    def test_dormant_low_intensity(self):
        assert classify_orange_fire({"intensity": 0.1}) == "dormant"

    def test_generative(self):
        assert classify_orange_fire({"intensity": 0.7, "direction": "outward"}) == "generative"

    def test_consuming(self):
        assert classify_orange_fire({"intensity": 0.6, "direction": "inward"}) == "consuming"


class TestAssessSolarIntegration:
    def test_full_integration(self):
        signal = {"grounded": True, "purposeful": True, "expressive": True, "intensity": 0.6}
        assert assess_solar_integration(signal) == 1.0

    def test_zero_integration(self):
        assert assess_solar_integration({}) == 0.0

    def test_partial(self):
        result = assess_solar_integration({"grounded": True, "intensity": 0.6})
        assert result == 0.5


class TestMapSolarArchetype:
    def test_dormant_low_integration_is_fool(self):
        assert map_solar_archetype({"blocked": True}) == "fool"

    def test_generative_high_integration_is_creator(self):
        signal = {"intensity": 0.7, "direction": "outward",
                  "grounded": True, "purposeful": True, "expressive": True}
        assert map_solar_archetype(signal) == "creator"

    def test_consuming_is_sovereign(self):
        assert map_solar_archetype({"intensity": 0.6, "direction": "inward"}) == "sovereign"
