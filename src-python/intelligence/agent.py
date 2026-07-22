"""
intelligence.agent — Agent Lifecycle & Coalition Management

Defines BaseAgent, the foundational agent abstraction for all NEXUS
intelligence agents, along with AgentLifecycle state management and
AgentCoalition for multi-agent coordination.

Design references:
  - FIPA agent lifecycle standard (initiated, active, suspended, terminated)
  - Multi-Agent Systems: Wooldridge & Jennings 1995
  - NEXUS_UNIVERSAL_OS.md Domain 2.2 — Agent Architecture
Ethics reference: ETHICS.md Commitment 7 — Agent Accountability
GAIAN law:        GAIAN_LAWS.md Law IV — Coalition Sovereignty
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("intelligence.agent")


class AgentLifecycle(Enum):
    """FIPA-inspired lifecycle states for a NEXUS agent."""
    INITIATED  = auto()  # Created, not yet active
    ACTIVE     = auto()  # Running and processing goals
    SUSPENDED  = auto()  # Temporarily paused by governance
    TERMINATED = auto()  # Permanently stopped


class BaseAgent:
    """Foundational base class for all NEXUS intelligence agents.

    Subclasses must implement the perceive() and act() methods.
    The run loop calls perceive → reason → act on each cycle.
    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.2; FIPA agent lifecycle.
    """

    def __init__(self, name: str, agent_id: Optional[str] = None) -> None:
        self.agent_id:  str            = agent_id or str(uuid.uuid4())
        self.name:      str            = name
        self.lifecycle: AgentLifecycle = AgentLifecycle.INITIATED
        self.created_at: datetime      = datetime.now(timezone.utc)
        logger.info("BaseAgent '%s' (%s) created.", name, self.agent_id)

    def perceive(self) -> dict[str, Any]:
        """Collect sensor / environment inputs for this agent cycle.

        Raises:
            NotImplementedError: Must be overridden by subclasses.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.perceive — must be implemented by subclasses."
        )

    def act(self, action: dict[str, Any]) -> None:
        """Execute the action selected by the reasoning engine.

        Raises:
            NotImplementedError: Must be overridden by subclasses.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__}.act — must be implemented by subclasses."
        )

    def run_cycle(self) -> None:
        """Execute one perceive→reason→act cycle.

        Raises:
            NotImplementedError: Always (stub in BaseAgent).
        """
        raise NotImplementedError(
            "BaseAgent.run_cycle — not yet implemented. "
            "Expected: observations = self.perceive(); action = self.reason(observations); "
            "self.act(action); record to AuditLog."
        )


@dataclass
class AgentCoalition:
    """A named coalition of cooperating NEXUS agents.

    Coalitions share a common goal and a negotiated resource budget.
    Membership is dynamic — agents can join or leave mid-execution.
    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.2; Wooldridge MAS ch.8.
    """
    coalition_id: str           = field(default_factory=lambda: str(uuid.uuid4()))
    name:         str           = "unnamed-coalition"
    members:      list[BaseAgent] = field(default_factory=list)
    shared_goal:  Optional[str] = None

    def add_member(self, agent: BaseAgent) -> None:
        """Add an agent to the coalition."""
        if agent not in self.members:
            self.members.append(agent)
            logger.info("Coalition '%s': added agent '%s'.", self.name, agent.name)

    def remove_member(self, agent: BaseAgent) -> None:
        """Remove an agent from the coalition."""
        self.members = [m for m in self.members if m.agent_id != agent.agent_id]
        logger.info("Coalition '%s': removed agent '%s'.", self.name, agent.name)
