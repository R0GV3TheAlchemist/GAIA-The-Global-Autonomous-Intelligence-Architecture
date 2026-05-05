"""GAIA-OS Sovereign Memory — Core Data Types

Issue #66 | Pillar III: Societas
All types that cross the sidecar boundary (Python ↔ Tauri IPC) are JSON-serialisable.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal, Sequence
import json

# ─────────────────────────────────────────────
# EMOTION / AFFECT
# ─────────────────────────────────────────────

EmotionLabel = Literal[
    "joy", "sadness", "anger", "fear", "disgust", "surprise", "neutral"
]

SignalType = Literal[
    "hrv_rmssd",
    "alignment_score",
    "affect_valence",
    "affect_arousal",
    "affect_dominance",
    "affect_entropy",
    "arc_stability",
    "kp_index",
    "schumann_amplitude",
]


@dataclass
class AffectSnapshot:
    """Point-in-time emotional + physiological state. Emitted by AffectEngine."""

    id: str                     # UUIDv7
    principal_id: str
    timestamp: int              # unix ms
    source: Literal["journal", "gaia_chat", "system"]
    emotion: EmotionLabel
    confidence: float           # 0.0–1.0
    valence: float              # -1.0–1.0  (Pleasure)
    arousal: float              # 0.0–1.0
    dominance: float            # 0.0–1.0
    entropy: float              # 0.0–1.0  (linguistic complexity)
    arc_stability: float        # 0.0–1.0  (rolling window stability)
    is_neutral_primary: bool    # True = primarily factual, skip heavy classification

    def to_biometric_rows(self) -> list[dict]:
        """Expand snapshot into individual biometric_history rows."""
        ts = self.timestamp
        pid = self.principal_id
        return [
            {"principal_id": pid, "timestamp": ts, "signal_type": "affect_valence",   "value": self.valence,       "source": self.source},
            {"principal_id": pid, "timestamp": ts, "signal_type": "affect_arousal",   "value": self.arousal,       "source": self.source},
            {"principal_id": pid, "timestamp": ts, "signal_type": "affect_dominance",  "value": self.dominance,     "source": self.source},
            {"principal_id": pid, "timestamp": ts, "signal_type": "affect_entropy",    "value": self.entropy,       "source": self.source},
            {"principal_id": pid, "timestamp": ts, "signal_type": "arc_stability",     "value": self.arc_stability, "source": self.source},
        ]

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────
# MEMORY RECORDS
# ─────────────────────────────────────────────

@dataclass
class MemoryRecord:
    """Decrypted episodic or semantic memory record returned from searches."""

    id: str
    principal_id: str
    type: str                   # 'journal' | 'event' | 'decision' | ...
    created_at: int             # unix ms
    tags: list[str]
    preview: str                # decrypted plaintext snippet (first 280 chars)
    score: float | None = None  # cosine similarity score for vector searches

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class BiometricSample:
    """Single time-series data point from biometric_history."""

    timestamp: int
    signal_type: str
    value: float
    source: str

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────
# STAGE ENGINE TYPES
# ─────────────────────────────────────────────

@dataclass
class MarkerScores:
    """Current marker scores used by the Stage Engine. All values 0–100."""

    decision_entropy: float          # 0–100 (100 = decisive)
    hrv_coherence: float             # 0–100
    journaling_depth: float          # 0–100
    focus_session_length_min: float  # raw minutes (scorer maps to 0–100)
    goal_completion_rate: float      # 0–100
    emotional_arc_stability: float   # 0–100

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StageRecord:
    """Current developmental stage state for a principal."""

    principal_id: str
    current_stage: int              # 1–5
    stage_entered_at: int           # unix ms
    days_in_stage: int
    marker_scores: MarkerScores
    transition_candidate: bool
    regression_risk: bool
    updated_at: int                 # unix ms

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


@dataclass
class StageTransitionRecord:
    """An immutable log entry for a stage change (forward or regression)."""

    id: int
    principal_id: str
    from_stage: int
    to_stage: int
    transitioned_at: int            # unix ms
    is_regression: bool
    markers_met: list[str]
    ceremony_shown: bool

    @property
    def stage_label(self) -> str:
        """Human-readable label, e.g. '3R' for a Crucible regression."""
        names = {
            1: "Divergence",
            2: "Awakening",
            3: "Crucible",
            4: "Convergence",
            5: "Ascendence",
        }
        label = names.get(self.to_stage, str(self.to_stage))
        return f"{self.to_stage}R — {label}" if self.is_regression else f"{self.to_stage} — {label}"

    def to_dict(self) -> dict:
        return asdict(self)


# ─────────────────────────────────────────────
# LEGACY ARTIFACTS
# ─────────────────────────────────────────────

@dataclass
class LegacyArtifact:
    """A Stage-4/5 legacy output (letter, wisdom distillation, etc.)."""

    id: str
    principal_id: str
    created_at: int
    stage_at_creation: int          # 4 or 5
    title: str                      # decrypted
    content: str                    # decrypted
    source_episode_id: str | None
    export_formats: list[str]
    tags: list[str]

    def to_dict(self) -> dict:
        return asdict(self)
