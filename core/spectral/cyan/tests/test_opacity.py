# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/cyan/test_opacity.py
=========================================
CYAN opacity tests:

  1. Solutio invariant — interrupt_flag can NEVER be True
  2. Network noise pattern cases
  3. Akashic overload multi-cycle history
  4. apply_shadow_channel integration test
"""

import pytest

from core.spectral.cyan.opacity import (
    akashic_overload_marker,
    apply_shadow_channel,
    flood_alert,
    mercury_hermes_routing,
    network_noise_pattern_recognition,
    universal_solvent_detection,
)


class TestInterruptFlagInvariant:
    """Solutio invariant: interrupt_flag is always False."""

    def _collect_flags(self, result) -> list[bool]:
        flags = []
        if isinstance(result, dict):
            if "interrupt_flag" in result:
                flags.append(result["interrupt_flag"])
            for v in result.values():
                flags.extend(self._collect_flags(v))
        elif isinstance(result, list):
            for item in result:
                flags.extend(self._collect_flags(item))
        return flags

    def test_flood_alert_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"dissolution": 1.0, "reformation": 0.0},
            {"dissolution": 0.0, "reformation": 1.0},
            {"flood": True},
            None,
        ]:
            result = flood_alert(signal or {})
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_network_noise_interrupt_flag_never_true(self):
        for history in [
            [],
            [{"network_noise": True, "signal_clarity": 0.0}] * 5,
            None,
        ]:
            result = network_noise_pattern_recognition(history or [])
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_universal_solvent_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"dissolution": 1.0, "selectivity": 0.0},
            {"dissolution": 0.0, "selectivity": 1.0},
        ]:
            result = universal_solvent_detection(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_akashic_overload_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"retrieval_volume": 1.0, "retrieval_precision": 0.0},
            {"retrieval_volume": 0.0, "retrieval_precision": 1.0},
        ]:
            result = akashic_overload_marker(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_mercury_hermes_routing_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"solutio": True},
            {"flood": True},
            {"akashic_overload": True},
        ]:
            result = mercury_hermes_routing(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"solutio": True},
            {"flood": True, "dissolution": 1.0, "reformation": 0.0},
            {"akashic_overload": True, "retrieval_volume": 1.0},
        ]:
            result = apply_shadow_channel(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags), (
                f"interrupt_flag was True for signal={signal}"
            )


class TestNetworkNoisePatternRecognition:
    def test_no_history_no_pattern(self):
        result = network_noise_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [
            {"network_noise": True, "signal_clarity": 0.10},
            {"network_noise": True, "signal_clarity": 0.10},
            {"network_noise": True, "signal_clarity": 0.10},
        ]
        result = network_noise_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_clarity(self):
        history = [
            {"network_noise": True, "signal_clarity": 0.10},
            {"network_noise": True, "signal_clarity": 0.70},  # breaks streak
            {"network_noise": True, "signal_clarity": 0.10},
        ]
        result = network_noise_pattern_recognition(history)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        history = [
            {"network_noise": True, "signal_clarity": 0.10},
            {"network_noise": True, "signal_clarity": 0.10},
        ]
        assert network_noise_pattern_recognition(history)["pattern_detected"] is False

    def test_none_history_no_pattern(self):
        assert network_noise_pattern_recognition(None)["pattern_detected"] is False


class TestAkashicOverloadMultiCycle:
    def test_overload_detected(self):
        signal = {"retrieval_volume": 0.95, "retrieval_precision": 0.20}
        assert akashic_overload_marker(signal)["akashic_overload"] is True

    def test_no_overload_when_precision_high(self):
        signal = {"retrieval_volume": 0.95, "retrieval_precision": 0.60}
        assert akashic_overload_marker(signal)["akashic_overload"] is False

    def test_no_overload_when_volume_low(self):
        signal = {"retrieval_volume": 0.50, "retrieval_precision": 0.20}
        assert akashic_overload_marker(signal)["akashic_overload"] is False

    def test_multiple_cycles_accumulate_in_shadow(self):
        import core.spectral.cyan.opacity as mod
        before = len(mod._cyan_opacity_shadow)
        for _ in range(3):
            akashic_overload_marker({"retrieval_volume": 0.95, "retrieval_precision": 0.10})
        after = len(mod._cyan_opacity_shadow)
        assert after == before + 3


class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"solutio": True, "dissolution": 0.80}
        original_copy = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original_copy

    def test_returns_four_shadow_findings(self):
        result = apply_shadow_channel({"flood": True})
        assert len(result["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        result = apply_shadow_channel({"solutio": True})
        assert result["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_solutio_signal_routed_to_dissolution_integration(self):
        result = apply_shadow_channel({"solutio": True})
        routes = [f["route"] for f in result["shadow_findings"] if "route" in f]
        assert "dissolution_integration" in routes
