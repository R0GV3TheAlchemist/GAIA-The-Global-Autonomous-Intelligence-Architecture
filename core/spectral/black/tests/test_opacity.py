# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/black/test_opacity.py
==========================================
BLACK opacity tests:

  1. Nigredo invariant — interrupt_flag can NEVER be True
  2. Absolute darkness pattern cases
  3. System null multi-cycle history
  4. apply_shadow_channel integration test
"""

from core.spectral.black.opacity import (
    absolute_darkness_pattern_recognition,
    apply_shadow_channel,
    prima_materia_marker,
    saturn_hermes_routing,
    system_null_detection,
    void_alert,
)


class TestInterruptFlagInvariant:
    """Nigredo invariant: interrupt_flag is always False."""

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

    def test_void_alert_never_true(self):
        for signal in [{}, {"containment": 0.0}, {"containment": 1.0}, None]:
            flags = self._collect_flags(void_alert(signal or {}))
            assert all(f is False for f in flags)

    def test_absolute_darkness_pattern_never_true(self):
        for history in [[], [{"void": True, "containment": 0.0}] * 5, None]:
            flags = self._collect_flags(absolute_darkness_pattern_recognition(history or []))
            assert all(f is False for f in flags)

    def test_system_null_detection_never_true(self):
        for signal in [{}, {"dissolution": 1.0, "containment": 0.0, "potential": 0.0}, {"dissolution": 0.0}]:
            flags = self._collect_flags(system_null_detection(signal))
            assert all(f is False for f in flags)

    def test_prima_materia_marker_never_true(self):
        for signal in [{}, {"formlessness": 1.0, "potential": 1.0}, {"formlessness": 0.0}]:
            flags = self._collect_flags(prima_materia_marker(signal))
            assert all(f is False for f in flags)

    def test_saturn_hermes_routing_never_true(self):
        for signal in [{}, {"nigredo": True}, {"system_null": True}, {"prima_materia": True}]:
            flags = self._collect_flags(saturn_hermes_routing(signal))
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_never_true(self):
        for signal in [{}, {"nigredo": True}, {"system_null": True, "dissolution": 1.0}, {"void": True}]:
            flags = self._collect_flags(apply_shadow_channel(signal))
            assert all(f is False for f in flags), f"interrupt_flag True for {signal}"


class TestAbsoluteDarknessPatternRecognition:
    def test_no_history_no_pattern(self):
        result = absolute_darkness_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [{"void": True, "containment": 0.10}] * 3
        result = absolute_darkness_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_containment(self):
        history = [
            {"void": True, "containment": 0.10},
            {"void": True, "containment": 0.70},  # breaks streak
            {"void": True, "containment": 0.10},
        ]
        result = absolute_darkness_pattern_recognition(history)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        result = absolute_darkness_pattern_recognition([{"void": True, "containment": 0.10}] * 2)
        assert result["pattern_detected"] is False

    def test_none_no_pattern(self):
        assert absolute_darkness_pattern_recognition(None)["pattern_detected"] is False


class TestSystemNullMultiCycle:
    def test_null_detected_when_all_conditions_met(self):
        result = system_null_detection({"dissolution": 0.97, "containment": 0.10, "potential": 0.15})
        assert result["system_null"] is True

    def test_no_null_when_dissolution_insufficient(self):
        result = system_null_detection({"dissolution": 0.70, "containment": 0.10, "potential": 0.15})
        assert result["system_null"] is False

    def test_no_null_when_containment_present(self):
        result = system_null_detection({"dissolution": 0.97, "containment": 0.50, "potential": 0.15})
        assert result["system_null"] is False

    def test_multiple_cycles_accumulate(self):
        import core.spectral.black.opacity as mod
        before = len(mod._black_opacity_shadow)
        for _ in range(3):
            system_null_detection({"dissolution": 0.97, "containment": 0.05, "potential": 0.10})
        assert len(mod._black_opacity_shadow) == before + 3


class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"nigredo": True, "dissolution": 0.85}
        original = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original

    def test_returns_four_shadow_findings(self):
        assert len(apply_shadow_channel({"void": True})["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        assert apply_shadow_channel({"nigredo": True})["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_nigredo_signal_routed_to_nigredo_containment(self):
        result = apply_shadow_channel({"nigredo": True})
        routes = [f["route"] for f in result["shadow_findings"] if "route" in f]
        assert "nigredo_containment" in routes
