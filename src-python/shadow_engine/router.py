"""
shadow_engine.router
====================
FastAPI router for Shadow Engine endpoints.

Endpoints
---------
  GET /shadow/health   — liveness probe
  GET /shadow/state    — current shadow state and load

Reference: NEXUS_UNIVERSAL_OS.md  Domain 2.4
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from shadow_engine.engine import ShadowEngine

logger = logging.getLogger("shadow_engine.router")

router = APIRouter(
    prefix="/shadow",
    tags=["shadow"],
    responses={404: {"description": "Shadow endpoint not found"}},
)

_engine: Optional[ShadowEngine] = None


@router.get("/health")
async def shadow_health() -> JSONResponse:
    return JSONResponse(content={"engine": "shadow", "status": "online"})


@router.get("/state")
async def shadow_state() -> JSONResponse:
    return JSONResponse(content={"engine": "shadow", "note": "State evaluation not yet implemented."})
