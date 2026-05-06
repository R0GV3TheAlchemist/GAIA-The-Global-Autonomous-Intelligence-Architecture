"""
core.planner.goal
=================
Goal representation and registry for GAIA's multi-step planner.

A *Goal* is a persistent, user-owned intention that GAIA works toward
across one or more sessions.  Goals decompose into *steps* (ordered
list of sub-tasks), and each step can itself reference a Goal, enabling
hierarchical / recursive planning.

GoalStatus lifecycle
--------------------

    PENDING → IN_PROGRESS → COMPLETED
                          ↘ FAILED
                          ↘ CANCELLED
                          ↘ PAUSED  → IN_PROGRESS  (resumable)

GoalRegistry
------------
In-process registry backed by a simple dict.  Thread-safe for the
single-writer GAIA runtime.  Persistence is delegated to the caller
(e.g. serialise to the memory store via ``goal.to_dict()``).
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class GoalStatus(str, Enum):
    PENDING     = "pending"
    IN_PROGRESS = "in_progress"
    PAUSED      = "paused"
    COMPLETED   = "completed"
    FAILED      = "failed"
    CANCELLED   = "cancelled"


class GoalPriority(int, Enum):
    LOW      = 1
    NORMAL   = 5
    HIGH     = 8
    CRITICAL = 10


@dataclass
class GoalStep:
    """
    One atomic step within a Goal.

    Attributes
    ----------
    index       : Position in the parent goal's step list (0-based).
    description : Human-readable description of the step.
    action      : Machine-readable action key (e.g. "web_search", "remember").
    params      : Arbitrary key-value parameters passed to the action handler.
    status      : Current step status.
    result      : Output of the action once completed.
    error       : Error message if the step failed.
    """
    index:       int
    description: str
    action:      str                   = "noop"
    params:      Dict[str, Any]        = field(default_factory=dict)
    status:      GoalStatus            = GoalStatus.PENDING
    result:      Optional[Any]         = None
    error:       Optional[str]         = None
    started_at:  Optional[float]       = None
    finished_at: Optional[float]       = None

    def mark_started(self) -> None:
        self.status     = GoalStatus.IN_PROGRESS
        self.started_at = time.time()

    def mark_done(self, result: Any = None) -> None:
        self.status      = GoalStatus.COMPLETED
        self.result      = result
        self.finished_at = time.time()

    def mark_failed(self, error: str) -> None:
        self.status      = GoalStatus.FAILED
        self.error       = error
        self.finished_at = time.time()

    def to_dict(self) -> dict:
        return {
            "index":       self.index,
            "description": self.description,
            "action":      self.action,
            "params":      self.params,
            "status":      self.status.value,
            "result":      str(self.result) if self.result is not None else None,
            "error":       self.error,
            "started_at":  self.started_at,
            "finished_at": self.finished_at,
        }


@dataclass
class Goal:
    """
    A persistent multi-step intention that GAIA pursues on behalf of
    a user.

    Attributes
    ----------
    id          : Unique goal identifier (UUID4 string).
    user_id     : Owner of this goal.
    title       : Short human-readable title.
    description : Full natural-language description of the desired outcome.
    steps       : Ordered list of GoalStep objects.
    status      : Current goal status.
    priority    : Scheduling priority (higher = processed first).
    created_at  : Unix timestamp of creation.
    updated_at  : Unix timestamp of last status change.
    session_id  : Optional session that spawned this goal.
    metadata    : Arbitrary extra data (tags, source, etc.).
    """
    user_id:     str
    title:       str
    description: str                   = ""
    steps:       List[GoalStep]        = field(default_factory=list)
    status:      GoalStatus            = GoalStatus.PENDING
    priority:    GoalPriority          = GoalPriority.NORMAL
    id:          str                   = field(default_factory=lambda: str(uuid.uuid4()))
    created_at:  float                 = field(default_factory=time.time)
    updated_at:  float                 = field(default_factory=time.time)
    session_id:  Optional[str]         = None
    metadata:    Dict[str, Any]        = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Step management
    # ------------------------------------------------------------------

    def add_step(
        self,
        description: str,
        action:      str            = "noop",
        params:      Optional[Dict] = None,
    ) -> GoalStep:
        """Append a new step and return it."""
        step = GoalStep(
            index=len(self.steps),
            description=description,
            action=action,
            params=params or {},
        )
        self.steps.append(step)
        self._touch()
        return step

    def next_step(self) -> Optional[GoalStep]:
        """Return the next PENDING step, or None if none remain."""
        for s in self.steps:
            if s.status == GoalStatus.PENDING:
                return s
        return None

    def current_step(self) -> Optional[GoalStep]:
        """Return the currently IN_PROGRESS step, or None."""
        for s in self.steps:
            if s.status == GoalStatus.IN_PROGRESS:
                return s
        return None

    @property
    def progress(self) -> float:
        """Completion fraction in [0.0, 1.0]."""
        if not self.steps:
            return 0.0
        done = sum(1 for s in self.steps if s.status == GoalStatus.COMPLETED)
        return done / len(self.steps)

    # ------------------------------------------------------------------
    # Lifecycle transitions
    # ------------------------------------------------------------------

    def start(self) -> "Goal":
        if self.status not in (GoalStatus.PENDING, GoalStatus.PAUSED):
            raise ValueError(f"Cannot start goal in status {self.status}")
        self.status = GoalStatus.IN_PROGRESS
        self._touch()
        return self

    def pause(self) -> "Goal":
        self.status = GoalStatus.PAUSED
        self._touch()
        return self

    def complete(self) -> "Goal":
        self.status = GoalStatus.COMPLETED
        self._touch()
        return self

    def fail(self, reason: str = "") -> "Goal":
        self.status = GoalStatus.FAILED
        self.metadata["failure_reason"] = reason
        self._touch()
        return self

    def cancel(self) -> "Goal":
        self.status = GoalStatus.CANCELLED
        self._touch()
        return self

    def auto_advance(self) -> bool:
        """
        Inspect step statuses and auto-advance the goal status:
        - All steps COMPLETED  → mark goal COMPLETED.
        - Any step FAILED      → mark goal FAILED.
        Returns True if the goal status changed.
        """
        statuses = [s.status for s in self.steps]
        if not statuses:
            return False
        if all(s == GoalStatus.COMPLETED for s in statuses):
            if self.status != GoalStatus.COMPLETED:
                self.complete()
                return True
        elif any(s == GoalStatus.FAILED for s in statuses):
            if self.status not in (GoalStatus.FAILED, GoalStatus.CANCELLED):
                self.fail(reason="One or more steps failed.")
                return True
        return False

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "id":          self.id,
            "user_id":     self.user_id,
            "title":       self.title,
            "description": self.description,
            "status":      self.status.value,
            "priority":    self.priority.value,
            "progress":    self.progress,
            "steps":       [s.to_dict() for s in self.steps],
            "created_at":  self.created_at,
            "updated_at":  self.updated_at,
            "session_id":  self.session_id,
            "metadata":    self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Goal":
        goal = cls(
            user_id=data["user_id"],
            title=data["title"],
            description=data.get("description", ""),
            status=GoalStatus(data["status"]),
            priority=GoalPriority(data.get("priority", 5)),
            id=data["id"],
            created_at=data["created_at"],
            updated_at=data["updated_at"],
            session_id=data.get("session_id"),
            metadata=data.get("metadata", {}),
        )
        for sd in data.get("steps", []):
            step = GoalStep(
                index=sd["index"],
                description=sd["description"],
                action=sd["action"],
                params=sd.get("params", {}),
                status=GoalStatus(sd["status"]),
                result=sd.get("result"),
                error=sd.get("error"),
                started_at=sd.get("started_at"),
                finished_at=sd.get("finished_at"),
            )
            goal.steps.append(step)
        return goal

    def _touch(self) -> None:
        self.updated_at = time.time()

    def __repr__(self) -> str:
        return (
            f"Goal(id={self.id[:8]}…, title={self.title!r}, "
            f"status={self.status.value}, progress={self.progress:.0%})"
        )


class GoalRegistry:
    """
    In-process registry of active Goals.

    Thread-safe for the single-writer GAIA async runtime.  Goals are
    stored by id and can be filtered by user_id or status.

    Persistence
    -----------
    Call ``goal.to_dict()`` and store in the MemoryStore with
    kind=MemoryKind.GOAL, tier=MemoryTier.LONG_TERM.  On startup,
    hydrate via ``GoalRegistry.load_from_dicts(data_list)``.
    """

    def __init__(self) -> None:
        self._goals: Dict[str, Goal] = {}

    def add(self, goal: Goal) -> Goal:
        self._goals[goal.id] = goal
        return goal

    def get(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def remove(self, goal_id: str) -> bool:
        return self._goals.pop(goal_id, None) is not None

    def for_user(self, user_id: str) -> List[Goal]:
        return [g for g in self._goals.values() if g.user_id == user_id]

    def active(self, user_id: Optional[str] = None) -> List[Goal]:
        active_statuses = {GoalStatus.PENDING, GoalStatus.IN_PROGRESS, GoalStatus.PAUSED}
        goals = self._goals.values()
        if user_id:
            goals = (g for g in goals if g.user_id == user_id)  # type: ignore
        return [
            g for g in goals
            if g.status in active_statuses
        ]

    def by_status(self, status: GoalStatus) -> List[Goal]:
        return [g for g in self._goals.values() if g.status == status]

    def next_goal(self, user_id: str) -> Optional[Goal]:
        """Return the highest-priority active goal for a user."""
        candidates = self.active(user_id=user_id)
        if not candidates:
            return None
        return max(candidates, key=lambda g: g.priority.value)

    def load_from_dicts(self, data_list: List[dict]) -> None:
        """Hydrate registry from serialised goal dicts."""
        for d in data_list:
            self.add(Goal.from_dict(d))

    def summary(self) -> dict:
        all_goals = list(self._goals.values())
        return {
            "total":       len(all_goals),
            "by_status":   {s.value: sum(1 for g in all_goals if g.status == s) for s in GoalStatus},
        }

    def __len__(self) -> int:
        return len(self._goals)

    def __repr__(self) -> str:
        return f"GoalRegistry(total={len(self)})"
