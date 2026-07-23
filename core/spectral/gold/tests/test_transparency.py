# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/gold/test_transparency.py
==============================================
Full coverage for all 5 GOLD transparency functions.
"""

import pytest

from core.spectral.gold.transparency import (
    classify_urgency,
    detect_aurum_state,
    emit_sentinel_alert,
    get_ui_state,
    is_gold_signal,
)


class TestDetectAurumState:
    def test_all_thresholds_met_returns_true(self):
        assert detect_aurum_state({"completion": 0.95, "incorruptibility": 0.85, "vitality": 0.70}) is True

    def test_exact_thresholds_returns_true(self):
        assert detect_aurum_state({"completion": 0.90, "incorruptibility": 0.80, "vitality": 0.60}) is True

    def test_low_vitality_returns_false(self):
        assert detect_aurum_state({"completion": 0.95, "incorruptibility": 0.85, "vitality": 0.40}) is False

    def test_low_completion_returns_false(self):
        assert detect_aurum_state({"completion": 0.70, "incorruptibility": 0.85, "vitality": 0.70}) is False

    def test_low_incorruptibility_returns_false(self):
        assert detect_aurum_state({"completion": 0.95, "incorruptibility": 0.60, "vitality": 0.70}) is False

    def test_empty_returns_false(self):
        assert detect_aurum_state({}) is False

    def test_none_returns_false(self):
        assert detect_aurum_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_aurum_state({"completion": 1.0}) is False


class TestEmitSentinelAlert:
    def test_level_1_returns_solar(self):
        alert = emit_sentinel_alert(1, "solar signal")
        assert alert["level"] == 1
        assert alert["label"] == "SOLAR"
        assert alert["tablet"] == "Solar Tablet"
        assert alert["layer"] == "transparency"

    def test_level_2_returns_deep_gold(self):
        assert emit_sentinel_alert(2, "test")["label"] == "DEEP_GOLD"

    def test_level_3_returns_ossification(self):
        assert emit_sentinel_alert(3, "test")["label"] == "OSSIFICATION"

    def test_below_1_clamped(self):
        assert emit_sentinel_alert(-1, "test")["level"] == 1

    def test_above_3_clamped(self):
        assert emit_sentinel_alert(99, "test")["level"] == 3

    def test_none_level_defaults_to_1(self):
        assert emit_sentinel_alert(None, "test")["level"] == 1

    def test_context_preserved(self):
        assert emit_sentinel_alert(1, "my context")["context"] == "my context"


class TestClassifyUrgency:
    def test_aurum_signal(self):
        assert classify_urgency({"aurum": True}) == "aurum"

    def test_ossification_signal(self):
        assert classify_urgency({"ossification": True}) == "ossification"

    def test_false_completion_signal(self):
        assert classify_urgency({"false_completion": True}) == "false_completion"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_aurum_priority_over_ossification(self):
        assert classify_urgency({"aurum": True, "ossification": True}) == "aurum"


class TestGetUiState:
    def test_aurum_activation(self):
        state = get_ui_state("aurum_activation")
        assert state["animation"] == "radiant"

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


class TestIsGoldSignal:
    def test_genuine_aurum_returns_true(self):
        assert is_gold_signal({"aurum": True}) is True

    def test_aurum_with_ossification_returns_false(self):
        assert is_gold_signal({"aurum": True, "ossification": True}) is False

    def test_aurum_with_false_completion_returns_false(self):
        assert is_gold_signal({"aurum": True, "false_completion": True}) is False

    def test_no_aurum_returns_false(self):
        assert is_gold_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_gold_signal({}) is False

    def test_none_returns_false(self):
        assert is_gold_signal(None) is False
