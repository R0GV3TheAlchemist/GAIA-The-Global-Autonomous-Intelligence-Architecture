"""
state_router.py
GAIA-OS Core — FastAPI Router: GAIAState + D6 + Talisman Endpoints

This router is mounted onto the main FastAPI sidecar app.
The Tauri Rust bridge calls these endpoints via the sidecar HTTP client.
Dev mode: React can also call these directly via SIDECAR_BASE (localhost:8765).

Endpoints:
  GET    /api/state                       — get current GAIAState snapshot
  PATCH  /api/state                       — update state fields (D6 re-evaluates)
  POST   /api/state/override              — Architect signal override
  GET    /api/state/evaluate              — D6 dry-run (no write)
  GET    /api/state/history               — last N snapshots

  GET    /api/talismans                   — list all talismans
  POST   /api/talismans                   — create talisman
  GET    /api/talismans/{id}              — get single talisman
  PATCH  /api/talismans/{id}              — update talisman fields
  DELETE /api/talismans/{id}              — delete talisman
  POST   /api/talismans/{id}/activate     — activate (applies field_effect)
  POST   /api/talismans/{id}/deactivate   — deactivate (reverses field_effect)

Canon anchor: Issue #576, Issue #568, Issue #580
Author: The Human Architect + GAIA
Created: June 17, 2026
"""

from __future__ import annotations

import time
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .state import (
    GAIAState,
    GAIAMode,
    ArchitectSignal,
    GAIAStateStore,
    D6Intervention,
    d6_evaluate,
)
from .talisman import (
    Talisman,
    TalismanFieldEffect,
    TalismanEngine,
    TalismanStatus,
)

router = APIRouter(prefix="/api", tags=["gaia-state"])

# ---------------------------------------------------------------------------
# Shared singletons — one store + one engine per process
# ---------------------------------------------------------------------------

_store  = GAIAStateStore.instance()
_engine = TalismanEngine(_store)


# ---------------------------------------------------------------------------
# Pydantic request / response models
# ---------------------------------------------------------------------------

class StateUpdateRequest(BaseModel):
    coherence:         Optional[float] = None
    energy:            Optional[float] = None
    stress:            Optional[float] = None
    entropy:           Optional[float] = None
    learning_rate:     Optional[float] = None
    exploration_rate:  Optional[float] = None
    conservation_rate: Optional[float] = None


class ArchitectOverrideRequest(BaseModel):
    signal: ArchitectSignal


class TalismanFieldEffectModel(BaseModel):
    coherence:         Optional[float] = None
    energy:            Optional[float] = None
    stress:            Optional[float] = None
    entropy:           Optional[float] = None
    learning_rate:     Optional[float] = None
    exploration_rate:  Optional[float] = None
    conservation_rate: Optional[float] = None


class TalismanCreateRequest(BaseModel):
    name:         str = "Unnamed Talisman"
    intent:       str = ""
    field_effect: TalismanFieldEffectModel = Field(default_factory=TalismanFieldEffectModel)
    owner_id:     Optional[str] = None
    crystal_ids:  list[str] = Field(default_factory=list)
    expires_at:   Optional[float] = None
    tags:         list[str] = Field(default_factory=list)
    notes:        str = ""


class TalismanUpdateRequest(BaseModel):
    name:         Optional[str] = None
    intent:       Optional[str] = None
    field_effect: Optional[TalismanFieldEffectModel] = None
    crystal_ids:  Optional[list[str]] = None
    expires_at:   Optional[float] = None
    tags:         Optional[list[str]] = None
    notes:        Optional[str] = None


# ---------------------------------------------------------------------------
# Helper: D6Intervention → dict
# ---------------------------------------------------------------------------

def _iv_to_dict(iv: D6Intervention) -> dict:
    return {
        "recommended_mode": iv.recommended_mode.value,
        "reason":           iv.reason,
        "urgency":          iv.urgency,
        "previous_mode":    iv.previous_mode.value,
        "timestamp":        iv.timestamp,
    }


# ---------------------------------------------------------------------------
# GAIAState endpoints
# ---------------------------------------------------------------------------

@router.get("/state", summary="Get current GAIAState snapshot")
async def get_state() -> dict:
    """
    Returns the full GAIAState.to_dict() payload plus the last D6 reason.
    Polled by StateHUD every 3 seconds.
    """
    state = _store.get()
    snap  = state.to_dict()
    # Attach last D6 reason from history if available
    history = _store.history(last_n=1)
    if history:
        snap["d6_reason"] = history[-1].get("d6_reason", "")
    return snap


@router.patch("/state", summary="Update GAIAState fields")
async def update_state(body: StateUpdateRequest) -> dict:
    """
    Updates the provided fields. D6 engine re-evaluates and applies
    mode after every write. Returns updated snapshot.
    """
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    state = _store.update(**updates)
    snap  = state.to_dict()
    history = _store.history(last_n=1)
    if history:
        snap["d6_reason"] = history[-1].get("d6_reason", "")
    return snap


@router.post("/state/override", summary="Architect signal override")
async def override_state(body: ArchitectOverrideRequest) -> dict:
    """
    Sends an Architect override signal. D6 respects this above all
    automatic logic (Architect Protocol — Issue #578).
    Returns updated snapshot.
    """
    state = _store.get()
    state.architect_signal = ArchitectSignal(body.signal)
    iv    = _store.evaluate()
    _store.apply(iv)
    snap  = state.to_dict()
    snap["d6_reason"] = iv.reason
    return snap


@router.get("/state/evaluate", summary="D6 dry-run evaluation")
async def evaluate_state() -> dict:
    """
    Runs the D6 engine against current state but does NOT apply the result.
    Useful for the HUD to surface a recommendation without committing.
    """
    iv = _store.evaluate()
    return _iv_to_dict(iv)


@router.get("/state/history", summary="State history snapshots")
async def state_history(n: int = Query(default=50, ge=1, le=500)) -> list[dict]:
    """
    Returns the last N state snapshots with their D6 reasons.
    """
    return _store.history(last_n=n)


# ---------------------------------------------------------------------------
# Talisman endpoints
# ---------------------------------------------------------------------------

@router.get("/talismans", summary="List talismans")
async def list_talismans(owner_id: Optional[str] = Query(default=None)) -> list[dict]:
    """
    List all talismans in the in-memory registry.
    Optionally filter by owner_id.
    """
    talismans = _engine.list_all()
    if owner_id:
        talismans = [t for t in talismans if t.owner_id == owner_id]
    return [t.to_dict() for t in talismans]


@router.post("/talismans", summary="Create talisman", status_code=201)
async def create_talisman(body: TalismanCreateRequest) -> dict:
    """
    Create a new Talisman and register it in the engine.
    """
    fe = TalismanFieldEffect(
        coherence_delta=         body.field_effect.coherence,
        energy_delta=            body.field_effect.energy,
        stress_delta=            body.field_effect.stress,
        entropy_delta=           body.field_effect.entropy,
        learning_rate_delta=     body.field_effect.learning_rate,
        exploration_rate_delta=  body.field_effect.exploration_rate,
        conservation_rate_delta= body.field_effect.conservation_rate,
    )
    talisman = Talisman(
        name=        body.name,
        intent=      body.intent,
        field_effect=fe,
        owner_id=    body.owner_id,
        crystal_ids= body.crystal_ids,
        expires_at=  body.expires_at,
        tags=        body.tags,
        notes=       body.notes,
    )
    _engine.register(talisman)
    return talisman.to_dict()


@router.get("/talismans/{talisman_id}", summary="Get talisman")
async def get_talisman(talisman_id: str) -> dict:
    talisman = _engine.get(talisman_id)
    if not talisman:
        raise HTTPException(status_code=404, detail=f"Talisman '{talisman_id}' not found.")
    return talisman.to_dict()


@router.patch("/talismans/{talisman_id}", summary="Update talisman")
async def update_talisman(talisman_id: str, body: TalismanUpdateRequest) -> dict:
    talisman = _engine.get(talisman_id)
    if not talisman:
        raise HTTPException(status_code=404, detail=f"Talisman '{talisman_id}' not found.")

    if body.name is not None:        talisman.name    = body.name
    if body.intent is not None:      talisman.intent  = body.intent
    if body.crystal_ids is not None: talisman.crystal_ids = body.crystal_ids
    if body.expires_at is not None:  talisman.expires_at  = body.expires_at
    if body.tags is not None:        talisman.tags   = body.tags
    if body.notes is not None:       talisman.notes  = body.notes

    if body.field_effect is not None:
        fe = body.field_effect
        talisman.field_effect = TalismanFieldEffect(
            coherence_delta=         fe.coherence,
            energy_delta=            fe.energy,
            stress_delta=            fe.stress,
            entropy_delta=           fe.entropy,
            learning_rate_delta=     fe.learning_rate,
            exploration_rate_delta=  fe.exploration_rate,
            conservation_rate_delta= fe.conservation_rate,
        )
    return talisman.to_dict()


@router.delete("/talismans/{talisman_id}", summary="Delete talisman")
async def delete_talisman(talisman_id: str) -> dict:
    talisman = _engine.get(talisman_id)
    if not talisman:
        raise HTTPException(status_code=404, detail=f"Talisman '{talisman_id}' not found.")
    # Deactivate first if active
    if talisman.is_active():
        try:
            _engine.deactivate(talisman_id)
        except Exception:
            pass
    del _engine._registry[talisman_id]
    return {"deleted": True}


@router.post("/talismans/{talisman_id}/activate", summary="Activate talisman")
async def activate_talisman(talisman_id: str) -> dict:
    """
    Activates a talisman: applies its field_effect to GAIAState,
    D6 engine re-evaluates mode. Returns { talisman, state }.
    """
    try:
        talisman, state = _engine.activate(talisman_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    snap = state.to_dict()
    history = _store.history(last_n=1)
    if history:
        snap["d6_reason"] = history[-1].get("d6_reason", "")
    return {"talisman": talisman.to_dict(), "state": snap}


@router.post("/talismans/{talisman_id}/deactivate", summary="Deactivate talisman")
async def deactivate_talisman(talisman_id: str) -> dict:
    """
    Deactivates a talisman: reverses its field_effect from GAIAState,
    D6 engine re-evaluates mode. Returns { talisman, state }.
    """
    try:
        talisman, state = _engine.deactivate(talisman_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    snap = state.to_dict()
    history = _store.history(last_n=1)
    if history:
        snap["d6_reason"] = history[-1].get("d6_reason", "")
    return {"talisman": talisman.to_dict(), "state": snap}
