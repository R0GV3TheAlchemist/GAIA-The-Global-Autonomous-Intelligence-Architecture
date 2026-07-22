"""mesh.router

FastAPI Router for GAIAN Mesh Network Endpoints

v0.1.0
  - GET  /mesh/health   mesh router health probe
  - GET  /mesh/peers    list known mesh peers
  - POST /mesh/send     send a message to a mesh peer

Reference:
    NEXUS_UNIVERSAL_OS.md Domain 1.5.
    GAIAN_LAWS.md Law IV - Mesh Sovereignty.
"""
from __future__ import annotations

import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger("mesh.router")

mesh_router = APIRouter(
    prefix="/mesh",
    tags=["mesh"],
    responses={404: {"description": "Mesh endpoint not found"}},
)

_initialized: bool = False


def init_mesh_router() -> None:
    """Initialise the GAIAN mesh router.

    Called once from src-python/main.py during application startup.
    In v0.1.0, registers the router but performs no hardware initialisation.
    Phase B will wire LoRa/BLE/IP transport discovery.
    """
    global _initialized
    _initialized = True
    logger.info("Mesh router initialised.")


@mesh_router.get("/health")
async def mesh_health() -> JSONResponse:
    return JSONResponse(content={"engine": "mesh", "initialized": _initialized})


@mesh_router.get("/peers")
async def mesh_peers() -> JSONResponse:
    return JSONResponse(content={
        "engine": "mesh",
        "peers": [],
        "note": "Peer discovery not yet implemented."
    })


@mesh_router.post("/send")
async def mesh_send(payload: dict) -> JSONResponse:
    return JSONResponse(content={
        "engine": "mesh",
        "note": "Mesh send not yet implemented.",
        "payload": payload
    })
