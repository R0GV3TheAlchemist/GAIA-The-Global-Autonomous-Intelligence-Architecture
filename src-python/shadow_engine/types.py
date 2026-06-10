"""
shadow_engine/types.py
======================
Data contracts for the Shadow Engine.

All types used across detectors.py, engine.py, integration.py,
and router.py are defined here to prevent circular imports and
F821 undefined-name errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime    import datetime
from enum        import Enum
from typing      import Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ShadowArchetype(str, Enum):
    """The seven shadow archetypes GAIA recognises."""
    NONE            = "none"
    ORPHAN          = "orphan"
    MARTYR          = "martyr"
    WANDERER        = "wanderer"
    DESTROYER       = "destroyer"
    WOUNDED_HEALER  = "wounded_healer"
    SABOTEUR        = "saboteur"       # future archetype slot


# ---------------------------------------------------------------------------
# Observation types
# ---------------------------------------------------------------------------

@dataclass
class ShadowObservation:
    """A single detected shadow pattern observation."""
    id                  : str
    principal_id        : str
    pattern_type        : str           # 'behavioral_loop' | 'contradiction' | 'recurring_theme'
    archetype           : ShadowArchetype
    description_neutral : str           # compassionate, non-blaming language
    supporting_episodes : List[str]     # episode IDs that support this observation
    first_detected_at   : int           # epoch ms
    times_observed      : int
    confidence          : float         # 0.0 – 1.0
    surfaced_at         : Optional[int] = None   # epoch ms when shown to user; None = unsurfaced


@dataclass
class ObservationFeedback:
    """User feedback on a ShadowObservation — used to calibrate future detections."""
    observation_id  : str
    principal_id    : str
    resonates       : bool              # True = user confirmed it felt true
    note            : str = ""          # optional free-text from user
    submitted_at    : Optional[int] = None


# ---------------------------------------------------------------------------
# Values ↔ Behavior gap  (referenced in detectors.py ContradictionDetector)
# ---------------------------------------------------------------------------

@dataclass
class ValuesBehaviorGap:
    """
    Weekly summary of the gap between a principal’s stated values
    and their observed behaviour.

    Produced by ContradictionDetector.detect() and consumed by:
      - ShadowEngine (for intensity calculation)
      - Stage Engine (for narrative framing)
      - Router (for API response)

    gap_score semantics
    -------------------
    0.0  — behaviour fully aligned with all stated values
    0.5  — moderate misalignment in one or more values
    1.0  — consistent behavioural contradiction across most stated values
    """
    principal_id         : str
    week_start_ms        : int           # epoch ms of the Monday that opens this window
    most_aligned_value   : str           # value with lowest gap_score this week
    least_aligned_value  : str           # value with highest gap_score this week
    gap_score            : float         # mean gap across all stated values  (0.0 – 1.0)
    episode_ids          : List[str]     # all episodes that contributed evidence
    computed_at          : int           # epoch ms
    per_value_scores     : Dict[str, float] = field(default_factory=dict)
                                         # {value_label: gap_score}  — detailed breakdown
    note                 : str = ""      # optional human-readable summary


# ---------------------------------------------------------------------------
# Shadow record types  (produced by engine.py)
# ---------------------------------------------------------------------------

@dataclass
class ArchetypeScore:
    name  : str
    score : float   # 0.0 – 1.0


@dataclass
class ShadowRecord:
    """Full shadow profile for one principal at one point in time."""
    principal_id          : str
    active_archetype      : Optional[str]         # None = below activation threshold
    co_active             : List[str]             # archetypes within CO_ACTIVE_DELTA of leader
    archetype_scores      : Dict[str, float]      # all archetype raw scores
    shadow_intensity      : float                 # 0.0 – 1.0
    integration_progress  : float                 # 0.0 – 1.0
    days_active           : int                   # consecutive days this archetype has been active
    last_evaluated        : datetime              # UTC
    evaluation_source     : str                   # 'scheduled' | 'on_demand' | 'post_chat'
    values_behavior_gap   : Optional[ValuesBehaviorGap] = None   # latest gap summary


@dataclass
class ShadowTransition:
    """Records when the active archetype changes or crosses an intensity threshold."""
    principal_id    : str
    timestamp       : datetime
    from_archetype  : Optional[str]
    to_archetype    : Optional[str]
    trigger         : str    # 'archetype_shift' | 'intensity_threshold' | 'integration_milestone'
    intensity_at    : float
    integration_at  : float
    note            : str


# ---------------------------------------------------------------------------
# Thresholds and constants
# ---------------------------------------------------------------------------

# Intensity threshold boundaries that trigger a ShadowTransition
INTENSITY_THRESHOLDS: List[float] = [0.25, 0.50, 0.75]

# Integration milestones that trigger a ShadowTransition
INTEGRATION_MILESTONES: List[float] = [0.50, 0.80]

# Minimum score for an archetype to become active
ACTIVATION_THRESHOLD: float = 0.38

# Two archetypes within this delta → co-active
CO_ACTIVE_DELTA: float = 0.05
