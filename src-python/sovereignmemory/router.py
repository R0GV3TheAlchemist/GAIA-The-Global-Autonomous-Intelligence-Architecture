"""sovereignmemory.router

FastAPI Router for Sovereign Memory Endpoints

v0.1.0
  - GET  /memory/health    engine health probe
  - GET  /memory/stats     record count per layer
  - POST /memory/store     store a new memory record

Reference:
    NEXUS_UNIVERSAL_OS.md Domain 3.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sovereignmemory.engine import SovereignMemory, MemoryLayer, MemoryRecord

logger = logging.getLogger("sovereignmemory.router")

memory_router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    responses={404: {"description": "Memory endpoint not found"}},
)

_engine: SovereignMemory | None = None


def _get_engine() -> SovereignMemory:
    if _engine is None:
        raise RuntimeError("SovereignMemory not initialised.")
    return _engine


def init_memory(engine: SovereignMemory) -> None:
    """Initialise the sovereign memory router with an engine instance."""
    global _engine
    _engine = engine
    logger.info("SovereignMemory router initialised.")


@memory_router.get("/health")
async def memory_health(engine: SovereignMemory = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "sovereign-memory", "status": "online"})


@memory_router.get("/stats")
async def memory_stats(engine: SovereignMemory = Depends(_get_engine)) -> JSONResponse:
    return JSONResponse(content={"engine": "sovereign-memory", "total_records": engine.count()})
