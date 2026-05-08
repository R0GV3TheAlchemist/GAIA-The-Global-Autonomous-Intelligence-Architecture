"""
core/infra/action_gate_ipc.py

Tauri IPC confirm_callback for the ActionGate.

Architecture
------------
When GAIA proposes a YELLOW or RED tier action, the ActionGate calls
`confirm_callback(action, tier)`.  This module provides that callback.

For GREEN tier: ActionGate auto-approves without calling this at all.

For YELLOW tier: The callback emits a Tauri IPC event so the frontend
can surface the action to the user.  It then waits up to YELLOW_TIMEOUT
seconds for an explicit veto.  If the user does not respond within the
window, the action is approved silently ("proceed on silence").

For RED tier: The callback emits a Tauri IPC event and waits up to
RED_TIMEOUT seconds for an explicit APPROVE from the human sovereign.
If no response arrives, the action is BLOCKED by default.  RED tier
never approves on silence.

The frontend sends its decision back via a POST to:
  /action-gate/respond
which calls `resolve_pending(request_id, approved)` below.

Thread safety
-------------
All pending confirmations are keyed by a unique `request_id` (UUID4).
Each confirmation holds an asyncio.Event that is set when the frontend
responds (or when the timeout fires).  The callback is sync-safe because
it runs `loop.run_until_complete()` in a thread executor — the same
pattern used by MemoryStore.remember_sync().

Canon Ref: Doc 35 (Security), Doc 21 (Sovereignty)
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Optional

log = logging.getLogger(__name__)

# Timeouts (seconds)
YELLOW_TIMEOUT: float = 15.0   # proceed on silence after this
RED_TIMEOUT:    float = 60.0   # hard block if no response within this

# Pending confirmations: request_id → {event, approved, tier}
_PENDING: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# Frontend resolution endpoint helper
# ---------------------------------------------------------------------------

def resolve_pending(request_id: str, approved: bool) -> bool:
    """
    Called by the /action-gate/respond router endpoint when the Tauri
    frontend sends back the human sovereign's decision.

    Returns True if the request_id was found and resolved, False if it
    had already timed out or never existed.
    """
    entry = _PENDING.get(request_id)
    if entry is None:
        log.warning("[ActionGateIPC] resolve_pending called for unknown id=%s", request_id)
        return False
    entry["approved"] = approved
    entry["event"].set()
    log.info(
        "[ActionGateIPC] Human sovereign %s action request_id=%s (tier=%s)",
        "APPROVED" if approved else "VETOED",
        request_id,
        entry.get("tier", "?"),
    )
    return True


# ---------------------------------------------------------------------------
# Tauri IPC emit helper
# ---------------------------------------------------------------------------

def _emit_ipc(event_name: str, payload: dict) -> None:
    """
    Emit a Tauri IPC event to the frontend.

    In production this calls the Tauri sidecar emit mechanism.
    Currently implemented as a structured log at WARNING level so the
    Tauri log-listener bridge can forward it to the frontend until
    Task 4 (frontend dialog component) is complete.

    Replace this function body with the real Tauri emit call in Task 4.
    """
    import json
    log.warning(
        "[TAURI_IPC] %s %s",
        event_name,
        json.dumps(payload),
    )
    # TODO (Task 4): replace with:
    # from tauri_ipc import emit  # or whatever the Tauri Python bridge exports
    # emit(event_name, payload)


# ---------------------------------------------------------------------------
# The confirm_callback
# ---------------------------------------------------------------------------

def make_ipc_confirm_callback():
    """
    Return a sync confirm_callback suitable for passing to ActionGate().

    The returned callable is sync (as ActionGate.evaluate() expects) but
    internally runs an async wait via a ThreadPoolExecutor so it doesn’t
    block the event loop.
    """

    def _callback(action: dict, tier) -> bool:
        from core.infra.action_gate import RiskTier

        request_id = str(uuid.uuid4())
        timeout = YELLOW_TIMEOUT if tier == RiskTier.YELLOW else RED_TIMEOUT
        default_approved = tier == RiskTier.YELLOW  # YELLOW: approve on silence; RED: block

        # Register the pending confirmation
        loop_event: asyncio.Event
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop_event = asyncio.Event()
        _PENDING[request_id] = {
            "event":    loop_event,
            "approved": default_approved,
            "tier":     tier.value,
        }

        # Emit IPC to frontend
        _emit_ipc(
            "action-gate-confirm",
            {
                "request_id":  request_id,
                "tier":        tier.value,
                "type":        action.get("type", "unknown"),
                "description": action.get("description", ""),
                "payload":     action.get("payload", {}),
                "timeout":     timeout,
                "default":     default_approved,
            },
        )

        # Wait for frontend response (or timeout)
        async def _wait() -> bool:
            try:
                await asyncio.wait_for(loop_event.wait(), timeout=timeout)
            except asyncio.TimeoutError:
                log.info(
                    "[ActionGateIPC] Timeout waiting for %s tier confirmation (id=%s). "
                    "Default: %s.",
                    tier.value.upper(), request_id,
                    "APPROVED" if default_approved else "BLOCKED",
                )
            finally:
                _PENDING.pop(request_id, None)
            return _PENDING.get(request_id, {}).get("approved", default_approved)

        # Run async wait synchronously without blocking the event loop
        import concurrent.futures
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                fut = ex.submit(asyncio.run, _wait())
                result = fut.result(timeout=timeout + 5)
        else:
            result = loop.run_until_complete(_wait())

        return result

    return _callback


# ---------------------------------------------------------------------------
# Singleton accessor
# ---------------------------------------------------------------------------

_ipc_callback = None


def get_ipc_confirm_callback():
    """Return the singleton IPC confirm_callback, creating it if needed."""
    global _ipc_callback
    if _ipc_callback is None:
        _ipc_callback = make_ipc_confirm_callback()
    return _ipc_callback
