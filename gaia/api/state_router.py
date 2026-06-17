"""
gaia/api/state_router.py
========================
GAIA State API — FastAPI Router
Canon reference: C52, GAIA_D6_META_COHERENCE_ENGINE.md
Issues: #576, #571

Exposes GAIAState and D6Engine via REST + WebSocket.
The Tauri frontend connects to these endpoints for the State HUD.

Endpoints:
  GET  /state              — current GAIAState snapshot
  POST /state              — update specific GAIAState fields
  POST /state/mode         — manually set mode
  POST /state/reset        — reset to default healthy state
  GET  /state/health       — full D6Engine health report (HUD payload)
  GET  /state/interventions — recent intervention log
  POST /state/talisman/activate   — activate a talisman
  POST /state/talisman/deactivate — deactivate a talisman
  WS   /state/ws           — real-time state stream
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from gaia.core.state import GAIAState, GAIAMode, default_state
from gaia.core.d6_engine import D6Engine, EngineProbes
from gaia.core.talisman import Talisman, TalismanEngine, make_talisman


# ---------------------------------------------------------------------------
# Router and shared instances
# (In production these would be injected via dependency injection;
#  for v0.x a module-level singleton is fine.)
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/state", tags=["state"])

# Singleton state and engine for this session
# In a multi-GAIAN deployment, these would be keyed by gaian_id/session_id
_state: GAIAState = default_state()
_engine: D6Engine = D6Engine(auto_apply=False)
_talisman_engine: TalismanEngine = TalismanEngine()
_talismans: Dict[str, Talisman] = {}  # id -> Talisman

# WebSocket connection pool
_ws_connections: List[WebSocket] = []


async def _broadcast_state():
    """Push current state snapshot to all connected WebSocket clients."""
    if not _ws_connections:
        return
    payload = json.dumps({
        "type": "STATE_UPDATE",
        "state": _state.to_dict(include_history=False),
        "t": time.time(),
    })
    dead = []
    for ws in _ws_connections:
        try:
            await ws.send_text(payload)
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_connections.remove(ws)


# ---------------------------------------------------------------------------
# Pydantic request/response models
# ---------------------------------------------------------------------------

class StateUpdateRequest(BaseModel):
    energy: Optional[float] = Field(None, ge=0.0, le=1.0)
    coherence: Optional[float] = Field(None, ge=0.0, le=1.0)
    stress: Optional[float] = Field(None, ge=0.0, le=1.0)
    learning_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    exploration_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    conservation_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    entropy: Optional[float] = Field(None, ge=0.0, le=1.0)


class ModeSetRequest(BaseModel):
    mode: str


class ProbesRequest(BaseModel):
    heart_rate_variability: Optional[float] = None
    sleep_quality: Optional[float] = None
    movement_today: Optional[float] = None
    noosphere_load: Optional[float] = None
    collective_coherence: Optional[float] = None
    schumann_coherence: Optional[float] = None
    lunar_phase_load: Optional[float] = None
    session_duration_hours: Optional[float] = None
    time_since_rest_hours: Optional[float] = None


class TalismanActivateRequest(BaseModel):
    talisman_id: Optional[str] = None   # activate existing by ID
    talisman_data: Optional[Dict[str, Any]] = None  # or create+activate inline
    activated_by: Optional[str] = None


class TalismanDeactivateRequest(BaseModel):
    talisman_id: str
    deactivated_by: Optional[str] = None


# ---------------------------------------------------------------------------
# REST Endpoints
# ---------------------------------------------------------------------------

@router.get("", summary="Get current GAIAState")
async def get_state() -> Dict[str, Any]:
    """Return the current GAIAState snapshot."""
    return _state.to_dict(include_history=False)


@router.post("", summary="Update GAIAState fields")
async def update_state(body: StateUpdateRequest) -> Dict[str, Any]:
    """Apply partial updates to GAIAState. Only provided fields are changed."""
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update.")
    try:
        _state.update(**updates)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    await _broadcast_state()
    return _state.to_dict(include_history=False)


@router.post("/mode", summary="Manually set operational mode")
async def set_mode(body: ModeSetRequest) -> Dict[str, Any]:
    """Override the current operational mode."""
    try:
        mode = GAIAMode(body.mode)
    except ValueError:
        valid = [m.value for m in GAIAMode]
        raise HTTPException(
            status_code=422,
            detail=f"Invalid mode '{body.mode}'. Valid: {valid}"
        )
    _state.update(mode=mode)
    await _broadcast_state()
    return {"mode": _state.mode.value, "state": _state.to_dict(include_history=False)}


@router.post("/reset", summary="Reset state to healthy baseline")
async def reset_state() -> Dict[str, Any]:
    """Reset GAIAState to default healthy baseline."""
    global _state
    _state = default_state(
        gaian_id=_state.gaian_id,
        session_id=_state.session_id,
    )
    await _broadcast_state()
    return _state.to_dict(include_history=False)


@router.get("/health", summary="D6Engine full health report")
async def get_health(probes: Optional[ProbesRequest] = None) -> Dict[str, Any]:
    """Full D6 Meta-Coherence Engine health report — primary HUD payload."""
    probe_obj = EngineProbes(
        **(probes.model_dump() if probes else {})
    ) if probes else EngineProbes()
    return _engine.health_report(_state, probe_obj)


@router.get("/interventions", summary="Recent D6 intervention log")
async def get_interventions(n: int = 20) -> Dict[str, Any]:
    """Return recent D6Engine intervention events."""
    return {
        "interventions": _engine.recent_interventions(n),
        "total": len(_engine.intervention_log),
        "critical_count": len(_engine.critical_interventions()),
    }


@router.post("/talisman/activate", summary="Activate a talisman")
async def activate_talisman(body: TalismanActivateRequest) -> Dict[str, Any]:
    """Activate a talisman by ID or create + activate inline."""
    if body.talisman_id:
        talisman = _talismans.get(body.talisman_id)
        if not talisman:
            raise HTTPException(status_code=404, detail=f"Talisman '{body.talisman_id}' not found.")
    elif body.talisman_data:
        try:
            talisman = Talisman.from_dict(body.talisman_data)
        except Exception as e:
            raise HTTPException(status_code=422, detail=f"Invalid talisman data: {e}")
        _talismans[talisman.id] = talisman
    else:
        raise HTTPException(status_code=400, detail="Provide talisman_id or talisman_data.")

    event = _talisman_engine.activate(talisman, _state, activated_by=body.activated_by)
    await _broadcast_state()
    return {"event": event, "state": _state.to_dict(include_history=False)}


@router.post("/talisman/deactivate", summary="Deactivate a talisman")
async def deactivate_talisman(body: TalismanDeactivateRequest) -> Dict[str, Any]:
    """Deactivate an active talisman."""
    talisman = _talismans.get(body.talisman_id)
    if not talisman:
        raise HTTPException(status_code=404, detail=f"Talisman '{body.talisman_id}' not found.")
    event = _talisman_engine.deactivate(talisman, _state, deactivated_by=body.deactivated_by)
    await _broadcast_state()
    return {"event": event, "state": _state.to_dict(include_history=False)}


# ---------------------------------------------------------------------------
# WebSocket — real-time state stream
# ---------------------------------------------------------------------------

@router.websocket("/ws")
async def state_websocket(websocket: WebSocket):
    """
    Real-time state stream for the Tauri frontend.

    On connect: immediately sends current state snapshot.
    Listens for JSON messages:
      { "type": "UPDATE", "fields": { ... } }  → partial state update
      { "type": "MODE", "mode": "BUILD" }       → mode override
      { "type": "PING" }                        → { "type": "PONG" }

    Broadcasts STATE_UPDATE to all connected clients on any change.
    """
    await websocket.accept()
    _ws_connections.append(websocket)

    # Send initial state snapshot
    await websocket.send_text(json.dumps({
        "type": "STATE_INIT",
        "state": _state.to_dict(include_history=False),
        "t": time.time(),
    }))

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "ERROR", "detail": "Invalid JSON"}))
                continue

            msg_type = msg.get("type", "")

            if msg_type == "PING":
                await websocket.send_text(json.dumps({"type": "PONG", "t": time.time()}))

            elif msg_type == "UPDATE":
                updates = {k: v for k, v in msg.get("fields", {}).items() if v is not None}
                if updates:
                    try:
                        _state.update(**updates)
                        await _broadcast_state()
                    except (ValueError, AttributeError) as e:
                        await websocket.send_text(json.dumps({"type": "ERROR", "detail": str(e)}))

            elif msg_type == "MODE":
                try:
                    mode = GAIAMode(msg.get("mode", ""))
                    _state.update(mode=mode)
                    await _broadcast_state()
                except ValueError:
                    await websocket.send_text(json.dumps({
                        "type": "ERROR",
                        "detail": f"Invalid mode: {msg.get('mode')}"
                    }))

            else:
                await websocket.send_text(json.dumps({
                    "type": "UNKNOWN",
                    "detail": f"Unknown message type: {msg_type}"
                }))

    except WebSocketDisconnect:
        if websocket in _ws_connections:
            _ws_connections.remove(websocket)
