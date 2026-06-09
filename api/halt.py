"""External halt API — POST /v1/governance/halt and related endpoints.

All write endpoints require a bearer token matching the GAIA_HALT_TOKEN
environment variable. If GAIA_HALT_TOKEN is unset the server refuses to
start (fail-secure).

Endpoints
---------
POST /v1/governance/halt        Trigger SOFT_STOP or HARD_STOP
POST /v1/governance/pause       Pause all sessions (resumable)
POST /v1/governance/resume      Resume paused sessions
POST /v1/governance/heartbeat   Reset the dead-man's switch timer
GET  /v1/governance/halt/audit  Return the signed audit trail
"""

from __future__ import annotations

import os
import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from core.governance.halt_controller import HaltController, HaltMode

# ---------------------------------------------------------------------------
# Token auth
# ---------------------------------------------------------------------------

_HALT_TOKEN: str = os.getenv("GAIA_HALT_TOKEN", "")

_bearer = HTTPBearer(auto_error=True)


def _require_halt_token(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> str:
    """Verify the bearer token; raise 401 on mismatch."""
    if not _HALT_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GAIA_HALT_TOKEN is not configured — halt API is disabled.",
        )
    if not secrets.compare_digest(creds.credentials, _HALT_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid halt token.",
        )
    return creds.credentials


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class HaltRequest(BaseModel):
    mode: HaltMode = HaltMode.SOFT_STOP
    triggered_by: str = "api"


class HeartbeatRequest(BaseModel):
    gaian_id: str = "unknown"


class HaltResponse(BaseModel):
    event_id: str
    mode: str
    triggered_by: str
    sessions_affected: list
    sla_met: Optional[bool]
    signature: str


class StatusResponse(BaseModel):
    status: str
    active_sessions: list


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/v1/governance", tags=["governance"])


@router.post(
    "/halt",
    response_model=HaltResponse,
    summary="Halt all GAIA sessions",
    description=(
        "Triggers a SOFT_STOP (finish current iteration) or HARD_STOP "
        "(immediate cancellation) across all registered sessions. "
        "Requires a valid bearer token (GAIA_HALT_TOKEN)."
    ),
)
def halt_all(
    req: HaltRequest,
    _token: str = Depends(_require_halt_token),
) -> HaltResponse:
    ctrl = HaltController.get_instance()
    record = ctrl.halt(mode=req.mode, triggered_by=req.triggered_by)
    return HaltResponse(
        event_id=record.event_id,
        mode=record.mode,
        triggered_by=record.triggered_by,
        sessions_affected=record.sessions_affected,
        sla_met=record.sla_met,
        signature=record.signature,
    )


@router.post(
    "/pause",
    response_model=HaltResponse,
    summary="Pause all GAIA sessions",
)
def pause_all(
    triggered_by: str = "api",
    _token: str = Depends(_require_halt_token),
) -> HaltResponse:
    ctrl = HaltController.get_instance()
    record = ctrl.pause(triggered_by=triggered_by)
    return HaltResponse(
        event_id=record.event_id,
        mode=record.mode,
        triggered_by=record.triggered_by,
        sessions_affected=record.sessions_affected,
        sla_met=record.sla_met,
        signature=record.signature,
    )


@router.post(
    "/resume",
    summary="Resume paused GAIA sessions",
    status_code=status.HTTP_204_NO_CONTENT,
)
def resume_all(
    triggered_by: str = "api",
    _token: str = Depends(_require_halt_token),
) -> None:
    ctrl = HaltController.get_instance()
    try:
        ctrl.resume(triggered_by=triggered_by)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(exc)
        ) from exc


@router.post(
    "/heartbeat",
    summary="Reset the dead-man's switch timer",
    status_code=status.HTTP_204_NO_CONTENT,
)
def heartbeat(
    req: HeartbeatRequest,
    _token: str = Depends(_require_halt_token),
) -> None:
    HaltController.get_instance().heartbeat(gaian_id=req.gaian_id)


@router.get(
    "/halt/audit",
    summary="Return the signed halt audit trail",
    description=(
        "Returns all halt events in chronological order. "
        "Each record includes an HMAC-SHA256 signature that can be "
        "verified offline using the GAIA_HALT_HMAC_SECRET env var."
    ),
)
def audit_trail(
    _token: str = Depends(_require_halt_token),
) -> list:
    return HaltController.get_instance().audit_trail()


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Current halt controller status",
)
def get_status(
    _token: str = Depends(_require_halt_token),
) -> StatusResponse:
    ctrl = HaltController.get_instance()
    return StatusResponse(
        status=ctrl.status.value,
        active_sessions=list(ctrl.active_session_ids()),
    )
