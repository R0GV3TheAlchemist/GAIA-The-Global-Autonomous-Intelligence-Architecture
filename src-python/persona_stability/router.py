"""
Persona Stability FastAPI router — mounted at /persona.

Endpoints
---------
POST /persona/session/begin     — start a new session for an archetype
POST /persona/session/end       — close session, write PersonaTrace
POST /persona/turn              — evaluate a turn, get injection decision
GET  /persona/anchor/{archetype} — retrieve anchor text for an archetype
GET  /persona/status            — current engine state

Issue: #115
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from .engine import PersonaStabilityEngine

logger = logging.getLogger("gaia.persona.router")

router = APIRouter(prefix="/persona", tags=["persona"])

# Module-level engine singleton — injected by init_persona_engine()
_engine: Optional[PersonaStabilityEngine] = None


def init_persona_engine(engine: PersonaStabilityEngine) -> None:
    """Inject the PersonaStabilityEngine singleton (called from main.py lifespan)."""
    global _engine
    _engine = engine
    logger.info("PersonaStabilityEngine injected into router ✓")


def _get_engine() -> PersonaStabilityEngine:
    if _engine is None:
        raise HTTPException(status_code=503, detail="PersonaStabilityEngine not initialised")
    return _engine


# ── Request / Response models ─────────────────────────────────────────────────

class BeginSessionRequest(BaseModel):
    archetype_id: str = Field(..., description="Gaian archetype ID (e.g. 'sage', 'alchemist')")
    voice_baseline: Optional[list[float]] = Field(None, description="Pre-computed voice baseline embedding")


class EndSessionRequest(BaseModel):
    notes: str = Field("", description="Optional session notes")


class TurnRequest(BaseModel):
    response_embedding: Optional[list[float]] = Field(None, description="LLM response embedding vector")
    affect_emotion: Optional[str] = Field(None, description="Top emotion from AffectEngine")
    affect_confidence: float = Field(0.0, ge=0.0, le=1.0, description="Affect confidence score")


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/session/begin")
async def begin_session(req: BeginSessionRequest):
    """Start a new persona stability session for the given archetype."""
    engine = _get_engine()
    engine.begin_session(
        archetype_id=req.archetype_id,
        voice_baseline=req.voice_baseline,
    )
    return {
        "ok": True,
        "session_id": engine.session_id,
        "archetype_id": engine.archetype_id,
    }


@router.post("/session/end")
async def end_session(req: EndSessionRequest):
    """Close the current session and write a PersonaTrace to SovereignMemory."""
    engine = _get_engine()
    trace = engine.end_session(notes=req.notes)
    if trace is None:
        raise HTTPException(status_code=400, detail="No active session to end")
    return {
        "ok": True,
        "session_id": trace.session_id,
        "archetype_id": trace.archetype_id,
        "total_turns": trace.total_turns,
        "drift_count": trace.drift_count,
        "avg_similarity": trace.avg_similarity,
        "duration_minutes": round(trace.duration_minutes, 2),
    }


@router.post("/turn")
async def on_turn(req: TurnRequest):
    """Evaluate a turn and return an anchor injection decision."""
    engine = _get_engine()
    result = engine.on_turn(
        response_embedding=req.response_embedding,
        affect_emotion=req.affect_emotion,
        affect_confidence=req.affect_confidence,
    )
    return {
        "should_inject": result.should_inject,
        "reason": result.reason,
        "anchor_text": result.anchor_text,
        "turn_index": result.turn_index,
    }


@router.get("/anchor/{archetype_id}")
async def get_anchor(archetype_id: str):
    """Retrieve the compressed anchor text for any archetype."""
    from .anchors import get_anchor as _get_anchor
    anchor = _get_anchor(archetype_id)
    return {
        "archetype_id": anchor.archetype_id,
        "essence": anchor.essence,
    }


@router.get("/status")
async def status():
    """Current engine state."""
    engine = _get_engine()
    return {
        "session_id": engine.session_id,
        "archetype_id": engine.archetype_id,
        "turn_index": engine.turn_index,
    }
