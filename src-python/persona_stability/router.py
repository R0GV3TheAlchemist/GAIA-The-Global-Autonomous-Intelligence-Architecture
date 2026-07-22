"""
persona_stability.router
========================
FastAPI router for Persona Stability Engine endpoints.

Endpoints
---------
  GET /persona/health   — liveness probe
  GET /persona/profile  — current persona stability profile

Reference: NEXUS_UNIVERSAL_OS.md  Domain 2.5
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from persona_stability.engine import PersonaStabilityEngine

logger = logging.getLogger("persona_stability.router")

router = APIRouter(
    prefix="/persona",
    tags=["persona"],
    responses={404: {"description": "Persona endpoint not found"}},
)

_engine: Optional[PersonaStabilityEngine] = None


def init_persona_engine(engine: PersonaStabilityEngine) -> None:
    """Inject the PersonaStabilityEngine into this router."""
    global _engine
    _engine = engine
    logger.info("PersonaStabilityEngine router initialised.")


@router.get("/health")
async def persona_health() -> JSONResponse:
    return JSONResponse(content={"engine": "persona-stability", "status": "online"})


@router.get("/profile")
async def persona_profile() -> JSONResponse:
    return JSONResponse(content={"engine": "persona-stability", "note": "Profile evaluation not yet implemented."})
