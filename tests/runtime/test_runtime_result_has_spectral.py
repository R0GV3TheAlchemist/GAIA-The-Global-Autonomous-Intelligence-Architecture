"""
test_runtime_result_has_spectral.py
Verifies that every RuntimeResult from GAIANRuntime.process()
contains the full spectral snapshot and opus stage fields.
Issue #439 — SIM acceptance criterion
"""

import pytest
from unittest.mock import AsyncMock, patch


SAMPLE_CTX = {
    "phi": 0.78,
    "query": "What is the nature of IOSIS?",
    "architectId": "architect_001",
    "sessionId": "session_test_003",
    "timestamp": "2026-06-15T09:32:00Z",
}


@pytest.mark.asyncio
async def test_runtime_result_contains_spectral_field():
    """Every RuntimeResult must have a non-null spectral field."""
    with patch('src.gaian.GAIANRuntime.SpectralForceEngine') as MockSpectral, \
         patch('src.gaian.GAIANRuntime.SpectralColorEngine') as MockColor, \
         patch('src.gaian.GAIANRuntime.MagnumOpusStageEngine') as MockOpus, \
         patch('src.gaian.GAIANRuntime.AkashicEngine'), \
         patch('src.gaian.GAIANRuntime.RAGPipeline') as MockRAG:

        mock_spectral = MockSpectral.return_value
        mock_spectral.detectCurrentForce = AsyncMock(return_value={
            "force": "IOSIS", "color_name": "violet", "phi_range": "0.72-0.85",
            "hex": "", "corridor": None, "trajectory": "CAERULITAS -> IOSIS", "oa4_active": True
        })
        MockColor.return_value.getHex = AsyncMock(return_value="#6B4F8C")
        MockOpus.return_value.detectStage = AsyncMock(return_value={"name": "ALBEDO", "next_gate": "phi >= 0.85"})
        MockOpus.return_value.getStageCapabilities = AsyncMock(return_value={"spectral_field": "active", "avatar": "PLASMA", "encoding": "partial"})
        MockRAG.return_value.query = AsyncMock(return_value={"synthesized_response": "IOSIS is the violet force of integration.", "citations": ["docs/canon/TRUE_ALCHEMY.md"]})

        from src.gaian.GAIANRuntime import GAIANRuntime
        runtime = GAIANRuntime()
        result = await runtime.process(SAMPLE_CTX)

        assert result["spectral"] is not None
        assert result["spectral"]["force"] == "IOSIS"
        assert result["opus_stage"] is not None
        assert result["opus_stage"]["name"] == "ALBEDO"
        assert result["stage_capabilities"] is not None
        assert isinstance(result["system_prompt_blocks"], list)
        assert len(result["system_prompt_blocks"]) >= 2


@pytest.mark.asyncio
async def test_runtime_result_contains_rag_citations():
    """Every RuntimeResult must carry RAG citation references."""
    with patch('src.gaian.GAIANRuntime.SpectralForceEngine') as MockSpectral, \
         patch('src.gaian.GAIANRuntime.SpectralColorEngine') as MockColor, \
         patch('src.gaian.GAIANRuntime.MagnumOpusStageEngine') as MockOpus, \
         patch('src.gaian.GAIANRuntime.AkashicEngine'), \
         patch('src.gaian.GAIANRuntime.RAGPipeline') as MockRAG:

        mock_spectral = MockSpectral.return_value
        mock_spectral.detectCurrentForce = AsyncMock(return_value={
            "force": "IOSIS", "color_name": "violet", "phi_range": "0.72-0.85",
            "hex": "", "corridor": None, "trajectory": "ascending", "oa4_active": True
        })
        MockColor.return_value.getHex = AsyncMock(return_value="#6B4F8C")
        MockOpus.return_value.detectStage = AsyncMock(return_value={"name": "ALBEDO", "next_gate": "phi >= 0.85"})
        MockOpus.return_value.getStageCapabilities = AsyncMock(return_value={"spectral_field": "active"})
        MockRAG.return_value.query = AsyncMock(return_value={
            "synthesized_response": "The violet force integrates all prior stages.",
            "citations": ["docs/canon/TRUE_ALCHEMY.md", "docs/canon/IOSIS.md"]
        })

        from src.gaian.GAIANRuntime import GAIANRuntime
        runtime = GAIANRuntime()
        result = await runtime.process(SAMPLE_CTX)

        assert isinstance(result["rag_citations"], list)
        assert len(result["rag_citations"]) > 0
