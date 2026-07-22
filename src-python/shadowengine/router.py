"""shadowengine.router

FastAPI Router for Shadow Engine Endpoints

v0.1.0
  - GET /shadow/health   engine health probe
  - GET /shadow/state    current shadow state and load

Reference:
    NEXUS_UNIVERSAL_OS.md Domain 2.8.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from shadowengine.engine import ShadowEngine

logger = logging.getLogger("shadowengine.router")

shadow_router = APIRouter(
    prefix="/shadow",
    tags=["shadow"],
    responses={404: {"description": "Shadow endpoint not found"}},
)

_engine: ShadowEngine | None = None


def _get_engine() -> ShadowEngine:
    if _engine is None:
        raise RuntimeError("ShadowEngine not initialised.")
    return _engine


@shadow_router.get("/health")
async def shadow_health(engine: ShadowEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "shadow", "status": "online"})


@shadow_router.get("/state")
async def shadow_state(engine: ShadowEngine = Depends(_get_engine)) -> JSONResponse:
    state = engine.get_state()
    return JSONResponse(content={
        "engine": "shadow",
        "total_load": state.total_load,
        "fragment_count": state.fragment_count,
        "integration_score": state.integration_score,
    })
