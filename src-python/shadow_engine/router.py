"""
shadow_engine/router.py
FastAPI router for the Shadow Engine.

Mounts at: /shadow
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing   import Optional

from fastapi            import APIRouter, HTTPException
from fastapi.responses  import JSONResponse
from pydantic           import BaseModel

from .engine import ShadowEngine
from .types  import ShadowRecord

router = APIRouter(prefix="/shadow", tags=["shadow"])
_engine = ShadowEngine()


# ── Schemas ────────────────────────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    principal_id: str
    source:       str = "on_demand"
    # Optional: pass raw inputs to skip stream fetching (used in tests)
    affect_trend:  Optional[dict] = None
    stage_record:  Optional[dict] = None


class IntegrateRequest(BaseModel):
    principal_id: str


# ── Routes ─────────────────────────────────────────────────────────────────

@router.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "shadow_engine",
            "timestamp": datetime.now(timezone.utc).isoformat()}


@router.get("/state/{principal_id}")
async def get_state(principal_id: str) -> JSONResponse:
    record = await _engine.get_current(principal_id)
    if record is None:
        # Auto-evaluate on first request
        record = await _engine.evaluate(principal_id, source="on_demand")
    return JSONResponse(_serialise(record))


@router.get("/history/{principal_id}")
async def get_history(principal_id: str, days: int = 7) -> JSONResponse:
    # Transitions are stored in SovereignMemory; return in-memory list for now
    # Full persistence integration is a follow-up to this issue.
    return JSONResponse({"principal_id": principal_id, "days": days, "transitions": []})


@router.post("/evaluate")
async def evaluate(req: EvaluateRequest) -> JSONResponse:
    from .archetypes import ShadowInputs

    override: Optional[ShadowInputs] = None
    if req.affect_trend or req.stage_record:
        override = {}
        if req.affect_trend:
            at = req.affect_trend
            override.update({
                "dominant_emotion": at.get("dominant_emotion", "neutral"),
                "valence_trend":    float(at.get("valence_trend", 0.0)),
                "mood_momentum":    float(at.get("mood_momentum", 0.0)),
                "volatility":       min(1.0, float(at.get("volatility", 0.0))),
                "is_volatile":      bool(at.get("is_volatile", False)),
                "arc_stability":    float(at.get("arc_stability", 0.5)),
                "low_energy_flag":  bool(at.get("low_energy_flag", False)),
                "arousal":          min(1.0, float(at.get("mean_arousal", 0.5))),
            })
        if req.stage_record:
            sr = req.stage_record
            m  = sr.get("marker_scores", {})
            override.update({
                "decision_entropy":        float(m.get("decision_entropy", 50.0)),
                "hrv_coherence":           float(m.get("hrv_coherence", 50.0)),
                "journaling_depth":        float(m.get("journaling_depth", 50.0)),
                "focus_session_length":    float(m.get("focus_session_length", 50.0)),
                "goal_completion_rate":    float(m.get("goal_completion_rate", 50.0)),
                "emotional_arc_stability": float(m.get("emotional_arc_stability", 50.0)),
                "days_in_stage":           int(sr.get("days_in_stage", 0)),
                "regression_active":       bool(sr.get("regression_active", False)),
            })

    record = await _engine.evaluate(
        req.principal_id,
        source=req.source,
        override_inputs=override,
    )
    return JSONResponse(_serialise(record))


@router.post("/integrate")
async def integrate(req: IntegrateRequest) -> JSONResponse:
    gain = _engine.record_reflection_session(req.principal_id)
    cached = await _engine.get_current(req.principal_id)
    return JSONResponse({
        "principal_id": req.principal_id,
        "gain":         gain,
        "integration_progress": cached.integration_progress if cached else 0.0,
    })


# ── Helpers ────────────────────────────────────────────────────────────────

def _serialise(record: ShadowRecord) -> dict:
    return {
        "principal_id":         record.principal_id,
        "active_archetype":     record.active_archetype,
        "co_active":            record.co_active,
        "archetype_scores":     record.archetype_scores,
        "shadow_intensity":     record.shadow_intensity,
        "integration_progress": record.integration_progress,
        "days_active":          record.days_active,
        "last_evaluated":       record.last_evaluated.isoformat(),
        "evaluation_source":    record.evaluation_source,
    }
