# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/brown/test_transparency.py
===============================================
Full coverage for all 5 BROWN transparency functions.
"""

import pytest

from core.spectral.brown.transparency import (
    classify_urgency,
    detect_humus_state,
    emit_sentinel_alert,
    get_ui_state,
    is_earth_signal,
)


class TestDetectHumusState:
    def test_all_thresholds_met_returns_true(self):
        assert detect_humus_state({
            "fertility": 0.80, "groundedness": 0.75, "porosity": 0.60
        }) is True

    def test_exact_thresholds_returns_true(self):
        assert detect_humus_state({
            "fertility": 0.75, "groundedness": 0.70, "porosity": 0.55
        }) is True

    def test_low_porosity_returns_false(self):
        assert detect_humus_state({
            "fertility": 0.80, "groundedness": 0.75, "porosity": 0.30
        }) is False

    def test_low_fertility_returns_false(self):
        assert detect_humus_state({
            "fertility": 0.50, "groundedness": 0.75, "porosity": 0.60
        }) is False

    def test_low_groundedness_returns_false(self):
        assert detect_humus_state({
            "fertility": 0.80, "groundedness": 0.50, "porosity": 0.60
        }) is False

    def test_empty_returns_false(self):
        assert detect_humus_state({}) is False

    def test_none_returns_false(self):
        assert detect_humus_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_humus_state({"fertility": 1.0}) is False


class TestEmitSentinelAlert:
    def test_level_1_returns_loam(self):
        alert = emit_sentinel_alert(1, "loam signal")
        assert alert["level"] == 1
        assert alert["label"] == "LOAM"
        assert alert["tablet"] == "Earth Tablet"
        assert alert["layer"] == "transparency"

    def test_level_2_returns_clay(self):
        assert emit_sentinel_alert(2, "test")["label"] == "CLAY"

    def test_level_3_returns_compaction(self):
        assert emit_sentinel_alert(3, "test")["label"] == "COMPACTION"

    def test_below_1_clamped(self):
        assert emit_sentinel_alert(-1, "test")["level"] == 1

    def test_above_3_clamped(self):
        assert emit_sentinel_alert(99, "test")["level"] == 3

    def test_none_level_defaults_to_1(self):
        assert emit_sentinel_alert(None, "test")["level"] == 1

    def test_context_preserved(self):
        assert emit_sentinel_alert(1, "my context")["context"] == "my context"


class TestClassifyUrgency:
    def test_humus_signal(self):
        assert classify_urgency({"humus": True}) == "humus"

    def test_compaction_signal(self):
        assert classify_urgency({"compaction": True}) == "compaction"

    def test_sediment_signal(self):
        assert classify_urgency({"sediment": True}) == "sediment"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_humus_priority_over_compaction(self):
        assert classify_urgency({"humus": True, "compaction": True}) == "humus"


class TestGetUiState:
    def test_humus_activation(self):
        assert get_ui_state("humus_activation")["animation"] == "grounding"

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


class TestIsEarthSignal:
    def test_genuine_humus_returns_true(self):
        assert is_earth_signal({"humus": True}) is True

    def test_with_compaction_returns_false(self):
        assert is_earth_signal({"humus": True, "compaction": True}) is False

    def test_with_sediment_returns_false(self):
        assert is_earth_signal({"humus": True, "sediment": True}) is False

    def test_no_humus_returns_false(self):
        assert is_earth_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_earth_signal({}) is False

    def test_none_returns_false(self):
        assert is_earth_signal(None) is False
