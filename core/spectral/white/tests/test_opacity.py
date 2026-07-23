# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/white/test_opacity.py
==========================================
WHITE opacity tests:

  1. Albedo invariant — interrupt_flag can NEVER be True
  2. Overexposure pattern cases
  3. Bleaching multi-cycle history
  4. apply_shadow_channel integration test
"""

from core.spectral.white.opacity import (
    albedo_hermes_routing,
    apply_shadow_channel,
    bleaching_alert,
    lunar_reflection_marker,
    overexposure_pattern_recognition,
    purification_null_detection,
)


class TestInterruptFlagInvariant:
    """Albedo invariant: interrupt_flag is always False."""

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

    def test_bleaching_alert_never_true(self):
        for signal in [{}, {"texture": 0.0}, {"texture": 1.0}, None]:
            flags = self._collect_flags(bleaching_alert(signal or {}))
            assert all(f is False for f in flags)

    def test_overexposure_pattern_never_true(self):
        for history in [[], [{"overexposed": True, "contrast": 0.0}] * 5, None]:
            flags = self._collect_flags(overexposure_pattern_recognition(history or []))
            assert all(f is False for f in flags)

    def test_purification_null_never_true(self):
        for signal in [{}, {"purification": 1.0, "texture": 0.0, "contrast": 0.0}, {"purification": 0.0}]:
            flags = self._collect_flags(purification_null_detection(signal))
            assert all(f is False for f in flags)

    def test_lunar_reflection_marker_never_true(self):
        for signal in [{}, {"reflection": 1.0, "texture": 1.0}, {"reflection": 0.0}]:
            flags = self._collect_flags(lunar_reflection_marker(signal))
            assert all(f is False for f in flags)

    def test_albedo_hermes_routing_never_true(self):
        for signal in [{}, {"albedo": True}, {"bleaching": True}, {"overexposed": True}]:
            flags = self._collect_flags(albedo_hermes_routing(signal))
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_never_true(self):
        for signal in [{}, {"albedo": True}, {"bleaching": True, "texture": 0.0}, {"overexposed": True}]:
            flags = self._collect_flags(apply_shadow_channel(signal))
            assert all(f is False for f in flags), f"interrupt_flag True for {signal}"


class TestOverexposurePatternRecognition:
    def test_no_history_no_pattern(self):
        result = overexposure_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [{"overexposed": True, "contrast": 0.10}] * 3
        result = overexposure_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_contrast(self):
        history = [
            {"overexposed": True, "contrast": 0.10},
            {"overexposed": True, "contrast": 0.60},  # breaks streak
            {"overexposed": True, "contrast": 0.10},
        ]
        result = overexposure_pattern_recognition(history)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        result = overexposure_pattern_recognition([{"overexposed": True, "contrast": 0.10}] * 2)
        assert result["pattern_detected"] is False

    def test_none_no_pattern(self):
        assert overexposure_pattern_recognition(None)["pattern_detected"] is False


class TestBleachingMultiCycle:
    def test_critical_severity_when_texture_very_low(self):
        assert bleaching_alert({"texture": 0.05})["severity"] == "critical"

    def test_high_severity_when_texture_moderate(self):
        assert bleaching_alert({"texture": 0.25})["severity"] == "high"

    def test_multiple_cycles_accumulate(self):
        import core.spectral.white.opacity as mod
        before = len(mod._white_opacity_shadow)
        for _ in range(3):
            bleaching_alert({"texture": 0.05})
        assert len(mod._white_opacity_shadow) == before + 3


class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"albedo": True, "texture": 0.70}
        original = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original

    def test_returns_four_shadow_findings(self):
        assert len(apply_shadow_channel({"bleaching": True})["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        assert apply_shadow_channel({"albedo": True})["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_albedo_signal_routed_to_purification_integration(self):
        result = apply_shadow_channel({"albedo": True})
        routes = [f["route"] for f in result["shadow_findings"] if "route" in f]
        assert "purification_integration" in routes
