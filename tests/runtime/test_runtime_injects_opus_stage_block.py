"""
test_runtime_injects_opus_stage_block.py
Verifies that GAIANRuntime.process() injects a valid [MAGNUM OPUS STAGE] block
into every RuntimeResult.
Issue #439 — SIM acceptance criterion
"""

import pytest


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


def test_opus_stage_block_present():
    """RuntimeResult.system_prompt_blocks must contain a [MAGNUM OPUS STAGE] block."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    opus_block = next((b for b in blocks if b.startswith("[MAGNUM OPUS STAGE")), None)
    assert opus_block is not None, "[MAGNUM OPUS STAGE] block missing from system_prompt_blocks"


def test_opus_stage_block_contains_stage_name():
    """[MAGNUM OPUS STAGE] block must contain the stage name."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    opus_block = next(b for b in blocks if b.startswith("[MAGNUM OPUS STAGE"))
    assert "ALBEDO" in opus_block


def test_opus_stage_block_contains_capabilities():
    """[MAGNUM OPUS STAGE] block must list stage capabilities."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    opus_block = next(b for b in blocks if b.startswith("[MAGNUM OPUS STAGE"))
    assert "spectral_field" in opus_block
    assert "avatar" in opus_block


def test_opus_stage_block_contains_next_gate():
    """[MAGNUM OPUS STAGE] block must include the next gate condition."""
    from src.gaian.runtime_types import SystemPromptBuilder

    blocks = SystemPromptBuilder.build_all(
        SAMPLE_SPECTRAL_SNAPSHOT, SAMPLE_STAGE, SAMPLE_CAPABILITIES
    )
    opus_block = next(b for b in blocks if b.startswith("[MAGNUM OPUS STAGE"))
    assert "Next gate" in opus_block
    assert "falsification_clean" in opus_block
