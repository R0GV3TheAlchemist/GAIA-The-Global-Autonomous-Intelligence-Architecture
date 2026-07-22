"""schumann.router

FastAPI Router for Schumann Engine Endpoints

v0.1.0
  - GET /schumann/health     engine health probe
  - GET /schumann/last-pulse last emitted SyncPulse

Reference:
    NEXUS_UNIVERSAL_OS.md Domain 4.1.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from schumann.engine import SchumannEngine

logger = logging.getLogger("schumann.router")

schumann_router = APIRouter(
    prefix="/schumann",
    tags=["schumann"],
    responses={404: {"description": "Schumann endpoint not found"}},
)

_engine: SchumannEngine | None = None


def _get_engine() -> SchumannEngine:
    if _engine is None:
        raise RuntimeError("SchumannEngine not initialised.")
    return _engine


def init_schumann_engine(engine: SchumannEngine) -> None:
    """Initialise the Schumann router with a SchumannEngine instance."""
    global _engine
    _engine = engine
    logger.info("SchumannEngine router initialised.")


@schumann_router.get("/health")
async def schumann_health(engine: SchumannEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "schumann", "status": "online"})


@schumann_router.get("/last-pulse")
async def schumann_last_pulse(engine: SchumannEngine = Depends(_get_engine)) -> JSONResponse:
    pulse = engine.last_pulse
    if pulse is None:
        return JSONResponse(content={"engine": "schumann", "pulse": None})
    return JSONResponse(content={
        "engine": "schumann",
        "confirmed": pulse.confirmed,
        "frequency_hz": pulse.frequency_hz,
        "confidence": pulse.confidence,
        "harmonics": pulse.harmonics,
    })
