"""
test_crystal_engine.py
======================
Integration tests for the Crystal Core engine and HTTP router.

All upstream HTTP calls (affect, stage, shadow, schumann) are mocked
so these tests run fully offline without a running sidecar.

Covers:
  - CrystalCore.tick() produces a valid CrystalState
  - CrystalState schema: all fields present and within spec ranges
  - Graceful degradation: shadow engine offline → E defaults to 0.5
  - Graceful degradation: schumann offline → H defaults to 0.5
  - POST /crystal/tick returns 200 + CrystalState JSON within 200ms budget
  - GET  /crystal/state returns 200 + valid CrystalState JSON
  - GET  /crystal/history?days=1 returns a list
  - GET  /crystal/health returns {"ok": true}
  - PersonaTone.SPARSE is injected when CoherenceBand == FRACTURED
  - PersonaTone.RADIANT is injected when CoherenceBand == CRYSTALLINE
"""

from __future__ import annotations

import time
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from crystal.types import CoherenceBand, CrystalState, OrbParams, PersonaTone
from crystal.engine import CrystalCore
from crystal.router import router as crystal_router


# ── Mock stream payloads ──────────────────────────────────────────────────────

MOCK_AFFECT_TREND = {
    "dominant_emotion": "neutral",
    "valence_trend": 0.1,
    "mood_momentum": 0.0,
    "volatility": 0.1,
    "is_volatile": False,
    "arc_stability": 0.7,
}

MOCK_STAGE_RECORD = {
    "stage": 3,
    "marker_scores": [60.0, 55.0, 70.0, 50.0, 65.0, 58.0],
    "days_in_stage": 14,
}

MOCK_SHADOW_STATE = {
    "active_archetype": "Seeker",
    "shadow_intensity": 0.2,
    "integration_progress": 0.6,
}

MOCK_SCHUMANN_STATE = {
    "alignment_score": 0.75,
    "disturbance_level": "stable",
    "confidence": 0.85,
    "deviation_sigma": 0.5,
}


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def crystal_core():
    """A CrystalCore instance with its HTTP client methods mocked."""
    core = CrystalCore(base_url="http://testserver")
    return core


@pytest.fixture()
def mock_streams(crystal_core):
    """Patch all four stream-fetch methods on the CrystalCore instance."""
    crystal_core._fetch_affect = AsyncMock(return_value=MOCK_AFFECT_TREND)
    crystal_core._fetch_stage = AsyncMock(return_value=MOCK_STAGE_RECORD)
    crystal_core._fetch_shadow = AsyncMock(return_value=MOCK_SHADOW_STATE)
    crystal_core._fetch_schumann = AsyncMock(return_value=MOCK_SCHUMANN_STATE)
    return crystal_core


@pytest.fixture()
def test_client(mock_streams):
    """FastAPI TestClient with crystal router mounted and engine injected."""
    from fastapi import FastAPI
    app = FastAPI()
    # Inject the mocked engine into the router's module-level reference
    import crystal.router as router_module
    router_module._crystal_core = mock_streams
    app.include_router(crystal_router)
    return TestClient(app)


# ── CrystalCore.tick() ────────────────────────────────────────────────────────

class TestCrystalCoreTick:
    @pytest.mark.asyncio
    async def test_tick_returns_crystal_state(self, mock_streams):
        """tick() returns a CrystalState dataclass with all required fields."""
        state = await mock_streams.tick(user_id="test-user")
        assert isinstance(state, CrystalState)

    @pytest.mark.asyncio
    async def test_crystal_state_fields_present(self, mock_streams):
        """All CrystalState fields are populated (no None where not expected)."""
        state = await mock_streams.tick(user_id="test-user")
        assert state.timestamp is not None
        assert isinstance(state.coherence, float)
        assert isinstance(state.coherence_band, CoherenceBand)
        assert isinstance(state.inner_narrative, str) and len(state.inner_narrative) > 0
        assert isinstance(state.persona_tone, PersonaTone)
        assert isinstance(state.orb_params, OrbParams)

    @pytest.mark.asyncio
    async def test_coherence_in_range(self, mock_streams):
        """Ψ is in [0.0, 1.0] for the mock stream inputs."""
        state = await mock_streams.tick(user_id="test-user")
        assert 0.0 <= state.coherence <= 1.0

    @pytest.mark.asyncio
    async def test_component_scores_in_range(self, mock_streams):
        """All four component scores are in [0.0, 1.0]."""
        state = await mock_streams.tick(user_id="test-user")
        for name, val in [
            ("affect_coherence", state.affect_coherence),
            ("stage_coherence", state.stage_coherence),
            ("shadow_integration", state.shadow_integration),
            ("schumann_alignment", state.schumann_alignment),
        ]:
            assert 0.0 <= val <= 1.0, f"{name} out of range: {val}"

    @pytest.mark.asyncio
    async def test_orb_params_within_spec_ranges(self, mock_streams):
        """All OrbParams fields are within their defined spec ranges."""
        state = await mock_streams.tick(user_id="test-user")
        orb = state.orb_params
        assert 0.0 <= orb.glow_intensity <= 1.0
        assert 0.10 <= orb.pulse_frequency <= 0.38
        assert 0.0 <= orb.pulse_amplitude
        assert 0.0 <= orb.cloud_opacity <= 1.0
        assert 0.0 <= orb.aurora_intensity <= 1.0
        assert 0.0 <= orb.coherence_ring <= 1.0

    @pytest.mark.asyncio
    async def test_timestamp_is_utc_aware(self, mock_streams):
        """CrystalState.timestamp is timezone-aware UTC."""
        state = await mock_streams.tick(user_id="test-user")
        assert state.timestamp.tzinfo is not None
        assert state.timestamp.tzinfo == timezone.utc


# ── Graceful degradation ──────────────────────────────────────────────────────

class TestGracefulDegradation:
    @pytest.mark.asyncio
    async def test_shadow_unavailable_defaults_to_half(self, crystal_core):
        """
        Spec §13: Shadow Engine unavailable → E = 0.5, no exception.
        """
        crystal_core._fetch_affect = AsyncMock(return_value=MOCK_AFFECT_TREND)
        crystal_core._fetch_stage = AsyncMock(return_value=MOCK_STAGE_RECORD)
        crystal_core._fetch_shadow = AsyncMock(return_value=None)  # offline
        crystal_core._fetch_schumann = AsyncMock(return_value=MOCK_SCHUMANN_STATE)

        try:
            state = await crystal_core.tick(user_id="test-user")
        except Exception as exc:
            pytest.fail(f"Shadow unavailable raised exception: {exc}")

        assert abs(state.shadow_integration - 0.5) < 1e-6
        assert 0.0 <= state.coherence <= 1.0

    @pytest.mark.asyncio
    async def test_schumann_low_confidence_defaults_to_half(self, crystal_core):
        """
        Spec §13: Schumann stream unavailable → H = 0.5, no exception.
        """
        low_confidence_schumann = {**MOCK_SCHUMANN_STATE, "confidence": 0.1}
        crystal_core._fetch_affect = AsyncMock(return_value=MOCK_AFFECT_TREND)
        crystal_core._fetch_stage = AsyncMock(return_value=MOCK_STAGE_RECORD)
        crystal_core._fetch_shadow = AsyncMock(return_value=MOCK_SHADOW_STATE)
        crystal_core._fetch_schumann = AsyncMock(return_value=low_confidence_schumann)

        try:
            state = await crystal_core.tick(user_id="test-user")
        except Exception as exc:
            pytest.fail(f"Low-confidence Schumann raised exception: {exc}")

        assert abs(state.schumann_alignment - 0.5) < 1e-6

    @pytest.mark.asyncio
    async def test_schumann_stream_none_defaults_to_half(self, crystal_core):
        """Schumann stream returning None → H = 0.5, no exception."""
        crystal_core._fetch_affect = AsyncMock(return_value=MOCK_AFFECT_TREND)
        crystal_core._fetch_stage = AsyncMock(return_value=MOCK_STAGE_RECORD)
        crystal_core._fetch_shadow = AsyncMock(return_value=MOCK_SHADOW_STATE)
        crystal_core._fetch_schumann = AsyncMock(return_value=None)  # offline

        try:
            state = await crystal_core.tick(user_id="test-user")
        except Exception as exc:
            pytest.fail(f"Schumann None raised exception: {exc}")

        assert abs(state.schumann_alignment - 0.5) < 1e-6


# ── Persona tone band mapping ─────────────────────────────────────────────────

class TestPersonaTone:
    @pytest.mark.asyncio
    async def test_sparse_when_fractured(self, crystal_core):
        """
        Spec §13: PersonaTone.SPARSE is injected when CoherenceBand == FRACTURED.
        We force a fractured state by driving all components to 0.
        """
        crystal_core._fetch_affect = AsyncMock(return_value={
            "dominant_emotion": "fear",
            "valence_trend": -1.0,
            "mood_momentum": -1.0,
            "volatility": 1.0,
            "is_volatile": True,
            "arc_stability": 0.0,
        })
        crystal_core._fetch_stage = AsyncMock(return_value={
            "stage": 1,
            "marker_scores": [0.0] * 6,
            "days_in_stage": 1,
        })
        crystal_core._fetch_shadow = AsyncMock(return_value={
            "active_archetype": "Shadow",
            "shadow_intensity": 1.0,
            "integration_progress": 0.0,
        })
        crystal_core._fetch_schumann = AsyncMock(return_value={
            "alignment_score": 0.0,
            "disturbance_level": "disturbed",
            "confidence": 0.9,
            "deviation_sigma": 3.0,
        })

        state = await crystal_core.tick(user_id="test-user")
        assert state.coherence_band == CoherenceBand.FRACTURED
        assert state.persona_tone == PersonaTone.SPARSE

    @pytest.mark.asyncio
    async def test_radiant_when_crystalline(self, crystal_core):
        """
        PersonaTone.RADIANT is injected when CoherenceBand == CRYSTALLINE.
        """
        crystal_core._fetch_affect = AsyncMock(return_value={
            "dominant_emotion": "joy",
            "valence_trend": 1.0,
            "mood_momentum": 1.0,
            "volatility": 0.0,
            "is_volatile": False,
            "arc_stability": 1.0,
        })
        crystal_core._fetch_stage = AsyncMock(return_value={
            "stage": 5,
            "marker_scores": [100.0] * 6,
            "days_in_stage": 60,
        })
        crystal_core._fetch_shadow = AsyncMock(return_value={
            "active_archetype": "Sage",
            "shadow_intensity": 0.0,
            "integration_progress": 1.0,
        })
        crystal_core._fetch_schumann = AsyncMock(return_value={
            "alignment_score": 1.0,
            "disturbance_level": "stable",
            "confidence": 1.0,
            "deviation_sigma": 0.0,
        })

        state = await crystal_core.tick(user_id="test-user")
        assert state.coherence_band == CoherenceBand.CRYSTALLINE
        assert state.persona_tone == PersonaTone.RADIANT


# ── HTTP Router ───────────────────────────────────────────────────────────────

class TestCrystalRouter:
    def test_health_returns_ok(self, test_client):
        """GET /crystal/health → 200 {"ok": true}."""
        resp = test_client.get("/crystal/health")
        assert resp.status_code == 200
        assert resp.json().get("ok") is True

    def test_get_state_returns_200(self, test_client):
        """GET /crystal/state → 200 + CrystalState JSON."""
        resp = test_client.get("/crystal/state", params={"user_id": "test-user"})
        assert resp.status_code == 200
        data = resp.json()
        assert "coherence" in data
        assert "coherence_band" in data
        assert "inner_narrative" in data
        assert "persona_tone" in data
        assert "orb_params" in data

    def test_post_tick_returns_200(self, test_client):
        """POST /crystal/tick → 200 + CrystalState JSON."""
        resp = test_client.post("/crystal/tick", json={"user_id": "test-user"})
        assert resp.status_code == 200
        data = resp.json()
        assert "coherence" in data

    def test_post_tick_within_200ms(self, test_client):
        """
        Spec §13: POST /crystal/tick with mocked streams returns within 200ms.
        """
        start = time.perf_counter()
        resp = test_client.post("/crystal/tick", json={"user_id": "test-user"})
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        assert elapsed_ms < 200, f"Tick took {elapsed_ms:.1f}ms — exceeds 200ms budget"

    def test_get_history_returns_list(self, test_client):
        """GET /crystal/history?days=1 → 200 + list."""
        resp = test_client.get("/crystal/history", params={"days": 1, "user_id": "test-user"})
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_coherence_field_in_range(self, test_client):
        """GET /crystal/state coherence is in [0.0, 1.0]."""
        resp = test_client.get("/crystal/state", params={"user_id": "test-user"})
        coherence = resp.json()["coherence"]
        assert 0.0 <= coherence <= 1.0

    def test_orb_params_fields_present(self, test_client):
        """OrbParams in /crystal/state has all 8 required fields."""
        resp = test_client.get("/crystal/state", params={"user_id": "test-user"})
        orb = resp.json()["orb_params"]
        required_fields = [
            "glow_color", "glow_intensity", "pulse_frequency", "pulse_amplitude",
            "cloud_opacity", "aurora_intensity", "rotation_speed", "coherence_ring",
        ]
        for field in required_fields:
            assert field in orb, f"Missing OrbParams field: {field}"
