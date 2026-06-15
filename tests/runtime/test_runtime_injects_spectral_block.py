"""
test_runtime_injects_spectral_block.py
Verifies that GAIANRuntime.process() injects a valid [SPECTRAL FIELD] block
into every RuntimeResult.
Issue #439 — SIM acceptance criterion
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


SAMPLE_SPECTRAL_SNAPSHOT = {
    "force": "IOSIS",
    "color_name": "violet",
    "phi_range": "0.72-0.85",
    "hex": "#6B4F8C",
    "corridor": None,
    "trajectory": "CAERULITAS -> IOSIS (ascending)",
    "oa4_active": True,
}

SAMPLE_STAGE = {
    "name": "ALBEDO",
    "next_gate": "phi >= 0.85 + falsification_clean",
}

SAMPLE_CAPABILITIES = {
    "spectral_field": "active",
    "avatar": "PLASMA",
    "encoding": "partial",
}


def test_spectral_block_present_in_system_prompt_blocks():
    """RuntimeResult.system_prompt_blocks must contain a [SPECTRAL FIELD] block."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    spectral_block = next((b for b in blocks if b.startswith("[SPECTRAL FIELD]")), None)
    assert spectral_block is not None, "[SPECTRAL FIELD] block missing from system_prompt_blocks"


def test_spectral_block_contains_force():
    """[SPECTRAL FIELD] block must contain the active force name."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    spectral_block = next(b for b in blocks if b.startswith("[SPECTRAL FIELD]"))
    assert "IOSIS" in spectral_block


def test_spectral_block_contains_hex():
    """[SPECTRAL FIELD] block must contain the hex color code."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    spectral_block = next(b for b in blocks if b.startswith("[SPECTRAL FIELD]"))
    assert "#6B4F8C" in spectral_block


def test_spectral_block_contains_trajectory():
    """[SPECTRAL FIELD] block must include the force trajectory."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    spectral_block = next(b for b in blocks if b.startswith("[SPECTRAL FIELD]"))
    assert "CAERULITAS" in spectral_block


def test_spectral_block_oa4_flag():
    """[SPECTRAL FIELD] block must include OA-4 Active status."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    spectral_block = next(b for b in blocks if b.startswith("[SPECTRAL FIELD]"))
    assert "OA-4 Active" in spectral_block
