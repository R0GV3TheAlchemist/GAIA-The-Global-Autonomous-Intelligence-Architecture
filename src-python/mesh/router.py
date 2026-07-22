"""
mesh.router
===========
FastAPI router for GAIAN Mesh Network endpoints.

Endpoints
---------
  GET  /mesh/health   — mesh router health probe
  GET  /mesh/peers    — list known mesh peers
  GET  /mesh/status   — aggregate mesh + engine health status
  POST /mesh/send     — send a message to a mesh peer

Reference: NEXUS_UNIVERSAL_OS.md  Domain 1.5
"""
from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger("mesh.router")

router = APIRouter(
    prefix="/mesh",
    tags=["mesh"],
    responses={404: {"description": "Mesh endpoint not found"}},
)

_mesh_initialized: bool = False
_audit_store: Any = None
_sovereign_memory: Any = None
_telemetry: Any = None
_crisis_engine: Any = None


def init_mesh_router(
    audit_store: Any = None,
    sovereign_memory: Any = None,
    telemetry: Any = None,
    crisis_engine: Any = None,
) -> None:
    """Initialise the GAIAN mesh router with injected engine references."""
    global _mesh_initialized, _audit_store, _sovereign_memory, _telemetry, _crisis_engine
    _mesh_initialized = True
    _audit_store = audit_store
    _sovereign_memory = sovereign_memory
    _telemetry = telemetry
    _crisis_engine = crisis_engine
    logger.info("Mesh router initialised.")


@router.get("/health")
async def mesh_health() -> JSONResponse:
    return JSONResponse(content={"engine": "mesh", "initialized": _mesh_initialized})


@router.get("/peers")
async def mesh_peers() -> JSONResponse:
    return JSONResponse(content={"engine": "mesh", "peers": [], "note": "Peer discovery not yet implemented."})


@router.get("/status")
async def mesh_status() -> JSONResponse:
    crisis_level = None
    if _crisis_engine is not None:
        try:
            crisis_level = _crisis_engine.current_level.name
        except Exception:
            crisis_level = "unknown"
    return JSONResponse(content={
        "engine": "mesh",
        "initialized": _mesh_initialized,
        "crisis_level": crisis_level,
        "note": "Full status aggregation not yet implemented.",
    })


@router.post("/send")
async def mesh_send(payload: dict) -> JSONResponse:
    return JSONResponse(content={"engine": "mesh", "note": "Mesh send not yet implemented.", "payload": payload})
