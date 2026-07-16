# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
"""
Tests for core/spectral/orange/opacity.py

CRITICAL: interrupt_flag invariant — it MUST always be False regardless of input.
"""
import pytest
from core.spectral.orange.opacity import (
    citrinitas_alert,
    creative_wound_recognition,
    phoenix_marker,
    ares_athena_routing,
    apply_shadow_channel,
)


class TestInterruptFlagInvariant:
    """interrupt_flag must ALWAYS be False — this is the non-negotiable invariant."""

    def test_citrinitas_alert_interrupt_false(self):
        assert citrinitas_alert({})["interrupt_flag"] is False

    def test_creative_wound_interrupt_false(self):
        assert creative_wound_recognition({})["interrupt_flag"] is False

    def test_phoenix_marker_interrupt_false(self):
        assert phoenix_marker({})["interrupt_flag"] is False

    def test_ares_athena_interrupt_false(self):
        assert ares_athena_routing({})["interrupt_flag"] is False

    def test_apply_shadow_strips_interrupt_true(self):
        result = apply_shadow_channel({}, {"interrupt_flag": True, "data": "x"})
        for shadow in result["_opacity_shadow"]:
            assert shadow["interrupt_flag"] is False


class TestPhoenixMarker:
    def test_no_history_no_resurrection(self):
        result = phoenix_marker({"intensity": 0.1})
        assert result["resurrection_detected"] is False

    def test_resurrection_detected(self):
        history = [
            {"blocked": True},
            {"intensity": 0.1},
        ]
        current = {"intensity": 0.7, "direction": "outward"}
        result = phoenix_marker(current, history=history)
        assert result["resurrection_detected"] is True


class TestAresAthenaRouting:
    def test_fool_routes_to_ares(self):
        result = ares_athena_routing({"blocked": True})
        assert result["channel"] == "ares"

    def test_creator_routes_to_athena(self):
        signal = {"intensity": 0.7, "direction": "outward",
                  "grounded": True, "purposeful": True, "expressive": True}
        result = ares_athena_routing(signal)
        assert result["channel"] == "athena"


class TestApplyShadowChannel:
    def test_primary_signal_not_mutated(self):
        primary = {"data": "original"}
        original_copy = dict(primary)
        apply_shadow_channel(primary, {"extra": "shadow"})
        assert primary == original_copy

    def test_shadow_appended_to_result(self):
        result = apply_shadow_channel({}, {"tag": "solar"})
        assert len(result["_opacity_shadow"]) == 1
        assert result["_opacity_shadow"][0]["tag"] == "solar"

    def test_multiple_shadows_accumulate(self):
        base = apply_shadow_channel({}, {"a": 1})
        result = apply_shadow_channel(base, {"b": 2})
        assert len(result["_opacity_shadow"]) == 2
