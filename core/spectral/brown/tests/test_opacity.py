# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/brown/test_opacity.py
==========================================
BROWN opacity tests:

  1. Humus invariant — interrupt_flag can NEVER be True
  2. Inertia pattern cases
  3. Compaction multi-cycle history
  4. apply_shadow_channel integration test
  5. earth/hermes vocabulary verified in routing
"""

from core.spectral.brown.opacity import (
    apply_shadow_channel,
    compaction_alert,
    earth_hermes_routing,
    humus_fertility_marker,
    inertia_pattern_recognition,
    sediment_null_detection,
)


class TestInterruptFlagInvariant:
    """Humus invariant: interrupt_flag is always False."""

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

    def test_compaction_alert_never_true(self):
        for signal in [{}, {"porosity": 0.0}, {"porosity": 1.0}, None]:
            flags = self._collect_flags(compaction_alert(signal or {}))
            assert all(f is False for f in flags)

    def test_inertia_pattern_never_true(self):
        for history in [[], [{"sediment": True, "decomposition_rate": 0.0}] * 5, None]:
            flags = self._collect_flags(inertia_pattern_recognition(history or []))
            assert all(f is False for f in flags)

    def test_sediment_null_detection_never_true(self):
        for signal in [
            {},
            {"groundedness": 1.0, "porosity": 0.0, "decomposition_rate": 0.0},
            {"groundedness": 0.0},
        ]:
            flags = self._collect_flags(sediment_null_detection(signal))
            assert all(f is False for f in flags)

    def test_humus_fertility_marker_never_true(self):
        for signal in [{}, {"porosity": 1.0, "decomposition_rate": 1.0}, {"porosity": 0.0}]:
            flags = self._collect_flags(humus_fertility_marker(signal))
            assert all(f is False for f in flags)

    def test_earth_hermes_routing_never_true(self):
        for signal in [{}, {"humus": True}, {"compaction": True}, {"sediment": True}]:
            flags = self._collect_flags(earth_hermes_routing(signal))
            assert all(f is False for f in flags)

    def test_apply_shadow_channel_never_true(self):
        for signal in [{}, {"humus": True}, {"compaction": True}, {"sediment": True}]:
            flags = self._collect_flags(apply_shadow_channel(signal))
            assert all(f is False for f in flags), f"interrupt_flag True for {signal}"


class TestInertiaPatternRecognition:
    def test_no_history_no_pattern(self):
        result = inertia_pattern_recognition([])
        assert result["pattern_detected"] is False
        assert result["streak_length"] == 0

    def test_streak_of_3_detects_pattern(self):
        history = [{"sediment": True, "decomposition_rate": 0.05}] * 3
        result = inertia_pattern_recognition(history)
        assert result["pattern_detected"] is True
        assert result["streak_length"] == 3

    def test_streak_broken_by_sufficient_decomposition(self):
        history = [
            {"sediment": True, "decomposition_rate": 0.05},
            {"sediment": True, "decomposition_rate": 0.70},  # breaks streak
            {"sediment": True, "decomposition_rate": 0.05},
        ]
        result = inertia_pattern_recognition(history)
        assert result["streak_length"] == 1

    def test_streak_of_2_no_pattern(self):
        result = inertia_pattern_recognition([{"sediment": True, "decomposition_rate": 0.05}] * 2)
        assert result["pattern_detected"] is False

    def test_none_no_pattern(self):
        assert inertia_pattern_recognition(None)["pattern_detected"] is False


class TestCompactionMultiCycle:
    def test_critical_severity_when_porosity_very_low(self):
        assert compaction_alert({"porosity": 0.05})["severity"] == "critical"

    def test_high_severity_when_porosity_moderate(self):
        assert compaction_alert({"porosity": 0.20})["severity"] == "high"

    def test_multiple_cycles_accumulate(self):
        import core.spectral.brown.opacity as mod
        before = len(mod._brown_opacity_shadow)
        for _ in range(3):
            compaction_alert({"porosity": 0.05})
        assert len(mod._brown_opacity_shadow) == before + 3


class TestEarthHermesRoutingVocabulary:
    def test_carries_earth_archetype(self):
        assert earth_hermes_routing({"humus": True})["archetype"] == "earth"

    def test_carries_hermes_messenger(self):
        assert earth_hermes_routing({"humus": True})["messenger"] == "hermes"

    def test_humus_routes_to_fertility_integration(self):
        assert earth_hermes_routing({"humus": True})["route"] == "fertility_integration"

    def test_compaction_routes_to_porosity_restoration(self):
        assert earth_hermes_routing({"compaction": True})["route"] == "porosity_restoration"

    def test_sediment_routes_to_decomposition_activation(self):
        assert earth_hermes_routing({"sediment": True})["route"] == "decomposition_activation"

    def test_default_routes_to_earth_holding(self):
        assert earth_hermes_routing({})["route"] == "earth_holding"


class TestApplyShadowChannel:
    def test_original_signal_not_mutated(self):
        signal = {"humus": True, "porosity": 0.70}
        original = dict(signal)
        apply_shadow_channel(signal)
        assert signal == original

    def test_returns_four_shadow_findings(self):
        assert len(apply_shadow_channel({"sediment": True})["shadow_findings"]) == 4

    def test_interrupt_flag_false_at_top_level(self):
        assert apply_shadow_channel({"humus": True})["interrupt_flag"] is False

    def test_empty_signal_handled_gracefully(self):
        result = apply_shadow_channel({})
        assert "original_signal" in result
        assert result["interrupt_flag"] is False

    def test_humus_routed_to_fertility_integration(self):
        result = apply_shadow_channel({"humus": True})
        routes = [f["route"] for f in result["shadow_findings"] if "route" in f]
        assert "fertility_integration" in routes
