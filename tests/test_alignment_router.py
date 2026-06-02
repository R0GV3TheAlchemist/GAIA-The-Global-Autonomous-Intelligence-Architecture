"""
tests/test_alignment_router.py

pytest suite for api/routers/alignment.py
Issue: #64 (Phase 2 — FastAPI endpoint)

Covers:
  - POST /alignment/compute happy path
  - POST /alignment/compute — all 4 failure modes
  - POST /alignment/compute — field validation (negative values, bad types)
  - GET  /alignment/status  — before and after a compute call
  - Response model shape (all required fields present + types)
  - Singleton emitter accumulates samples across calls
"""

from __future__ import annotations

import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from fastapi import FastAPI

import api.routers.alignment as alignment_module
from api.routers.alignment import router


# ===========================================================================
# Test app fixture
# ===========================================================================

@pytest.fixture(autouse=True)
def reset_emitter():
    """Isolate each test: force a fresh emitter singleton."""
    alignment_module._emitter = None
    yield
    alignment_module._emitter = None


@pytest.fixture()
def app():
    _app = FastAPI()
    _app.include_router(router, prefix="/alignment")
    return _app


# ===========================================================================
# POST /alignment/compute — happy path
# ===========================================================================

class TestComputeHappyPath:

    @pytest.mark.asyncio
    async def test_returns_200(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 1.0,
            })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_response_has_all_fields(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 1.0,
            })
        body = resp.json()
        for key in ("score", "hrv_score", "schumann_score", "solar_kp",
                    "ui_tier", "last_updated", "fallback_mode"):
            assert key in body, f"missing key: {key}"

    @pytest.mark.asyncio
    async def test_score_in_range(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 1.0,
            })
        assert 0.0 <= resp.json()["score"] <= 100.0

    @pytest.mark.asyncio
    async def test_ui_tier_valid(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 0.0,
            })
        assert resp.json()["ui_tier"] in ("minimal", "core", "standard", "full", "vibrant")

    @pytest.mark.asyncio
    async def test_fallback_mode_empty_on_healthy_feeds(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 0.0,
            })
        assert resp.json()["fallback_mode"] == ""

    @pytest.mark.asyncio
    async def test_solar_kp_echoed_in_response(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 3.5,
            })
        assert resp.json()["solar_kp"] == pytest.approx(3.5, abs=0.01)


# ===========================================================================
# POST /alignment/compute — failure modes
# ===========================================================================

class TestComputeFailureModes:

    @pytest.mark.asyncio
    async def test_hrv_unavailable_returns_200(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": None,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 0.0,
            })
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_hrv_unavailable_fallback_recorded(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": None,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 0.0,
            })
        assert "hrv_unavailable" in resp.json()["fallback_mode"]

    @pytest.mark.asyncio
    async def test_schumann_unavailable_fallback_recorded(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": None,
                "solar_kp": 0.0,
            })
        assert "schumann_unavailable" in resp.json()["fallback_mode"]

    @pytest.mark.asyncio
    async def test_both_unavailable_score_is_50(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": None,
                "raw_schumann_amplitude": None,
                "solar_kp": 0.0,
            })
        assert resp.json()["score"] == pytest.approx(50.0)

    @pytest.mark.asyncio
    async def test_both_unavailable_tier_is_standard(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": None,
                "raw_schumann_amplitude": None,
                "solar_kp": 0.0,
            })
        assert resp.json()["ui_tier"] == "standard"

    @pytest.mark.asyncio
    async def test_kp_storm_score_is_zero(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 9.0,
            })
        assert resp.json()["score"] == pytest.approx(0.0)

    @pytest.mark.asyncio
    async def test_kp_storm_tier_is_minimal(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 9.0,
            })
        assert resp.json()["ui_tier"] == "minimal"

    @pytest.mark.asyncio
    async def test_kp_storm_fallback_recorded(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 9.0,
            })
        assert "kp_storm" in resp.json()["fallback_mode"]


# ===========================================================================
# POST /alignment/compute — field validation
# ===========================================================================

class TestComputeValidation:

    @pytest.mark.asyncio
    async def test_negative_rmssd_returns_422(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": -1.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": 0.0,
            })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_amplitude_returns_422(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": -0.5,
                "solar_kp": 0.0,
            })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_kp_returns_422(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
                "solar_kp": -1.0,
            })
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_all_fields_uses_defaults(self, app):
        """Empty body is valid — all fields have defaults (None / 0.0)."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={})
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_solar_kp_defaults_to_zero(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0,
                "raw_schumann_amplitude": 2.0,
            })
        assert resp.json()["solar_kp"] == pytest.approx(0.0, abs=0.01)


# ===========================================================================
# GET /alignment/status
# ===========================================================================

class TestAlignmentStatus:

    @pytest.mark.asyncio
    async def test_status_200_before_compute(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/alignment/status")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_emitter_ready_true(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/alignment/status")
        assert resp.json()["emitter_ready"] is True

    @pytest.mark.asyncio
    async def test_last_state_none_before_compute(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/alignment/status")
        assert resp.json()["last_state"] is None

    @pytest.mark.asyncio
    async def test_last_state_populated_after_compute(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.post("/alignment/compute", json={
                "raw_rmssd": 60.0, "raw_schumann_amplitude": 2.0, "solar_kp": 1.0,
            })
            resp = await client.get("/alignment/status")
        assert resp.json()["last_state"] is not None

    @pytest.mark.asyncio
    async def test_sample_counts_increment(self, app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            for _ in range(3):
                await client.post("/alignment/compute", json={
                    "raw_rmssd": 55.0, "raw_schumann_amplitude": 2.0, "solar_kp": 0.0,
                })
            status = (await client.get("/alignment/status")).json()
        assert status["hrv_sample_count"] == 3
        assert status["schumann_sample_count"] == 3
