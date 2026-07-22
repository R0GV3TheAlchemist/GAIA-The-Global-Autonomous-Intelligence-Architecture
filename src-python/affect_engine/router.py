"""
affect_engine.router
====================
FastAPI router for Affect Engine endpoints.

Endpoints
---------
  GET  /affect/health   — liveness probe
  GET  /affect/state    — return current PAD affect state
  POST /affect/ingest   — ingest a new signal

Reference: NEXUS_UNIVERSAL_OS.md  Domain 2.2
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from affect_engine.engine import AffectEngine

logger = logging.getLogger("affect_engine.router")

affect_router = APIRouter(
    prefix="/affect",
    tags=["affect"],
    responses={404: {"description": "Affect endpoint not found"}},
)

_affect_engine: Optional[AffectEngine] = None


def init_affect_engine(engine: AffectEngine, backend_name: str = "heuristic") -> None:
    """Inject the AffectEngine instance into this router."""
    global _affect_engine
    _affect_engine = engine
    _affect_engine._backend_name = backend_name
    logger.info("AffectEngine router initialised (backend=%s).", backend_name)


def _get_affect_engine() -> AffectEngine:
    if _affect_engine is None:
        raise RuntimeError("AffectEngine not initialised.")
    return _affect_engine


@affect_router.get("/health")
async def affect_health(engine: AffectEngine = Depends(_get_affect_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "affect", "status": "online"})


@affect_router.get("/state")
async def affect_state(engine: AffectEngine = Depends(_get_affect_engine)) -> JSONResponse:
    s = engine.state
    return JSONResponse(content={
        "pleasure": s.pleasure,
        "arousal": s.arousal,
        "dominance": s.dominance,
        "label": s.label,
    })


@affect_router.post("/ingest")
async def affect_ingest(payload: dict, engine: AffectEngine = Depends(_get_affect_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "affect", "note": "Ingest not yet implemented.", "payload": payload})
