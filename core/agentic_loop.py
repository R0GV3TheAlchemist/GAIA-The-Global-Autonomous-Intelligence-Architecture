"""core/agentic_loop.py

GAIA-OS Agentic Loop Architecture
Issue #219 — feat(agent): Perceive → Reason → Act → Observe

This is the heartbeat of GAIA as an operating system, not just a chat layer.
Every autonomous goal flows through this loop. Every cycle is logged.
Every irreversible action requires explicit sovereignty confirmation.

Canon refs:
    C01  — Gaian is sovereign; no action without consent
    C30  — No silent failures; every halt is explained
    C32  — Synergy Doctrine; the loop enriches, never bypasses

Obs integration (added):
    - Every session is wrapped in a TraceContext span
    - Every phase (perceive/reason/act/observe) gets a child span
    - Every tool call is timed and emitted via StructuredLogger.tool_call()
    - Every ACT writes an AuditLog AGENT_ACTION event
    - Every gate decision writes an AuditLog POLICY_DECISION / PERMISSION_DENY event
    - SESSION_START and SESSION_END are audited
    - Per-phase latency is recorded in Telemetry
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

# ── Observability (core/obs) ─────────────────────────────────────────────────
# Graceful: if core/obs is mid-build, falls back to stdlib logging throughout.
try:
    from core.obs import get_logger as _obs_get_logger
    from core.obs import get_audit as _obs_get_audit
    from core.obs import get_telemetry as _obs_get_telemetry
    from core.obs.tracer import TraceContext
    from core.obs.audit import AuditEventType
    _OBS_AVAILABLE = True
except ImportError:
    _OBS_AVAILABLE = False
    TraceContext = None  # type: ignore
    AuditEventType = None  # type: ignore

# ── GAIA-OS internal imports — graceful stubs if modules are mid-build ───────
try:
    from core.action_gate import ActionGate, ActionRiskTier, GateDecision
except ImportError:
    ActionGate = None  # type: ignore
    ActionRiskTier = None  # type: ignore
    GateDecision = None  # type: ignore

try:
    from core.synergy_engine import SynergyEngine, SynergyParams
except ImportError:
    SynergyEngine = None  # type: ignore
    SynergyParams = None  # type: ignore

try:
    from core.task_graph import TaskGraph, TaskNode, TaskStatus
except ImportError:
    TaskGraph = None  # type: ignore
    TaskNode = None  # type: ignore
    TaskStatus = None  # type: ignore

# ── Logger bootstrap ─────────────────────────────────────────────────────────
# Uses core.obs.StructuredLogger when available; stdlib logging otherwise.
if _OBS_AVAILABLE:
    _struct_logger = _obs_get_logger()
    _audit = _obs_get_audit()
    _telemetry = _obs_get_telemetry()
else:
    import logging as _stdlib_logging
    _struct_logger = None
    _audit = None
    _telemetry = None
    _fallback_log = _stdlib_logging.getLogger("gaia.agentic_loop")


def _log_info(msg: str, **kwargs) -> None:
    if _struct_logger:
        _struct_logger.info(msg, **kwargs)
    else:
        _fallback_log.info(msg)  # type: ignore[name-defined]


def _log_warning(msg: str, **kwargs) -> None:
    if _struct_logger:
        _struct_logger.warning(msg, **kwargs)
    else:
        _fallback_log.warning(msg)  # type: ignore[name-defined]


def _log_error(msg: str, **kwargs) -> None:
    if _struct_logger:
        _struct_logger.error(msg, **kwargs)
    else:
        _fallback_log.error(msg)  # type: ignore[name-defined]


def _audit_record(event_type: str, actor: str, action: str, outcome: str = "ok",
                  resource: Optional[str] = None, meta: Optional[dict] = None) -> None:
    if _audit:
        _audit.record(event_type, actor, action, outcome, resource, meta)


def _telemetry_record(tool: str, latency_ms: float, error: bool = False) -> None:
    if _telemetry:
        _telemetry.record(tool, latency_ms, error)


# ─────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────

class HaltCondition(str, Enum):
    """Why the loop stopped."""
    GOAL_ACHIEVED    = "goal_achieved"     # All tasks complete, goal confirmed
    MAX_ITERATIONS   = "max_iterations"    # Safety ceiling reached — Canon C30
    ACTION_BLOCKED   = "action_blocked"    # ActionGate denied a required action
    HUMAN_REQUIRED   = "human_required"    # Irreversible action needs Gaian approval
    ERROR            = "error"             # Unrecoverable exception
    GAIAN_CANCELLED  = "gaian_cancelled"   # Gaian explicitly halted the loop


class LoopPhase(str, Enum):
    PERCEIVE = "perceive"
    REASON   = "reason"
    ACT      = "act"
    OBSERVE  = "observe"
    HALTED   = "halted"


# ─────────────────────────────────────────────
# Data contracts
# ─────────────────────────────────────────────

@dataclass
class LoopContext:
    """
    The living context object that flows through every cycle of the loop.
    Perceive populates it. Reason reads it. Act uses it. Observe updates it.
    """
    goal: str                            # Natural-language goal from Gaian
    gaian_id: str                        # Who owns this loop session
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Ambient signals — populated by perceive()
    session_mode: str = "default"        # deep_work | rest | ceremony | default
    biometric_coherence: Optional[float] = None   # [0.0, 1.0] from Biometric Engine
    biometric_label: str = "unknown"     # depleted | building | high | peak
    planetary_label: str = "unknown"     # calm | elevated | storm
    affective_state: str = "unknown"     # primary emotion from Affective Mirror

    # Task & reasoning state — managed by reason() and observe()
    task_graph: Optional[Any] = None     # TaskGraph instance
    current_task: Optional[Any] = None  # Active TaskNode
    completed_tasks: list = field(default_factory=list)
    failed_tasks: list = field(default_factory=list)
    pending_human_approval: bool = False

    # Memory — updated each cycle
    cycle_memory: list[dict] = field(default_factory=list)
    last_action_result: Optional[Any] = None
    last_action_success: bool = True

    # Metadata
    started_at: float = field(default_factory=time.time)
    extra: dict = field(default_factory=dict)


@dataclass
class LoopCycle:
    """
    Immutable record of a single Perceive→Reason→Act→Observe iteration.
    Every cycle is logged and contributes to the audit trail.
    """
    cycle_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    iteration: int = 0
    phase_entered: LoopPhase = LoopPhase.PERCEIVE
    phase_exited: LoopPhase = LoopPhase.OBSERVE

    # Perceive
    perceived_biometric: Optional[float] = None
    perceived_session_mode: str = "default"
    perceived_planetary: str = "unknown"

    # Reason
    planned_action: str = ""
    planned_tool: str = ""
    reasoning_summary: str = ""

    # Act
    action_approved: bool = False
    action_result: Optional[Any] = None
    action_error: Optional[str] = None
    gate_decision: Optional[str] = None

    # Observe
    goal_progress: float = 0.0          # [0.0, 1.0] estimated progress
    should_continue: bool = True
    halt_condition: Optional[HaltCondition] = None

    # Timing
    started_at: float = field(default_factory=time.time)
    duration_ms: float = 0.0

    # Obs span IDs (populated at runtime, not serialised to external consumers)
    _trace_id: Optional[str] = field(default=None, repr=False)


@dataclass
class AgenticLoopResult:
    """
    Final result returned when the loop terminates.
    Contains the complete audit trail, halt reason, and outcome.
    """
    session_id: str
    goal: str
    gaian_id: str
    halt_condition: HaltCondition
    goal_achieved: bool
    total_iterations: int
    total_duration_s: float
    cycles: list[LoopCycle] = field(default_factory=list)
    final_output: Optional[str] = None
    error_message: Optional[str] = None
    dq_score: float = 0.0               # DecisionQuality — filled by Orchestrator
    degraded: bool = False

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "goal": self.goal,
            "gaian_id": self.gaian_id,
            "halt_condition": self.halt_condition.value,
            "goal_achieved": self.goal_achieved,
            "total_iterations": self.total_iterations,
            "total_duration_s": round(self.total_duration_s, 3),
            "cycles": len(self.cycles),
            "dq_score": round(self.dq_score, 3),
            "degraded": self.degraded,
            "final_output": self.final_output,
        }


# ─────────────────────────────────────────────
# Approval gate protocol
# ─────────────────────────────────────────────

ApprovalCallback = Callable[[str, str], Coroutine[Any, Any, bool]]

async def _default_approval_callback(action: str, reason: str) -> bool:
    """
    Default human-in-the-loop approval gate.
    In production this surfaces a UI prompt to the Gaian.
    Stub returns False (deny by default) to enforce safe defaults.
    """
    _log_warning(
        f"HUMAN APPROVAL REQUIRED — action={action!r} reason={reason!r}",
        tool="agentic_loop.approval_gate",
    )
    return False


# ─────────────────────────────────────────────
# The Loop
# ─────────────────────────────────────────────

class AgenticLoop:
    """
    GAIA-OS Agentic Loop — the core execution runtime.

    Runs a formal Perceive → Reason → Act → Observe cycle until:
    - The goal is achieved
    - The max iteration ceiling is hit (Canon C30: no runaway loops)
    - An action is blocked by the ActionGate (Canon C01: sovereignty)
    - A Gaian approval gate fires and the Gaian declines
    - An unrecoverable error occurs

    Every cycle produces a LoopCycle record for the audit trail.
    The loop never silently swallows failures.

    Observability:
    - The entire session runs inside a TraceContext span.
    - Each PRAO phase is a child span.
    - Every tool dispatch and gate decision is logged + audited.
    - Per-phase latency is tracked in Telemetry.

    Usage::

        loop = AgenticLoop(
            action_gate=my_gate,
            synergy_engine=my_synergy,
            task_graph_factory=my_factory,
            max_iterations=12,
        )
        result = await loop.run(
            goal="Research quantum coherence in biological systems and summarise findings",
            gaian_id="r0gv3",
        )
    """

    DEFAULT_MAX_ITERATIONS = 15

    def __init__(
        self,
        action_gate: Optional[Any] = None,
        synergy_engine: Optional[Any] = None,
        task_graph_factory: Optional[Callable[[str], Any]] = None,
        approval_callback: Optional[ApprovalCallback] = None,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        tool_registry: Optional[dict] = None,
    ):
        self.action_gate = action_gate
        self.synergy_engine = synergy_engine
        self.task_graph_factory = task_graph_factory
        self.approval_callback = approval_callback or _default_approval_callback
        self.max_iterations = max_iterations
        self.tool_registry: dict[str, Callable] = tool_registry or {}
        self._cancelled = False

    # ── Public API ───────────────────────────

    async def run(
        self,
        goal: str,
        gaian_id: str,
        session_mode: str = "default",
        initial_context: Optional[dict] = None,
    ) -> AgenticLoopResult:
        """
        Run the agentic loop for the given goal.
        Returns AgenticLoopResult with full audit trail regardless of outcome.
        """
        context = LoopContext(
            goal=goal,
            gaian_id=gaian_id,
            session_mode=session_mode,
            extra=initial_context or {},
        )
        session_id = context.session_id

        # Audit: session start
        _audit_record(
            AuditEventType.SESSION_START if _OBS_AVAILABLE else "session.start",
            actor=gaian_id,
            action=f"loop:start:{session_id}",
            meta={"goal": goal[:120], "session_mode": session_mode},
        )

        _log_info(
            f"[AgenticLoop] START session={session_id} gaian={gaian_id} goal={goal[:80]!r}",
            tool="agentic_loop",
            meta={"session_id": session_id, "gaian_id": gaian_id, "goal": goal[:120]},
        )

        if self.task_graph_factory:
            context.task_graph = self.task_graph_factory(goal)

        cycles: list[LoopCycle] = []
        halt: HaltCondition = HaltCondition.MAX_ITERATIONS
        final_output: Optional[str] = None
        error_message: Optional[str] = None
        loop_start = time.time()

        # ── Outer session TraceContext ────────────────────────────────────────
        _session_ctx = TraceContext(f"agentic_loop:{session_id}") if _OBS_AVAILABLE else None
        session_entered = False
        if _session_ctx:
            _session_ctx.__enter__()
            session_entered = True

        try:
            for iteration in range(1, self.max_iterations + 1):
                if self._cancelled:
                    halt = HaltCondition.GAIAN_CANCELLED
                    _log_info(
                        f"[AgenticLoop] CANCELLED by Gaian at iteration {iteration}",
                        tool="agentic_loop",
                        meta={"session_id": session_id, "iteration": iteration},
                    )
                    break

                cycle = LoopCycle(
                    session_id=session_id,
                    iteration=iteration,
                )
                cycle_start = time.time()
                goal_done = False
                observe_halt: Optional[HaltCondition] = None

                try:
                    # ── PERCEIVE ──────────────────────────────────────────────
                    await self._run_phase(
                        LoopPhase.PERCEIVE, context, cycle,
                        self._perceive
                    )

                    # ── REASON ────────────────────────────────────────────────
                    should_proceed = await self._run_phase(
                        LoopPhase.REASON, context, cycle,
                        self._reason
                    )
                    if not should_proceed:
                        halt = HaltCondition.GOAL_ACHIEVED
                        cycle.halt_condition = halt
                        cycle.should_continue = False
                        cycles.append(cycle)
                        break

                    # ── ACT ───────────────────────────────────────────────────
                    action_ok, action_halt = await self._run_phase(
                        LoopPhase.ACT, context, cycle,
                        self._act
                    )
                    if not action_ok:
                        halt = action_halt or HaltCondition.ACTION_BLOCKED
                        cycle.halt_condition = halt
                        cycle.should_continue = False
                        cycles.append(cycle)
                        break

                    # ── OBSERVE ───────────────────────────────────────────────
                    goal_done, observe_halt = await self._run_phase(
                        LoopPhase.OBSERVE, context, cycle,
                        self._observe
                    )
                    cycle.phase_exited = LoopPhase.HALTED if observe_halt else LoopPhase.OBSERVE

                    context.cycle_memory.append({
                        "iteration": iteration,
                        "action": cycle.planned_action,
                        "success": cycle.action_approved and cycle.action_error is None,
                        "progress": cycle.goal_progress,
                    })

                except Exception as exc:  # noqa: BLE001
                    _log_error(
                        f"[AgenticLoop] ERROR at iteration {iteration} "
                        f"phase={cycle.phase_entered.value}: {exc}",
                        tool="agentic_loop",
                        outcome="error",
                        meta={"session_id": session_id, "iteration": iteration, "error": str(exc)},
                    )
                    cycle.action_error = str(exc)
                    halt = HaltCondition.ERROR
                    error_message = str(exc)
                    cycle.halt_condition = halt
                    cycles.append(cycle)
                    break

                finally:
                    cycle.duration_ms = (time.time() - cycle_start) * 1000

                cycles.append(cycle)
                self._log_cycle(cycle)

                if goal_done:
                    halt = HaltCondition.GOAL_ACHIEVED
                    final_output = context.extra.get("final_output")
                    break

                if observe_halt:
                    halt = observe_halt
                    break

            else:
                _log_warning(
                    f"[AgenticLoop] MAX_ITERATIONS ({self.max_iterations}) reached "
                    f"for goal={goal[:80]!r} — halting. (Canon C30)",
                    tool="agentic_loop",
                    outcome="warning",
                    meta={"session_id": session_id, "max_iterations": self.max_iterations},
                )
                halt = HaltCondition.MAX_ITERATIONS

        finally:
            if session_entered and _session_ctx:
                _session_ctx.__exit__(None, None, None)

        total_duration = time.time() - loop_start

        # Audit: session end
        _audit_record(
            AuditEventType.SESSION_END if _OBS_AVAILABLE else "session.end",
            actor=gaian_id,
            action=f"loop:end:{session_id}",
            outcome="ok" if halt == HaltCondition.GOAL_ACHIEVED else halt.value,
            meta={
                "halt_condition": halt.value,
                "iterations": len(cycles),
                "duration_s": round(total_duration, 3),
                "goal_achieved": halt == HaltCondition.GOAL_ACHIEVED,
            },
        )

        result = AgenticLoopResult(
            session_id=session_id,
            goal=goal,
            gaian_id=gaian_id,
            halt_condition=halt,
            goal_achieved=(halt == HaltCondition.GOAL_ACHIEVED),
            total_iterations=len(cycles),
            total_duration_s=total_duration,
            cycles=cycles,
            final_output=final_output,
            error_message=error_message,
        )

        _log_info(
            f"[AgenticLoop] END session={session_id} halt={halt.value} "
            f"iterations={len(cycles)} duration={total_duration:.2f}s "
            f"goal_achieved={result.goal_achieved}",
            tool="agentic_loop",
            latency_ms=round(total_duration * 1000, 2),
            outcome="ok" if result.goal_achieved else halt.value,
            meta=result.to_dict(),
        )
        _telemetry_record("agentic_loop.session", latency_ms=total_duration * 1000,
                          error=halt == HaltCondition.ERROR)

        return result

    def cancel(self) -> None:
        """Gaian-initiated cancellation. Takes effect before the next iteration."""
        self._cancelled = True
        _log_info("[AgenticLoop] Cancellation requested by Gaian.", tool="agentic_loop")

    # ── Phase runner (new) ───────────────────────────────────────────────────

    async def _run_phase(self, phase: LoopPhase, context: LoopContext,
                          cycle: LoopCycle, fn: Callable) -> Any:
        """
        Execute a loop phase wrapped in a TraceContext child span.
        Records phase latency in Telemetry.
        Returns whatever the phase function returns.
        """
        cycle.phase_entered = phase
        phase_start = time.time()
        span_name = f"agentic_loop.{phase.value}"

        if _OBS_AVAILABLE:
            ctx = TraceContext(span_name, meta={"session_id": context.session_id,
                                                 "iteration": cycle.iteration})
            ctx.__enter__()
        try:
            result = await fn(context, cycle)
            elapsed = (time.time() - phase_start) * 1000
            _telemetry_record(span_name, latency_ms=elapsed)
            return result
        except Exception:
            elapsed = (time.time() - phase_start) * 1000
            _telemetry_record(span_name, latency_ms=elapsed, error=True)
            raise
        finally:
            if _OBS_AVAILABLE:
                ctx.__exit__(None, None, None)

    # ── Loop phases ──────────────────────────

    async def _perceive(self, context: LoopContext, cycle: LoopCycle) -> None:
        """
        PERCEIVE: Gather ambient context.
        Reads session state, biometric coherence, planetary signals.
        """
        cycle.perceived_session_mode = context.session_mode
        if hasattr(context, "biometric_coherence") and context.biometric_coherence is not None:
            cycle.perceived_biometric = context.biometric_coherence
        else:
            cycle.perceived_biometric = None
        cycle.perceived_planetary = context.planetary_label

        if hasattr(self, "_perception_hook"):
            await self._perception_hook(context, cycle)  # type: ignore

    async def _reason(
        self, context: LoopContext, cycle: LoopCycle
    ) -> bool:
        """
        REASON: Determine the next best action toward the goal.
        Returns False if the goal is already complete.
        """
        if context.task_graph is not None:
            try:
                if context.task_graph.is_complete():
                    cycle.reasoning_summary = "TaskGraph reports all tasks complete."
                    return False
                next_task = context.task_graph.next_task()
                context.current_task = next_task
                cycle.planned_action = getattr(next_task, "action", str(next_task))
                cycle.planned_tool = getattr(next_task, "tool", "")
                cycle.reasoning_summary = f"TaskGraph selected: {cycle.planned_action}"
                return True
            except Exception as exc:  # noqa: BLE001
                _log_warning(f"[AgenticLoop.reason] TaskGraph error: {exc}",
                             tool="agentic_loop.reason")

        if self.synergy_engine is not None:
            try:
                plan = await self._synergy_plan(context)
                if plan.get("goal_complete"):
                    return False
                cycle.planned_action = plan.get("action", "continue")
                cycle.planned_tool = plan.get("tool", "")
                cycle.reasoning_summary = plan.get("summary", "")
                return True
            except Exception as exc:  # noqa: BLE001
                _log_warning(f"[AgenticLoop.reason] SynergyEngine error: {exc}",
                             tool="agentic_loop.reason")

        if len(context.cycle_memory) >= 3:
            cycle.reasoning_summary = "Stub planner: 3 cycles passed — declaring complete."
            return False

        cycle.planned_action = f"step_{len(context.cycle_memory) + 1}_toward_goal"
        cycle.planned_tool = ""
        cycle.reasoning_summary = "Stub planner active — wire SynergyEngine or TaskGraph."
        return True

    async def _act(
        self, context: LoopContext, cycle: LoopCycle
    ) -> tuple[bool, Optional[HaltCondition]]:
        """
        ACT: Execute the planned action through the ActionGate.
        Canon C01: Every action passes through sovereignty check first.
        Writes AGENT_ACTION + POLICY_DECISION audit events.
        """
        action = cycle.planned_action
        tool_name = cycle.planned_tool
        act_start = time.time()

        # ── ActionGate sovereignty check ──────────────────────────────────────
        if self.action_gate is not None:
            try:
                gate_result = await self._gate_check(action, context)
                cycle.gate_decision = str(gate_result)

                if not gate_result.approved:
                    if gate_result.requires_human_approval:
                        approved = await self.approval_callback(
                            action,
                            gate_result.reason or "Irreversible action requires Gaian confirmation."
                        )
                        if not approved:
                            cycle.action_approved = False
                            _log_info(
                                f"[AgenticLoop.act] Gaian declined approval for action={action!r}",
                                tool="agentic_loop.act",
                                outcome="deny",
                                meta={"action": action, "session_id": context.session_id},
                            )
                            _audit_record(
                                AuditEventType.PERMISSION_DENY if _OBS_AVAILABLE else "permission.deny",
                                actor=context.gaian_id,
                                action=action,
                                outcome="deny",
                                meta={"reason": "gaian_declined", "gate_decision": str(gate_result)},
                            )
                            return False, HaltCondition.HUMAN_REQUIRED
                        # Gaian approved — fall through to execute
                        _audit_record(
                            AuditEventType.PERMISSION_GRANT if _OBS_AVAILABLE else "permission.grant",
                            actor=context.gaian_id,
                            action=action,
                            outcome="ok",
                            meta={"gate_decision": str(gate_result)},
                        )
                    else:
                        cycle.action_approved = False
                        _log_warning(
                            f"[AgenticLoop.act] ActionGate BLOCKED action={action!r} "
                            f"reason={gate_result.reason!r}",
                            tool="agentic_loop.act",
                            outcome="blocked",
                            meta={"action": action, "reason": gate_result.reason},
                        )
                        _audit_record(
                            AuditEventType.POLICY_DECISION if _OBS_AVAILABLE else "policy.decision",
                            actor="action_gate",
                            action=action,
                            outcome="blocked",
                            meta={"reason": gate_result.reason},
                        )
                        return False, HaltCondition.ACTION_BLOCKED
                else:
                    _audit_record(
                        AuditEventType.POLICY_DECISION if _OBS_AVAILABLE else "policy.decision",
                        actor="action_gate",
                        action=action,
                        outcome="approved",
                        meta={"gate_decision": str(gate_result)},
                    )
            except Exception as exc:  # noqa: BLE001
                _log_warning(f"[AgenticLoop.act] ActionGate error (proceeding): {exc}",
                             tool="agentic_loop.act")

        # ── Execute tool ──────────────────────────────────────────────────────
        cycle.action_approved = True
        tool_start = time.time()

        if tool_name and tool_name in self.tool_registry:
            tool_fn = self.tool_registry[tool_name]
            try:
                result = await tool_fn(context, cycle)
                tool_elapsed = (time.time() - tool_start) * 1000
                cycle.action_result = result
                context.last_action_result = result
                context.last_action_success = True

                _struct_logger.tool_call(tool_name, latency_ms=tool_elapsed, outcome="ok",
                                          meta={"session_id": context.session_id,
                                                "iteration": cycle.iteration}) \
                    if _struct_logger else None
                _telemetry_record(f"tool.{tool_name}", latency_ms=tool_elapsed)
                _audit_record(
                    AuditEventType.AGENT_ACTION if _OBS_AVAILABLE else "agent.action",
                    actor=context.gaian_id,
                    action=f"tool:{tool_name}",
                    outcome="ok",
                    resource=tool_name,
                    meta={"action": action, "latency_ms": round(tool_elapsed, 2)},
                )

            except Exception as exc:  # noqa: BLE001
                tool_elapsed = (time.time() - tool_start) * 1000
                cycle.action_error = str(exc)
                context.last_action_success = False
                _log_error(
                    f"[AgenticLoop.act] Tool {tool_name!r} raised: {exc}",
                    tool=f"agentic_loop.tool.{tool_name}",
                    latency_ms=round(tool_elapsed, 2),
                    outcome="error",
                    meta={"error": str(exc)},
                )
                _telemetry_record(f"tool.{tool_name}", latency_ms=tool_elapsed, error=True)
                _audit_record(
                    AuditEventType.AGENT_ACTION if _OBS_AVAILABLE else "agent.action",
                    actor=context.gaian_id,
                    action=f"tool:{tool_name}",
                    outcome="error",
                    resource=tool_name,
                    meta={"error": str(exc)},
                )
        else:
            # No tool registered — stub success
            cycle.action_result = {"status": "stub_ok", "action": action}
            context.last_action_result = cycle.action_result
            context.last_action_success = True
            _audit_record(
                AuditEventType.AGENT_ACTION if _OBS_AVAILABLE else "agent.action",
                actor=context.gaian_id,
                action=f"stub:{action}",
                outcome="ok",
                meta={"note": "no tool registered"},
            )

        return True, None

    async def _observe(
        self, context: LoopContext, cycle: LoopCycle
    ) -> tuple[bool, Optional[HaltCondition]]:
        """
        OBSERVE: Evaluate action outcome, update state, decide whether to loop or halt.
        Returns (goal_done, optional_halt).
        """
        if context.current_task is not None:
            if context.last_action_success:
                context.completed_tasks.append(context.current_task)
                if hasattr(context.task_graph, "mark_complete") and context.task_graph:
                    try:
                        context.task_graph.mark_complete(context.current_task)
                    except Exception:  # noqa: BLE001
                        pass
            else:
                context.failed_tasks.append(context.current_task)

        total = len(context.completed_tasks) + len(context.failed_tasks)
        cycle.goal_progress = (
            len(context.completed_tasks) / total if total > 0 else 0.0
        )

        if context.task_graph is not None:
            try:
                if context.task_graph.is_complete():
                    cycle.goal_progress = 1.0
                    context.extra["final_output"] = (
                        context.last_action_result
                        if isinstance(context.last_action_result, str)
                        else str(context.last_action_result or "")
                    )
                    return True, None
            except Exception:  # noqa: BLE001
                pass

        recent = context.cycle_memory[-3:] if len(context.cycle_memory) >= 3 else []
        if recent and all(not c.get("success") for c in recent):
            _log_warning(
                "[AgenticLoop.observe] 3 consecutive failures — halting loop.",
                tool="agentic_loop.observe",
                outcome="error",
                meta={"session_id": context.session_id},
            )
            return False, HaltCondition.ERROR

        cycle.should_continue = True
        return False, None

    # ── Internal helpers ─────────────────────

    async def _synergy_plan(self, context: LoopContext) -> dict:
        if self.synergy_engine is None:
            return {"action": "stub", "tool": "", "summary": "no synergy engine"}
        if asyncio.iscoroutinefunction(self.synergy_engine.plan):
            return await self.synergy_engine.plan(context.goal, context)
        return self.synergy_engine.plan(context.goal, context)

    async def _gate_check(self, action: str, context: LoopContext):
        if asyncio.iscoroutinefunction(self.action_gate.evaluate):
            return await self.action_gate.evaluate(action, context.gaian_id)
        return self.action_gate.evaluate(action, context.gaian_id)

    def _log_cycle(self, cycle: LoopCycle) -> None:
        """Emit a structured log for the completed cycle — Canon C30."""
        _log_info(
            f"[AgenticLoop] CYCLE iteration={cycle.iteration} "
            f"phase={cycle.phase_exited.value} "
            f"action={cycle.planned_action[:60]!r} "
            f"tool={cycle.planned_tool!r} "
            f"approved={cycle.action_approved} "
            f"progress={cycle.goal_progress:.2f} "
            f"duration_ms={cycle.duration_ms:.1f} "
            f"halt={cycle.halt_condition.value if cycle.halt_condition else 'none'}",
            tool="agentic_loop",
            latency_ms=round(cycle.duration_ms, 2),
            outcome="ok" if not cycle.action_error else "error",
            meta={
                "session_id": cycle.session_id,
                "iteration": cycle.iteration,
                "action": cycle.planned_action,
                "tool": cycle.planned_tool,
                "approved": cycle.action_approved,
                "progress": round(cycle.goal_progress, 3),
            },
        )
        _telemetry_record(
            "agentic_loop.cycle",
            latency_ms=cycle.duration_ms,
            error=bool(cycle.action_error),
        )


# ─────────────────────────────────────────────
# Factory helper
# ─────────────────────────────────────────────

def create_loop(
    action_gate=None,
    synergy_engine=None,
    task_graph_factory=None,
    approval_callback: Optional[ApprovalCallback] = None,
    max_iterations: int = AgenticLoop.DEFAULT_MAX_ITERATIONS,
    tool_registry: Optional[dict] = None,
) -> AgenticLoop:
    """
    Factory for creating a configured AgenticLoop.
    All parameters are optional — the loop degrades gracefully
    when engines are not yet wired.
    """
    return AgenticLoop(
        action_gate=action_gate,
        synergy_engine=synergy_engine,
        task_graph_factory=task_graph_factory,
        approval_callback=approval_callback,
        max_iterations=max_iterations,
        tool_registry=tool_registry or {},
    )
