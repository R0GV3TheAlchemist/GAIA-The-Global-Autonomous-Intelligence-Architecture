# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
Tests for core/spectral/red/opacity.py
"""

from __future__ import annotations

import pytest

from core.spectral.red.opacity import (
    apply_shadow_channel,
    ares_athena_routing,
    nigredo_alert,
    phoenix_marker,
    red_lion_detection,
    wound_pattern_recognition,
)


# ---------------------------------------------------------------------------
# nigredo_alert — INVARIANT: interrupt_flag is ALWAYS False
# ---------------------------------------------------------------------------

class TestNigredoAlert:
    @pytest.mark.parametrize("signal", [
        {"nigredo": True},
        {"dissolution": True},
        {"prima_materia": True},
        {"nigredo": True, "dissolution": True},
        {"nigredo": False, "dissolution": False},
        {},
        None,
        {"nigredo": True, "interrupt_flag": True},   # caller cannot force True
        {"interrupt_flag": True, "dissolution": True},
        {"anything": "goes"},
    ])
    def test_interrupt_flag_invariant(self, signal):
        result = nigredo_alert(signal)
        assert result["interrupt_flag"] is False, (
            f"INVARIANT VIOLATED: interrupt_flag must never be True. signal={signal!r}"
        )

    def test_nigredo_active_when_flag_set(self):
        assert nigredo_alert({"nigredo": True})["nigredo_active"] is True

    def test_dissolution_active(self):
        assert nigredo_alert({"dissolution": True})["nigredo_active"] is True

    def test_prima_materia_active(self):
        assert nigredo_alert({"prima_materia": True})["nigredo_active"] is True

    def test_no_markers_inactive(self):
        assert nigredo_alert({"something_else": True})["nigredo_active"] is False

    def test_empty_signal_inactive(self):
        result = nigredo_alert({})
        assert result["nigredo_active"] is False
        assert result["interrupt_flag"] is False


# ---------------------------------------------------------------------------
# wound_pattern_recognition
# ---------------------------------------------------------------------------

class TestWoundPatternRecognition:
    def test_real_urgency_markers(self):
        result = wound_pattern_recognition(
            {"features": ["present_threat", "immediate_danger", "live_emergency"]},
            []
        )
        assert result["urgency_type"] == "real_urgency"

    def test_echo_urgency_markers(self):
        result = wound_pattern_recognition(
            {"features": ["historical_trigger", "wound_resonance"]},
            []
        )
        assert result["urgency_type"] == "echo_urgency"
        assert result["wound_echo"] is True

    def test_history_strengthens_echo(self):
        history = [
            {"features": ["historical_trigger"]},
            {"features": ["wound_resonance"]},
            {"features": ["historical_trigger"]},
        ]
        result = wound_pattern_recognition(
            {"features": ["present_threat"]},
            history
        )
        assert result["urgency_type"] == "echo_urgency"

    def test_explicit_metabolization_stage_respected(self):
        result = wound_pattern_recognition(
            {"features": ["wound_resonance"], "metabolization_stage": "integrating"},
            []
        )
        assert result["metabolization_stage"] == "integrating"

    def test_invalid_stage_inferred(self):
        result = wound_pattern_recognition(
            {"features": ["wound_resonance"], "metabolization_stage": "not_valid"},
            []
        )
        assert result["metabolization_stage"] == "metabolizing"

    def test_empty_signal(self):
        result = wound_pattern_recognition({}, [])
        assert result["urgency_type"] == "echo_urgency"
        assert result["wound_echo"] is False

    def test_none_signal(self):
        result = wound_pattern_recognition(None, [])
        assert result["urgency_type"] == "echo_urgency"


# ---------------------------------------------------------------------------
# red_lion_detection
# ---------------------------------------------------------------------------

class TestRedLionDetection:
    def test_explicit_force_level_high(self):
        result = red_lion_detection({"force_level": 0.9})
        assert result["red_lion_active"] is True
        assert result["transmutation_required"] is True

    def test_explicit_force_level_low(self):
        result = red_lion_detection({"force_level": 0.3})
        assert result["red_lion_active"] is True
        assert result["transmutation_required"] is False

    def test_force_level_zero(self):
        result = red_lion_detection({"force_level": 0.0})
        assert result["red_lion_active"] is False

    def test_force_level_clamped_above_one(self):
        result = red_lion_detection({"force_level": 99.0})
        assert result["force_level"] == 1.0

    def test_inferred_from_features(self):
        result = red_lion_detection(
            {"features": ["unbound_force", "directionless", "uncontrolled",
                          "destructive", "escalating"]}
        )
        assert result["red_lion_active"] is True

    def test_empty_signal(self):
        result = red_lion_detection({})
        assert result["red_lion_active"] is False
        assert result["force_level"] == 0.0

    def test_none_signal(self):
        result = red_lion_detection(None)
        assert result["red_lion_active"] is False


# ---------------------------------------------------------------------------
# phoenix_marker
# ---------------------------------------------------------------------------

class TestPhoenixMarker:
    def test_complete_cycle(self):
        history = [
            {"phase": "nigredo"},
            {"phase": "albedo"},
            {"phase": "rubedo"},
        ]
        result = phoenix_marker("entity", history)
        assert result["phoenix_complete"] is True
        assert result["cycle_count"] == 1
        assert result["integration_gain"] > 0

    def test_incomplete_cycle_no_rubedo(self):
        history = [{"phase": "nigredo"}, {"phase": "albedo"}]
        result = phoenix_marker("e", history)
        assert result["phoenix_complete"] is False
        assert result["cycle_count"] == 0

    def test_rubedo_without_nigredo_not_counted(self):
        history = [{"phase": "rubedo"}]
        result = phoenix_marker("e", history)
        assert result["cycle_count"] == 0

    def test_multiple_cycles(self):
        history = [
            {"phase": "nigredo"}, {"phase": "rubedo"},
            {"phase": "nigredo"}, {"phase": "rubedo"},
            {"phase": "nigredo"}, {"phase": "rubedo"},
        ]
        result = phoenix_marker("e", history)
        assert result["cycle_count"] == 3

    def test_integration_gain_bounded_to_one(self):
        history = []
        for _ in range(50):
            history += [{"phase": "nigredo"}, {"phase": "rubedo"}]
        result = phoenix_marker("e", history)
        assert result["integration_gain"] <= 1.0

    def test_empty_history(self):
        result = phoenix_marker("e", [])
        assert result["phoenix_complete"] is False
        assert result["cycle_count"] == 0
        assert result["integration_gain"] == 0.0


# ---------------------------------------------------------------------------
# ares_athena_routing
# ---------------------------------------------------------------------------

class TestAresAthenaRouting:
    def test_shadow_override_athena(self):
        assert ares_athena_routing({"_shadow_archetype": "athena"}) == "athena"

    def test_shadow_override_ares(self):
        assert ares_athena_routing({"_shadow_archetype": "ares"}) == "ares"

    def test_delegates_to_clarity_generative(self):
        assert ares_athena_routing({"completion": True}) == "athena"

    def test_delegates_to_clarity_reactive(self):
        assert ares_athena_routing({"reactive": True}) == "ares"

    def test_empty_signal(self):
        assert ares_athena_routing({}) == "ares"

    def test_none_signal(self):
        assert ares_athena_routing(None) == "ares"


# ---------------------------------------------------------------------------
# apply_shadow_channel — non-mutation invariant
# ---------------------------------------------------------------------------

class TestApplyShadowChannel:
    def test_shadow_key_appended(self):
        signal = {"living_flame": True}
        result = apply_shadow_channel(signal)
        assert "_opacity_shadow" in result

    def test_primary_signal_not_mutated(self):
        original_keys = {"living_flame", "completion"}
        signal = {"living_flame": True, "completion": True}
        apply_shadow_channel(signal)
        assert set(signal.keys()) == original_keys, (
            "apply_shadow_channel must not mutate the caller's signal dict"
        )

    def test_returns_new_dict(self):
        signal = {"living_flame": True}
        result = apply_shadow_channel(signal)
        assert result is not signal

    def test_shadow_contains_all_keys(self):
        result = apply_shadow_channel({"nigredo": True}, "entity", [], [])
        shadow = result["_opacity_shadow"]
        assert "nigredo" in shadow
        assert "wound_pattern" in shadow
        assert "red_lion" in shadow
        assert "phoenix" in shadow
        assert "ares_athena" in shadow

    def test_nigredo_in_shadow_respects_invariant(self):
        result = apply_shadow_channel({"nigredo": True, "interrupt_flag": True})
        assert result["_opacity_shadow"]["nigredo"]["interrupt_flag"] is False

    def test_empty_signal(self):
        result = apply_shadow_channel({})
        assert "_opacity_shadow" in result

    def test_none_history_defaults(self):
        result = apply_shadow_channel({"living_flame": True}, "e", None, None)
        assert "_opacity_shadow" in result

    @pytest.mark.parametrize("force_level", [0.0, 0.3, 0.7, 0.9, 1.0])
    def test_force_levels_propagate_correctly(self, force_level):
        result = apply_shadow_channel({"force_level": force_level})
        assert result["_opacity_shadow"]["red_lion"]["force_level"] == pytest.approx(
            max(0.0, min(1.0, force_level)), abs=1e-4
        )
