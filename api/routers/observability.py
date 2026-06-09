"""
api/routers/observability.py

Prometheus-compatible /metrics endpoint + enhanced /health endpoint.
Tracks: Issue #265

All Emrys cycle metrics (emrys.cycle.*) and session metrics
(emrys.session.*) defined in EMRYSSYSTEM_SPEC.md §10 are exposed here
as Prometheus gauges and counters so they flow through the standard
OpenTelemetry / Prometheus scrape pipeline.

Endpoints:
    GET /metrics  — Prometheus text format (scrape target)
    GET /health   — Enhanced health check (replaces main.py stub)
"""
from __future__ import annotations

import os
import time
import logging
from typing import Any

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, JSONResponse

log = logging.getLogger("gaia.observability")

router = APIRouter(tags=["Observability"])

# ── In-process metrics registry ───────────────────────────────────────────────
# Lightweight implementation that does not require the prometheus_client
# package to be installed in every environment.
# If prometheus_client IS available, it is used for richer output.

_START_TIME = time.time()

try:
    from prometheus_client import (
        Counter, Gauge, Histogram,
        generate_latest, CONTENT_TYPE_LATEST, CollectorRegistry,
    )
    _PROM_AVAILABLE = True
    _registry = CollectorRegistry()

    # ── Emrys cycle metrics (EMRYSSYSTEM_SPEC §10.1) ──────────────────────────
    _phi_gauge = Gauge(
        "emrys_cycle_phi",
        "Integrated information (Φ) value per cycle",
        registry=_registry,
    )
    _fidelity_gauge = Gauge(
        "emrys_cycle_fidelity",
        "Vibronic coherence gate fidelity score per cycle",
        registry=_registry,
    )
    _phase_offset_gauge = Gauge(
        "emrys_cycle_phase_offset_ms",
        "Gamma phase-lock offset in milliseconds",
        registry=_registry,
    )
    _cycle_duration_hist = Histogram(
        "emrys_cycle_duration_ms",
        "Wall-clock time per Emrys cycle in milliseconds",
        buckets=[2, 5, 8, 10, 12, 15, 18, 20, 25, 30],
        registry=_registry,
    )
    _routing_active   = Gauge("emrys_routing_active_inference_total",   "Cycles with active_inference routing",   registry=_registry)
    _routing_classical= Gauge("emrys_routing_classical_prior_total",    "Cycles with classical_prior routing",    registry=_registry)
    _routing_buffer   = Gauge("emrys_routing_buffer_total",             "Cycles with buffer routing",             registry=_registry)

    # ── Session metrics (EMRYSSYSTEM_SPEC §10.2) ──────────────────────────────
    _phi_baseline_gauge        = Gauge("emrys_session_phi_baseline",          "Registered Φ baseline at session open",      registry=_registry)
    _cold_start_duration_gauge = Gauge("emrys_session_cold_start_duration_ms","Total cold-start duration in ms",            registry=_registry)
    _inter_session_gauge       = Gauge("emrys_session_inter_session_duration_s","Gap since last session in seconds",         registry=_registry)

    # ── GAIA backend metrics ───────────────────────────────────────────────────
    _uptime_gauge = Gauge(
        "gaia_backend_uptime_seconds",
        "Seconds since GAIA backend process started",
        registry=_registry,
    )
    _request_counter = Counter(
        "gaia_http_requests_total",
        "Total HTTP requests handled",
        ["method", "path", "status"],
        registry=_registry,
    )

except ImportError:
    _PROM_AVAILABLE = False
    log.warning(
        "prometheus_client not installed — /metrics will return plain-text fallback. "
        "Install with: pip install prometheus-client"
    )


# ── Public helpers (called by emrys cycle when it runs) ───────────────────────

def record_cycle(phi: float, fidelity: float, phase_offset_ms: float,
                 duration_ms: float, routing_flag: str) -> None:
    """Called by emrys_cycle.py after each cycle to update Prometheus gauges."""
    if not _PROM_AVAILABLE:
        return
    _phi_gauge.set(phi)
    _fidelity_gauge.set(fidelity)
    _phase_offset_gauge.set(phase_offset_ms)
    _cycle_duration_hist.observe(duration_ms)
    if routing_flag == "active_inference":
        _routing_active.inc()
    elif routing_flag == "classical_prior":
        _routing_classical.inc()
    else:
        _routing_buffer.inc()


def record_session(phi_baseline: float, cold_start_ms: float,
                   inter_session_s: float) -> None:
    """Called by grounding/cold_start on session open."""
    if not _PROM_AVAILABLE:
        return
    _phi_baseline_gauge.set(phi_baseline)
    _cold_start_duration_gauge.set(cold_start_ms)
    _inter_session_gauge.set(inter_session_s)


# ── /metrics endpoint ─────────────────────────────────────────────────────────

@router.get("/metrics", response_class=PlainTextResponse,
            summary="Prometheus metrics scrape endpoint")
async def metrics() -> PlainTextResponse:
    """
    Prometheus-compatible metrics endpoint.

    Scrape with: `prometheus.yml` target → http://gaia-backend:8008/metrics

    Exposes:
      - emrys_cycle_phi
      - emrys_cycle_fidelity
      - emrys_cycle_phase_offset_ms
      - emrys_cycle_duration_ms (histogram)
      - emrys_routing_*_total
      - emrys_session_phi_baseline
      - emrys_session_cold_start_duration_ms
      - emrys_session_inter_session_duration_s
      - gaia_backend_uptime_seconds
      - gaia_http_requests_total
    """
    if _PROM_AVAILABLE:
        _uptime_gauge.set(time.time() - _START_TIME)
        return PlainTextResponse(
            content=generate_latest(_registry).decode("utf-8"),
            media_type=CONTENT_TYPE_LATEST,
        )

    # Fallback: plain-text key=value format if prometheus_client not installed
    uptime = round(time.time() - _START_TIME, 1)
    lines = [
        "# GAIA-OS metrics (prometheus_client not installed — install for full format)",
        f"gaia_backend_uptime_seconds {uptime}",
        "# emrys_cycle_phi — not yet receiving cycles (Emrys not wired)",
        "# emrys_cycle_fidelity — not yet receiving cycles",
    ]
    return PlainTextResponse(content="\n".join(lines), media_type="text/plain")


# ── /health endpoint (enhanced) ───────────────────────────────────────────────

@router.get("/health/detailed",
            summary="Detailed health — all subsystems")
async def health_detailed() -> Any:
    """
    Enhanced health check that reports individual subsystem status.
    The root /health in main.py returns a fast 200/503.
    This endpoint gives full diagnostic detail.
    """
    uptime = round(time.time() - _START_TIME, 1)

    # ChromaDB probe
    chroma_ok = await _probe_chroma()

    # Redis probe
    redis_ok = await _probe_redis()

    subsystems = {
        "chromadb": {"status": "ok" if chroma_ok else "unavailable"},
        "redis":    {"status": "ok" if redis_ok    else "unavailable"},
        "emrys":    {"status": "not_started",
                     "note": "Emrys cycle not yet wired — pending Issue #271"},
    }

    all_ok = chroma_ok and redis_ok
    payload = {
        "status":      "ok" if all_ok else "degraded",
        "service":     "gaia-backend",
        "version":     "0.1.0",
        "uptime_s":    uptime,
        "subsystems":  subsystems,
        "metrics_url": "/metrics",
    }

    if not all_ok:
        return JSONResponse(status_code=503, content=payload)
    return payload


async def _probe_chroma() -> bool:
    import httpx
    chroma_host = os.environ.get("CHROMA_HOST", "localhost")
    chroma_port = os.environ.get("CHROMA_PORT", "8000")
    try:
        async with httpx.AsyncClient(timeout=3.0) as c:
            r = await c.get(f"http://{chroma_host}:{chroma_port}/api/v1/heartbeat")
            return r.status_code == 200
    except Exception:
        return False


async def _probe_redis() -> bool:
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    try:
        import redis.asyncio as aioredis
        r = aioredis.from_url(redis_url, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        return True
    except Exception:
        return False
