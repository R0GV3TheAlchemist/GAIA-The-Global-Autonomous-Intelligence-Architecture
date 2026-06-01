"""FastAPI router for the GAIA-OS Safety Engine — mounted at /safety."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .safety_engine import SafetyEngine
from .types import CrisisLevel, SessionRiskProfile, TurnRiskFrame

router = APIRouter(prefix="/safety", tags=["safety"])

# In-memory engine registry — in production, keyed per user+session in SovereignMemory
_engines: dict[str, SafetyEngine] = {}


class TurnRequest(BaseModel):
    user_id: str
    session_id: str
    turn_index: int
    user_text: str
    mirroring_score: float
    vulnerability_score: float
    affect_valence: float
    affect_arousal: float
    crisis_level: str = "none"
    escalation_delta: float = 0.0
    past_profiles: Optional[List[dict]] = None
    region: str = "default"


class SessionCloseRequest(BaseModel):
    user_id: str
    session_id: str


@router.post("/turn")
async def process_turn(req: TurnRequest):
    """Process a single conversation turn through the safety engine."""
    engine_key = f"{req.user_id}:{req.session_id}"
    if engine_key not in _engines:
        _engines[engine_key] = SafetyEngine(
            user_id=req.user_id,
            session_id=req.session_id,
            region=req.region,
        )

    engine = _engines[engine_key]
    frame = TurnRiskFrame(
        turn_index=req.turn_index,
        timestamp=datetime.utcnow(),
        mirroring_score=req.mirroring_score,
        vulnerability_score=req.vulnerability_score,
        affect_valence=req.affect_valence,
        affect_arousal=req.affect_arousal,
        crisis_level=CrisisLevel(req.crisis_level),
        escalation_delta=req.escalation_delta,
    )

    past_profiles = None
    if req.past_profiles:
        past_profiles = [
            SessionRiskProfile(
                session_id=p["session_id"],
                user_id=p["user_id"],
                started_at=datetime.fromisoformat(p["started_at"]),
                ended_at=datetime.fromisoformat(p["ended_at"]),
                peak_crisis_level=CrisisLevel(p["peak_crisis_level"]),
                mean_vulnerability_score=p["mean_vulnerability_score"],
                escalation_events=p["escalation_events"],
                circuit_breaker_trips=p["circuit_breaker_trips"],
                cumulative_risk_score=p["cumulative_risk_score"],
            )
            for p in req.past_profiles
        ]

    result = engine.process_turn(frame, req.user_text, past_profiles)
    return result


@router.post("/session/close")
async def close_session(req: SessionCloseRequest):
    """Close a session and return its risk profile for storage."""
    engine_key = f"{req.user_id}:{req.session_id}"
    if engine_key not in _engines:
        raise HTTPException(status_code=404, detail="Session engine not found")
    profile = _engines.pop(engine_key).close_session()
    return {
        "session_id": profile.session_id,
        "user_id": profile.user_id,
        "peak_crisis_level": profile.peak_crisis_level.value,
        "mean_vulnerability_score": profile.mean_vulnerability_score,
        "escalation_events": profile.escalation_events,
        "circuit_breaker_trips": profile.circuit_breaker_trips,
        "cumulative_risk_score": profile.cumulative_risk_score,
    }


@router.get("/status/{user_id}/{session_id}")
async def get_status(user_id: str, session_id: str):
    """Return current circuit breaker state for an active session."""
    engine_key = f"{user_id}:{session_id}"
    if engine_key not in _engines:
        return {"state": "no_session"}
    engine = _engines[engine_key]
    return {"state": engine._escalation_detector.state.value}
