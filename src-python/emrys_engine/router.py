"""
src-python/emrys_engine/router.py
GAIA-OS Emrys L2 Vibronic Bridge — FastAPI APIRouter

Exposes EmrysCycle (src/crystals/emryscycle.py) as REST endpoints.
All routes are read-only GET requests. The EmrysCycle instance is
created once at startup by init_emrys_engine() and cached at module
level. CrystalDB is immutable after load, so concurrent reads are safe.

Routes (all prefixed /api/emrys in main.py include_router call):
  GET /field-report          — full EmrysFieldReport
  GET /cold-start            — C165a cold-start sequence
  GET /grounding             — C165 Grounding Protocol
  GET /state/{state}         — best crystal for L2 state
  GET /crystals              — all L2-compatible crystal resonators

Registration in main.py:
    from emrys_engine.router import emrys_router, init_emrys_engine
    init_emrys_engine()
    app.include_router(emrys_router, prefix="/api/emrys", tags=["Emrys"])

Per C164: the router is the digital bridge. The crystals are real.
Per C165.1: grounding precedes coherence. Always.
Per C166.A4: physics and metaphysics are the same layer.
"""

from __future__ import annotations

import sys
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from .models import (
    EmrysFieldReportModel,
    VibronicResonatorModel,
    ColdStartStepModel,
    GroundingProtocolModel,
    L2_STATES,
)

# ---------------------------------------------------------------------------
# Path resolution
# Allow import of emryscycle and crystal_db regardless of working directory.
# Works for: uvicorn main:app (from project root), pytest, and direct run.
# ---------------------------------------------------------------------------
_CRYSTALS_DIR = Path(__file__).resolve().parents[2] / "src" / "crystals"
if str(_CRYSTALS_DIR) not in sys.path:
    sys.path.insert(0, str(_CRYSTALS_DIR))

try:
    from emryscycle import EmrysCycle, L2CoherenceState
    from crystal_db import CrystalDB
except ImportError as e:
    raise ImportError(
        f"emrys_engine.router: cannot import EmrysCycle/CrystalDB — "
        f"ensure src/crystals/ exists and emryscycle.py + crystal_db.py "
        f"are present. Original error: {e}"
    ) from e

# ---------------------------------------------------------------------------
# Module-level singleton (initialised by init_emrys_engine)
# ---------------------------------------------------------------------------
_cycle: Optional[EmrysCycle] = None


def init_emrys_engine() -> None:
    """
    Initialise the Emrys engine singleton.
    Call once at application startup before the first request.

    Example (main.py lifespan or startup event):
        @app.on_event("startup")
        async def startup():
            init_emrys_engine()

    Or directly before app.include_router():
        init_emrys_engine()
        app.include_router(emrys_router, prefix="/api/emrys", tags=["Emrys"])
    """
    global _cycle
    db = CrystalDB()
    _cycle = EmrysCycle(db)
    count = _cycle.l2_crystal_count()
    print(
        f"[emrys_engine] Initialised — "
        f"{count} L2-compatible crystal(s) loaded.",
        flush=True,
    )


def _get_cycle() -> EmrysCycle:
    """Return singleton or raise 503 if not yet initialised."""
    if _cycle is None:
        raise HTTPException(
            status_code=503,
            detail=(
                "Emrys engine not initialised. "
                "Call init_emrys_engine() during application startup."
            ),
        )
    return _cycle


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
emrys_router = APIRouter()


# ─────────────────────────────────────────────────────────────
# GET /field-report
# ─────────────────────────────────────────────────────────────
@emrys_router.get(
    "/field-report",
    response_model=EmrysFieldReportModel,
    summary="Full Emrys L2 field report",
    description=(
        "Returns the complete Emrys L2 vibronic field report: "
        "all L2-compatible crystals with resonator data, state index, "
        "C165a cold-start sequence, and C165 Grounding Protocol. "
        "Optionally inject GAIAN EV1B stage context via ?stage=."
    ),
)
async def get_field_report(
    stage: Optional[str] = Query(
        default=None,
        description=(
            "GAIAN EV1B stage name (e.g. 'Initiation'). "
            "When provided, the grounding protocol includes "
            "stage-specific L2 crystal context."
        ),
    ),
) -> dict:
    cycle = _get_cycle()
    try:
        return cycle.emrys_field_report()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Emrys field report generation failed: {exc}",
        ) from exc


# ─────────────────────────────────────────────────────────────
# GET /cold-start
# ─────────────────────────────────────────────────────────────
@emrys_router.get(
    "/cold-start",
    response_model=list[ColdStartStepModel],
    summary="C165a cold-start crystal activation sequence",
    description=(
        "Returns the ordered 4-step crystal activation sequence per C165a. "
        "Steps proceed GROUNDING → BRIDGING → COHERENCE → PEAK. "
        "Per C165a: do not skip steps. Each activation is irreversible."
    ),
)
async def get_cold_start() -> list[dict]:
    cycle = _get_cycle()
    try:
        return cycle.cold_start_sequence()
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Cold-start sequence generation failed: {exc}",
        ) from exc


# ─────────────────────────────────────────────────────────────
# GET /grounding
# ─────────────────────────────────────────────────────────────
@emrys_router.get(
    "/grounding",
    response_model=GroundingProtocolModel,
    summary="C165 Grounding Protocol",
    description=(
        "Returns the full C165 Grounding Protocol with phase-by-phase "
        "crystal placement instructions. "
        "Per C165.1: grounding precedes coherence. Always. "
        "Optionally inject GAIAN EV1B stage context via ?stage=."
    ),
)
async def get_grounding(
    stage: Optional[str] = Query(
        default=None,
        description="GAIAN EV1B stage name for stage-specific crystal context.",
    ),
) -> dict:
    cycle = _get_cycle()
    try:
        return cycle.grounding_protocol(gaian_stage=stage)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Grounding protocol generation failed: {exc}",
        ) from exc


# ─────────────────────────────────────────────────────────────
# GET /state/{state}
# ─────────────────────────────────────────────────────────────
@emrys_router.get(
    "/state/{state}",
    response_model=VibronicResonatorModel,
    summary="Best crystal for a given L2 coherence state",
    description=(
        "Returns the highest-confidence VibronicResonator for the "
        "requested L2CoherenceState. "
        "Valid states: GROUNDING, BRIDGING, COHERENCE, PEAK. "
        "Optional ?anchor= parameter biases selection toward a specific "
        "backbone anchor (YSZ | BTS | AlScN-GaN)."
    ),
)
async def get_state_crystal(
    state: str,
    anchor: Optional[str] = Query(
        default=None,
        description="Prefer crystals with this backbone anchor (YSZ | BTS | AlScN-GaN).",
    ),
) -> dict:
    state_upper = state.upper()
    if state_upper not in L2_STATES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Invalid L2 state: '{state}'. "
                f"Valid values: {L2_STATES}."
            ),
        )
    cycle = _get_cycle()
    try:
        l2_state = L2CoherenceState(state_upper)
        resonator = cycle.match_crystal_to_state(l2_state, prefer_anchor=anchor)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"State matching failed: {exc}",
        ) from exc

    if resonator is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"No L2-compatible crystal available for state '{state_upper}'. "
                f"Ensure at least one crystal has emrys_l2_compatible: true "
                f"and a resonant_frequency_hz range overlapping this state."
            ),
        )

    return asdict(resonator)


# ─────────────────────────────────────────────────────────────
# GET /crystals
# ─────────────────────────────────────────────────────────────
@emrys_router.get(
    "/crystals",
    response_model=list[VibronicResonatorModel],
    summary="All L2-compatible crystal resonators",
    description=(
        "Returns all crystals flagged emrys_l2_compatible: true, "
        "sorted alphabetically by name. Each entry includes full "
        "VibronicResonator data: frequency range, active L2 states, "
        "backbone anchor, piezoelectric and pyroelectric parameters."
    ),
)
async def get_crystals() -> list[dict]:
    cycle = _get_cycle()
    try:
        return [asdict(r) for r in cycle.all_resonators()]
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Crystal list generation failed: {exc}",
        ) from exc
