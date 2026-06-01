"""FastAPI router for the Crisis Engine.

Mount with:
    from crisis_engine.router import crisis_router, init_crisis_engine
    app.include_router(crisis_router, prefix="/crisis")

Endpoints:
    GET  /crisis/health           — Liveness probe
    POST /crisis/evaluate         — Evaluate a turn of user text
    GET  /crisis/history/{pid}    — Recent snapshot history for a principal
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .engine import CrisisEngine, EngineConfig
from .types import RiskLevel

crisis_router = APIRouter(tags=["crisis"])

_engines: dict[str, CrisisEngine] = {}


def init_crisis_engine(principal_id: str, db_dir: Optional[Path] = None) -> CrisisEngine:
    """Initialise (or retrieve) a CrisisEngine for a principal."""
    if principal_id not in _engines:
        db_path = (db_dir / f"crisis_{principal_id}.db") if db_dir else None
        _engines[principal_id] = CrisisEngine(
            EngineConfig(principal_id=principal_id, db_path=db_path)
        )
    return _engines[principal_id]


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class EvaluateRequest(BaseModel):
    principal_id: str
    user_text:    str
    session_id:   str
    turn_index:   int = 0


class EvaluateResponse(BaseModel):
    principal_id:         str
    current_risk:         str
    escalation_tier:      str
    trajectory_slope:     float
    sessions_in_distress: int
    peak_risk_72h:        str
    requires_action:      bool
    intervention_message: str
    active_signal_count:  int


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@crisis_router.get("/health")
def health():
    return {"status": "ok", "engines_loaded": len(_engines)}


@crisis_router.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest):
    engine   = init_crisis_engine(req.principal_id)
    snapshot = engine.evaluate(
        user_text=req.user_text,
        session_id=req.session_id,
        turn_index=req.turn_index,
    )
    return EvaluateResponse(
        principal_id=snapshot.principal_id,
        current_risk=snapshot.current_risk.value,
        escalation_tier=snapshot.escalation_tier.value,
        trajectory_slope=round(snapshot.trajectory_slope, 4),
        sessions_in_distress=snapshot.sessions_in_distress,
        peak_risk_72h=snapshot.peak_risk_72h.value,
        requires_action=snapshot.requires_action,
        intervention_message=engine.get_intervention_message(),
        active_signal_count=len(snapshot.active_signals),
    )


@crisis_router.get("/history/{principal_id}")
def history(principal_id: str, limit: int = 30):
    if principal_id not in _engines:
        raise HTTPException(status_code=404, detail="No engine found for principal")
    return {"principal_id": principal_id, "history": _engines[principal_id].history(limit)}
