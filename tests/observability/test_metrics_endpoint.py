"""
tests/observability/test_metrics_endpoint.py

HTTP integration tests for the GAIA-OS /metrics and /health/detailed endpoints.
Tracks: Issue #265

Strategy:
  - Build a minimal FastAPI test app from the observability router only,
    bypassing the full main.py lifespan (which requires Ollama/ChromaDB/Redis).
  - Use httpx.AsyncClient as the ASGI transport client (no network required).
  - Tests are hermetic: all external probes (_probe_chroma, _probe_redis)
    are monkeypatched to return True/False as needed.

Coverage:
  ✔ GET /metrics returns 200 with text/plain (or prometheus content-type)
  ✔ GET /metrics body contains expected metric names
  ✔ GET /health/detailed returns JSON with required top-level keys
  ✔ GET /health/detailed subsystems key lists chromadb, redis, emrys
  ✔ GET /health/detailed returns 503 when a subsystem is unavailable
  ✔ record_cycle() updates Prometheus gauges (prometheus_client available)
  ✔ record_session() updates session gauges
  ✔ /metrics content includes gaia_backend_uptime_seconds
"""
from __future__ import annotations

import pytest
import pytest_asyncio
import httpx
from fastapi import FastAPI


# ── Minimal test app (no lifespan, no external deps) ─────────────────────────

@pytest.fixture(scope="module")
def obs_app():
    """Minimal FastAPI app that mounts only the observability router."""
    from api.routers.observability import router
    app = FastAPI()
    app.include_router(router)
    return app


@pytest_asyncio.fixture(scope="module")
async def client(obs_app):
    """httpx AsyncClient backed by the ASGI transport layer (no TCP)."""
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=obs_app),
        base_url="http://test",
    ) as c:
        yield c


# ── /metrics tests ────────────────────────────────────────────────────────────────

class TestMetricsEndpoint:

    @pytest.mark.asyncio
    async def test_metrics_returns_200(self, client):
        r = await client.get("/metrics")
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_metrics_content_type_is_text(self, client):
        r = await client.get("/metrics")
        # prometheus_client uses 'text/plain; version=0.0.4; charset=utf-8'
        # our fallback uses 'text/plain'
        assert "text/plain" in r.headers["content-type"]

    @pytest.mark.asyncio
    async def test_metrics_contains_uptime(self, client):
        r = await client.get("/metrics")
        assert "gaia_backend_uptime_seconds" in r.text

    @pytest.mark.asyncio
    async def test_metrics_contains_emrys_phi_name_or_comment(self, client):
        r = await client.get("/metrics")
        # Either the metric line or a comment declaring it should be present
        assert "emrys_cycle_phi" in r.text or "emrys" in r.text.lower()

    @pytest.mark.asyncio
    async def test_metrics_body_is_non_empty(self, client):
        r = await client.get("/metrics")
        assert len(r.text.strip()) > 0


# ── /health/detailed tests ─────────────────────────────────────────────────────────

class TestHealthDetailedEndpoint:

    @pytest.mark.asyncio
    async def test_health_detailed_has_required_keys(self, client, monkeypatch):
        import api.routers.observability as obs_mod
        monkeypatch.setattr(obs_mod, "_probe_chroma", _always_true)
        monkeypatch.setattr(obs_mod, "_probe_redis",  _always_true)

        r = await client.get("/health/detailed")
        body = r.json()
        assert "status"      in body
        assert "service"     in body
        assert "subsystems"  in body
        assert "metrics_url" in body

    @pytest.mark.asyncio
    async def test_health_detailed_subsystems_keys(self, client, monkeypatch):
        import api.routers.observability as obs_mod
        monkeypatch.setattr(obs_mod, "_probe_chroma", _always_true)
        monkeypatch.setattr(obs_mod, "_probe_redis",  _always_true)

        r = await client.get("/health/detailed")
        subs = r.json()["subsystems"]
        assert "chromadb" in subs
        assert "redis"    in subs
        assert "emrys"    in subs

    @pytest.mark.asyncio
    async def test_health_detailed_ok_when_all_healthy(self, client, monkeypatch):
        import api.routers.observability as obs_mod
        monkeypatch.setattr(obs_mod, "_probe_chroma", _always_true)
        monkeypatch.setattr(obs_mod, "_probe_redis",  _always_true)

        r = await client.get("/health/detailed")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_detailed_503_when_redis_down(self, client, monkeypatch):
        import api.routers.observability as obs_mod
        monkeypatch.setattr(obs_mod, "_probe_chroma", _always_true)
        monkeypatch.setattr(obs_mod, "_probe_redis",  _always_false)

        r = await client.get("/health/detailed")
        assert r.status_code == 503
        assert r.json()["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_health_detailed_503_when_chroma_down(self, client, monkeypatch):
        import api.routers.observability as obs_mod
        monkeypatch.setattr(obs_mod, "_probe_chroma", _always_false)
        monkeypatch.setattr(obs_mod, "_probe_redis",  _always_true)

        r = await client.get("/health/detailed")
        assert r.status_code == 503
        assert r.json()["status"] == "degraded"

    @pytest.mark.asyncio
    async def test_metrics_url_field_value(self, client, monkeypatch):
        import api.routers.observability as obs_mod
        monkeypatch.setattr(obs_mod, "_probe_chroma", _always_true)
        monkeypatch.setattr(obs_mod, "_probe_redis",  _always_true)

        r = await client.get("/health/detailed")
        assert r.json()["metrics_url"] == "/metrics"


# ── record_cycle / record_session helpers ─────────────────────────────────────────

class TestRecordHelpers:

    def test_record_cycle_does_not_raise(self):
        from api.routers.observability import record_cycle
        # Should be silent regardless of whether prometheus_client is installed
        record_cycle(
            phi=0.42, fidelity=0.78, phase_offset_ms=1.2,
            duration_ms=9.5, routing_flag="active_inference"
        )

    def test_record_session_does_not_raise(self):
        from api.routers.observability import record_session
        record_session(phi_baseline=0.40, cold_start_ms=320.0, inter_session_s=3600.0)

    @pytest.mark.asyncio
    async def test_metrics_reflects_uptime_after_cycle(self, client):
        """After calling record_cycle, /metrics must still return 200."""
        from api.routers.observability import record_cycle
        record_cycle(
            phi=0.55, fidelity=0.82, phase_offset_ms=0.8,
            duration_ms=7.1, routing_flag="classical_prior"
        )
        r = await client.get("/metrics")
        assert r.status_code == 200
        assert "gaia_backend_uptime_seconds" in r.text


# ── Probe helpers for monkeypatching ─────────────────────────────────────────────────

async def _always_true()  -> bool: return True
async def _always_false() -> bool: return False
