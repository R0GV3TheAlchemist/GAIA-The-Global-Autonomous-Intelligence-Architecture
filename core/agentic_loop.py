"""
agentic_loop.py
~~~~~~~~~~~~~~~
GAIA's core Perceive → Reason → Act → Observe (PRAO) loop.

Revision notes
--------------
obs-wiring (prev)  : TraceContext spans, Telemetry counters, AuditLog events.
canon-rag (this)   : _reason() now calls RAGPipeline.retrieve() before the
                     planner so every reasoning step is grounded in Canon.
                     ingest_canon() is called once at session start.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

# ---------------------------------------------------------------------------
# Observability layer (optional — degrades gracefully if not installed)
# ---------------------------------------------------------------------------
try:
    from core.obs.trace import TraceContext
    from core.obs.telemetry import Telemetry
    from core.obs.audit import AuditLog
    _OBS_AVAILABLE = True
except ImportError:  # pragma: no cover
    _OBS_AVAILABLE = False
    TraceContext = None  # type: ignore[assignment,misc]
    Telemetry = None    # type: ignore[assignment,misc]
    AuditLog = None     # type: ignore[assignment,misc]

# ---------------------------------------------------------------------------
# RAG layer (optional — degrades gracefully)
# ---------------------------------------------------------------------------
try:
    from core.rag.pipeline import RAGPipeline
    _RAG_AVAILABLE = True
except ImportError:  # pragma: no cover
    _RAG_AVAILABLE = False
    RAGPipeline = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Supporting data structures
# ---------------------------------------------------------------------------

@dataclass
class AgentState:
    """Mutable snapshot passed through each PRAO phase."""
    goal: str
    observations: List[str] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    complete: bool = False
    error: Optional[str] = None

    def summary(self) -> str:
        """Short natural-language description of current state — used as RAG query."""
        obs_tail = self.observations[-3:] if self.observations else []
        obs_str = " | ".join(obs_tail) if obs_tail else "none yet"
        return f"Goal: {self.goal}. Recent observations: {obs_str}"

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "observations": self.observations,
            "history": self.history,
            "complete": self.complete,
            "error": self.error,
        }


@dataclass
class ActionResult:
    tool: str
    output: Any
    success: bool
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Action gate (human-in-the-loop)
# ---------------------------------------------------------------------------

class ActionGate:
    """
    Decides whether a proposed action requires human approval.
    Override `requires_human()` for custom policy.
    """

    def requires_human(self, action: dict) -> bool:
        return action.get("requires_human", False)

    def approve(self, action: dict, human_callback: Optional[Callable]) -> bool:
        if not self.requires_human(action):
            return True
        if human_callback is None:
            return False
        return bool(human_callback(action))


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

class AgenticLoop:
    """
    Orchestrates the PRAO cycle for a single GAIA session.

    Parameters
    ----------
    planner        : callable(state, canon_context) → action dict
    tools          : mapping of tool name → callable
    perceiver      : callable(state) → updated state (optional)
    observer       : callable(state, result) → updated state (optional)
    rag            : RAGPipeline instance (optional; auto-created if available)
    human_callback : callable(action) → bool for human-approval gate
    max_iterations : safety ceiling
    """

    def __init__(
        self,
        planner: Callable,
        tools: Dict[str, Callable],
        perceiver: Optional[Callable] = None,
        observer: Optional[Callable] = None,
        rag: Optional[Any] = None,
        human_callback: Optional[Callable] = None,
        max_iterations: int = 50,
        telemetry: Optional[Any] = None,
        audit: Optional[Any] = None,
    ) -> None:
        self._planner = planner
        self._tools = tools
        self._perceiver = perceiver
        self._observer = observer
        self._human_callback = human_callback
        self._max_iterations = max_iterations
        self._gate = ActionGate()

        # Observability
        self._telemetry = telemetry or (Telemetry() if _OBS_AVAILABLE and Telemetry else None)
        self._audit = audit or (AuditLog() if _OBS_AVAILABLE and AuditLog else None)

        # RAG
        self._rag: Optional[RAGPipeline] = rag
        if self._rag is None and _RAG_AVAILABLE:
            self._rag = RAGPipeline()

    # ------------------------------------------------------------------
    # Logging helpers
    # ------------------------------------------------------------------

    def _log_info(self, msg: str, meta: Optional[dict] = None) -> None:
        if _OBS_AVAILABLE and self._audit:
            self._audit.log("INFO", msg, meta=meta or {})
        logger.info("%s | meta=%s", msg, meta)

    def _log_warning(self, msg: str, meta: Optional[dict] = None) -> None:
        if _OBS_AVAILABLE and self._audit:
            self._audit.log("WARNING", msg, meta=meta or {})
        logger.warning("%s | meta=%s", msg, meta)

    def _log_error(self, msg: str, meta: Optional[dict] = None) -> None:
        if _OBS_AVAILABLE and self._audit:
            self._audit.log("ERROR", msg, meta=meta or {})
        logger.error("%s | meta=%s", msg, meta)

    def _audit_record(self, event: str, meta: Optional[dict] = None) -> None:
        if _OBS_AVAILABLE and self._audit:
            self._audit.record(event, meta=meta or {})

    def _telemetry_record(self, key: str, value: float, tags: Optional[dict] = None) -> None:
        if _OBS_AVAILABLE and self._telemetry:
            self._telemetry.record(key, value, tags=tags or {})

    # ------------------------------------------------------------------
    # Phase runner
    # ------------------------------------------------------------------

    def _run_phase(self, name: str, fn: Callable, *args, **kwargs) -> Any:
        """
        Execute *fn* inside a child trace span, timing it and recording
        latency to telemetry regardless of success or failure.
        """
        span_name = f"agentic_loop.{name}"
        t0 = time.monotonic()
        try:
            if _OBS_AVAILABLE and TraceContext:
                with TraceContext(span_name):
                    result = fn(*args, **kwargs)
            else:
                result = fn(*args, **kwargs)
            elapsed = time.monotonic() - t0
            self._telemetry_record(span_name, elapsed)
            return result
        except Exception as exc:
            elapsed = time.monotonic() - t0
            self._telemetry_record(span_name, elapsed, tags={"error": "1"})
            raise

    # ------------------------------------------------------------------
    # PRAO phases
    # ------------------------------------------------------------------

    def _perceive(self, state: AgentState) -> AgentState:
        if self._perceiver:
            return self._perceiver(state)
        return state

    def _reason(self, state: AgentState) -> dict:
        """
        Produce the next action plan.

        If Canon is loaded, retrieve the top-K most relevant passages
        for the current state and inject them as *canon_context* into
        the planner call.  Falls back gracefully if RAG is unavailable.
        """
        canon_context: str = ""

        if self._rag is not None:
            try:
                canon_context = self._rag.retrieve(state.summary())
                if canon_context:
                    self._log_info(
                        "rag.retrieve: context injected",
                        meta={
                            "query_len": len(state.summary()),
                            "context_len": len(canon_context),
                            "canon_loaded": getattr(self._rag, "canon_loaded", False),
                        },
                    )
            except Exception as exc:  # noqa: BLE001
                self._log_warning(
                    f"rag.retrieve: failed, reasoning without Canon context — {exc}",
                    meta={"error": str(exc)},
                )

        return self._planner(state, canon_context=canon_context)

    def _act(self, state: AgentState, action: dict) -> ActionResult:
        tool_name = action.get("tool", "")
        tool_fn = self._tools.get(tool_name)
        if tool_fn is None:
            return ActionResult(tool=tool_name, output=None, success=False,
                                error=f"Unknown tool: {tool_name}")
        t0 = time.monotonic()
        try:
            output = tool_fn(**action.get("args", {}))
            elapsed = time.monotonic() - t0
            self._telemetry_record(f"tool.{tool_name}", elapsed)
            self._audit_record(
                "AGENT_ACTION",
                meta={"tool": tool_name, "success": True, "duration_s": round(elapsed, 4)},
            )
            return ActionResult(tool=tool_name, output=output, success=True)
        except Exception as exc:  # noqa: BLE001
            elapsed = time.monotonic() - t0
            self._telemetry_record(f"tool.{tool_name}", elapsed, tags={"error": "1"})
            self._audit_record(
                "AGENT_ACTION",
                meta={"tool": tool_name, "success": False, "error": str(exc)},
            )
            return ActionResult(tool=tool_name, output=None, success=False, error=str(exc))

    def _observe(self, state: AgentState, result: ActionResult) -> AgentState:
        if self._observer:
            return self._observer(state, result)
        obs = f"{result.tool}: {'ok' if result.success else result.error}"
        state.observations.append(obs)
        state.history.append(result.__dict__)
        return state

    def _log_cycle(
        self,
        session_id: str,
        iteration: int,
        action: dict,
        result: ActionResult,
        approved: bool,
        progress: Optional[str] = None,
    ) -> None:
        self._log_info(
            "agentic_loop.cycle",
            meta={
                "session_id": session_id,
                "iteration": iteration,
                "action": action.get("tool"),
                "approved": approved,
                "success": result.success,
                "progress": progress,
            },
        )

    # ------------------------------------------------------------------
    # Canon startup
    # ------------------------------------------------------------------

    def _maybe_ingest_canon(self, session_id: str) -> None:
        """
        Ingest Canon at session start if RAG is available and not yet loaded.
        Emits an audit event regardless of outcome.
        """
        if self._rag is None:
            return
        if getattr(self._rag, "canon_loaded", False):
            return  # already loaded (e.g. shared RAG instance)

        self._log_info(
            "canon.ingest.start",
            meta={"session_id": session_id},
        )
        try:
            report = self._rag.ingest_canon()
            self._audit_record(
                "CANON_INGESTED",
                meta={"session_id": session_id, **report},
            )
            self._log_info(
                "canon.ingest.complete",
                meta={"session_id": session_id, **report},
            )
        except Exception as exc:  # noqa: BLE001
            self._log_error(
                f"canon.ingest.failed — {exc}",
                meta={"session_id": session_id, "error": str(exc)},
            )

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, goal: str, initial_state: Optional[AgentState] = None) -> AgentState:
        """
        Execute the PRAO loop until the goal is complete, an error occurs,
        or *max_iterations* is reached.

        Parameters
        ----------
        goal          : Natural-language goal string.
        initial_state : Pre-populated AgentState (optional).

        Returns
        -------
        AgentState  Final state with complete=True or error set.
        """
        session_id = str(uuid.uuid4())
        state = initial_state or AgentState(goal=goal)
        t_session = time.monotonic()

        root_span = f"agentic_loop:{session_id}"

        def _inner():
            nonlocal state

            # Canon ingestion at session start
            self._maybe_ingest_canon(session_id)

            self._audit_record(
                "SESSION_START",
                meta={"session_id": session_id, "goal": goal},
            )

            for iteration in range(1, self._max_iterations + 1):
                # --- Perceive ---
                state = self._run_phase("perceive", self._perceive, state)

                # --- Reason (with Canon context) ---
                action = self._run_phase("reason", self._reason, state)

                if action.get("complete"):
                    state.complete = True
                    break

                # --- Action gate ---
                approved = self._gate.approve(action, self._human_callback)
                if not approved:
                    policy = "requires_human" if self._gate.requires_human(action) else "denied"
                    self._audit_record(
                        "POLICY_DECISION",
                        meta={
                            "session_id": session_id,
                            "iteration": iteration,
                            "action": action,
                            "approved": False,
                            "reason": policy,
                        },
                    )
                    if self._gate.requires_human(action):
                        self._audit_record(
                            "PERMISSION_DENY",
                            meta={"session_id": session_id, "action": action},
                        )
                    break

                self._audit_record(
                    "POLICY_DECISION",
                    meta={
                        "session_id": session_id,
                        "iteration": iteration,
                        "action": action,
                        "approved": True,
                    },
                )

                # --- Act ---
                result = self._run_phase("act", self._act, state, action)

                # --- Observe ---
                state = self._run_phase("observe", self._observe, state, result)

                self._log_cycle(
                    session_id=session_id,
                    iteration=iteration,
                    action=action,
                    result=result,
                    approved=True,
                    progress=action.get("progress"),
                )

                t_cycle = time.monotonic() - t_session
                self._telemetry_record("agentic_loop.cycle", t_cycle)

            else:
                state.error = f"max_iterations ({self._max_iterations}) reached"

        # Wrap entire session in a root trace span
        try:
            if _OBS_AVAILABLE and TraceContext:
                with TraceContext(root_span):
                    _inner()
            else:
                _inner()
        except Exception as exc:  # noqa: BLE001
            state.error = str(exc)
            self._log_error(
                f"agentic_loop.session.error — {exc}",
                meta={"session_id": session_id},
            )
        finally:
            session_duration = time.monotonic() - t_session
            halt_reason = "complete" if state.complete else (state.error or "unknown")
            self._telemetry_record(
                "agentic_loop.session",
                session_duration,
                tags={"error": "0" if state.complete else "1"},
            )
            self._audit_record(
                "SESSION_END",
                meta={
                    "session_id": session_id,
                    "halt_reason": halt_reason,
                    "duration_s": round(session_duration, 3),
                    "iterations": len(state.history),
                },
            )

        return state
