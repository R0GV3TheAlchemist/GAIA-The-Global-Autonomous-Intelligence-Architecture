# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
"""
Tests for core/spectral/orange/transparency.py
"""
import pytest
from core.spectral.orange.transparency import (
    detect_citrinitas_state,
    emit_sentinel_alert,
    classify_urgency,
    get_ui_state,
    is_solar_completion_signal,
)
from core.spectral.orange.constants import ORANGE_HEX, ALCHEMICAL_PHASE


class TestDetectCitrinitasState:
    def test_phase_match(self):
        assert detect_citrinitas_state({"phase": ALCHEMICAL_PHASE}) is True

    def test_phase_case_insensitive(self):
        assert detect_citrinitas_state({"phase": "citrinitas"}) is True

    def test_hex_match(self):
        assert detect_citrinitas_state({"hex": ORANGE_HEX["CITRINITAS"]}) is True

    def test_wavelength_in_range(self):
        assert detect_citrinitas_state({"wavelength": 605}) is True

    def test_wavelength_edge_low(self):
        assert detect_citrinitas_state({"wavelength": 590}) is True

    def test_wavelength_edge_high(self):
        assert detect_citrinitas_state({"wavelength": 620}) is True

    def test_wavelength_out_of_range(self):
        assert detect_citrinitas_state({"wavelength": 700}) is False

    def test_non_dict_returns_false(self):
        assert detect_citrinitas_state("not a dict") is False  # type: ignore


class TestEmitSentinelAlert:
    def test_level_1(self):
        alert = emit_sentinel_alert(1, "test context")
        assert alert["level"] == 1
        assert alert["interrupt_flag"] is False
        assert alert["module"] == "spectral.orange"

    def test_invalid_level_defaults_to_1(self):
        alert = emit_sentinel_alert(99)
        assert alert["level"] == 1

    def test_interrupt_flag_always_false(self):
        for level in (1, 2, 3):
            assert emit_sentinel_alert(level)["interrupt_flag"] is False


class TestClassifyUrgency:
    def test_low(self):
        assert classify_urgency(0.1) == "low"

    def test_moderate(self):
        assert classify_urgency(0.5) == "moderate"

    def test_high(self):
        assert classify_urgency(0.9) == "high"

    def test_boundary_low_moderate(self):
        assert classify_urgency(0.33) == "moderate"

    def test_boundary_moderate_high(self):
        assert classify_urgency(0.66) == "high"


class TestGetUiState:
    def test_known_state(self):
        state = get_ui_state("citrinitas_activation")
        assert state["hex"] == ORANGE_HEX["CITRINITAS"]

    def test_unknown_state_returns_empty(self):
        assert get_ui_state("nonexistent") == {}


class TestIsSolarCompletionSignal:
    def test_amber_hex_is_completion(self):
        assert is_solar_completion_signal({"hex": ORANGE_HEX["AMBER"]}) is True

    def test_completion_flag_with_citrinitas_phase(self):
        signal = {"completion": True, "phase": ALCHEMICAL_PHASE}
        assert is_solar_completion_signal(signal) is True

    def test_no_completion(self):
        assert is_solar_completion_signal({"hex": "#000000"}) is False

    def test_non_dict(self):
        assert is_solar_completion_signal(None) is False  # type: ignore
