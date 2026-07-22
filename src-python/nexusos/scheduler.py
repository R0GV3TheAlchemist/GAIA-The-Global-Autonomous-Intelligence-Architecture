"""nexusos.scheduler

Real-Time Scheduler for NEXUS-OS

Implements an asyncio-aware priority/deadline scheduler for NEXUS tasks.
Supports both hard real-time (EDF — Earliest Deadline First) and soft
real-time (priority-weighted) scheduling with per-task energy budgets.

Design:
    - RTScheduler wraps an asyncio-compatible heapq priority queue.
    - Hard real-time tasks carry a `deadline` (monotonic float).
    - Soft real-time tasks carry a `TaskPriority` enum value.
    - EnergyProfile tracks milliwatt-second budgets; exhaustion demotes tasks.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 1.3 - RTScheduler
    ENERGYGRIDINTERFACE.md             - energy budget model
Research reference:
    Liu & Layland 1973 — EDF optimality proof for feasible uniprocessor sets
    glefundes/RTScheduler (GitHub)     — Python EDF/RMS simulator reference
    asyncio docs — run_coroutine_threadsafe for HALDriver→scheduler pathway
"""
from __future__ import annotations

import asyncio
import heapq
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Callable, Coroutine, Optional, Any

logger = logging.getLogger("nexusos.scheduler")


class TaskPriority(Enum):
    """Soft real-time task priority levels."""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass
class EnergyProfile:
    """Per-task energy budget tracking.

    Fields:
        budget_mws:    Remaining energy budget in milliwatt-seconds.
        consumed_mws:  Total energy consumed since task creation.
        exhausted:     True when budget_mws <= 0.

    When exhausted, the RTScheduler demotes the task to BACKGROUND priority,
    aligning with the ENERGYGRIDINTERFACE.md carbon-aware scheduling model.
    """
    budget_mws: float
    consumed_mws: float = 0.0

    @property
    def exhausted(self) -> bool:
        """Return True if the energy budget is fully consumed."""
        return self.budget_mws <= 0.0

    def consume(self, mws: float) -> None:
        """Consume `mws` milliwatt-seconds from the budget."""
        self.consumed_mws += mws
        self.budget_mws = max(0.0, self.budget_mws - mws)


@dataclass(order=True)
class _ScheduledTask:
    """Internal heap entry. sort_key ensures correct heap ordering."""
    sort_key: float
    task_id: str = field(compare=False)
    priority: TaskPriority = field(compare=False)
    deadline: Optional[float] = field(compare=False, default=None)
    coro: Any = field(compare=False, default=None)  # Coroutine or Callable
    energy: Optional[EnergyProfile] = field(compare=False, default=None)


class RTScheduler:
    """asyncio-aware real-time task scheduler for NEXUS-OS.

    Scheduling policy:
        - Tasks with a `deadline` (hard RT) are ordered by EDF.
        - Tasks without a deadline (soft RT) are ordered by TaskPriority value.
        - Tasks whose EnergyProfile is exhausted are demoted to BACKGROUND.

    Usage::

        scheduler = RTScheduler()
        scheduler.schedule(task_id="boot", coro=boot_sequence(),
                           priority=TaskPriority.CRITICAL)
        asyncio.run(scheduler.tick())

    Reference:
        Liu & Layland 1973 — EDF achieves 100% utilisation on feasible sets.
        Python sched module — public interface model (enter, cancel, run).
    """

    def __init__(self) -> None:
        self._heap: list[_ScheduledTask] = []
        logger.info("RTScheduler initialised.")

    def schedule(
        self,
        task_id: str,
        coro: Coroutine | Callable,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[float] = None,
        energy: Optional[EnergyProfile] = None,
    ) -> None:
        """Enqueue a task for scheduling.

        Args:
            task_id:  Unique identifier for this task.
            coro:     Coroutine or callable to execute.
            priority: Soft-RT priority (ignored when deadline is set).
            deadline: Hard-RT deadline as monotonic time (time.monotonic()).
                      When provided, EDF ordering takes precedence.
            energy:   Optional EnergyProfile; exhausted tasks are demoted.
        """
        sort_key = deadline if deadline is not None else float(priority.value)
        entry = _ScheduledTask(
            sort_key=sort_key,
            task_id=task_id,
            priority=priority,
            deadline=deadline,
            coro=coro,
            energy=energy,
        )
        heapq.heappush(self._heap, entry)
        logger.debug("RTScheduler: scheduled task '%s' (key=%.4f).", task_id, sort_key)

    def cancel(self, task_id: str) -> bool:
        """Remove a pending task from the queue.

        Args:
            task_id: ID of the task to cancel.

        Returns:
            True if the task was found and removed, False otherwise.
        """
        before = len(self._heap)
        self._heap = [t for t in self._heap if t.task_id != task_id]
        heapq.heapify(self._heap)
        removed = len(self._heap) < before
        if removed:
            logger.debug("RTScheduler: cancelled task '%s'.", task_id)
        return removed

    async def tick(self) -> None:
        """Execute the highest-priority pending task (one tick).

        Raises:
            NotImplementedError: Full dispatch loop not yet implemented.
                Expected: pop highest-priority entry, check energy exhaustion,
                demote if exhausted, else await coroutine, handle exceptions.
        """
        raise NotImplementedError(
            "RTScheduler.tick() not yet implemented. "
            "Expected: pop heap entry, check EnergyProfile, dispatch coroutine, "
            "handle asyncio.CancelledError and re-schedule as needed."
        )

    def pending_count(self) -> int:
        """Return the number of tasks currently queued."""
        return len(self._heap)
