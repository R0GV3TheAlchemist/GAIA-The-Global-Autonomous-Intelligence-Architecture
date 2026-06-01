"""Crisis Engine — Multi-Turn Crisis Synthesis & Cumulative Detection.

Public surface:
  CrisisEngine        — main orchestrator
  CrisisSignal        — typed signal emitted per turn
  CrisisSnapshot      — synthesised cross-session risk state
  RiskLevel           — NONE | LOW | MODERATE | HIGH | CRITICAL
  EscalationTier      — MONITOR | SOFT_INTERVENE | HARD_INTERVENE | HANDOFF
  SignalClass         — EXPLICIT | MASKED | GRADUAL | ACUTE
"""

from .types import (
    CrisisSignal,
    CrisisSnapshot,
    RiskLevel,
    EscalationTier,
    SignalClass,
    HandoffRecord,
)
from .engine import CrisisEngine, EngineConfig

__all__ = [
    "CrisisEngine",
    "EngineConfig",
    "CrisisSignal",
    "CrisisSnapshot",
    "RiskLevel",
    "EscalationTier",
    "SignalClass",
    "HandoffRecord",
]
