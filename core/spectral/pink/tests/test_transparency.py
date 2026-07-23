# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/pink/test_transparency.py
==============================================
Full coverage for all 5 PINK transparency functions.
"""

import pytest

from core.spectral.pink.transparency import (
    classify_urgency,
    detect_rosa_mystica_state,
    emit_sentinel_alert,
    get_ui_state,
    is_rose_signal,
)


# ---------------------------------------------------------------------------
# detect_rosa_mystica_state
# ---------------------------------------------------------------------------

class TestDetectRosaMysticaState:
    def test_all_thresholds_met_returns_true(self):
        metrics = {"tenderness": 0.80, "groundedness": 0.70, "openness": 0.75}
        assert detect_rosa_mystica_state(metrics) is True

    def test_exact_thresholds_returns_true(self):
        metrics = {"tenderness": 0.75, "groundedness": 0.65, "openness": 0.70}
        assert detect_rosa_mystica_state(metrics) is True

    def test_low_groundedness_returns_false(self):
        # groundedness below 0.65 → false albedo risk
        metrics = {"tenderness": 0.80, "groundedness": 0.50, "openness": 0.75}
        assert detect_rosa_mystica_state(metrics) is False

    def test_low_tenderness_returns_false(self):
        metrics = {"tenderness": 0.60, "groundedness": 0.70, "openness": 0.75}
        assert detect_rosa_mystica_state(metrics) is False

    def test_low_openness_returns_false(self):
        metrics = {"tenderness": 0.80, "groundedness": 0.70, "openness": 0.60}
        assert detect_rosa_mystica_state(metrics) is False

    def test_empty_dict_returns_false(self):
        assert detect_rosa_mystica_state({}) is False

    def test_none_returns_false(self):
        assert detect_rosa_mystica_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_rosa_mystica_state({"tenderness": 0.90}) is False


# ---------------------------------------------------------------------------
# emit_sentinel_alert
# ---------------------------------------------------------------------------

class TestEmitSentinelAlert:
    def test_level_1_returns_soft_albedo(self):
        alert = emit_sentinel_alert(1, "low tenderness anomaly")
        assert alert["level"] == 1
        assert alert["label"] == "SOFT_ALBEDO"
        assert alert["tablet"] == "Rose Tablet"
        assert alert["layer"] == "transparency"

    def test_level_2_returns_deep_rose(self):
        alert = emit_sentinel_alert(2, "false albedo detected")
        assert alert["level"] == 2
        assert alert["label"] == "DEEP_ROSE"

    def test_level_3_returns_false_albedo(self):
        alert = emit_sentinel_alert(3, "critical rose denial")
        assert alert["level"] == 3
        assert alert["label"] == "FALSE_ALBEDO"

    def test_level_below_1_clamped_to_1(self):
        alert = emit_sentinel_alert(-5, "test")
        assert alert["level"] == 1

    def test_level_above_3_clamped_to_3(self):
        alert = emit_sentinel_alert(99, "test")
        assert alert["level"] == 3

    def test_context_preserved(self):
        alert = emit_sentinel_alert(1, "my context string")
        assert alert["context"] == "my context string"

    def test_none_level_defaults_to_1(self):
        alert = emit_sentinel_alert(None, "test")
        assert alert["level"] == 1


# ---------------------------------------------------------------------------
# classify_urgency
# ---------------------------------------------------------------------------

class TestClassifyUrgency:
    def test_rosa_mystica_signal(self):
        assert classify_urgency({"rosa_mystica": True}) == "rosa_mystica"

    def test_false_albedo_signal(self):
        assert classify_urgency({"false_albedo": True}) == "false_albedo"

    def test_rose_denial_signal(self):
        assert classify_urgency({"rose_denial": True}) == "rose_denial"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_rosa_mystica_takes_priority_over_false_albedo(self):
        # rosa_mystica has highest priority
        signal = {"rosa_mystica": True, "false_albedo": True}
        assert classify_urgency(signal) == "rosa_mystica"


# ---------------------------------------------------------------------------
# get_ui_state
# ---------------------------------------------------------------------------

class TestGetUiState:
    def test_rosa_mystica_activation(self):
        state = get_ui_state("rosa_mystica_activation")
        assert "hex" in state
        assert state["animation"] == "pulsing"

    def test_sentinel_alert(self):
        state = get_ui_state("sentinel_alert")
        assert state["label"] == "SENTINEL Alert"

    def test_false_albedo_state(self):
        state = get_ui_state("false_albedo_state")
        assert state["animation"] == "static"

    def test_returns_copy_not_reference(self):
        s1 = get_ui_state("sentinel_alert")
        s2 = get_ui_state("sentinel_alert")
        s1["hex"] = "mutated"
        assert s2["hex"] != "mutated"

    def test_unknown_state_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state("nonexistent_state")

    def test_none_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state(None)


# ---------------------------------------------------------------------------
# is_rose_signal
# ---------------------------------------------------------------------------

class TestIsRoseSignal:
    def test_genuine_rosa_mystica_returns_true(self):
        assert is_rose_signal({"rosa_mystica": True}) is True

    def test_rosa_mystica_with_sentinel_returns_false(self):
        assert is_rose_signal({"rosa_mystica": True, "sentinel": True}) is False

    def test_rosa_mystica_with_false_albedo_returns_false(self):
        assert is_rose_signal({"rosa_mystica": True, "false_albedo": True}) is False

    def test_no_rosa_mystica_returns_false(self):
        assert is_rose_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_rose_signal({}) is False

    def test_none_returns_false(self):
        assert is_rose_signal(None) is False
