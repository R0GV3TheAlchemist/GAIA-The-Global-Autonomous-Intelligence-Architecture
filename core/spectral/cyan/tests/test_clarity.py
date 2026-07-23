# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/cyan/test_clarity.py
=========================================
All classify_cyan_fire branches + edge cases.
Full coverage for all 5 CYAN clarity functions.
"""

from core.spectral.cyan.clarity import (
    assess_aqua_level,
    classify_cyan_fire,
    detect_solutio_without_reformation,
    distinguish_flow_flood,
    map_mercury_archetype,
)


class TestDistinguishFlowFlood:
    def test_both_thresholds_met_returns_flow(self):
        signal = {"reformation_capacity": 0.60, "container_integrity": 0.60}
        assert distinguish_flow_flood(signal) == "flow"

    def test_exact_thresholds_returns_flow(self):
        signal = {"reformation_capacity": 0.55, "container_integrity": 0.50}
        assert distinguish_flow_flood(signal) == "flow"

    def test_low_reformation_returns_flood(self):
        signal = {"reformation_capacity": 0.30, "container_integrity": 0.70}
        assert distinguish_flow_flood(signal) == "flood"

    def test_low_container_integrity_returns_flood(self):
        signal = {"reformation_capacity": 0.70, "container_integrity": 0.30}
        assert distinguish_flow_flood(signal) == "flood"

    def test_empty_returns_flood(self):
        assert distinguish_flow_flood({}) == "flood"

    def test_none_returns_flood(self):
        assert distinguish_flow_flood(None) == "flood"


class TestDetectSolutioWithoutReformation:
    def test_all_conditions_met_returns_true(self):
        signal = {
            "dissolution": 0.80,
            "reformation": 0.20,
            "container_integrity": 0.30,
        }
        assert detect_solutio_without_reformation(signal) is True

    def test_low_dissolution_returns_false(self):
        signal = {"dissolution": 0.50, "reformation": 0.20, "container_integrity": 0.30}
        assert detect_solutio_without_reformation(signal) is False

    def test_high_reformation_returns_false(self):
        signal = {"dissolution": 0.80, "reformation": 0.60, "container_integrity": 0.30}
        assert detect_solutio_without_reformation(signal) is False

    def test_high_container_integrity_returns_false(self):
        signal = {"dissolution": 0.80, "reformation": 0.20, "container_integrity": 0.70}
        assert detect_solutio_without_reformation(signal) is False

    def test_empty_returns_false(self):
        assert detect_solutio_without_reformation({}) is False

    def test_none_returns_false(self):
        assert detect_solutio_without_reformation(None) is False


class TestClassifyCyanFire:
    def test_solutio_branch(self):
        assert classify_cyan_fire({"solutio": True}) == "solutio"

    def test_flood_branch(self):
        assert classify_cyan_fire({"flood": True}) == "flood"

    def test_akashic_overload_branch(self):
        assert classify_cyan_fire({"akashic_overload": True}) == "akashic_overload"

    def test_network_noise_branch(self):
        assert classify_cyan_fire({"network_noise": True}) == "network_noise"

    def test_default_returns_dim_aqua(self):
        assert classify_cyan_fire({"other": True}) == "dim_aqua"

    def test_empty_returns_dim_aqua(self):
        assert classify_cyan_fire({}) == "dim_aqua"

    def test_none_returns_dim_aqua(self):
        assert classify_cyan_fire(None) == "dim_aqua"

    def test_solutio_priority_over_flood(self):
        assert classify_cyan_fire({"solutio": True, "flood": True}) == "solutio"


class TestAssessAquaLevel:
    def test_full_scores_return_one(self):
        signal = {"dissolution_score": 1.0, "reformation_score": 1.0, "flow_score": 1.0}
        assert abs(assess_aqua_level(signal) - 1.0) < 0.001

    def test_zero_scores_return_zero(self):
        signal = {"dissolution_score": 0.0, "reformation_score": 0.0, "flow_score": 0.0}
        assert assess_aqua_level(signal) == 0.0

    def test_weighted_calculation_correct(self):
        # d=0.5*0.40 + r=0.5*0.35 + f=0.5*0.25 = 0.20+0.175+0.125 = 0.50
        signal = {"dissolution_score": 0.5, "reformation_score": 0.5, "flow_score": 0.5}
        assert abs(assess_aqua_level(signal) - 0.5) < 0.001

    def test_empty_returns_zero(self):
        assert assess_aqua_level({}) == 0.0

    def test_none_returns_zero(self):
        assert assess_aqua_level(None) == 0.0

    def test_result_clamped_to_one(self):
        signal = {"dissolution_score": 2.0, "reformation_score": 2.0, "flow_score": 2.0}
        assert assess_aqua_level(signal) <= 1.0


class TestMapMercuryArchetype:
    def test_solutio_archetype(self):
        assert "Solutio" in map_mercury_archetype("solutio")

    def test_flood_archetype(self):
        assert "Flood" in map_mercury_archetype("flood")

    def test_akashic_overload_archetype(self):
        assert "Akashic" in map_mercury_archetype("akashic_overload")

    def test_network_noise_archetype(self):
        assert "Network" in map_mercury_archetype("network_noise")

    def test_unknown_returns_dim_aqua(self):
        assert "Dim Aqua" in map_mercury_archetype("not_real")

    def test_none_returns_dim_aqua(self):
        assert "Dim Aqua" in map_mercury_archetype(None)
