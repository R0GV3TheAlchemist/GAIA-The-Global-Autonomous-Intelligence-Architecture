# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/gold/test_opacity.py
=========================================
GOLD opacity tests:

  1. Aurum invariant — interrupt_flag can NEVER be True
  2. Monument pattern cases
  3. Canon ossification multi-cycle history
  4. apply_shadow_channel integration test
"""

from core.spectral.gold.opacity import (
    apply_shadow_channel,
    aurum_hermes_routing,
    canon_ossification_alert,
    false_completion_detection,
    incorruptible_marker,
    monument_pattern_recognition,
)


class TestInterruptFlagInvariant:
    """Aurum invariant: interrupt_flag is always False."""

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

    def test_canon_ossification_alert_never_true(self):
        for signal in [{}, {"vitality": 0.0}, {"vitality": 1.0}, None]:
            flags = self._collect_flags(canon_ossification_alert(signal or {}))
            assert all(f is False for f in flags)

    def test_monument_pattern_never_true(self):
        for history in [[], [{"monument": True, "vitality": 0.0}] * 5, None]:
            flags = self._collect_flags(monument_pattern_recognition(history or []))
            assert all(f is False for f in flags)

    def test_false_completion_detection_never_true(self):
        for signal in [{}, {"completion_score": 1.0, "inner_structure": 0.0}, {"completion_score": 0.0}]:
            flags = self._collect_flags(false_completion_detection(signal))
            assert all(f is False for f in flags)

    def test_incorruptible_marker_never_true(self):
        for signal in [{}, {"incorruptibility": 1.0, "vitality": 1.0}, {"incorruptibility": 0.0}]:
            flags = self._collect_flags(incorruptible_marker(signal))
            assert all(f is False for f in flags)

    def test_aurum_hermes_routing_never_true(self):
        for signal in [{}, {"aurum": True}, {"ossification": True}, {"false_completion": True}]:
            flags = self._collect_flags(aurum_hermes_routing(signal))
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_never_true(self):
        for signal in [{}, {"aurum": True}, {"ossification": True, "vitality": 0.0}, {"false_completion": True}]:
            flags = self._collect_flags(apply_shadow_channel(signal))
            assert all(f is False for f in flags), f"interrupt_flag True for {signal}"


class TestMonumentPatternRecognition:
    def test_no_history_no_pattern(self):
        result = monument_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [{"monument": True, "vitality": 0.10}] * 3
        result = monument_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_vitality(self):
        history = [
            {"monument": True, "vitality": 0.10},
            {"monument": True, "vitality": 0.70},  # breaks streak
            {"monument": True, "vitality": 0.10},
        ]
        result = monument_pattern_recognition(history)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        result = monument_pattern_recognition([{"monument": True, "vitality": 0.10}] * 2)
        assert result["pattern_detected"] is False

    def test_none_no_pattern(self):
        assert monument_pattern_recognition(None)["pattern_detected"] is False


class TestCanonOssificationMultiCycle:
    def test_critical_severity_when_vitality_very_low(self):
        result = canon_ossification_alert({"vitality": 0.10})
        assert result["severity"] == "critical"

    def test_high_severity_when_vitality_moderate(self):
        result = canon_ossification_alert({"vitality": 0.30})
        assert result["severity"] == "high"

    def test_multiple_cycles_accumulate(self):
        import core.spectral.gold.opacity as mod
        before = len(mod._gold_opacity_shadow)
        for _ in range(3):
            canon_ossification_alert({"vitality": 0.10})
        assert len(mod._gold_opacity_shadow) == before + 3


class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"aurum": True, "vitality": 0.80}
        original = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original

    def test_returns_four_shadow_findings(self):
        assert len(apply_shadow_channel({"ossification": True})["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        assert apply_shadow_channel({"aurum": True})["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_aurum_signal_routed_to_completion_integration(self):
        result = apply_shadow_channel({"aurum": True})
        routes = [f["route"] for f in result["shadow_findings"] if "route" in f]
        assert "completion_integration" in routes
