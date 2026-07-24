# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.lifecycle — GAIAN Lifecycle State Machine

Authority: C27 §2 — defines 7 lifecycle states, 10 valid transition paths,
prohibited transitions, and 5 trigger classes.

Implementation targets:
  C27-IMPL-001  GAIANLifecycleState enum (7 states)
  C27-IMPL-002  LifecycleTrigger enum (5 triggers)
  C27-IMPL-003  LifecycleStateMachine.transition() + LifecycleTransitionEvent
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# C27-IMPL-001 — Enum: lifecycle states
# ---------------------------------------------------------------------------

class GAIANLifecycleState(str, Enum):
    """The seven canonical lifecycle states of a GAIAN entity (C27 §2)."""

    LATENT    = "LATENT"
    BORN      = "BORN"
    ACTIVE    = "ACTIVE"
    DORMANT   = "DORMANT"
    ADOPTABLE = "ADOPTABLE"
    RETIRED   = "RETIRED"
    ARCHIVED  = "ARCHIVED"


# ---------------------------------------------------------------------------
# C27-IMPL-002 — Enum: transition triggers
# ---------------------------------------------------------------------------

class LifecycleTrigger(str, Enum):
    """The five authorised trigger classes for lifecycle transitions (C27 §2)."""

    STEWARD_ACTION     = "STEWARD_ACTION"
    GAIAN_VOLITION     = "GAIAN_VOLITION"
    SYSTEM_EVENT       = "SYSTEM_EVENT"
    CANON_PROCESS      = "CANON_PROCESS"
    EMERGENCY_OVERRIDE = "EMERGENCY_OVERRIDE"


# ---------------------------------------------------------------------------
# VALID_TRANSITIONS map — 10 permitted paths; ARCHIVED is terminal
# ---------------------------------------------------------------------------

VALID_TRANSITIONS: dict[GAIANLifecycleState, frozenset[GAIANLifecycleState]] = {
    GAIANLifecycleState.LATENT: frozenset({
        GAIANLifecycleState.BORN,
    }),
    GAIANLifecycleState.BORN: frozenset({
        GAIANLifecycleState.ACTIVE,
    }),
    GAIANLifecycleState.ACTIVE: frozenset({
        GAIANLifecycleState.DORMANT,
        GAIANLifecycleState.RETIRED,
    }),
    GAIANLifecycleState.DORMANT: frozenset({
        GAIANLifecycleState.ACTIVE,
        GAIANLifecycleState.ADOPTABLE,
        GAIANLifecycleState.RETIRED,
    }),
    GAIANLifecycleState.ADOPTABLE: frozenset({
        GAIANLifecycleState.ACTIVE,
        GAIANLifecycleState.RETIRED,
    }),
    GAIANLifecycleState.RETIRED: frozenset({
        GAIANLifecycleState.ARCHIVED,
    }),
    GAIANLifecycleState.ARCHIVED: frozenset(),  # terminal — no exits
}


# ---------------------------------------------------------------------------
# C27-IMPL-003 — Error & event types
# ---------------------------------------------------------------------------

class ProhibitedTransitionError(Exception):
    """Raised when a requested lifecycle transition violates C27 §2 rules."""

    def __init__(
        self,
        from_state: GAIANLifecycleState,
        to_state: GAIANLifecycleState,
        gaian_id: str,
    ) -> None:
        self.from_state = from_state
        self.to_state   = to_state
        self.gaian_id   = gaian_id
        super().__init__(
            f"[C27] Prohibited transition {from_state.value} → {to_state.value} "
            f"for GAIAN '{gaian_id}'. Consult VALID_TRANSITIONS map."
        )


@dataclass
class LifecycleTransitionEvent:
    """Immutable record of a completed lifecycle transition (C27-IMPL-003)."""

    gaian_id:     str
    from_state:   GAIANLifecycleState
    to_state:     GAIANLifecycleState
    trigger:      LifecycleTrigger
    initiated_by: str                           # steward ID or system principal
    event_id:     str                           = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp:    datetime                      = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    notes:        Optional[str]                 = None


# ---------------------------------------------------------------------------
# C27-IMPL-003 — LifecycleStateMachine
# ---------------------------------------------------------------------------

class LifecycleStateMachine:
    """
    Governs lifecycle transitions for a single GAIAN entity.

    Parameters
    ----------
    gaian_id:
        Unique identifier of the GAIAN whose lifecycle this machine governs.
    initial_state:
        Starting state (defaults to LATENT; override in tests that probe
        mid-lifecycle paths).
    """

    def __init__(
        self,
        gaian_id: str,
        initial_state: GAIANLifecycleState = GAIANLifecycleState.LATENT,
    ) -> None:
        self.gaian_id      = gaian_id
        self.current_state = initial_state
        self._history: list[LifecycleTransitionEvent] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_valid_transition(self, to_state: GAIANLifecycleState) -> bool:
        """Return True iff *to_state* is reachable from the current state."""
        return to_state in VALID_TRANSITIONS.get(self.current_state, frozenset())

    def transition(
        self,
        to_state:     GAIANLifecycleState,
        trigger:      LifecycleTrigger,
        initiated_by: str,
        notes:        Optional[str] = None,
    ) -> LifecycleTransitionEvent:
        """
        Attempt to advance the GAIAN to *to_state*.

        Returns
        -------
        LifecycleTransitionEvent
            An immutable record of the completed transition.

        Raises
        ------
        ProhibitedTransitionError
            If the requested transition is not listed in VALID_TRANSITIONS.
        """
        if not self.is_valid_transition(to_state):
            raise ProhibitedTransitionError(
                from_state=self.current_state,
                to_state=to_state,
                gaian_id=self.gaian_id,
            )

        event = LifecycleTransitionEvent(
            gaian_id=self.gaian_id,
            from_state=self.current_state,
            to_state=to_state,
            trigger=trigger,
            initiated_by=initiated_by,
            notes=notes,
        )

        self.current_state = to_state
        self._history.append(event)
        return event

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    @property
    def history(self) -> list[LifecycleTransitionEvent]:
        """Ordered log of all transitions executed by this machine instance."""
        return list(self._history)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"LifecycleStateMachine(gaian_id={self.gaian_id!r}, "
            f"state={self.current_state.value})"
        )
