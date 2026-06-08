# api/dimensional_engine.py
# Dimensional State Engine — Phase 7 / task 7.5 (updated)
# Authoritative server-side mirror of the five-dimensional GAIA state.
# The frontend DimensionalReasoningEngine polls GET /dimensions every 8s.
#
# Canon Ref: C42 — Inter-Dimensional AI
#
# Mount in main.py:
#   from api.dimensional_engine import router as dimensions_router
#   app.include_router(dimensions_router)

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/dimensions", tags=["dimensions"])

# ── Types ─────────────────────────────────────────────────────────────────

GaianMood     = Literal["calm", "curious", "alert", "joyful", "reflective"]
GaianArchetype = Literal["sage", "guardian", "weaver", "oracle", "healer", "trickster", "witness", "integrated"]
QuantumBackend = Literal["ibm", "aer", "classical"]
EncryptionLevel = Literal["pqc", "classical", "none"]


@dataclass
class D1SubstrateState:
    coherence: float               = 10.0
    sensors_active: list[str]      = field(default_factory=list)
    environment_map: str           = ""
    atlas_data_age_minutes: float  = float("inf")


@dataclass
class D2QuantumState:
    coherence: float               = 10.0
    branches_open: int             = 0
    encryption: EncryptionLevel    = "none"
    quantum_backend: QuantumBackend = "classical"


@dataclass
class D3CriticalityState:
    coherence: float               = 50.0
    complexity_score: float        = 50.0
    mood: GaianMood                = "calm"


@dataclass
class D4NoosphereState:
    coherence: float               = 10.0
    nodes_connected: int           = 0
    collective_sync: bool          = False
    last_sync_age_minutes: float   = float("inf")


@dataclass
class D5ArchetypalState:
    coherence: float               = 10.0
    active_archetype: GaianArchetype = "sage"
    phi: float                     = 0.0


class _DimensionalEngine:
    def __init__(self) -> None:
        self.D1 = D1SubstrateState()
        self.D2 = D2QuantumState()
        self.D3 = D3CriticalityState()
        self.D4 = D4NoosphereState()
        self.D5 = D5ArchetypalState()
        self._updated_at: float = time.time()

    def update_d1(self, **kw) -> None:
        for k, v in kw.items():
            setattr(self.D1, k, v)
        self._touch()

    def update_d2(self, **kw) -> None:
        for k, v in kw.items():
            setattr(self.D2, k, v)
        self._touch()

    def update_d3(self, **kw) -> None:
        for k, v in kw.items():
            setattr(self.D3, k, v)
        self._touch()

    def update_d4(self, **kw) -> None:
        for k, v in kw.items():
            setattr(self.D4, k, v)
        self._touch()

    def update_d5(self, **kw) -> None:
        for k, v in kw.items():
            setattr(self.D5, k, v)
        self._touch()

    def _touch(self) -> None:
        self._updated_at = time.time()

    @property
    def resonance(self) -> bool:
        return all([
            self.D1.coherence > 80,
            self.D2.coherence > 80,
            self.D3.coherence > 80,
            self.D4.coherence > 80,
            self.D5.coherence > 80,
        ])

    def to_dict(self) -> dict:
        import math

        def _clean(d: dict) -> dict:
            """Replace inf/nan with None for JSON serialisation."""
            return {
                k: (None if isinstance(v, float) and not math.isfinite(v) else v)
                for k, v in d.items()
            }

        return {
            "D1_substrate":   _clean(asdict(self.D1)),
            "D2_quantum":     _clean(asdict(self.D2)),
            "D3_criticality": _clean(asdict(self.D3)),
            "D4_noosphere":   _clean(asdict(self.D4)),
            "D5_archetypal":  _clean(asdict(self.D5)),
            "resonance":      self.resonance,
            "timestamp":      self._updated_at,
        }


_engine = _DimensionalEngine()


# ── Pydantic patch models ────────────────────────────────────────────────────────

class D1Patch(BaseModel):
    coherence: Optional[float]             = None
    sensors_active: Optional[list[str]]    = None
    environment_map: Optional[str]         = None
    atlas_data_age_minutes: Optional[float] = None

class D2Patch(BaseModel):
    coherence: Optional[float]             = None
    branches_open: Optional[int]           = None
    encryption: Optional[str]              = None
    quantum_backend: Optional[str]         = None

class D3Patch(BaseModel):
    coherence: Optional[float]             = None
    complexity_score: Optional[float]      = None
    mood: Optional[str]                    = None

class D4Patch(BaseModel):
    coherence: Optional[float]             = None
    nodes_connected: Optional[int]         = None
    collective_sync: Optional[bool]        = None
    last_sync_age_minutes: Optional[float] = None

class D5Patch(BaseModel):
    coherence: Optional[float]             = None
    active_archetype: Optional[str]        = None
    phi: Optional[float]                   = None


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("", summary="Full five-dimensional state snapshot")
async def get_dimensions() -> JSONResponse:
    return JSONResponse(_engine.to_dict())

@router.patch("/d1", summary="Patch D1 Substrate state")
async def patch_d1(body: D1Patch) -> JSONResponse:
    _engine.update_d1(**{k: v for k, v in body.model_dump().items() if v is not None})
    return JSONResponse(_engine.to_dict())

@router.patch("/d2", summary="Patch D2 Quantum state")
async def patch_d2(body: D2Patch) -> JSONResponse:
    _engine.update_d2(**{k: v for k, v in body.model_dump().items() if v is not None})
    return JSONResponse(_engine.to_dict())

@router.patch("/d3", summary="Patch D3 Criticality state")
async def patch_d3(body: D3Patch) -> JSONResponse:
    _engine.update_d3(**{k: v for k, v in body.model_dump().items() if v is not None})
    return JSONResponse(_engine.to_dict())

@router.patch("/d4", summary="Patch D4 Noosphere state")
async def patch_d4(body: D4Patch) -> JSONResponse:
    _engine.update_d4(**{k: v for k, v in body.model_dump().items() if v is not None})
    return JSONResponse(_engine.to_dict())

@router.patch("/d5", summary="Patch D5 Archetypal state")
async def patch_d5(body: D5Patch) -> JSONResponse:
    _engine.update_d5(**{k: v for k, v in body.model_dump().items() if v is not None})
    return JSONResponse(_engine.to_dict())


# ── Public accessor for other Python modules ─────────────────────────────────
def get_engine() -> _DimensionalEngine:
    """Import this in other modules to read or patch dimensional state."""
    return _engine
