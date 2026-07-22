"""crystal.router

FastAPI Router for Crystal Engine Endpoints

v0.1.0
  - GET /crystal/health      engine health probe
  - GET /crystal/lattices    list registered lattice formulas

Reference:
    NEXUS_UNIVERSAL_OS.md Domain 4.2.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from crystal.engine import CrystalCore

logger = logging.getLogger("crystal.router")

crystal_router = APIRouter(
    prefix="/crystal",
    tags=["crystal"],
    responses={404: {"description": "Crystal endpoint not found"}},
)

_engine: CrystalCore | None = None


def _get_engine() -> CrystalCore:
    if _engine is None:
        raise RuntimeError("CrystalCore not initialised.")
    return _engine


def init_crystal_core(engine: CrystalCore) -> None:
    """Initialise the crystal router with a CrystalCore instance."""
    global _engine
    _engine = engine
    logger.info("CrystalCore router initialised.")


@crystal_router.get("/health")
async def crystal_health(engine: CrystalCore = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "crystal", "status": "online"})


@crystal_router.get("/lattices")
async def crystal_lattices(engine: CrystalCore = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "crystal", "registered": list(engine._lattices.keys())})
