"""
core/protocols.py
=================
Structural typing contracts for the GAIA agentic layer.

Using ``typing.Protocol`` (PEP 544) means any object that exposes the
right attributes/methods automatically satisfies the contract — no
subclassing or explicit registration needed.  This keeps the real
implementations (AgentState, SynergyEngine) decoupled from the
contracts they satisfy.

Canon refs
----------
C01  — Sovereignty: gate decides, planner proposes.
C30  — No silent failures: planner must always return a dict with at
        least one of ``complete``, ``tool``, or ``error`` keys.
C32  — Synergy Doctrine: planner integrates multiple signals; the
        canon_context kwarg is the Canon signal injection point.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# LoopContextProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class LoopContextProtocol(Protocol):
    """
    Structural twin of ``AgentState`` (core/agentic_loop.py).

    Any object that provides these six attributes satisfies the protocol
    without inheriting from ``AgentState``.  This allows test doubles,
    alternate state containers, and future state v2 objects to be passed
    into ``SynergyEngine.plan()`` and ``AgenticLoop._reason()`` without
    any import coupling.

    Attributes
    ----------
    goal : str
        The current goal string driving the agentic loop.
    observations : list[str]
        Ordered list of observation strings accumulated across cycles.
    history : list[dict]
        Ordered list of ``ActionResult.__dict__`` snapshots.
    memory : dict[str, Any]
        Arbitrary key-value store for inter-cycle state.
    complete : bool
        True once the loop has determined the goal is achieved.
    error : str | None
        Set to a non-empty string if an unrecoverable error occurred.
    """

    goal:         str
    observations: List[str]
    history:      List[Dict[str, Any]]
    memory:       Dict[str, Any]
    complete:     bool
    error:        Optional[str]

    def summary(self) -> str:
        """Return a single-line summary of current state."""
        ...

    def to_dict(self) -> Dict[str, Any]:
        """Serialise state to a plain dict."""
        ...


# Backwards-compatible alias — older code imported under this name.
AgentStateProtocol = LoopContextProtocol


# ---------------------------------------------------------------------------
# PlannerProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class PlannerProtocol(Protocol):
    """
    Typing contract for any callable that satisfies the planner role
    consumed by ``AgenticLoop._reason()``.

    A planner receives the current loop context and an optional Canon
    passage, and returns a plain dict describing the next action.

    Return dict contract (C30 — no silent failures)
    ------------------------------------------------
    The returned dict MUST contain at least one of:
      ``complete`` : bool   — True signals goal achieved; loop halts.
      ``tool``     : str    — Name of the tool to invoke next.
      ``error``    : str    — Unrecoverable planning error; loop halts.

    Optional keys (consumed downstream):
      ``args``     : dict   — Kwargs forwarded to the tool function.
      ``register`` : str    — ``executive`` | ``reflective`` | ``minimal``
      ``rationale``: str    — Human-readable explanation (C30 audit trail).
      ``confidence``: float — [0, 1] planning confidence score.
      ``canon_hint``: dict  — Serialised ``CanonPlanHint`` (C32).

    Sovereignty (C01)
    -----------------
    The planner **proposes** an action.  Execution is always subject to
    ``ActionGate.approve()`` — the planner must never assume its output
    will be executed.
    """

    def __call__(
        self,
        state: LoopContextProtocol,
        *,
        canon_context: str = "",
    ) -> Dict[str, Any]:
        ...


# ---------------------------------------------------------------------------
# ObserverProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class ObserverProtocol(Protocol):
    """
    Typing contract for the observer phase of the PRAO loop.

    Receives the current state and an ``ActionResult``-like object and
    returns the updated state.
    """

    def __call__(
        self,
        state:  LoopContextProtocol,
        result: Any,
    ) -> LoopContextProtocol:
        ...


# ---------------------------------------------------------------------------
# PerceiverProtocol
# ---------------------------------------------------------------------------

@runtime_checkable
class PerceiverProtocol(Protocol):
    """
    Typing contract for the perceiver phase of the PRAO loop.

    Receives the current state and returns an enriched state (same type).
    """

    def __call__(
        self,
        state: LoopContextProtocol,
    ) -> LoopContextProtocol:
        ...
