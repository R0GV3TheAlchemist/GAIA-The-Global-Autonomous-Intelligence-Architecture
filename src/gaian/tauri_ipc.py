"""
src/gaian/tauri_ipc.py

Tauri IPC command handlers for the GAIAN Profile UI.

All handlers return a structured response dict:
  Success: {"ok": True,  "data": {...}}
  Failure: {"ok": False, "error": "<message>"}

Handlers NEVER raise exceptions to the Tauri layer — all errors are
caught and returned as {"ok": False, ...}. This prevents Tauri from
presenting unformatted Python tracebacks in the frontend.

ADR-FE-006 invariant: no handler may set ethical_guardrail_active=False.

Issue: #825
Canon: docs/canon/GAIAN_IDENTITY.md
"""

from __future__ import annotations

import dataclasses
import logging
from typing import Any

from src.gaian.profile_manager import GaianProfileManager, ProfileNotFoundError

log = logging.getLogger(__name__)

# Module-level manager instance (can be overridden in tests via dependency injection)
_manager = GaianProfileManager()


def _ok(data: Any) -> dict:
    return {"ok": True, "data": data}


def _err(message: str) -> dict:
    return {"ok": False, "error": message}


# ------------------------------------------------------------------
# IPC Commands
# ------------------------------------------------------------------

def cmd_get_profile(architect_id: str) -> dict:
    """
    Tauri command: fetch the serialised profile for *architect_id*.

    Returns:
        {"ok": True,  "data": <profile dict>}  on success
        {"ok": False, "error": "..."}           if not found or error
    """
    try:
        profile = _manager.load_profile(architect_id)
        return _ok(dataclasses.asdict(profile))
    except ProfileNotFoundError as exc:
        return _err(str(exc))
    except Exception as exc:  # noqa: BLE001
        log.exception("cmd_get_profile: unexpected error for %s", architect_id)
        return _err(f"Unexpected error: {exc}")


def cmd_update_lci(
    architect_id: str,
    phi: float,
    session_id: str,
    timestamp: str | None = None,
) -> dict:
    """
    Tauri command: append a new LCI reading to the architect's profile.

    Returns:
        {"ok": True,  "data": <updated profile dict>}  on success
        {"ok": False, "error": "..."}                   on failure
    """
    try:
        if not 0.0 <= phi <= 1.0:
            return _err(f"phi must be in [0, 1], got {phi}")
        profile = _manager.load_profile(architect_id)
        updated = _manager.update_lci(profile, new_phi=phi, session_id=session_id, timestamp=timestamp)
        _manager.save_profile(updated)
        return _ok(dataclasses.asdict(updated))
    except ProfileNotFoundError as exc:
        return _err(str(exc))
    except Exception as exc:  # noqa: BLE001
        log.exception("cmd_update_lci: unexpected error for %s", architect_id)
        return _err(f"Unexpected error: {exc}")


def cmd_reset_profile(architect_id: str) -> dict:
    """
    Tauri command: reset a volatile profile back to baseline.

    Returns:
        {"ok": True,  "data": <reset profile dict>}  on success
        {"ok": False, "error": "..."}                 on failure
    """
    try:
        profile = _manager.load_profile(architect_id)
        reset = _manager.reset_to_baseline(profile)
        _manager.save_profile(reset)
        return _ok(dataclasses.asdict(reset))
    except ProfileNotFoundError as exc:
        return _err(str(exc))
    except Exception as exc:  # noqa: BLE001
        log.exception("cmd_reset_profile: unexpected error for %s", architect_id)
        return _err(f"Unexpected error: {exc}")
