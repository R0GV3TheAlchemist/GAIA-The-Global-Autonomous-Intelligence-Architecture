"""
stage_engine.router
===================
FastAPI router for Stage Engine endpoints.

Endpoints
---------
  GET  /stage/health    — liveness probe
  GET  /stage/current   — current alchemical stage
  POST /stage/evaluate  — trigger a stage evaluation pass

Reference: NEXUS_UNIVERSAL_OS.md  Domain 2.3
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from stage_engine.engine import StageEngine
from stage_engine.window_tracker import WindowTracker

logger = logging.getLogger("stage_engine.router")

stage_router = APIRouter(
    prefix="/stage",
    tags=["stage"],
    responses={404: {"description": "Stage endpoint not found"}},
)

_engine: Optional[StageEngine] = None
_tracker: Optional[WindowTracker] = None


def init_stage_engine(
    memory: Any = None,
    engine: Optional[StageEngine] = None,
    tracker: Optional[WindowTracker] = None,
) -> None:
    """Inject StageEngine and WindowTracker into this router."""
    global _engine, _tracker
    _engine = engine or StageEngine(memory=memory)
    _tracker = tracker or WindowTracker()
    logger.info("StageEngine router initialised.")


def _get_engine() -> StageEngine:
    if _engine is None:
        raise RuntimeError("StageEngine not initialised.")
    return _engine


@stage_router.get("/health")
async def stage_health(engine: StageEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "stage", "status": "online"})


@stage_router.get("/current")
async def stage_current(engine: StageEngine = Depends(_get_engine)) -> JSONResponse:
    stage = engine.current_stage
    return JSONResponse(content={
        "engine": "stage",
        "current_stage": stage.name if stage else None,
    })


@stage_router.post("/evaluate")
async def stage_evaluate(payload: dict, engine: StageEngine = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "stage", "note": "Evaluation not yet implemented.", "payload": payload})
