# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/white/test_transparency.py
===============================================
Full coverage for all 5 WHITE transparency functions.
"""

import pytest

from core.spectral.white.transparency import (
    classify_urgency,
    detect_albedo_state,
    emit_sentinel_alert,
    get_ui_state,
    is_luna_signal,
)


class TestDetectAlbedoState:
    def test_all_thresholds_met_returns_true(self):
        assert detect_albedo_state({"purification": 0.85, "reflection": 0.75, "texture": 0.60}) is True

    def test_exact_thresholds_returns_true(self):
        assert detect_albedo_state({"purification": 0.80, "reflection": 0.70, "texture": 0.50}) is True

    def test_low_texture_returns_false(self):
        assert detect_albedo_state({"purification": 0.85, "reflection": 0.75, "texture": 0.30}) is False

    def test_low_purification_returns_false(self):
        assert detect_albedo_state({"purification": 0.60, "reflection": 0.75, "texture": 0.60}) is False

    def test_low_reflection_returns_false(self):
        assert detect_albedo_state({"purification": 0.85, "reflection": 0.50, "texture": 0.60}) is False

    def test_empty_returns_false(self):
        assert detect_albedo_state({}) is False

    def test_none_returns_false(self):
        assert detect_albedo_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_albedo_state({"purification": 1.0}) is False


class TestEmitSentinelAlert:
    def test_level_1_returns_lunar(self):
        alert = emit_sentinel_alert(1, "lunar signal")
        assert alert["level"] == 1
        assert alert["label"] == "LUNAR"
        assert alert["tablet"] == "Lunar Tablet"
        assert alert["layer"] == "transparency"

    def test_level_2_returns_pale(self):
        assert emit_sentinel_alert(2, "test")["label"] == "PALE"

    def test_level_3_returns_bleaching(self):
        assert emit_sentinel_alert(3, "test")["label"] == "BLEACHING"

    def test_below_1_clamped(self):
        assert emit_sentinel_alert(-1, "test")["level"] == 1

    def test_above_3_clamped(self):
        assert emit_sentinel_alert(99, "test")["level"] == 3

    def test_none_level_defaults_to_1(self):
        assert emit_sentinel_alert(None, "test")["level"] == 1

    def test_context_preserved(self):
        assert emit_sentinel_alert(1, "my context")["context"] == "my context"


class TestClassifyUrgency:
    def test_albedo_signal(self):
        assert classify_urgency({"albedo": True}) == "albedo"

    def test_bleaching_signal(self):
        assert classify_urgency({"bleaching": True}) == "bleaching"

    def test_overexposed_signal(self):
        assert classify_urgency({"overexposed": True}) == "overexposed"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_albedo_priority_over_bleaching(self):
        assert classify_urgency({"albedo": True, "bleaching": True}) == "albedo"


class TestGetUiState:
    def test_albedo_activation(self):
        assert get_ui_state("albedo_activation")["animation"] == "reflecting"

    def test_sentinel_alert(self):
        assert get_ui_state("sentinel_alert")["label"] == "SENTINEL Alert"

    def test_returns_copy_not_reference(self):
        s1 = get_ui_state("sentinel_alert")
        s2 = get_ui_state("sentinel_alert")
        s1["hex"] = "mutated"
        assert s2["hex"] != "mutated"

    def test_unknown_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state("nonexistent")

    def test_none_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state(None)


class TestIsLunaSignal:
    def test_genuine_albedo_returns_true(self):
        assert is_luna_signal({"albedo": True}) is True

    def test_albedo_with_bleaching_returns_false(self):
        assert is_luna_signal({"albedo": True, "bleaching": True}) is False

    def test_albedo_with_overexposed_returns_false(self):
        assert is_luna_signal({"albedo": True, "overexposed": True}) is False

    def test_no_albedo_returns_false(self):
        assert is_luna_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_luna_signal({}) is False

    def test_none_returns_false(self):
        assert is_luna_signal(None) is False
