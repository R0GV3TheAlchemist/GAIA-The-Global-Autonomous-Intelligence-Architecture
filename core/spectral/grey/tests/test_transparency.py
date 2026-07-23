# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/grey/test_transparency.py
==============================================
Full coverage for all 5 GREY transparency functions.
"""

import pytest

from core.spectral.grey.transparency import (
    classify_urgency,
    detect_cauda_pavonis_state,
    emit_sentinel_alert,
    get_ui_state,
    is_threshold_signal,
)


class TestDetectCaudaPavonisState:
    def test_all_thresholds_met_returns_true(self):
        assert detect_cauda_pavonis_state({
            "transition_momentum": 0.75, "iridescence": 0.65, "directionality": 0.55
        }) is True

    def test_exact_thresholds_returns_true(self):
        assert detect_cauda_pavonis_state({
            "transition_momentum": 0.70, "iridescence": 0.60, "directionality": 0.50
        }) is True

    def test_low_directionality_returns_false(self):
        assert detect_cauda_pavonis_state({
            "transition_momentum": 0.75, "iridescence": 0.65, "directionality": 0.30
        }) is False

    def test_low_transition_momentum_returns_false(self):
        assert detect_cauda_pavonis_state({
            "transition_momentum": 0.50, "iridescence": 0.65, "directionality": 0.55
        }) is False

    def test_low_iridescence_returns_false(self):
        assert detect_cauda_pavonis_state({
            "transition_momentum": 0.75, "iridescence": 0.40, "directionality": 0.55
        }) is False

    def test_empty_returns_false(self):
        assert detect_cauda_pavonis_state({}) is False

    def test_none_returns_false(self):
        assert detect_cauda_pavonis_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_cauda_pavonis_state({"transition_momentum": 1.0}) is False


class TestEmitSentinelAlert:
    def test_level_1_returns_twilight(self):
        alert = emit_sentinel_alert(1, "twilight signal")
        assert alert["level"] == 1
        assert alert["label"] == "TWILIGHT"
        assert alert["tablet"] == "Threshold Tablet"
        assert alert["layer"] == "transparency"

    def test_level_2_returns_dusk(self):
        assert emit_sentinel_alert(2, "test")["label"] == "DUSK"

    def test_level_3_returns_liminal(self):
        assert emit_sentinel_alert(3, "test")["label"] == "LIMINAL"

    def test_below_1_clamped(self):
        assert emit_sentinel_alert(-1, "test")["level"] == 1

    def test_above_3_clamped(self):
        assert emit_sentinel_alert(99, "test")["level"] == 3

    def test_none_level_defaults_to_1(self):
        assert emit_sentinel_alert(None, "test")["level"] == 1

    def test_context_preserved(self):
        assert emit_sentinel_alert(1, "my context")["context"] == "my context"


class TestClassifyUrgency:
    def test_cauda_pavonis_signal(self):
        assert classify_urgency({"cauda_pavonis": True}) == "cauda_pavonis"

    def test_permanent_threshold_signal(self):
        assert classify_urgency({"permanent_threshold": True}) == "permanent_threshold"

    def test_twilight_signal(self):
        assert classify_urgency({"twilight": True}) == "twilight"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_cauda_pavonis_priority_over_permanent_threshold(self):
        assert classify_urgency({"cauda_pavonis": True, "permanent_threshold": True}) == "cauda_pavonis"


class TestGetUiState:
    def test_cauda_pavonis_activation(self):
        assert get_ui_state("cauda_pavonis_activation")["animation"] == "iridescent"

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


class TestIsThresholdSignal:
    def test_genuine_cauda_pavonis_returns_true(self):
        assert is_threshold_signal({"cauda_pavonis": True}) is True

    def test_with_permanent_threshold_returns_false(self):
        assert is_threshold_signal({"cauda_pavonis": True, "permanent_threshold": True}) is False

    def test_with_twilight_returns_false(self):
        assert is_threshold_signal({"cauda_pavonis": True, "twilight": True}) is False

    def test_no_cauda_pavonis_returns_false(self):
        assert is_threshold_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_threshold_signal({}) is False

    def test_none_returns_false(self):
        assert is_threshold_signal(None) is False
