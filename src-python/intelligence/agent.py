"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEXUS — The Universal Autonomous Intelligence Architecture
  GAIA  — The Global Autonomous Intelligence Architecture

  Author   : Kyle Steen
  GitHub   : R0GV3TheAlchemist (https://github.com/R0GV3TheAlchemist)
  Email    : xxkylesteenxx@outlook.com
  Project  : NEXUS / GAIA
  License  : All Rights Reserved © 2026 Kyle Steen
             Unauthorized use, reproduction, or distribution
             of this file or its contents is strictly prohibited.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

agent.py — NEXUS Agent Framework.

BaseAgent, AgentLifecycle state machine, and AgentCoalition for
collaborative multi-agent problem solving.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4
import time


class AgentState(Enum):
    SPAWNED = auto()
    ACTIVE = auto()
    HIBERNATING = auto()
    TERMINATED = auto()


@dataclass
class AgentLifecycle:
    """Tracks the lifecycle state transitions of an agent."""
    current_state: AgentState = AgentState.SPAWNED
    history: List[tuple] = field(default_factory=list)

    def transition(self, new_state: AgentState) -> None:
        self.history.append((self.current_state, new_state, time.time()))
        self.current_state = new_state


class BaseAgent(ABC):
    """
    Abstract base for all NEXUS agents.

    Concrete agents implement perceive(), decide(), and act().
    The lifecycle transitions are managed by AgentLifecycle.
    """

    def __init__(self, name: str) -> None:
        self.agent_id: UUID = uuid4()
        self.name = name
        self.lifecycle = AgentLifecycle()
        self._coalition: Optional[AgentCoalition] = None

    @abstractmethod
    def perceive(self, world_model: object) -> None:
        """Ingest the current world model snapshot."""
        ...

    @abstractmethod
    def decide(self) -> str:
        """Return an action string based on current perception and goals."""
        ...

    @abstractmethod
    def act(self, action: str) -> None:
        """Execute the decided action."""
        ...

    def activate(self) -> None:
        self.lifecycle.transition(AgentState.ACTIVE)

    def hibernate(self) -> None:
        self.lifecycle.transition(AgentState.HIBERNATING)

    def terminate(self) -> None:
        self.lifecycle.transition(AgentState.TERMINATED)

    def join_coalition(self, coalition: AgentCoalition) -> None:
        self._coalition = coalition
        coalition.add_member(self)

    @property
    def state(self) -> AgentState:
        return self.lifecycle.current_state


class AgentCoalition:
    """
    A capability-gated coalition of cooperating agents.

    Membership is logged. Coalitions can elect a coordinator
    and broadcast shared goals to all members.
    """

    def __init__(self, name: str) -> None:
        self.coalition_id: UUID = uuid4()
        self.name = name
        self._members: Dict[UUID, BaseAgent] = {}
        self.audit_log: List[dict] = []
        self.coordinator_id: Optional[UUID] = None

    def add_member(self, agent: BaseAgent) -> None:
        self._members[agent.agent_id] = agent
        self.audit_log.append({
            "event": "MEMBER_JOINED",
            "agent_id": str(agent.agent_id),
            "name": agent.name,
            "timestamp": time.time(),
        })

    def remove_member(self, agent_id: UUID) -> None:
        agent = self._members.pop(agent_id, None)
        if agent:
            self.audit_log.append({
                "event": "MEMBER_LEFT",
                "agent_id": str(agent_id),
                "timestamp": time.time(),
            })

    def elect_coordinator(self, agent_id: UUID) -> None:
        if agent_id in self._members:
            self.coordinator_id = agent_id
            self.audit_log.append({
                "event": "COORDINATOR_ELECTED",
                "agent_id": str(agent_id),
                "timestamp": time.time(),
            })

    def broadcast_goal(self, goal_description: str) -> None:
        """Broadcast a shared goal description to all active members."""
        self.audit_log.append({
            "event": "GOAL_BROADCAST",
            "goal": goal_description,
            "recipients": [str(aid) for aid in self._members],
            "timestamp": time.time(),
        })

    @property
    def members(self) -> List[BaseAgent]:
        return list(self._members.values())

    def __len__(self) -> int:
        return len(self._members)
