# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
import pytest
from core.spectral.yellow.transparency import (
    detect_xanthosis_state, emit_sentinel_alert, classify_urgency,
    get_ui_state, is_illumination_signal,
)
from core.spectral.yellow.constants import YELLOW_HEX, ALCHEMICAL_PHASE


class TestDetectXanthosisState:
    def test_phase_match(self):
        assert detect_xanthosis_state({"phase": ALCHEMICAL_PHASE}) is True

    def test_hex_match(self):
        assert detect_xanthosis_state({"hex": YELLOW_HEX["XANTHOSIS"]}) is True

    def test_wavelength_in_range(self):
        assert detect_xanthosis_state({"wavelength": 575}) is True

    def test_wavelength_out_of_range(self):
        assert detect_xanthosis_state({"wavelength": 700}) is False

    def test_non_dict(self):
        assert detect_xanthosis_state(None) is False


class TestEmitSentinelAlert:
    def test_interrupt_always_false(self):
        for lvl in (1, 2, 3):
            assert emit_sentinel_alert(lvl)["interrupt_flag"] is False

    def test_invalid_level_defaults_1(self):
        assert emit_sentinel_alert(99)["level"] == 1


class TestClassifyUrgency:
    def test_low(self): assert classify_urgency(0.1) == "low"
    def test_moderate(self): assert classify_urgency(0.5) == "moderate"
    def test_high(self): assert classify_urgency(0.9) == "high"


class TestGetUiState:
    def test_known(self):
        assert get_ui_state("xanthosis_activation")["hex"] == YELLOW_HEX["XANTHOSIS"]

    def test_unknown(self):
        assert get_ui_state("????") == {}


class TestIsIlluminationSignal:
    def test_amber_hex(self):
        assert is_illumination_signal({"hex": YELLOW_HEX["AMBER"]}) is True

    def test_completion_with_phase(self):
        assert is_illumination_signal({"completion": True, "phase": ALCHEMICAL_PHASE}) is True

    def test_no_signal(self):
        assert is_illumination_signal({"hex": "#000"}) is False
