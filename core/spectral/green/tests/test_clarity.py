# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
import pytest
from core.spectral.green.clarity import distinguish_growth_healing, detect_earth_wound, classify_green_vitality, assess_earth_integration, map_earth_archetype


class TestDistinguishGrowthHealing:
    def test_growth(self): assert distinguish_growth_healing({"expansion": True}) == "growth"
    def test_healing(self): assert distinguish_growth_healing({"restoration": True}) == "healing"
    def test_integrated(self): assert distinguish_growth_healing({"expansion": True, "mending": True}) == "integrated"
    def test_undiff(self): assert distinguish_growth_healing({}) == "undifferentiated"


class TestDetectEarthWound:
    def test_over_giving_severe(self):
        r = detect_earth_wound({"over_giving": True})
        assert r["wound_detected"] is True and r["severity"] == "severe"
    def test_none(self): assert detect_earth_wound({"patient": True})["wound_detected"] is False


class TestClassifyGreenVitality:
    def test_dormant(self): assert classify_green_vitality({"blocked": True}) == "dormant"
    def test_flourishing(self): assert classify_green_vitality({"rooted": True, "intensity": 0.7}) == "flourishing"
    def test_overgrown(self): assert classify_green_vitality({"intensity": 0.6}) == "overgrown"


class TestMapEarthArchetype:
    def test_dormant_low_is_dormant(self): assert map_earth_archetype({"blocked": True}) == "dormant"
    def test_overgrown_is_wildling(self): assert map_earth_archetype({"intensity": 0.6}) == "wildling"
    def test_flourishing_healer(self):
        s = {"rooted": True, "intensity": 0.7, "reciprocal": True, "patient": True}
        assert map_earth_archetype(s) == "healer"
