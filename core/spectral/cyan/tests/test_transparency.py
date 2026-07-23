# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/cyan/test_transparency.py
==============================================
Full coverage for all 5 CYAN transparency functions.
"""

import pytest

from core.spectral.cyan.transparency import (
    classify_urgency,
    detect_solutio_state,
    emit_sentinel_alert,
    get_ui_state,
    is_aqua_signal,
)


class TestDetectSolutioState:
    def test_all_thresholds_met_returns_true(self):
        metrics = {"dissolution": 0.80, "flow": 0.75, "reformation": 0.60}
        assert detect_solutio_state(metrics) is True

    def test_exact_thresholds_returns_true(self):
        metrics = {"dissolution": 0.75, "flow": 0.70, "reformation": 0.55}
        assert detect_solutio_state(metrics) is True

    def test_low_reformation_returns_false(self):
        metrics = {"dissolution": 0.80, "flow": 0.75, "reformation": 0.40}
        assert detect_solutio_state(metrics) is False

    def test_low_dissolution_returns_false(self):
        metrics = {"dissolution": 0.60, "flow": 0.75, "reformation": 0.60}
        assert detect_solutio_state(metrics) is False

    def test_low_flow_returns_false(self):
        metrics = {"dissolution": 0.80, "flow": 0.50, "reformation": 0.60}
        assert detect_solutio_state(metrics) is False

    def test_empty_returns_false(self):
        assert detect_solutio_state({}) is False

    def test_none_returns_false(self):
        assert detect_solutio_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_solutio_state({"dissolution": 0.90}) is False


class TestEmitSentinelAlert:
    def test_level_1_returns_aqua_vitae(self):
        alert = emit_sentinel_alert(1, "flow anomaly")
        assert alert["level"] == 1
        assert alert["label"] == "AQUA_VITAE"
        assert alert["tablet"] == "Aqua Tablet"
        assert alert["layer"] == "transparency"

    def test_level_2_returns_aquamarine(self):
        alert = emit_sentinel_alert(2, "approaching flood")
        assert alert["label"] == "AQUAMARINE"

    def test_level_3_returns_flood(self):
        alert = emit_sentinel_alert(3, "dissolution critical")
        assert alert["label"] == "FLOOD"

    def test_level_below_1_clamped_to_1(self):
        assert emit_sentinel_alert(-1, "test")["level"] == 1

    def test_level_above_3_clamped_to_3(self):
        assert emit_sentinel_alert(99, "test")["level"] == 3

    def test_none_level_defaults_to_1(self):
        assert emit_sentinel_alert(None, "test")["level"] == 1

    def test_context_preserved(self):
        assert emit_sentinel_alert(1, "my context")["context"] == "my context"


class TestClassifyUrgency:
    def test_solutio_signal(self):
        assert classify_urgency({"solutio": True}) == "solutio"

    def test_flood_signal(self):
        assert classify_urgency({"flood": True}) == "flood"

    def test_akashic_overload_signal(self):
        assert classify_urgency({"akashic_overload": True}) == "akashic_overload"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_solutio_priority_over_flood(self):
        assert classify_urgency({"solutio": True, "flood": True}) == "solutio"


class TestGetUiState:
    def test_solutio_activation(self):
        state = get_ui_state("solutio_activation")
        assert state["animation"] == "flowing"

    def test_sentinel_alert(self):
        state = get_ui_state("sentinel_alert")
        assert state["label"] == "SENTINEL Alert"

    def test_returns_copy_not_reference(self):
        s1 = get_ui_state("sentinel_alert")
        s2 = get_ui_state("sentinel_alert")
        s1["hex"] = "mutated"
        assert s2["hex"] != "mutated"

    def test_unknown_state_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state("nonexistent")

    def test_none_raises_key_error(self):
        with pytest.raises(KeyError):
            get_ui_state(None)


class TestIsAquaSignal:
    def test_genuine_solutio_returns_true(self):
        assert is_aqua_signal({"solutio": True}) is True

    def test_solutio_with_flood_returns_false(self):
        assert is_aqua_signal({"solutio": True, "flood": True}) is False

    def test_solutio_with_akashic_overload_returns_false(self):
        assert is_aqua_signal({"solutio": True, "akashic_overload": True}) is False

    def test_no_solutio_returns_false(self):
        assert is_aqua_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_aqua_signal({}) is False

    def test_none_returns_false(self):
        assert is_aqua_signal(None) is False
