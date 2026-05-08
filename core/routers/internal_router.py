"""
core/routers/internal_router.py

Internal endpoints — called by the Tauri Rust layer only.
Not part of the public API; no auth required (loopback-only traffic).

Endpoints:
  POST /internal/ipc-ready
    Called by Rust after the Axum IPC bridge (port 8009) is confirmed live.
    Switches action_gate_ipc from log-bridge fallback to native Tauri emit.

Canon: Doc 35 (Security), Doc 21 (Sovereignty)
"""

from fastapi import APIRouter
from core.infra.action_gate_ipc import mark_ipc_bridge_ready

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/ipc-ready")
async def ipc_ready() -> dict:
    """Signal from Rust: Axum IPC bridge on :8009 is live.

    After this call, all ActionGate events will be emitted via
    POST http://127.0.0.1:8009/emit → Tauri AppHandle.emit() → WebView.
    """
    mark_ipc_bridge_ready()
    return {"status": "ok", "ipc_bridge": "active"}
