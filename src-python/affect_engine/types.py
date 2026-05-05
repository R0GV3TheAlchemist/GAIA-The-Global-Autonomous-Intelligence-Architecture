"""GAIA-OS Affect Engine — Core Types"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Literal

EmotionLabel = Literal[
    "joy",
    "sadness",
    "anger",
    "fear",
    "disgust",
    "surprise",
    "neutral",
]


@dataclass
class PadVector:
    pleasure: float   # -1.0 to 1.0
    arousal: float    # 0.0 to 1.0
    dominance: float  # 0.0 to 1.0

    def clamp(self) -> "PadVector":
        self.pleasure = max(-1.0, min(1.0, self.pleasure))
        self.arousal = max(0.0, min(1.0, self.arousal))
        self.dominance = max(0.0, min(1.0, self.dominance))
        return self

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AffectSnapshot:
    id: str
    principal_id: str
    timestamp: int
    source: Literal["journal", "gaia_chat", "system"]
    emotion: EmotionLabel
    confidence: float
    valence: float
    arousal: float
    dominance: float
    entropy: float
    arc_stability: float
    is_neutral_primary: bool
    explanation: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AffectAnalysisResult:
    label: EmotionLabel
    confidence: float
    pad: PadVector
    is_neutral_primary: bool
    entropy: float
    explanation: str

    def to_dict(self) -> dict:
        data = asdict(self)
        data["pad"] = self.pad.to_dict()
        return data
