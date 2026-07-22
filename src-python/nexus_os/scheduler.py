"""
nexus_os.scheduler — Real-Time Scheduler

Implements a hybrid real-time task scheduler for the NEXUS OS kernel.
Supports both hard real-time tasks (Earliest Deadline First) and soft
priority tasks (weighted priority queue), unified under a single
asyncio-compatible scheduling loop.

Additionally models per-task energy profiles, enabling carbon-aware and
battery-constrained scheduling aligned with NEXUS's planetary energy grid
interface.

Design references:
  - Liu & Layland 1973 EDF and RMS scheduling proofs
  - asyncio event loop integration patterns (Python 3.11+)
  - NEXUS_UNIVERSAL_OS.md Domain 1.3 — Scheduler Architecture
  - ENERGY_GRID_INTERFACE.md — Carbon-aware scheduling
Ethics reference: ETHICS.md Commitment 5 — Resource Accountability
GAIAN law:        GAIAN_LAWS.md Law II — Memory Sovereignty (task isolation)
"""
from __future__ import annotations

import asyncio
import heapq
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import IntEnum
from typing import Awaitable, Callable, Optional

logger = logging.getLogger("nexus_os.scheduler")


class TaskPriority(IntEnum):
    """Priority levels for NEXUS OS tasks.

    CRITICAL and HIGH tasks are treated as hard real-time and scheduled
    under Earliest Deadline First. NORMAL and LOW tasks use weighted priority
    queuing. IDLE tasks run only when no other work exists.
    Reference: NEXUS_UNIVERSAL_OS.md Domain 1.3
    """
    CRITICAL = 0  # Hard real-time, kernel-level (EDF)
    HIGH     = 1  # Hard real-time, governance/ethics layer (EDF)
    NORMAL   = 2  # Soft priority, standard engine tasks
    LOW      = 3  # Soft priority, background analytics
    IDLE     = 4  # Runs only when scheduler is otherwise empty


@dataclass
class EnergyProfile:
    """Energy budget descriptor for a scheduled task.

    Models the expected and maximum energy consumption of a task in
    milliwatt-hours (mWh). When a task's measured consumption exceeds
    max_budget_mwh, the scheduler may demote its priority or suspend it
    pending ENERGY_GRID_INTERFACE negotiation.
    Reference: ENERGY_GRID_INTERFACE.md; Green Software Foundation SCI spec.
    """
    expected_mwh:      float = 0.0
    max_budget_mwh:    float = float("inf")
    carbon_intensity:  float = 0.0   # gCO2/kWh — 0.0 = unknown

    def is_within_budget(self, actual_mwh: float) -> bool:
        """Return True if actual consumption is within the max budget."""
        return actual_mwh <= self.max_budget_mwh


@dataclass(order=True)
class _TaskDescriptor:
    """Internal descriptor for a task in the RTScheduler queue.

    order=True makes tasks sortable by (deadline_ts, priority) supporting
    both EDF (sort by deadline) and priority queuing in a unified heapq.
    Not part of the public API — use RTScheduler to enqueue tasks.
    """
    deadline_ts:    float                            # Monotonic timestamp (seconds)
    priority:       TaskPriority = field(compare=True)
    task_id:        str          = field(compare=False)
    coroutine_fn:   Callable[[], Awaitable[None]] = field(compare=False)
    energy_profile: EnergyProfile = field(compare=False, default_factory=EnergyProfile)


class RTScheduler:
    """Hybrid real-time scheduler for NEXUS OS.

    Maintains two queues:
      - Hard RT queue (CRITICAL, HIGH): sorted by deadline (EDF)
      - Soft priority queue (NORMAL, LOW, IDLE): sorted by priority weight

    The tick coroutine is called by the kernel's asyncio event loop on each
    scheduling cycle. It selects the highest-urgency task and dispatches it
    via asyncio.ensure_future.

    Energy-aware demotion: tasks that exceed their EnergyProfile.max_budget_mwh
    are demoted from HIGH→NORMAL on the next cycle and a warning is logged.
    Reference: Liu & Layland 1973 EDF; NEXUS_UNIVERSAL_OS.md Domain 1.3
    """

    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None) -> None:
        self._hard_rt_queue: list[_TaskDescriptor] = []   # heapq
        self._soft_queue:    list[_TaskDescriptor] = []   # heapq
        self._loop = loop or asyncio.get_event_loop()
        self.running = False
        logger.info("RTScheduler initialised.")

    def enqueue(
        self,
        task_id: str,
        coroutine_fn: Callable[[], Awaitable[None]],
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
        energy_profile: Optional[EnergyProfile] = None,
    ) -> None:
        """Enqueue a task for scheduled execution.

        Args:
            task_id:        Unique identifier string for this task.
            coroutine_fn:   Zero-argument async callable to execute.
            priority:       TaskPriority level (default NORMAL).
            deadline:       Optional hard deadline. Required for CRITICAL/HIGH.
            energy_profile: Optional EnergyProfile for carbon-aware scheduling.
        Raises:
            NotImplementedError: Always (stub).
        Reference: NEXUS_UNIVERSAL_OS.md Domain 1.3 — Task Queuing
        """
        raise NotImplementedError(
            "RTScheduler.enqueue — not yet implemented. "
            "Expected: compute deadline_ts from deadline datetime, construct "
            "_TaskDescriptor, heapq.heappush to appropriate queue."
        )

    async def tick(self) -> None:
        """Execute one scheduling cycle.

        Selects the most urgent task from the hard RT queue (if non-empty)
        or the soft queue, and dispatches it. Handles energy demotion.
        Raises:
            NotImplementedError: Always (stub).
        Reference: NEXUS_UNIVERSAL_OS.md Domain 1.3 — Scheduler Loop
        """
        raise NotImplementedError(
            "RTScheduler.tick — not yet implemented. "
            "Expected: pop from hard_rt_queue if non-empty (EDF), else soft_queue, "
            "dispatch via asyncio.ensure_future(task.coroutine_fn()), "
            "handle energy budget tracking."
        )

    async def run(self) -> None:
        """Start the continuous scheduling loop.

        Calls tick in an infinite loop with a short asyncio.sleep yield
        between cycles to allow other coroutines to run.
        Raises:
            NotImplementedError: Always (stub).
        """
        raise NotImplementedError(
            "RTScheduler.run — not yet implemented. "
            "Expected: self.running = True; while self.running: await self.tick(); "
            "await asyncio.sleep(0)"
        )

    def stop(self) -> None:
        """Signal the scheduler run loop to exit after the current tick."""
        self.running = False
        logger.info("RTScheduler stop signal received.")
