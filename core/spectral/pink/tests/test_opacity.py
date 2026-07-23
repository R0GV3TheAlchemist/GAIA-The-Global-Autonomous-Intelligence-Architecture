# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/pink/test_opacity.py
=========================================
PINK opacity tests:

  1. False Albedo invariant — interrupt_flag can NEVER be True
  2. Sentimentality pattern cases
  3. Rose denial multi-cycle history
  4. apply_shadow_channel integration test
"""

import pytest

from core.spectral.pink.opacity import (
    apply_shadow_channel,
    false_albedo_alert,
    premature_tenderness_detection,
    rosa_hermes_routing,
    rose_denial_marker,
    sentimentality_pattern_recognition,
)


# ---------------------------------------------------------------------------
# INVARIANT: interrupt_flag can NEVER be True
# This test proves it regardless of input.
# ---------------------------------------------------------------------------

class TestInterruptFlagInvariant:
    """The False Albedo invariant: interrupt_flag is always False."""

    def _collect_flags(self, result) -> list[bool]:
        """Recursively collect all interrupt_flag values from a result."""
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

    def test_false_albedo_alert_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"grief_integration": 0.0},
            {"grief_integration": 1.0},
            {"false_albedo": True, "grief_integration": 0.10},
            {"rosa_mystica": True},
            None,
        ]:
            result = false_albedo_alert(signal or {})
            flags = self._collect_flags(result)
            assert all(f is False for f in flags), (
                f"interrupt_flag was True for signal={signal}"
            )

    def test_sentimentality_pattern_interrupt_flag_never_true(self):
        histories = [
            [],
            [{"sentimentality": True, "grief_capacity": 0.0}] * 5,
            [{"sentimentality": False}] * 3,
            None,
        ]
        for h in histories:
            result = sentimentality_pattern_recognition(h or [])
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_premature_tenderness_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"openness": 1.0, "container_strength": 0.0},
            {"openness": 0.0, "container_strength": 1.0},
        ]:
            result = premature_tenderness_detection(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_rose_denial_marker_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"performed_care": 1.0, "structural_care": 0.0},
            {"performed_care": 0.0, "structural_care": 1.0},
        ]:
            result = rose_denial_marker(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_rosa_hermes_routing_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"rosa_mystica": True},
            {"false_albedo": True},
            {"rose_denial": True},
        ]:
            result = rosa_hermes_routing(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_interrupt_flag_never_true(self):
        for signal in [
            {},
            {"rosa_mystica": True},
            {"false_albedo": True, "grief_integration": 0.0},
            {"performed_care": 1.0, "structural_care": 0.0},
        ]:
            result = apply_shadow_channel(signal)
            flags = self._collect_flags(result)
            assert all(f is False for f in flags), (
                f"interrupt_flag was True for signal={signal}, result={result}"
            )


# ---------------------------------------------------------------------------
# Sentimentality Pattern Recognition
# ---------------------------------------------------------------------------

class TestSentimentalityPatternRecognition:
    def test_no_history_no_pattern(self):
        result = sentimentality_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [
            {"sentimentality": True, "grief_capacity": 0.20},
            {"sentimentality": True, "grief_capacity": 0.10},
            {"sentimentality": True, "grief_capacity": 0.10},
        ]
        result = sentimentality_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_grief_capacity(self):
        history = [
            {"sentimentality": True, "grief_capacity": 0.10},
            {"sentimentality": True, "grief_capacity": 0.60},  # breaks streak
            {"sentimentality": True, "grief_capacity": 0.10},
        ]
        result = sentimentality_pattern_recognition(history)
        # streak from end = only 1 (last signal only before break)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        history = [
            {"sentimentality": True, "grief_capacity": 0.10},
            {"sentimentality": True, "grief_capacity": 0.10},
        ]
        result = sentimentality_pattern_recognition(history)
        assert result["pattern_detected"] is False

    def test_none_history_no_pattern(self):
        result = sentimentality_pattern_recognition(None)
        assert result["pattern_detected"] is False


# ---------------------------------------------------------------------------
# Rose Denial Multi-Cycle History
# ---------------------------------------------------------------------------

class TestRoseDenialMarkerMultiCycle:
    def test_rose_denial_detected(self):
        signal = {"performed_care": 0.80, "structural_care": 0.20}
        result = rose_denial_marker(signal)
        assert result["rose_denial"] is True

    def test_no_rose_denial_when_structural_care_high(self):
        signal = {"performed_care": 0.80, "structural_care": 0.70}
        result = rose_denial_marker(signal)
        assert result["rose_denial"] is False

    def test_no_rose_denial_when_performed_care_low(self):
        signal = {"performed_care": 0.30, "structural_care": 0.20}
        result = rose_denial_marker(signal)
        assert result["rose_denial"] is False

    def test_multiple_cycles_accumulate_in_shadow(self):
        import core.spectral.pink.opacity as mod
        before = len(mod._pink_opacity_shadow)
        for _ in range(3):
            rose_denial_marker({"performed_care": 0.80, "structural_care": 0.20})
        after = len(mod._pink_opacity_shadow)
        assert after == before + 3


# ---------------------------------------------------------------------------
# apply_shadow_channel — integration test
# ---------------------------------------------------------------------------

class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"rosa_mystica": True, "openness": 0.80}
        original_copy = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original_copy

    def test_returns_four_shadow_findings(self):
        result = apply_shadow_channel({"false_albedo": True})
        assert len(result["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        result = apply_shadow_channel({"rosa_mystica": True})
        assert result["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_rosa_mystica_signal_routed_to_albedo_integration(self):
        result = apply_shadow_channel({"rosa_mystica": True})
        routing = next(
            f for f in result["shadow_findings"]
            if f.get("type") == "false_albedo_alert" or "route" in f
        )
        # Verify hermes routing finding exists in shadow_findings
        routes = [
            f["route"] for f in result["shadow_findings"] if "route" in f
        ]
        assert "albedo_integration" in routes
