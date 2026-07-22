"""
crystal.router
==============
FastAPI router for Crystal Core endpoints.

Endpoints
---------
  GET /crystal/health  — liveness probe
  GET /crystal/orb     — current orb parameters

Reference: NEXUS_UNIVERSAL_OS.md  Domain 2.6
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from crystal.engine import CrystalCore

logger = logging.getLogger("crystal.router")

router = APIRouter(
    prefix="/crystal",
    tags=["crystal"],
    responses={404: {"description": "Crystal endpoint not found"}},
)

_engine: Optional[CrystalCore] = None


def init_crystal_core(engine: CrystalCore) -> None:
    """Inject the CrystalCore instance into this router."""
    global _engine
    _engine = engine
    logger.info("CrystalCore router initialised.")


@router.get("/health")
async def crystal_health() -> JSONResponse:
    return JSONResponse(content={"engine": "crystal", "status": "online"})


@router.get("/orb")
async def crystal_orb() -> JSONResponse:
    return JSONResponse(content={"engine": "crystal", "note": "Orb synthesis not yet implemented."})
