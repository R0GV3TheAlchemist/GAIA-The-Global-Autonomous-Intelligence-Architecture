"""GAIA-OS Stage Engine — Core Types"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

StageName = Literal[
    "Divergence",
    "Awakening",
    "Crucible",
    "Convergence",
    "Ascendence",
]

STAGE_NAMES: dict[int, StageName] = {
    1: "Divergence",
    2: "Awakening",
    3: "Crucible",
    4: "Convergence",
    5: "Ascendence",
}

# Minimum days each marker must be sustained before a transition is evaluated.
TRANSITION_WINDOWS: dict[tuple[int, int], int] = {
    (1, 2): 21,
    (2, 3): 30,
    (3, 4): 45,
    (4, 5): 60,
}

# Regression: 5 of 6 prior-stage markers for 14+ consecutive days.
REGRESSION_WINDOW_DAYS = 14
REGRESSION_MARKERS_REQUIRED = 5

# Forward transition: 4 of 6 markers sustained.
FORWARD_MARKERS_REQUIRED = 4


@dataclass
class MarkerScores:
    """All six stage markers. All values 0–100 except focus_session_length_min (raw minutes)."""

    decision_entropy: float          # 0–100 (higher = more decisive)
    hrv_coherence: float             # 0–100
    journaling_depth: float          # 0–100
    focus_session_length_min: float  # raw minutes (converted to 0–100 inside scorer)
    goal_completion_rate: float      # 0–100
    emotional_arc_stability: float   # 0–100

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StageRecord:
    principal_id: str
    current_stage: int              # 1–5
    stage_name: StageName
    stage_entered_at: int           # unix ms
    days_in_stage: int
    marker_scores: MarkerScores
    transition_candidate: bool
    regression_risk: bool
    updated_at: int

    @property
    def stage_label(self) -> str:
        return f"Stage {self.current_stage} — {self.stage_name}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["stage_label"] = self.stage_label
        return d


@dataclass
class StageTransition:
    principal_id: str
    from_stage: int
    to_stage: int
    transitioned_at: int            # unix ms
    is_regression: bool
    markers_met: list[str]
    ceremony_shown: bool = False

    @property
    def label(self) -> str:
        name = STAGE_NAMES.get(self.to_stage, str(self.to_stage))
        suffix = "R" if self.is_regression else ""
        return f"Stage {self.to_stage}{suffix} — {name}"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["label"] = self.label
        return d


@dataclass
class TransitionResult:
    """Returned by StageEngine.evaluate(). May or may not contain a transition."""
    record: StageRecord
    transition: StageTransition | None  # None = no change this evaluation

    def to_dict(self) -> dict:
        return {
            "record": self.record.to_dict(),
            "transition": self.transition.to_dict() if self.transition else None,
        }
