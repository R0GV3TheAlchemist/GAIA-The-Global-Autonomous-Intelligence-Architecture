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

Emission strategy
-----------------
Tauri v2 Python sidecar: we emit via the Tauri JS bridge by dispatching
a window CustomEvent from the Python side using the `@tauri-apps/api`
command bridge.  The sidecar exposes a `emit_to_frontend` Tauri command
that calls `app_handle.emit(event, payload)` on the Rust side.

Fallback: if the Tauri command is unavailable (dev server, unit tests),
the payload is written as a structured JSON log at WARNING level.  The
frontend log-bridge in app.ts parses lines prefixed [TAURI_IPC] and
dispatches the equivalent window CustomEvent, providing a zero-config
dev experience.

Thread safety
-------------
All pending confirmations are keyed by a unique `request_id` (UUID4).
Each confirmation holds an asyncio.Event that is set when the frontend
responds (or when the timeout fires).  The callback is sync-safe because
it runs `loop.run_until_complete()` in a thread executor.

Canon Ref: Doc 35 (Security), Doc 21 (Sovereignty)
"""

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Optional

log = logging.getLogger(__name__)

# Timeouts (seconds)
YELLOW_TIMEOUT: float = 15.0   # proceed on silence after this
RED_TIMEOUT:    float = 60.0   # hard block if no response within this

# Pending confirmations: request_id → {event, approved, tier}
_PENDING: dict[str, dict] = {}

# Tauri app handle — set by _startup() once the server is live
# Type: any (tauri-python binding or None)
_tauri_app_handle = None


def set_tauri_app_handle(handle) -> None:
    """Register the Tauri app handle for IPC emit. Called from _startup()."""
    global _tauri_app_handle
    _tauri_app_handle = handle
    log.info("[ActionGateIPC] Tauri app handle registered — IPC emit active.")


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
# Tauri IPC emit
# ---------------------------------------------------------------------------

def _emit_ipc(event_name: str, payload: dict) -> None:
    """
    Emit an event to the Tauri frontend.

    Strategy (in priority order):
    1. If a Tauri app handle is registered, call app_handle.emit().
       This is the production path — the Rust sidecar forwards the
       event directly to the WebView window.
    2. If no handle is available, emit via structured WARNING log.
       The frontend log-bridge (app.ts) parses [TAURI_IPC] prefixed
       lines and dispatches the equivalent window CustomEvent.
       This gives zero-config IPC in dev without Tauri running.
    """
    payload_json = json.dumps(payload)

    if _tauri_app_handle is not None:
        try:
            _tauri_app_handle.emit(event_name, payload)
            log.debug("[ActionGateIPC] Emitted via Tauri handle: %s", event_name)
            return
        except Exception as exc:
            log.warning(
                "[ActionGateIPC] Tauri emit failed (%s), falling back to log bridge: %s",
                exc, event_name,
            )

    # Fallback: structured log line — parsed by frontend log-bridge
    log.warning("[TAURI_IPC] %s %s", event_name, payload_json)


# ---------------------------------------------------------------------------
# The confirm_callback
# ---------------------------------------------------------------------------

def make_ipc_confirm_callback():
    """
    Return a sync confirm_callback suitable for passing to ActionGate().

    The returned callable is sync (as ActionGate.evaluate() expects) but
    internally runs an async wait so it doesn't block the event loop.
    """

    def _callback(action: dict, tier) -> bool:
        from core.infra.action_gate import RiskTier

        request_id = str(uuid.uuid4())
        timeout = YELLOW_TIMEOUT if tier == RiskTier.YELLOW else RED_TIMEOUT
        default_approved = tier == RiskTier.YELLOW  # YELLOW: approve on silence; RED: block

        # Get or create event loop
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

        # Wait for frontend response or timeout
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
