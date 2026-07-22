"""intelligence.agent

NEXUS Agent Abstraction

Defines the Agent class — a self-contained, goal-directed reasoning unit
within the NEXUS intelligence layer. Each Agent owns a CognitiveKernel
instance and operates within the governance framework.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.2 - Agent
    GOVERNANCE.md          Agent accountability requirements
Research reference:
    Constitutional AI          - agent decision guardrails
    MemGPT arXiv:2310.08560    - agent-level memory paging
"""
from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Optional

logger = logging.getLogger("intelligence.agent")


class AgentStatus(Enum):
    """Lifecycle status of a NEXUS Agent."""
    INITIALISING = auto()
    IDLE = auto()
    RUNNING = auto()
    SUSPENDED = auto()
    TERMINATED = auto()
    ERROR = auto()


@dataclass
class AgentConfig:
    """Configuration for a NEXUS Agent.

    Fields:
        name:           Human-readable agent name.
        max_cycles:     Maximum cognitive cycles before mandatory rest (0 = unlimited).
        memory_quota:   Maximum MemorySegment bytes (0 = unlimited).
        governance_mode: 'strict' | 'audit' | 'permissive' — passed to GovernanceEngine.
    """
    name: str
    max_cycles: int = 0
    memory_quota: int = 0
    governance_mode: str = "strict"


class Agent:
    """A self-contained NEXUS reasoning agent.

    Each Agent wraps a CognitiveKernel, maintains its own goal stack,
    and reports lifecycle events to TelemetryCollector.

    Reference:
        NEXUS_UNIVERSAL_OS.md Domain 2.2.
        GAIAN_LAWS.md Law I — Sovereignty of Self.
    """

    def __init__(self, config: AgentConfig) -> None:
        self.agent_id: str = str(uuid.uuid4())
        self.config = config
        self.status: AgentStatus = AgentStatus.INITIALISING
        self._goals: list[str] = []
        logger.info("Agent '%s' (%s) initialised.", config.name, self.agent_id)

    def run(self, percept: Any) -> Any:
        """Run one cognitive cycle on the given percept.

        Args:
            percept: Input from PerceptionEngine.

        Returns:
            Decision or action result.

        Raises:
            NotImplementedError: Always in Phase A stub.
                Expected: delegate to CognitiveKernel.process(), update status,
                emit telemetry event, enforce max_cycles limit.
        """
        raise NotImplementedError(
            "Agent.run() not yet implemented. "
            "Expected: CognitiveKernel.process(percept), telemetry emit, status update."
        )

    def add_goal(self, goal: str) -> None:
        """Add a goal to this agent's goal stack.

        Args:
            goal: Natural-language or structured goal description.
        """
        self._goals.append(goal)
        logger.debug("Agent '%s': goal added — %s.", self.config.name, goal)

    def terminate(self) -> None:
        """Gracefully terminate this agent."""
        self.status = AgentStatus.TERMINATED
        logger.info("Agent '%s' terminated.", self.config.name)
