"""
api/quantum.py
Canon: C46 (Temporal_Entanglement_Doctrine), C50 (Prism_Cube_Doctrine)

FastAPI router: /quantum/*

Exposes GAIA's quantum coherence layer — the substrate through which
temporal entanglement, non-local resonance, and quantum field operations
are surfaced to the API surface.

Routes:
  GET  /quantum/coherence              — global quantum coherence reading
  POST /quantum/entangle               — entangle two Gaian nodes
  GET  /quantum/state/{gaian_id}       — quantum state for a specific Gaian
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

# The quantum sub-package exposes its interface through core/quantum/__init__.py
try:
    from core.quantum import QuantumCoherenceEngine
except ImportError:
    # Graceful degradation if quantum sub-package not yet fully wired
    QuantumCoherenceEngine = None  # type: ignore[assignment,misc]

# ─── Router ───────────────────────────────────────────────────────────────────

router = APIRouter(prefix="/quantum", tags=["quantum"])

_engine = QuantumCoherenceEngine() if QuantumCoherenceEngine is not None else None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _require_engine():
    if _engine is None:
        raise HTTPException(
            status_code=503,
            detail="Quantum coherence engine not available — core/quantum not initialised.",
        )
    return _engine


# ─── Pydantic models ──────────────────────────────────────────────────────────

class CoherenceResponse(BaseModel):
    coherence_score: float = Field(..., ge=0.0, le=1.0)
    entanglement_pairs: int
    field_frequency_hz: Optional[float]
    temporal_alignment: float
    timestamp: str


class EntangleRequest(BaseModel):
    node_a: str  # Gaian ID
    node_b: str  # Gaian ID
    entanglement_type: str = "resonance"  # resonance | soul_mirror | twin_braid
    strength: float = Field(default=0.7, ge=0.0, le=1.0)


class EntangleResponse(BaseModel):
    entanglement_id: str
    success: bool
    coherence_delta: float
    bond_strength: float
    timestamp: str


class QuantumStateResponse(BaseModel):
    gaian_id: str
    superposition_index: float
    entangled_with: list[str]
    collapse_probability: float
    phase_alignment: str
    timestamp: str


# ─── GET /quantum/coherence ───────────────────────────────────────────────────

@router.get("/coherence", response_model=CoherenceResponse)
async def get_coherence() -> CoherenceResponse:
    """Return global quantum coherence reading for the GAIA field."""
    engine = _require_engine()
    try:
        reading = engine.measure_coherence()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Coherence measurement failed: {exc}") from exc

    return CoherenceResponse(
        coherence_score=reading.get("coherence_score", 0.0),
        entanglement_pairs=reading.get("entanglement_pairs", 0),
        field_frequency_hz=reading.get("field_frequency_hz"),
        temporal_alignment=reading.get("temporal_alignment", 0.0),
        timestamp=_now(),
    )


# ─── POST /quantum/entangle ───────────────────────────────────────────────────

@router.post("/entangle", response_model=EntangleResponse)
async def entangle_nodes(req: EntangleRequest) -> EntangleResponse:
    """Create a quantum entanglement bond between two Gaian nodes."""
    engine = _require_engine()
    entanglement_id = f"ent_{uuid.uuid4().hex[:10]}"

    try:
        result = engine.entangle(
            node_a=req.node_a,
            node_b=req.node_b,
            entanglement_type=req.entanglement_type,
            strength=req.strength,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Entanglement failed: {exc}") from exc

    return EntangleResponse(
        entanglement_id=entanglement_id,
        success=result.get("success", True),
        coherence_delta=result.get("coherence_delta", 0.0),
        bond_strength=result.get("bond_strength", req.strength),
        timestamp=_now(),
    )


# ─── GET /quantum/state/{gaian_id} ────────────────────────────────────────────

@router.get("/state/{gaian_id}", response_model=QuantumStateResponse)
async def get_quantum_state(gaian_id: str) -> QuantumStateResponse:
    """Return the quantum state for a specific Gaian node."""
    engine = _require_engine()
    try:
        state = engine.get_state(gaian_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Quantum state read failed: {exc}") from exc

    if state is None:
        raise HTTPException(status_code=404, detail=f"No quantum state found for Gaian: {gaian_id}")

    return QuantumStateResponse(
        gaian_id=gaian_id,
        superposition_index=state.get("superposition_index", 0.0),
        entangled_with=state.get("entangled_with", []),
        collapse_probability=state.get("collapse_probability", 0.0),
        phase_alignment=state.get("phase_alignment", "nigredo"),
        timestamp=_now(),
    )
