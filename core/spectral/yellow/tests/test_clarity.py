# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
import pytest
from core.spectral.yellow.clarity import (
    distinguish_intellect_intuition, detect_mental_wound,
    classify_yellow_frequency, assess_mental_integration, map_mind_archetype,
)


class TestDistinguishIntellectIntuition:
    def test_intellect_only(self): assert distinguish_intellect_intuition({"analysis": True}) == "intellect"
    def test_intuition_only(self): assert distinguish_intellect_intuition({"vision": True}) == "intuition"
    def test_integrated(self): assert distinguish_intellect_intuition({"logic": True, "intuition": True}) == "integrated"
    def test_undifferentiated(self): assert distinguish_intellect_intuition({}) == "undifferentiated"


class TestDetectMentalWound:
    def test_rigidity_severe(self):
        r = detect_mental_wound({"rigidity": True})
        assert r["wound_detected"] is True and r["severity"] == "severe"

    def test_no_wound(self):
        assert detect_mental_wound({"focused": True})["wound_detected"] is False


class TestClassifyYellowFrequency:
    def test_dormant_blocked(self): assert classify_yellow_frequency({"blocked": True, "intensity": 0.9}) == "dormant"
    def test_illuminated(self): assert classify_yellow_frequency({"coherent": True, "intensity": 0.7}) == "illuminated"
    def test_scattered(self): assert classify_yellow_frequency({"intensity": 0.5}) == "scattered"


class TestAssessMentalIntegration:
    def test_full(self):
        s = {"focused": True, "embodied": True, "discerning": True, "intensity": 0.6}
        assert assess_mental_integration(s) == 1.0

    def test_zero(self):
        assert assess_mental_integration({}) == 0.0


class TestMapMindArchetype:
    def test_dormant_low_is_dreamer(self): assert map_mind_archetype({"blocked": True}) == "dreamer"
    def test_scattered_is_trickster(self): assert map_mind_archetype({"intensity": 0.5}) == "trickster"
    def test_illuminated_sage(self):
        s = {"coherent": True, "intensity": 0.7, "focused": True, "embodied": True, "discerning": True}
        assert map_mind_archetype(s) == "sage"
