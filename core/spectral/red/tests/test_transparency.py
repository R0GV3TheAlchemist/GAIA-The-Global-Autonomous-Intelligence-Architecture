# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
Tests for core/spectral/red/transparency.py
"""

from __future__ import annotations

import pytest

from core.spectral.red.transparency import (
    classify_urgency,
    detect_rubedo_state,
    emit_sentinel_alert,
    get_ui_state,
    is_completion_signal,
)


# ---------------------------------------------------------------------------
# detect_rubedo_state
# ---------------------------------------------------------------------------

class TestDetectRubedoState:
    def test_all_thresholds_met(self):
        assert detect_rubedo_state(
            {"coherence": 0.90, "integration": 0.85, "actualization": 0.80}
        ) is True

    def test_coherence_below_threshold(self):
        assert detect_rubedo_state(
            {"coherence": 0.80, "integration": 0.85, "actualization": 0.80}
        ) is False

    def test_integration_below_threshold(self):
        assert detect_rubedo_state(
            {"coherence": 0.90, "integration": 0.75, "actualization": 0.80}
        ) is False

    def test_actualization_below_threshold(self):
        assert detect_rubedo_state(
            {"coherence": 0.90, "integration": 0.85, "actualization": 0.74}
        ) is False

    def test_exact_thresholds(self):
        assert detect_rubedo_state(
            {"coherence": 0.85, "integration": 0.80, "actualization": 0.75}
        ) is True

    def test_empty_dict(self):
        assert detect_rubedo_state({}) is False

    def test_none_input(self):
        assert detect_rubedo_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_rubedo_state({"coherence": 0.99}) is False


# ---------------------------------------------------------------------------
# emit_sentinel_alert
# ---------------------------------------------------------------------------

class TestEmitSentinelAlert:
    def test_level_1_alert(self):
        result = emit_sentinel_alert(1, "test context")
        assert result["level"] == 1
        assert result["label"] == "ALERT"
        assert result["layer"] == "transparency"
        assert result["tablet"] == "Ruby Tablet"
        assert result["context"] == "test context"

    def test_level_2_danger(self):
        result = emit_sentinel_alert(2, "boundary violation")
        assert result["level"] == 2
        assert result["label"] == "DANGER"

    def test_level_3_scarlet(self):
        result = emit_sentinel_alert(3, "critical")
        assert result["level"] == 3
        assert result["label"] == "SCARLET"

    def test_level_below_1_clamped(self):
        result = emit_sentinel_alert(0, "low")
        assert result["level"] == 1

    def test_level_above_3_clamped(self):
        result = emit_sentinel_alert(99, "overflow")
        assert result["level"] == 3

    def test_hex_present(self):
        result = emit_sentinel_alert(1, "x")
        assert result["hex"].startswith("#")


# ---------------------------------------------------------------------------
# classify_urgency
# ---------------------------------------------------------------------------

class TestClassifyUrgency:
    def test_living_flame_priority(self):
        assert classify_urgency({"living_flame": True, "completion": True}) == "living_flame"

    def test_completion_over_error(self):
        assert classify_urgency({"completion": True, "error": True}) == "completion"

    def test_error_flag(self):
        assert classify_urgency({"error": True}) == "error"

    def test_error_code_flag(self):
        assert classify_urgency({"error_code": "E001"}) == "error"

    def test_default_alert(self):
        assert classify_urgency({"some_other_key": True}) == "alert"

    def test_empty_signal(self):
        assert classify_urgency({}) == "alert"

    def test_none_signal(self):
        assert classify_urgency(None) == "alert"


# ---------------------------------------------------------------------------
# get_ui_state
# ---------------------------------------------------------------------------

class TestGetUiState:
    def test_rubedo_activation(self):
        state = get_ui_state("rubedo_activation")
        assert state["hex"] == "#CC2200"
        assert state["animation"] == "pulsing"

    def test_sentinel_alert(self):
        state = get_ui_state("sentinel_alert")
        assert state["animation"] == "solid"

    def test_completion_signal(self):
        state = get_ui_state("completion_signal")
        assert state["hex"] == "#DC143C"

    def test_error_state(self):
        state = get_ui_state("error_state")
        assert state["hex"] == "#FF3333"

    def test_living_flame_mode(self):
        state = get_ui_state("living_flame_mode")
        assert state["animation"] == "animated"

    def test_returns_copy_not_reference(self):
        s1 = get_ui_state("rubedo_activation")
        s2 = get_ui_state("rubedo_activation")
        s1["hex"] = "#000000"
        assert s2["hex"] == "#CC2200"

    def test_unknown_state_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state("nonexistent_state")

    def test_empty_string_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state("")


# ---------------------------------------------------------------------------
# is_completion_signal
# ---------------------------------------------------------------------------

class TestIsCompletionSignal:
    def test_pure_completion(self):
        assert is_completion_signal({"completion": True}) is True

    def test_completion_plus_sentinel_is_not_completion(self):
        assert is_completion_signal({"completion": True, "sentinel": True}) is False

    def test_completion_plus_error_is_not_completion(self):
        assert is_completion_signal({"completion": True, "error": True}) is False

    def test_no_completion_flag(self):
        assert is_completion_signal({"sentinel": True}) is False

    def test_empty_signal(self):
        assert is_completion_signal({}) is False

    def test_none_signal(self):
        assert is_completion_signal(None) is False
