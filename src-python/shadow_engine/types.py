"""
Shadow Engine — Core Types  (Issue #67)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


# ─────────────────────────────────────────────
# Enumerations
# ─────────────────────────────────────────────

class ShadowMode(str, Enum):
    OFF          = "off"          # Stage 1 — not ready
    OBSERVATION  = "observation"  # Stage 2 — detect but do not surface
    FULL         = "full"         # Stage 3 — detect and surface
    SYNTHESIS    = "synthesis"    # Stage 4 — multi-year arc analysis
    COLLECTIVE   = "collective"   # Stage 5 — extends to Trusted Circle


# Stage → mode mapping (authoritative)
STAGE_TO_MODE: dict[int, ShadowMode] = {
    1: ShadowMode.OFF,
    2: ShadowMode.OBSERVATION,
    3: ShadowMode.FULL,
    4: ShadowMode.SYNTHESIS,
    5: ShadowMode.COLLECTIVE,
}


class ShadowArchetype(str, Enum):
    """
    Jungian shadow archetypes detected by the engine.
    Mapped from ArcTrend fields.
    """
    NONE            = "none"
    ORPHAN          = "orphan"           # chronic sadness / grief, low energy
    MARTYR          = "martyr"           # low energy + recurring self-sacrifice patterns
    WANDERER        = "wanderer"         # volatile, high mood variance, directionless
    DESTROYER       = "destroyer"        # recurring anger, high arousal + negative valence
    WOUNDED_HEALER  = "wounded_healer"   # high empathy themes + chronic sadness


class ObservationFeedback(str, Enum):
    SEEN_IT        = "seen_it"         # user acknowledges
    NOT_ACCURATE   = "not_accurate"    # user disputes — decreases confidence
    THIS_IS_KEY    = "this_is_key"     # user flags as important — increases confidence


# ─────────────────────────────────────────────
# Core structs
# ─────────────────────────────────────────────

@dataclass
class ShadowObservation:
    """
    A single surfaced shadow pattern observation.
    Phrased in second person, present tense, non-judgmentally.

    Example description:
        "It looks like when you feel overlooked, you tend to withdraw
         rather than express what you need."
    """
    id                 : str
    principal_id       : str
    pattern_type       : str              # e.g. 'behavioral_loop', 'contradiction', 'theme'
    archetype          : ShadowArchetype
    description_neutral: str              # user-facing phrasing
    supporting_episodes: List[str]        # episode IDs
    first_detected_at  : int              # unix ms
    times_observed     : int
    surfaced_at        : Optional[int]    # unix ms; None if in OBSERVATION mode
    confidence         : float            # 0.0 – 1.0
    user_feedback      : Optional[ObservationFeedback] = None

    def to_dict(self) -> dict:
        return {
            "id"                  : self.id,
            "principal_id"        : self.principal_id,
            "pattern_type"        : self.pattern_type,
            "archetype"           : self.archetype.value,
            "description_neutral" : self.description_neutral,
            "supporting_episodes" : self.supporting_episodes,
            "first_detected_at"   : self.first_detected_at,
            "times_observed"      : self.times_observed,
            "surfaced_at"         : self.surfaced_at,
            "confidence"          : self.confidence,
            "user_feedback"       : self.user_feedback.value if self.user_feedback else None,
        }


@dataclass
class ShadowRecord:
    """
    Persisted state row for a principal (maps to shadow_records DB table).
    """
    principal_id         : str
    active_archetype     : ShadowArchetype  = ShadowArchetype.NONE
    shadow_intensity     : float            = 0.0   # 0.0 – 1.0
    dominant_emotion     : str              = "neutral"
    is_volatile          : bool             = False
    low_energy_flag      : bool             = False
    mood_momentum        : float            = 0.0
    valence_trend        : float            = 0.0
    arc_stability        : float            = 0.5
    recommended_practice : Optional[str]   = None
    updated_at           : int              = 0


@dataclass
class ValuesVector:
    """
    Up to 10 user-articulated core values, distilled into a structured form.
    """
    principal_id  : str
    raw_values    : List[str]         # free-text input, up to 10
    distilled     : List[str]         # GAIA-distilled canonical labels
    created_at    : int
    updated_at    : int


@dataclass
class ValuesBehaviorGap:
    """
    Weekly values-behavior alignment gap score.
    """
    principal_id       : str
    week_start_ms      : int
    most_aligned_value : str        # value most reflected in behaviour this week
    least_aligned_value: str        # value least reflected in behaviour this week
    gap_score          : float      # 0.0 (full alignment) – 1.0 (total contradiction)
    episode_ids        : List[str]  # episodes used to compute gap
    computed_at        : int
