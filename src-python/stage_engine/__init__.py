"""GAIA-OS Stage Engine

Issue #63 | Pillar I: Magnum Opus

Tracks each user's position along the five-stage developmental arc:
  Stage 1 — Divergence
  Stage 2 — Awakening
  Stage 3 — Crucible
  Stage 4 — Convergence
  Stage 5 — Ascendence

Consumes:
  - SovereignMemory (biometric_history, stage_records, stage_transitions)
  - AffectEngine (arc_stability signal)

Emits:
  - StageRecord (current state)
  - StageTransition events (forward + regression)
"""

from .engine import StageEngine
from .markers import MarkerScorer
from .types import (
    StageName,
    MarkerScores,
    StageRecord,
    StageTransition,
    TransitionResult,
)

__all__ = [
    "StageEngine",
    "MarkerScorer",
    "StageName",
    "MarkerScores",
    "StageRecord",
    "StageTransition",
    "TransitionResult",
]
