"""
core/routers/action_gate_router.py

ActionGate resolution endpoint.

The Tauri frontend POSTs here when the human sovereign approves or
denies a RED or YELLOW tier action that was surfaced via the
`action-gate-confirm` IPC event.

Endpoints
---------
  POST /action-gate/respond
    Body: { "request_id": str, "approved": bool }
    Returns: { "resolved": bool, "request_id": str, "approved": bool }

  GET /action-gate/audit
    Returns: the full ActionGate audit log for this process lifetime.
    Requires auth.

Canon Ref: Doc 35 (Security), Doc 21 (Sovereignty)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from core.auth import TokenPayload, require_auth
from core.infra.action_gate_ipc import resolve_pending
from core.server_state import get_action_gate

router = APIRouter(prefix="/action-gate", tags=["action-gate"])


class ActionGateResponse(BaseModel):
    request_id: str
    approved: bool


@router.post("/respond")
async def action_gate_respond(body: ActionGateResponse):
    """
    Called by the Tauri frontend to resolve a pending action gate
    confirmation.  Does not require auth — the request_id is a
    UUID4 nonce that acts as a short-lived capability token.
    The endpoint is only reachable from localhost (Tauri sidecar).
    """
    resolved = resolve_pending(
        request_id=body.request_id,
        approved=body.approved,
    )
    if not resolved:
        raise HTTPException(
            status_code=404,
            detail=f"No pending action gate request with id={body.request_id}",
        )
    return {
        "resolved":   True,
        "request_id": body.request_id,
        "approved":   body.approved,
    }


@router.get("/audit")
async def action_gate_audit(user: TokenPayload = Depends(require_auth)):
    """Return the full ActionGate audit log. Requires auth."""
    gate = get_action_gate()
    return {
        "log":   gate.get_audit_log(),
        "count": len(gate.get_audit_log()),
    }
