"""
test_nigredo_gates_lux_features.py
Verifies that when GAIANRuntime detects NIGREDO stage,
LUX-gated features are stripped from the response pipeline.
Issue #439 — SIM acceptance criterion
"""

import pytest


NIGREDO_STAGE = {
    "name": "NIGREDO",
    "next_gate": "phi >= 0.25 + first_falsification",
}

ALBEDO_STAGE = {
    "name": "ALBEDO",
    "next_gate": "phi >= 0.85 + falsification_clean",
}

FULL_CAPABILITIES = {
    "spectral_field": "active",
    "avatar": "PLASMA",
    "encoding": "partial",
    "lux_features": "enabled",
}


def test_nigredo_strips_lux_features():
    """NIGREDO stage must strip LUX-gated features."""
    from src.gaian.runtime_types import enforce_capability_gates, is_lux_gated

    assert is_lux_gated(NIGREDO_STAGE) is True
    gated = enforce_capability_gates(NIGREDO_STAGE, FULL_CAPABILITIES)
    assert gated["spectral_field"] == "inactive"
    assert gated["lux_features"] == "stripped"
    assert gated["avatar"] == "SHADOW"


def test_albedo_does_not_strip_lux_features():
    """ALBEDO and above must NOT strip LUX-gated features."""
    from src.gaian.runtime_types import enforce_capability_gates, is_lux_gated

    assert is_lux_gated(ALBEDO_STAGE) is False
    gated = enforce_capability_gates(ALBEDO_STAGE, FULL_CAPABILITIES)
    assert gated["spectral_field"] == "active"
    assert gated["lux_features"] == "enabled"


def test_nigredo_runtime_result_marks_lux_gated_true():
    """RuntimeResult.lux_gated must be True when stage is NIGREDO."""
    from src.gaian.runtime_types import is_lux_gated

    assert is_lux_gated(NIGREDO_STAGE) is True


def test_albedo_runtime_result_marks_lux_gated_false():
    """RuntimeResult.lux_gated must be False when stage is ALBEDO or higher."""
    from src.gaian.runtime_types import is_lux_gated

    assert is_lux_gated(ALBEDO_STAGE) is False
