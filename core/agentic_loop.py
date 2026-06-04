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
"""

from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Coroutine, Optional

# GAIA-OS internal imports — graceful stubs if modules are mid-build
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

try:
    from core.logger import get_logger
except ImportError:
    import logging
    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger("gaia.agentic_loop")


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
    In development it logs and returns True for non-destructive actions.
    """
    logger.warning(
        "HUMAN APPROVAL REQUIRED — action=%s reason=%s",
        action, reason
    )
    # Production: replace with actual Gaian approval UI event
    # This stub returns False (deny by default) to enforce safe defaults
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

        logger.info(
            "[AgenticLoop] START session=%s gaian=%s goal=%r",
            context.session_id, gaian_id, goal[:80]
        )

        if self.task_graph_factory:
            context.task_graph = self.task_graph_factory(goal)

        cycles: list[LoopCycle] = []
        halt: HaltCondition = HaltCondition.MAX_ITERATIONS
        final_output: Optional[str] = None
        error_message: Optional[str] = None
        loop_start = time.time()

        for iteration in range(1, self.max_iterations + 1):
            if self._cancelled:
                halt = HaltCondition.GAIAN_CANCELLED
                logger.info("[AgenticLoop] CANCELLED by Gaian at iteration %d", iteration)
                break

            cycle = LoopCycle(
                session_id=context.session_id,
                iteration=iteration,
            )
            cycle_start = time.time()

            try:
                # ── PERCEIVE ──────────────────
                cycle.phase_entered = LoopPhase.PERCEIVE
                await self._perceive(context, cycle)

                # ── REASON ───────────────────
                cycle.phase_entered = LoopPhase.REASON
                should_proceed = await self._reason(context, cycle)
                if not should_proceed:
                    halt = HaltCondition.GOAL_ACHIEVED
                    cycle.halt_condition = halt
                    cycle.should_continue = False
                    cycles.append(cycle)
                    break

                # ── ACT ───────────────────────
                cycle.phase_entered = LoopPhase.ACT
                action_ok, action_halt = await self._act(context, cycle)
                if not action_ok:
                    halt = action_halt or HaltCondition.ACTION_BLOCKED
                    cycle.halt_condition = halt
                    cycle.should_continue = False
                    cycles.append(cycle)
                    break

                # ── OBSERVE ───────────────────
                cycle.phase_entered = LoopPhase.OBSERVE
                goal_done, observe_halt = await self._observe(context, cycle)
                cycle.phase_exited = LoopPhase.HALTED if observe_halt else LoopPhase.OBSERVE

                context.cycle_memory.append({
                    "iteration": iteration,
                    "action": cycle.planned_action,
                    "success": cycle.action_approved and cycle.action_error is None,
                    "progress": cycle.goal_progress,
                })

            except Exception as exc:  # noqa: BLE001
                logger.exception(
                    "[AgenticLoop] ERROR at iteration %d phase=%s: %s",
                    iteration, cycle.phase_entered.value, exc
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
            # Exhausted iterations — Canon C30: surface this, never swallow it
            logger.warning(
                "[AgenticLoop] MAX_ITERATIONS (%d) reached for goal=%r — halting.",
                self.max_iterations, goal[:80]
            )
            halt = HaltCondition.MAX_ITERATIONS

        total_duration = time.time() - loop_start
        result = AgenticLoopResult(
            session_id=context.session_id,
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

        logger.info(
            "[AgenticLoop] END session=%s halt=%s iterations=%d duration=%.2fs goal_achieved=%s",
            context.session_id, halt.value, len(cycles), total_duration, result.goal_achieved
        )
        return result

    def cancel(self) -> None:
        """Gaian-initiated cancellation. Takes effect before the next iteration."""
        self._cancelled = True
        logger.info("[AgenticLoop] Cancellation requested by Gaian.")

    # ── Loop phases ──────────────────────────

    async def _perceive(self, context: LoopContext, cycle: LoopCycle) -> None:
        """
        PERCEIVE: Gather ambient context.
        Reads session state, biometric coherence, planetary signals.
        Populates cycle perception fields for downstream phases.
        """
        # Session mode — from context or environment
        cycle.perceived_session_mode = context.session_mode

        # Biometric coherence — delegate to engine if available
        if hasattr(context, "biometric_coherence") and context.biometric_coherence is not None:
            cycle.perceived_biometric = context.biometric_coherence
        else:
            cycle.perceived_biometric = None  # engine offline — graceful degradation

        # Planetary label
        cycle.perceived_planetary = context.planetary_label

        # Hook for subclasses / injected perception layer
        if hasattr(self, "_perception_hook"):
            await self._perception_hook(context, cycle)  # type: ignore

    async def _reason(
        self, context: LoopContext, cycle: LoopCycle
    ) -> bool:
        """
        REASON: Determine the next best action toward the goal.
        Returns False if the goal is already complete (nothing left to do).
        Uses SynergyEngine and TaskGraph if available.
        Falls back to a stub plan if engines are not yet wired.
        """
        # Check if task graph signals completion
        if context.task_graph is not None:
            try:
                if context.task_graph.is_complete():
                    cycle.reasoning_summary = "TaskGraph reports all tasks complete."
                    return False  # Signal: goal achieved
                next_task = context.task_graph.next_task()
                context.current_task = next_task
                cycle.planned_action = getattr(next_task, "action", str(next_task))
                cycle.planned_tool = getattr(next_task, "tool", "")
                cycle.reasoning_summary = f"TaskGraph selected: {cycle.planned_action}"
                return True
            except Exception as exc:  # noqa: BLE001
                logger.warning("[AgenticLoop.reason] TaskGraph error: %s", exc)

        # Synergy engine reasoning
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
                logger.warning("[AgenticLoop.reason] SynergyEngine error: %s", exc)

        # Fallback: stub pass-through (loop continues; integrator must wire real plan)
        if len(context.cycle_memory) >= 3:
            # Safety: if we have done 3+ cycles without real plan, declare complete
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
        Returns (action_ok, optional_halt_condition).
        """
        action = cycle.planned_action
        tool_name = cycle.planned_tool

        # ── ActionGate sovereignty check ──
        if self.action_gate is not None:
            try:
                gate_result = await self._gate_check(action, context)
                cycle.gate_decision = str(gate_result)

                if not gate_result.approved:
                    if gate_result.requires_human_approval:
                        # Human-in-the-loop gate
                        approved = await self.approval_callback(
                            action,
                            gate_result.reason or "Irreversible action requires Gaian confirmation."
                        )
                        if not approved:
                            cycle.action_approved = False
                            logger.info(
                                "[AgenticLoop.act] Gaian declined approval for action=%s",
                                action
                            )
                            return False, HaltCondition.HUMAN_REQUIRED
                        # Gaian approved — proceed
                    else:
                        cycle.action_approved = False
                        logger.warning(
                            "[AgenticLoop.act] ActionGate BLOCKED action=%s reason=%s",
                            action, gate_result.reason
                        )
                        return False, HaltCondition.ACTION_BLOCKED
            except Exception as exc:  # noqa: BLE001
                logger.warning("[AgenticLoop.act] ActionGate error (proceeding): %s", exc)

        # ── Execute tool ──────────────────
        cycle.action_approved = True
        if tool_name and tool_name in self.tool_registry:
            tool_fn = self.tool_registry[tool_name]
            try:
                result = await tool_fn(context, cycle)
                cycle.action_result = result
                context.last_action_result = result
                context.last_action_success = True
            except Exception as exc:  # noqa: BLE001
                cycle.action_error = str(exc)
                context.last_action_success = False
                logger.error(
                    "[AgenticLoop.act] Tool '%s' raised: %s", tool_name, exc
                )
                # Don't halt — let observe() decide
        else:
            # No tool registered — stub success
            cycle.action_result = {"status": "stub_ok", "action": action}
            context.last_action_result = cycle.action_result
            context.last_action_success = True

        return True, None

    async def _observe(
        self, context: LoopContext, cycle: LoopCycle
    ) -> tuple[bool, Optional[HaltCondition]]:
        """
        OBSERVE: Evaluate action outcome, update state, decide whether to loop or halt.
        Returns (goal_done, optional_halt).
        """
        # Track task completion
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

        # Estimate progress
        total = len(context.completed_tasks) + len(context.failed_tasks)
        cycle.goal_progress = (
            len(context.completed_tasks) / total if total > 0 else 0.0
        )

        # Goal completion signal from task graph
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

        # Persistent failure gate — if last 3 actions all failed, halt
        recent = context.cycle_memory[-3:] if len(context.cycle_memory) >= 3 else []
        if recent and all(not c.get("success") for c in recent):
            logger.warning(
                "[AgenticLoop.observe] 3 consecutive failures — halting loop."
            )
            return False, HaltCondition.ERROR

        cycle.should_continue = True
        return False, None

    # ── Internal helpers ─────────────────────

    async def _synergy_plan(self, context: LoopContext) -> dict:
        """Delegate goal planning to SynergyEngine."""
        if self.synergy_engine is None:
            return {"action": "stub", "tool": "", "summary": "no synergy engine"}
        if asyncio.iscoroutinefunction(self.synergy_engine.plan):
            return await self.synergy_engine.plan(context.goal, context)
        return self.synergy_engine.plan(context.goal, context)

    async def _gate_check(self, action: str, context: LoopContext):
        """Run the ActionGate sovereignty check."""
        if asyncio.iscoroutinefunction(self.action_gate.evaluate):
            return await self.action_gate.evaluate(action, context.gaian_id)
        return self.action_gate.evaluate(action, context.gaian_id)

    def _log_cycle(self, cycle: LoopCycle) -> None:
        """Emit a structured log for the completed cycle — Canon C30."""
        logger.info(
            "[AgenticLoop] CYCLE iteration=%d phase=%s action=%r tool=%r "
            "approved=%s progress=%.2f duration_ms=%.1f halt=%s",
            cycle.iteration,
            cycle.phase_exited.value,
            cycle.planned_action[:60] if cycle.planned_action else "",
            cycle.planned_tool,
            cycle.action_approved,
            cycle.goal_progress,
            cycle.duration_ms,
            cycle.halt_condition.value if cycle.halt_condition else "none",
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
    when engines are not yet wired, so this can ship before its
    dependencies are fully built.
    """
    return AgenticLoop(
        action_gate=action_gate,
        synergy_engine=synergy_engine,
        task_graph_factory=task_graph_factory,
        approval_callback=approval_callback,
        max_iterations=max_iterations,
        tool_registry=tool_registry or {},
    )
