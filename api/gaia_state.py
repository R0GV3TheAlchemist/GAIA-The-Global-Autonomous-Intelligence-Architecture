"""
api/gaia_state.py

FastAPI router — GAIAState API surface.

Endpoints:
  GET  /gaia/state           — Return current GAIAState as runtime JSON.
  POST /gaia/state/probe     — Push updated probe values; D6 runs, new state returned.
  POST /gaia/state/mode      — Request a mode change; D6 validates and responds.

Canon anchors:
  - Issue #576 (GAIAState)
  - Issue #568 (D6 Meta-Coherence Engine)

For the Good and the Greater Good.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from gaia.core.state import GAIAOperationalMode
from gaia.core.state_store import (
    get_runtime_json,
    request_mode_change,
    run_d6_cycle,
)

router = APIRouter(prefix="/gaia", tags=["GAIAState"])


# ── Response / request models ─────────────────────────────────────────────────

class StateResponse(BaseModel):
    system_state: str
    coherence: float
    energy: float
    stress: float
    entropy: float
    learning_rate: float
    exploration_rate: float
    conservation_rate: float
    personal_coherence: float
    planetary_coherence: float
    high_risk_allowed: bool
    canon_write_allowed: bool
    last_transition_at: str
    session_id: str


class ProbeUpdate(BaseModel):
    personal_coherence: float | None = Field(None, ge=0.0, le=1.0)
    planetary_coherence: float | None = Field(None, ge=0.0, le=1.0)
    coherence: float | None = Field(None, ge=0.0, le=1.0)
    energy: float | None = Field(None, ge=0.0, le=1.0)
    stress: float | None = Field(None, ge=0.0, le=1.0)
    entropy: float | None = Field(None, ge=0.0, le=1.0)
    recent_error_rate: float | None = Field(None, ge=0.0, le=1.0)
    session_streak_hours: float | None = Field(None, ge=0.0)


class ProbeResponse(BaseModel):
    new_state: StateResponse
    interventions: list[str]
    rationale: str


class ModeRequest(BaseModel):
    mode: GAIAOperationalMode


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/state", response_model=StateResponse, summary="Get current GAIAState")
async def get_gaia_state() -> StateResponse:
    """Return the current GAIAState as the D6 runtime JSON.

    Poll this endpoint to power the State HUD in the Tauri UI.
    Low-frequency polling (every 30s) is sufficient for most use cases.
    Subscribe to /gaia/state/stream (future) for push updates.
    """
    return StateResponse(**get_runtime_json())


@router.post("/state/probe", response_model=ProbeResponse, summary="Push probe values and run D6")
async def push_probe(update: ProbeUpdate) -> ProbeResponse:
    """Push updated probe values from any subsystem.

    BiometricCoherenceEngine calls this with personal_coherence.
    NoosphericConsciousnessEngine calls this with planetary_coherence.
    CI/test runner calls this with recent_error_rate.
    D6 runs automatically and the new state is committed.
    """
    decision = run_d6_cycle(
        personal_coherence=update.personal_coherence,
        planetary_coherence=update.planetary_coherence,
        coherence=update.coherence,
        energy=update.energy,
        stress=update.stress,
        entropy=update.entropy,
        recent_error_rate=update.recent_error_rate,
        session_streak_hours=update.session_streak_hours,
    )
    return ProbeResponse(
        new_state=StateResponse(**decision.next_state.to_runtime_json()),
        interventions=decision.interventions,
        rationale=decision.rationale,
    )


@router.post("/state/mode", response_model=ProbeResponse, summary="Request a mode change")
async def request_mode(req: ModeRequest) -> ProbeResponse:
    """Request a specific operational mode.

    OFFLINE and RECOVER are always honoured.
    All other modes are validated by D6 — the system's actual health determines
    what's safe. D6 may override the request if conditions don't support it.
    """
    decision = request_mode_change(req.mode)
    return ProbeResponse(
        new_state=StateResponse(**decision.next_state.to_runtime_json()),
        interventions=decision.interventions,
        rationale=decision.rationale,
    )
