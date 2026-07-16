"""
core/api/chat_router.py
=======================
FastAPI router: /chat/*

Provides the primary human-facing conversational HTTP surface for GAIA-OS.
Each turn is recorded to the audit ledger via EventType.ACTION_EXECUTED.
Requires a live PrimordialSession injected via app.state.

Endpoints:
    POST /chat/turn          — submit one conversational turn
    POST /chat/session/begin — open a new session for a GAIAN
    POST /chat/session/end   — close the active session
    GET  /chat/session       — get active session metadata

Auth:
    Reads request.state.jti set by the auth middleware in create_app().
    Logs auth events for session open/close.

Canon Refs: C01 (Sovereignty), C15 (Consent), C06 (Memory)
Author: Kyle Steen / R0GV3TheAlchemist
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, Field

from core.audit.ledger import (
    AuditEvent,
    EventType,
    get_default_ledger,
    log_auth_event,
)
from core.runtime.runtime import InputModality

chat_router = APIRouter(prefix="/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------


class TurnRequest(BaseModel):
    gaian_id:   str                = Field(..., description="Target GAIAN's ID")
    human_id:   str                = Field("",   description="Human participant ID")
    content:    str                = Field(..., min_length=1, description="Message content")
    modality:   str                = Field("text", description="Input modality")
    session_id: Optional[str]      = Field(None, description="Existing session ID (optional)")


class TurnResponse(BaseModel):
    response:       str
    session_id:     str
    turn:           int
    gaian_id:       str
    cognitive_state: Dict[str, Any]


class SessionBeginRequest(BaseModel):
    gaian_id: str = Field(..., description="GAIAN to open a session with")
    human_id: str = Field("",   description="Human participant ID")


class SessionBeginResponse(BaseModel):
    session_id: str
    gaian_id:   str
    started_at: str


class SessionEndRequest(BaseModel):
    gaian_id: str = Field(..., description="GAIAN whose session to close")


class SessionEndResponse(BaseModel):
    session_id: str
    turns:      int
    ended_at:   str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_runtime(request: Request, gaian_id: str):
    """Resolve a GAIAN runtime from app.state.session."""
    session = getattr(request.app.state, "gaia_session", None)
    if session is None or not session.is_live:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GAIA Primordial Session is not live.",
        )
    rt = session.get_runtime(gaian_id)
    if rt is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No runtime found for gaian_id '{gaian_id}'.",
        )
    return rt


def _jti(request: Request) -> str:
    return getattr(request.state, "jti", "")


# ---------------------------------------------------------------------------
# POST /chat/turn
# ---------------------------------------------------------------------------


@chat_router.post("/turn", response_model=TurnResponse)
async def chat_turn(body: TurnRequest, request: Request) -> TurnResponse:
    """
    Submit one conversational turn to a GAIAN.

    If no session is currently active for the GAIAN, one is opened
    automatically before the turn is processed.
    """
    rt = _get_runtime(request, body.gaian_id)
    ledger = get_default_ledger()
    jti    = _jti(request)

    # Auto-open session if none is active
    if rt.current_session is None or not rt.current_session.is_active:
        rt.begin_session(human_id=body.human_id)
        log_auth_event(
            actor      = body.human_id or "anonymous",
            action     = "session_auto_begin",
            outcome    = "success",
            user_id    = body.human_id,
            jti        = jti,
            session_id = rt.current_session.session_id if rt.current_session else "",
            ledger     = ledger,
        )

    try:
        mod      = InputModality(body.modality)
    except ValueError:
        mod      = InputModality.TEXT

    response = rt.turn(body.content, modality=mod, human_id=body.human_id)
    session  = rt.current_session

    ledger.append(AuditEvent(
        event_type    = EventType.ACTION_EXECUTED,
        actor         = body.human_id or "anonymous",
        action        = "chat_turn",
        outcome       = "success",
        user_id       = body.human_id,
        session_id    = session.session_id if session else "",
        jti           = jti,
        justification = f"modality={body.modality}",
        metadata      = {
            "gaian_id": body.gaian_id,
            "turn":     session.turn_count if session else 0,
        },
    ))

    return TurnResponse(
        response        = response,
        session_id      = session.session_id if session else "",
        turn            = session.turn_count if session else 0,
        gaian_id        = body.gaian_id,
        cognitive_state = rt.cognitive_state.summary(),
    )


# ---------------------------------------------------------------------------
# POST /chat/session/begin
# ---------------------------------------------------------------------------


@chat_router.post("/session/begin", response_model=SessionBeginResponse)
async def session_begin(
    body: SessionBeginRequest, request: Request
) -> SessionBeginResponse:
    """Open a new conversational session with a GAIAN."""
    rt     = _get_runtime(request, body.gaian_id)
    ledger = get_default_ledger()
    jti    = _jti(request)

    session = rt.begin_session(human_id=body.human_id)

    log_auth_event(
        actor      = body.human_id or "anonymous",
        action     = "session_begin",
        outcome    = "success",
        user_id    = body.human_id,
        jti        = jti,
        session_id = session.session_id,
        ledger     = ledger,
    )

    return SessionBeginResponse(
        session_id = session.session_id,
        gaian_id   = body.gaian_id,
        started_at = session.started_at,
    )


# ---------------------------------------------------------------------------
# POST /chat/session/end
# ---------------------------------------------------------------------------


@chat_router.post("/session/end", response_model=SessionEndResponse)
async def session_end(
    body: SessionEndRequest, request: Request
) -> SessionEndResponse:
    """Close the active conversational session for a GAIAN."""
    rt     = _get_runtime(request, body.gaian_id)
    ledger = get_default_ledger()
    jti    = _jti(request)

    ended = rt.end_session()
    if not ended:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No active session to end.",
        )

    log_auth_event(
        actor      = "system",
        action     = "session_end",
        outcome    = "success",
        jti        = jti,
        session_id = ended.session_id,
        ledger     = ledger,
    )

    return SessionEndResponse(
        session_id = ended.session_id,
        turns      = ended.turn_count,
        ended_at   = ended.ended_at,
    )


# ---------------------------------------------------------------------------
# GET /chat/session
# ---------------------------------------------------------------------------


@chat_router.get("/session")
async def session_status(
    gaian_id: str,
    request: Request,
) -> Dict[str, Any]:
    """Return metadata about the currently active session for a GAIAN."""
    rt      = _get_runtime(request, gaian_id)
    session = rt.current_session
    if not session or not session.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active session.",
        )
    return {
        "session_id": session.session_id,
        "gaian_id":   gaian_id,
        "turn_count": session.turn_count,
        "started_at": session.started_at,
    }


__all__ = ["chat_router"]
