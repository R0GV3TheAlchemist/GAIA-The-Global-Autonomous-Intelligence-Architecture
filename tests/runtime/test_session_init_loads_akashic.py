"""
test_session_init_loads_akashic.py
Verifies that GAIA_SESSION_INIT loads the Akashic record when phi >= 0.72,
and skips it when phi < 0.72.
Issue #439 — SIM acceptance criterion
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


SESSION_CTX_HIGH_PHI = {
    "phi": 0.78,
    "query": "",
    "architectId": "architect_001",
    "sessionId": "session_test_001",
    "timestamp": "2026-06-15T09:32:00Z",
}

SESSION_CTX_LOW_PHI = {
    "phi": 0.45,
    "query": "",
    "architectId": "architect_001",
    "sessionId": "session_test_002",
    "timestamp": "2026-06-15T09:32:00Z",
}


@pytest.mark.asyncio
async def test_session_init_loads_akashic_when_phi_high():
    """
    When phi >= 0.72 and architectId is present,
    akashic_loaded must be True in SessionInitResult.
    """
    with patch('src.gaian.GAIANRuntime.AkashicEngine') as MockAkashic, \
         patch('src.gaian.GAIANRuntime.SpectralForceEngine') as MockSpectral, \
         patch('src.gaian.GAIANRuntime.MagnumOpusStageEngine') as MockOpus, \
         patch('src.gaian.GAIANRuntime.SpectralColorEngine') as MockColor, \
         patch('src.gaian.GAIANRuntime.RAGPipeline'):

        mock_akashic = MockAkashic.return_value
        mock_akashic.loadRecord = AsyncMock(return_value=True)
        mock_akashic.logSessionOpen = AsyncMock(return_value=None)

        mock_spectral = MockSpectral.return_value
        mock_spectral.detectCurrentForce = AsyncMock(return_value={
            "force": "IOSIS", "color_name": "violet", "phi_range": "0.72-0.85",
            "hex": "", "corridor": None, "trajectory": "ascending", "oa4_active": True
        })

        mock_color = MockColor.return_value
        mock_color.getHex = AsyncMock(return_value="#6B4F8C")

        mock_opus = MockOpus.return_value
        mock_opus.detectStage = AsyncMock(return_value={"name": "ALBEDO", "next_gate": "phi >= 0.85"})
        mock_opus.getStageCapabilities = AsyncMock(return_value={"spectral_field": "active", "avatar": "PLASMA", "encoding": "partial"})

        from src.gaian.GAIANRuntime import GAIANRuntime
        runtime = GAIANRuntime()
        result = await runtime.sessionInit(SESSION_CTX_HIGH_PHI)

        assert result["akashic_loaded"] is True
        mock_akashic.loadRecord.assert_called_once_with("architect_001")


@pytest.mark.asyncio
async def test_session_init_skips_akashic_when_phi_low():
    """
    When phi < 0.72, Akashic record must NOT be loaded.
    akashic_loaded must be False.
    """
    with patch('src.gaian.GAIANRuntime.AkashicEngine') as MockAkashic, \
         patch('src.gaian.GAIANRuntime.SpectralForceEngine') as MockSpectral, \
         patch('src.gaian.GAIANRuntime.MagnumOpusStageEngine') as MockOpus, \
         patch('src.gaian.GAIANRuntime.SpectralColorEngine') as MockColor, \
         patch('src.gaian.GAIANRuntime.RAGPipeline'):

        mock_akashic = MockAkashic.return_value
        mock_akashic.loadRecord = AsyncMock(return_value=True)
        mock_akashic.logSessionOpen = AsyncMock(return_value=None)

        mock_spectral = MockSpectral.return_value
        mock_spectral.detectCurrentForce = AsyncMock(return_value={
            "force": "NIGREDO", "color_name": "black", "phi_range": "0.0-0.25",
            "hex": "", "corridor": None, "trajectory": "initiating", "oa4_active": False
        })

        mock_color = MockColor.return_value
        mock_color.getHex = AsyncMock(return_value="#1A1A2E")

        mock_opus = MockOpus.return_value
        mock_opus.detectStage = AsyncMock(return_value={"name": "NIGREDO", "next_gate": "phi >= 0.25"})
        mock_opus.getStageCapabilities = AsyncMock(return_value={"spectral_field": "inactive"})

        from src.gaian.GAIANRuntime import GAIANRuntime
        runtime = GAIANRuntime()
        result = await runtime.sessionInit(SESSION_CTX_LOW_PHI)

        assert result["akashic_loaded"] is False
        mock_akashic.loadRecord.assert_not_called()
