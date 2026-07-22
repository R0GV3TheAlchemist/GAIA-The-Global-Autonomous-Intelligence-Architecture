"""affectengine.router

FastAPI Router for Affect Engine Endpoints

v0.1.0
  - GET /affect/health   engine health probe
  - GET /affect/state    current PAD emotional state

Reference:
    NEXUS_UNIVERSAL_OS.md Domain 2.6.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from affectengine.engine import AffectEngine

logger = logging.getLogger("affectengine.router")

affect_router = APIRouter(
    prefix="/affect",
    tags=["affect"],
    responses={404: {"description": "Affect endpoint not found"}},
)

_engine: AffectEngine | None = None


def _get_engine() -> AffectEngine:
    if _engine is None:
        raise RuntimeError("AffectEngine not initialised.")
    return _engine


def init_affect_engine(engine: AffectEngine) -> None:
    """Initialise the affect router with an AffectEngine instance."""
    global _engine
    _engine = engine
    logger.info("AffectEngine router initialised.")


@affect_router.get("/health")
async def affect_health(engine: AffectEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "affect", "status": "online"})


@affect_router.get("/state")
async def affect_state(engine: AffectEngine = Depends(_get_engine)) -> JSONResponse:
    s = engine.state
    return JSONResponse(content={
        "engine": "affect",
        "valence": s.valence,
        "arousal": s.arousal,
        "dominance": s.dominance,
    })
