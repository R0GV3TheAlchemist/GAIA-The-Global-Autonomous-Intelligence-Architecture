"""
sovereign_memory.router
=======================
FastAPI router for Sovereign Memory endpoints.

Endpoints
---------
  GET  /memory/health    — liveness probe
  GET  /memory/episodic  — return recent episodic records
  POST /memory/episodic  — store a new episodic record

Reference: NEXUS_UNIVERSAL_OS.md  Domain 2.1
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from sovereign_memory.engine import SovereignMemory

logger = logging.getLogger("sovereign_memory.router")

memory_router = APIRouter(
    prefix="/memory",
    tags=["memory"],
    responses={404: {"description": "Memory endpoint not found"}},
)

_memory: Optional[SovereignMemory] = None


def init_memory(memory: SovereignMemory) -> None:
    """Inject the SovereignMemory instance into this router."""
    global _memory
    _memory = memory
    logger.info("SovereignMemory router initialised.")


def _get_memory() -> SovereignMemory:
    if _memory is None:
        raise RuntimeError("SovereignMemory not initialised.")
    return _memory


@memory_router.get("/health")
async def memory_health(memory: SovereignMemory = Depends(_get_memory)) -> JSONResponse:
    return JSONResponse(content={"engine": "sovereign-memory", "status": "online"})


@memory_router.get("/episodic")
async def get_episodic(memory: SovereignMemory = Depends(_get_memory)) -> JSONResponse:
    return JSONResponse(content={"engine": "sovereign-memory", "note": "Episodic retrieval not yet implemented."})


@memory_router.post("/episodic")
async def post_episodic(payload: dict, memory: SovereignMemory = Depends(_get_memory)) -> JSONResponse:
    return JSONResponse(content={"engine": "sovereign-memory", "note": "Episodic store not yet implemented.", "payload": payload})
