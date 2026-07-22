"""stageengine.router

FastAPI Router for Stage Engine Endpoints

v0.1.0
  - GET /stage/health    engine health probe
  - GET /stage/current   current GAIA developmental stage

Reference:
    GAIA_ASCENDENCE_DOCTRINE.md
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from stageengine.engine import StageEngine

logger = logging.getLogger("stageengine.router")

stage_router = APIRouter(
    prefix="/stage",
    tags=["stage"],
    responses={404: {"description": "Stage endpoint not found"}},
)

_engine: StageEngine | None = None


def _get_engine() -> StageEngine:
    if _engine is None:
        raise RuntimeError("StageEngine not initialised.")
    return _engine


def init_stage_engine(engine: StageEngine) -> None:
    """Initialise the stage router with a StageEngine instance."""
    global _engine
    _engine = engine
    logger.info("StageEngine router initialised.")


@stage_router.get("/health")
async def stage_health(engine: StageEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "stage", "status": "online"})


@stage_router.get("/current")
async def stage_current(engine: StageEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "stage", "current_stage": engine.current_stage.name})
