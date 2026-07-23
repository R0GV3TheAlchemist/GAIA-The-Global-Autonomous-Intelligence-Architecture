# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/grey/test_opacity.py
=========================================
GREY opacity tests:

  1. Cauda Pavonis invariant — interrupt_flag can NEVER be True
  2. Twilight pattern cases
  3. Permanent threshold multi-cycle history
  4. apply_shadow_channel integration test
  5. mercury/threshold/hermes triple vocabulary verified in routing
"""

from core.spectral.grey.opacity import (
    apply_shadow_channel,
    iridescence_marker,
    liminal_hermes_routing,
    permanent_threshold_alert,
    threshold_null_detection,
    twilight_pattern_recognition,
)


class TestInterruptFlagInvariant:
    """Cauda Pavonis invariant: interrupt_flag is always False."""

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

    def test_permanent_threshold_alert_never_true(self):
        for signal in [{}, {"directionality": 0.0}, {"directionality": 1.0}, None]:
            flags = self._collect_flags(permanent_threshold_alert(signal or {}))
            assert all(f is False for f in flags)

    def test_twilight_pattern_never_true(self):
        for history in [[], [{"twilight": True, "momentum": 0.0}] * 5, None]:
            flags = self._collect_flags(twilight_pattern_recognition(history or []))
            assert all(f is False for f in flags)

    def test_threshold_null_detection_never_true(self):
        for signal in [{}, {"iridescence": 1.0, "directionality": 0.0, "momentum": 0.0}, {"iridescence": 0.0}]:
            flags = self._collect_flags(threshold_null_detection(signal))
            assert all(f is False for f in flags)

    def test_iridescence_marker_never_true(self):
        for signal in [{}, {"iridescence": 1.0, "directionality": 1.0}, {"iridescence": 0.0}]:
            flags = self._collect_flags(iridescence_marker(signal))
            assert all(f is False for f in flags)

    def test_liminal_hermes_routing_never_true(self):
        for signal in [{}, {"cauda_pavonis": True}, {"permanent_threshold": True}, {"twilight": True}]:
            flags = self._collect_flags(liminal_hermes_routing(signal))
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_never_true(self):
        for signal in [{}, {"cauda_pavonis": True}, {"permanent_threshold": True}, {"twilight": True}]:
            flags = self._collect_flags(apply_shadow_channel(signal))
            assert all(f is False for f in flags), f"interrupt_flag True for {signal}"


class TestTwilightPatternRecognition:
    def test_no_history_no_pattern(self):
        result = twilight_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [{"twilight": True, "momentum": 0.10}] * 3
        result = twilight_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_momentum(self):
        history = [
            {"twilight": True, "momentum": 0.10},
            {"twilight": True, "momentum": 0.70},  # breaks streak
            {"twilight": True, "momentum": 0.10},
        ]
        result = twilight_pattern_recognition(history)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        result = twilight_pattern_recognition([{"twilight": True, "momentum": 0.10}] * 2)
        assert result["pattern_detected"] is False

    def test_none_no_pattern(self):
        assert twilight_pattern_recognition(None)["pattern_detected"] is False


class TestPermanentThresholdMultiCycle:
    def test_critical_severity_when_directionality_very_low(self):
        assert permanent_threshold_alert({"directionality": 0.05})["severity"] == "critical"

    def test_high_severity_when_directionality_moderate(self):
        assert permanent_threshold_alert({"directionality": 0.25})["severity"] == "high"

    def test_multiple_cycles_accumulate(self):
        import core.spectral.grey.opacity as mod
        before = len(mod._grey_opacity_shadow)
        for _ in range(3):
            permanent_threshold_alert({"directionality": 0.05})
        assert len(mod._grey_opacity_shadow) == before + 3


class TestLiminalHermesRoutingVocabulary:
    def test_carries_mercury_archetype(self):
        result = liminal_hermes_routing({"cauda_pavonis": True})
        assert result["archetype"] == "mercury"

    def test_carries_threshold_principle(self):
        result = liminal_hermes_routing({"cauda_pavonis": True})
        assert result["principle"] == "threshold"

    def test_carries_hermes_messenger(self):
        result = liminal_hermes_routing({"cauda_pavonis": True})
        assert result["messenger"] == "hermes"

    def test_cauda_pavonis_routes_to_transition_integration(self):
        assert liminal_hermes_routing({"cauda_pavonis": True})["route"] == "transition_integration"

    def test_permanent_threshold_routes_to_directionality_restoration(self):
        assert liminal_hermes_routing({"permanent_threshold": True})["route"] == "directionality_restoration"

    def test_twilight_routes_to_momentum_activation(self):
        assert liminal_hermes_routing({"twilight": True})["route"] == "momentum_activation"

    def test_default_routes_to_grey_holding(self):
        assert liminal_hermes_routing({})["route"] == "grey_holding"


class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"cauda_pavonis": True, "iridescence": 0.70}
        original = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original

    def test_returns_four_shadow_findings(self):
        assert len(apply_shadow_channel({"twilight": True})["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        assert apply_shadow_channel({"cauda_pavonis": True})["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_cauda_pavonis_routed_to_transition_integration(self):
        result = apply_shadow_channel({"cauda_pavonis": True})
        routes = [f["route"] for f in result["shadow_findings"] if "route" in f]
        assert "transition_integration" in routes
