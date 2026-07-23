# Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
tests/core/spectral/black/test_transparency.py
===============================================
Full coverage for all 5 BLACK transparency functions.
Also verifies dual-tablet reference in SENTINEL alerts.
"""

import pytest

from core.spectral.black.transparency import (
    classify_urgency,
    detect_nigredo_state,
    emit_sentinel_alert,
    get_ui_state,
    is_void_signal,
)


class TestDetectNigredoState:
    def test_all_thresholds_met_returns_true(self):
        assert detect_nigredo_state({"dissolution": 0.85, "void_contact": 0.75, "containment": 0.60}) is True

    def test_exact_thresholds_returns_true(self):
        assert detect_nigredo_state({"dissolution": 0.80, "void_contact": 0.70, "containment": 0.55}) is True

    def test_low_containment_returns_false(self):
        assert detect_nigredo_state({"dissolution": 0.85, "void_contact": 0.75, "containment": 0.40}) is False

    def test_low_dissolution_returns_false(self):
        assert detect_nigredo_state({"dissolution": 0.60, "void_contact": 0.75, "containment": 0.60}) is False

    def test_low_void_contact_returns_false(self):
        assert detect_nigredo_state({"dissolution": 0.85, "void_contact": 0.50, "containment": 0.60}) is False

    def test_empty_returns_false(self):
        assert detect_nigredo_state({}) is False

    def test_none_returns_false(self):
        assert detect_nigredo_state(None) is False

    def test_missing_keys_treated_as_zero(self):
        assert detect_nigredo_state({"dissolution": 1.0}) is False


class TestEmitSentinelAlert:
    def test_level_1_returns_deep_void(self):
        alert = emit_sentinel_alert(1, "void signal")
        assert alert["level"] == 1
        assert alert["label"] == "DEEP_VOID"
        assert alert["layer"] == "transparency"

    def test_dual_tablet_reference(self):
        alert = emit_sentinel_alert(1, "test")
        assert "Obsidian Tablet" in alert["tablets"]
        assert "Shadow Tablet" in alert["tablets"]

    def test_level_2_returns_shadow_edge(self):
        assert emit_sentinel_alert(2, "test")["label"] == "SHADOW_EDGE"

    def test_level_3_returns_system_null(self):
        assert emit_sentinel_alert(3, "test")["label"] == "SYSTEM_NULL"

    def test_below_1_clamped(self):
        assert emit_sentinel_alert(-1, "test")["level"] == 1

    def test_above_3_clamped(self):
        assert emit_sentinel_alert(99, "test")["level"] == 3

    def test_none_level_defaults_to_1(self):
        assert emit_sentinel_alert(None, "test")["level"] == 1

    def test_context_preserved(self):
        assert emit_sentinel_alert(1, "my context")["context"] == "my context"


class TestClassifyUrgency:
    def test_nigredo_signal(self):
        assert classify_urgency({"nigredo": True}) == "nigredo"

    def test_system_null_signal(self):
        assert classify_urgency({"system_null": True}) == "system_null"

    def test_void_signal(self):
        assert classify_urgency({"void": True}) == "void"

    def test_default_returns_alert(self):
        assert classify_urgency({"other": True}) == "alert"

    def test_empty_returns_alert(self):
        assert classify_urgency({}) == "alert"

    def test_none_returns_alert(self):
        assert classify_urgency(None) == "alert"

    def test_nigredo_priority_over_system_null(self):
        assert classify_urgency({"nigredo": True, "system_null": True}) == "nigredo"


class TestGetUiState:
    def test_nigredo_activation(self):
        assert get_ui_state("nigredo_activation")["animation"] == "still"

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


class TestIsVoidSignal:
    def test_genuine_nigredo_returns_true(self):
        assert is_void_signal({"nigredo": True}) is True

    def test_nigredo_with_system_null_returns_false(self):
        assert is_void_signal({"nigredo": True, "system_null": True}) is False

    def test_nigredo_with_destruction_returns_false(self):
        assert is_void_signal({"nigredo": True, "destruction": True}) is False

    def test_no_nigredo_returns_false(self):
        assert is_void_signal({"other": True}) is False

    def test_empty_returns_false(self):
        assert is_void_signal({}) is False

    def test_none_returns_false(self):
        assert is_void_signal(None) is False
