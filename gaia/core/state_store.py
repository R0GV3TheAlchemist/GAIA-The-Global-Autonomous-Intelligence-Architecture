"""
gaia/core/state_store.py

Singleton state store — the ONLY source of truth for GAIAState at runtime.

Canon anchors:
  - Issue #576 (GAIAState — central state object)
  - Issue #568 (D6 Meta-Coherence Engine)

Design rules:
  - ONE module owns the live GAIAState instance.
  - All reads go through get_state().
  - All writes go through set_state(), which ALWAYS runs the D6 engine first.
  - Raw field mutation (e.g. _state.coherence = 0.5) is forbidden.
    Route all updates through update_probes() → D6 → set_state().

For the Good and the Greater Good.
"""

from __future__ import annotations

import threading
from datetime import datetime, timezone

from gaia.core.state import GAIAOperationalMode, GAIAState
from gaia.core.d6_engine import D6Decision, D6Inputs, compute_next_state, clamp


# ── Internal singleton ────────────────────────────────────────────────────────
_lock = threading.Lock()
_state: GAIAState = GAIAState()  # boot with safe defaults


def get_state() -> GAIAState:
    """Return the current GAIAState snapshot (thread-safe read)."""
    with _lock:
        return _state


def set_state(new_state: GAIAState) -> None:
    """Commit a new GAIAState (thread-safe write).

    Prefer calling run_d6_cycle() rather than this directly —
    it ensures D6 logic has been applied before committing.
    """
    global _state
    with _lock:
        _state = new_state


def run_d6_cycle(
    *,
    personal_coherence: float | None = None,
    planetary_coherence: float | None = None,
    coherence: float | None = None,
    energy: float | None = None,
    stress: float | None = None,
    entropy: float | None = None,
    recent_error_rate: float | None = None,
    session_streak_hours: float | None = None,
) -> D6Decision:
    """Update probe values on the current state, run D6, commit, and return the decision.

    This is the primary write path for the whole backend.
    Any subsystem that wants to update state (biometrics, noosphere,
    error monitors, etc.) calls this function.

    Only the probes you pass will be updated; others retain their current value.
    All values are clamped to [0.0, 1.0] before being applied.
    """
    with _lock:
        from copy import deepcopy
        updated = deepcopy(_state)

        if personal_coherence is not None:
            updated.personal_coherence = clamp(personal_coherence)
        if planetary_coherence is not None:
            updated.planetary_coherence = clamp(planetary_coherence)
        if coherence is not None:
            updated.coherence = clamp(coherence)
        if energy is not None:
            updated.energy = clamp(energy)
        if stress is not None:
            updated.stress = clamp(stress)
        if entropy is not None:
            updated.entropy = clamp(entropy)

        inputs = D6Inputs(
            current_state=updated,
            recent_error_rate=recent_error_rate,
            session_streak_hours=session_streak_hours,
        )
        decision = compute_next_state(inputs)
        global _state
        _state = decision.next_state

    return decision


def request_mode_change(requested_mode: GAIAOperationalMode) -> D6Decision:
    """Request a specific mode change.

    D6 still runs — if conditions don't support the requested mode,
    D6 will override it. This is intentional: the human can request,
    but the system's actual health determines what's safe.

    Exception: OFFLINE and RECOVER are always accepted as requests.
    """
    with _lock:
        from copy import deepcopy
        candidate = deepcopy(_state)

        # For OFFLINE / RECOVER requests, honour immediately
        if requested_mode in (GAIAOperationalMode.OFFLINE, GAIAOperationalMode.RECOVER):
            candidate.mode = requested_mode
            candidate.last_transition_at = datetime.now(timezone.utc)
            global _state
            _state = candidate
            return D6Decision(
                next_state=candidate,
                interventions=[f"mode_change_honoured: {requested_mode.value}"],
                rationale=f"Architect requested {requested_mode.value} — accepted unconditionally.",
            )

        # For all other modes, run D6 and return its decision
        inputs = D6Inputs(current_state=candidate)
        decision = compute_next_state(inputs)
        _state = decision.next_state

    return decision


def get_runtime_json() -> dict:
    """Return the full D6 runtime JSON schema (Issue #568)."""
    return get_state().to_runtime_json()
