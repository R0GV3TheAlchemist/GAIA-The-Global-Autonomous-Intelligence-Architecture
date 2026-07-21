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

explainability.py — NEXUS Explainability Subsystem.

Every decision produces a DecisionTrace — a causal chain from goal
through reasoning steps to action. ExplanationSummary condenses the
trace into human-readable justifications at three verbosity levels.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import time


class ExplainLevel(Enum):
    L1_USER = auto()     # One-sentence plain language
    L2_OPERATOR = auto() # Step-by-step reasoning chain
    L3_AUDITOR = auto()  # Full causal graph with confidence values


@dataclass
class ReasoningStep:
    """One step in a causal reasoning chain."""
    step_id: UUID = field(default_factory=uuid4)
    description: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class DecisionTrace:
    """
    Complete causal trace from goal through reasoning to final action.

    Produced by the CognitiveKernel on every decision cycle.
    Used as the input to ExplanationSummary for human-readable output.
    """
    trace_id: UUID = field(default_factory=uuid4)
    goal_id: UUID = field(default_factory=uuid4)
    goal_description: str = ""
    action_taken: str = ""
    steps: List[ReasoningStep] = field(default_factory=list)
    outcome: str = ""
    overall_confidence: float = 1.0
    timestamp: float = field(default_factory=time.time)

    def add_step(self, description: str,
                 inputs: Dict[str, Any] = None,
                 outputs: Dict[str, Any] = None,
                 confidence: float = 1.0) -> ReasoningStep:
        step = ReasoningStep(
            description=description,
            inputs=inputs or {},
            outputs=outputs or {},
            confidence=confidence,
        )
        self.steps.append(step)
        self.overall_confidence = sum(s.confidence for s in self.steps) / len(self.steps)
        return step

    def to_dict(self) -> Dict[str, Any]:
        return {
            "trace_id": str(self.trace_id),
            "goal_id": str(self.goal_id),
            "goal_description": self.goal_description,
            "action_taken": self.action_taken,
            "steps": [
                {
                    "step_id": str(s.step_id),
                    "description": s.description,
                    "confidence": s.confidence,
                } for s in self.steps
            ],
            "outcome": self.outcome,
            "overall_confidence": self.overall_confidence,
        }


class ExplanationSummary:
    """
    Condenses a DecisionTrace into a human-readable explanation.

    Three levels of verbosity:
      L1 — one sentence for end-users
      L2 — numbered step-by-step for operators
      L3 — full JSON causal graph for auditors
    """

    def summarize(self, trace: DecisionTrace,
                  level: ExplainLevel = ExplainLevel.L1_USER) -> str:
        if level == ExplainLevel.L1_USER:
            return self._l1(trace)
        elif level == ExplainLevel.L2_OPERATOR:
            return self._l2(trace)
        else:
            return self._l3(trace)

    def _l1(self, trace: DecisionTrace) -> str:
        return (f"Goal: '{trace.goal_description}' → "
                f"Action: '{trace.action_taken}' "
                f"(confidence: {trace.overall_confidence:.0%}).")

    def _l2(self, trace: DecisionTrace) -> str:
        lines = [f"Goal: {trace.goal_description}"]
        for i, step in enumerate(trace.steps, 1):
            lines.append(f"  {i}. {step.description} [conf={step.confidence:.2f}]")
        lines.append(f"Action: {trace.action_taken}")
        lines.append(f"Outcome: {trace.outcome}")
        return "\n".join(lines)

    def _l3(self, trace: DecisionTrace) -> str:
        import json
        return json.dumps(trace.to_dict(), indent=2)
