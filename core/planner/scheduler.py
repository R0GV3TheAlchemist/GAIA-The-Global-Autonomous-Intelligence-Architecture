"""
core.planner.scheduler
======================
Async priority-queue task scheduler for GAIA-OS.

The TaskScheduler manages a queue of discrete Tasks — coroutine-based
work items representing tool calls, memory writes, API calls, planner
steps, or any other async operation GAIA needs to perform.

Key features
 ------------
- Priority queue: higher-priority tasks execute first.
- Concurrency cap: configurable max concurrent tasks (default 4).
- Retry logic: each task has a max_retries and backoff_seconds setting.
- TTL expiry: tasks can declare a time-to-live; expired tasks are
  discarded before execution.
- Hooks: on_success / on_failure callbacks per task for integration
  with the goal registry and audit ledger.
- Policy gate: optional PolicyEngine integration — tasks that fail
  policy are moved to DENIED status without execution.

Usage
 -----
    from core.planner import TaskScheduler, Task

    scheduler = TaskScheduler(max_concurrent=4)

    async def my_work():
        await asyncio.sleep(0.1)
        return "done"

    task = Task(name="demo", coroutine=my_work, priority=7)
    scheduler.submit(task)

    # In your async event loop:
    await scheduler.run_once()     # process one batch
    await scheduler.run_forever()  # continuous background loop
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

log = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    QUEUED    = "queued"
    RUNNING   = "running"
    COMPLETED = "completed"
    FAILED    = "failed"
    DENIED    = "denied"    # blocked by policy engine
    EXPIRED   = "expired"   # TTL elapsed before execution
    CANCELLED = "cancelled"


@dataclass(order=False)
class Task:
    """
    A single schedulable work item.

    Attributes
    ----------
    name         : Human-readable identifier (need not be unique).
    coroutine    : A zero-argument async callable that performs the work.
    priority     : 0 (lowest) → 10 (highest).  Default 5.
    max_retries  : How many times to retry on failure.  Default 0.
    backoff_sec  : Seconds to wait between retries.  Default 1.0.
    ttl_seconds  : Discard if still QUEUED after this many seconds.
    action_key   : Optional action key for policy engine evaluation
                   (e.g. "web_search", "file_write").  If None, no
                   policy check is performed.
    context      : Arbitrary context dict forwarded to the policy engine.
    on_success   : Optional async callback(result) invoked on success.
    on_failure   : Optional async callback(error) invoked on failure.
    goal_id      : Optional Goal id this task belongs to.
    step_index   : Optional GoalStep index within the goal.
    id           : UUID4 string assigned at creation.
    status       : Current task status.
    result       : Output of the coroutine once completed.
    error        : Error message if the task failed.
    attempts     : How many times execution has been attempted.
    submitted_at : Unix timestamp of submission.
    started_at   : Unix timestamp of first execution attempt.
    finished_at  : Unix timestamp of completion/failure.
    """
    name:         str
    coroutine:    Callable[[], Awaitable[Any]]
    priority:     int                           = 5
    max_retries:  int                           = 0
    backoff_sec:  float                         = 1.0
    ttl_seconds:  Optional[float]               = None
    action_key:   Optional[str]                 = None
    context:      Dict[str, Any]                = field(default_factory=dict)
    on_success:   Optional[Callable]            = field(default=None, repr=False)
    on_failure:   Optional[Callable]            = field(default=None, repr=False)
    goal_id:      Optional[str]                 = None
    step_index:   Optional[int]                 = None
    id:           str                           = field(default_factory=lambda: str(uuid.uuid4()))
    status:       TaskStatus                    = TaskStatus.QUEUED
    result:       Optional[Any]                 = field(default=None, repr=False)
    error:        Optional[str]                 = None
    attempts:     int                           = 0
    submitted_at: float                         = field(default_factory=time.time)
    started_at:   Optional[float]               = None
    finished_at:  Optional[float]               = None

    def is_expired(self) -> bool:
        if self.ttl_seconds is None:
            return False
        return time.time() > self.submitted_at + self.ttl_seconds

    # Tasks are ordered by priority (descending) for the heap
    def __lt__(self, other: "Task") -> bool:
        return self.priority > other.priority

    def to_dict(self) -> dict:
        return {
            "id":           self.id,
            "name":         self.name,
            "priority":     self.priority,
            "status":       self.status.value,
            "attempts":     self.attempts,
            "action_key":   self.action_key,
            "goal_id":      self.goal_id,
            "step_index":   self.step_index,
            "result":       str(self.result) if self.result is not None else None,
            "error":        self.error,
            "submitted_at": self.submitted_at,
            "started_at":   self.started_at,
            "finished_at":  self.finished_at,
        }


class TaskScheduler:
    """
    Async priority-queue task scheduler.

    Parameters
    ----------
    max_concurrent  : Maximum tasks running simultaneously.  Default 4.
    policy_engine   : Optional PolicyEngine for gating tasks before
                      execution.  If None, all tasks bypass policy check.
    poll_interval   : Seconds between queue polls in run_forever().  Default 0.1.
    """

    def __init__(
        self,
        max_concurrent: int  = 4,
        policy_engine         = None,   # PolicyEngine | None
        poll_interval:  float = 0.1,
    ) -> None:
        self._max   = max_concurrent
        self._policy = policy_engine
        self._poll  = poll_interval
        self._queue: List[Task] = []
        self._running: Dict[str, asyncio.Task] = {}
        self._history: List[Task] = []
        self._running_flag = False

    # ------------------------------------------------------------------
    # Submission
    # ------------------------------------------------------------------

    def submit(self, task: Task) -> Task:
        """Add a task to the queue.  Returns the task."""
        import heapq
        heapq.heappush(self._queue, task)
        log.debug("TaskScheduler: submitted task %r (priority=%d)", task.name, task.priority)
        return task

    def cancel(self, task_id: str) -> bool:
        """Cancel a QUEUED task by id.  Returns True if found."""
        for t in self._queue:
            if t.id == task_id and t.status == TaskStatus.QUEUED:
                t.status = TaskStatus.CANCELLED
                t.finished_at = time.time()
                return True
        return False

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def run_once(self) -> int:
        """
        Process one batch: fill up to max_concurrent slots from the
        queue, await all running tasks to completion, return count
        of tasks completed in this batch.
        """
        import heapq
        started = 0
        while self._queue and len(self._running) < self._max:
            task = heapq.heappop(self._queue)
            if task.status == TaskStatus.CANCELLED:
                self._history.append(task)
                continue
            if task.is_expired():
                task.status = TaskStatus.EXPIRED
                task.finished_at = time.time()
                self._history.append(task)
                log.info("TaskScheduler: task %r expired.", task.name)
                continue
            # Policy gate
            if self._policy and task.action_key:
                decision = self._policy.evaluate(task.action_key, task.context)
                if not decision.allowed and not decision.needs_consent:
                    task.status = TaskStatus.DENIED
                    task.error  = decision.reason
                    task.finished_at = time.time()
                    self._history.append(task)
                    log.warning(
                        "TaskScheduler: task %r DENIED by policy (%s)",
                        task.name, decision.rule_name,
                    )
                    continue
            # Launch
            atask = asyncio.create_task(self._execute(task))
            self._running[task.id] = atask
            started += 1

        # Await all running
        if self._running:
            done, _ = await asyncio.wait(
                self._running.values(),
                return_when=asyncio.ALL_COMPLETED,
            )
            for _fut in done:
                pass  # results stored on task objects in _execute()
            self._running.clear()

        return started

    async def run_forever(self) -> None:
        """Run the scheduler loop until stop() is called."""
        self._running_flag = True
        log.info("TaskScheduler: starting continuous loop (poll=%.2fs)", self._poll)
        while self._running_flag:
            if self._queue or self._running:
                await self.run_once()
            await asyncio.sleep(self._poll)

    def stop(self) -> None:
        """Signal run_forever() to exit after the current batch."""
        self._running_flag = False

    # ------------------------------------------------------------------
    # Stats
    # ------------------------------------------------------------------

    def stats(self) -> dict:
        all_tasks = list(self._queue) + list(self._history)
        return {
            "queued":    sum(1 for t in self._queue if t.status == TaskStatus.QUEUED),
            "running":   len(self._running),
            "completed": sum(1 for t in self._history if t.status == TaskStatus.COMPLETED),
            "failed":    sum(1 for t in self._history if t.status == TaskStatus.FAILED),
            "denied":    sum(1 for t in self._history if t.status == TaskStatus.DENIED),
            "expired":   sum(1 for t in self._history if t.status == TaskStatus.EXPIRED),
            "total":     len(all_tasks) + len(self._running),
        }

    def pending_for_goal(self, goal_id: str) -> List[Task]:
        """Return all queued tasks linked to a specific goal."""
        return [t for t in self._queue if t.goal_id == goal_id and t.status == TaskStatus.QUEUED]

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    async def _execute(self, task: Task) -> None:
        task.status     = TaskStatus.RUNNING
        task.started_at = time.time()
        task.attempts  += 1
        last_exc: Optional[Exception] = None

        for attempt in range(task.max_retries + 1):
            try:
                result     = await task.coroutine()
                task.result = result
                task.status = TaskStatus.COMPLETED
                task.finished_at = time.time()
                log.debug("TaskScheduler: task %r completed (attempt %d)", task.name, attempt + 1)
                if task.on_success:
                    try:
                        await task.on_success(result)
                    except Exception as cb_exc:
                        log.warning("Task on_success callback raised: %s", cb_exc)
                self._history.append(task)
                return
            except Exception as exc:
                last_exc = exc
                task.attempts += 1
                log.warning(
                    "TaskScheduler: task %r attempt %d/%d failed: %s",
                    task.name, attempt + 1, task.max_retries + 1, exc,
                )
                if attempt < task.max_retries:
                    await asyncio.sleep(task.backoff_sec * (attempt + 1))

        # All retries exhausted
        task.status      = TaskStatus.FAILED
        task.error       = str(last_exc)
        task.finished_at = time.time()
        if task.on_failure:
            try:
                await task.on_failure(str(last_exc))
            except Exception as cb_exc:
                log.warning("Task on_failure callback raised: %s", cb_exc)
        self._history.append(task)
