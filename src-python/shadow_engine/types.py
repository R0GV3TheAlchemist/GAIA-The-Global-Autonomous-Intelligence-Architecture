"""
shadow_engine/types.py
Data contracts for the Shadow Engine.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime    import datetime
from typing      import Optional


@dataclass
class ArchetypeScore:
    name:  str
    score: float   # 0.0 – 1.0


@dataclass
class ShadowRecord:
    principal_id:         str
    active_archetype:     Optional[str]        # None = below activation threshold
    co_active:            list[str]            # archetypes within 0.05 of active score
    archetype_scores:     dict[str, float]     # all seven raw scores
    shadow_intensity:     float                # 0.0 – 1.0
    integration_progress: float               # 0.0 – 1.0
    days_active:          int                 # consecutive days this archetype has been active
    last_evaluated:       datetime            # UTC
    evaluation_source:    str                 # 'scheduled' | 'on_demand' | 'post_chat'


@dataclass
class ShadowTransition:
    principal_id:   str
    timestamp:      datetime
    from_archetype: Optional[str]
    to_archetype:   Optional[str]
    trigger:        str          # 'archetype_shift' | 'intensity_threshold' | 'integration_milestone'
    intensity_at:   float
    integration_at: float
    note:           str


# Intensity threshold boundaries that trigger a ShadowTransition
INTENSITY_THRESHOLDS: list[float] = [0.25, 0.50, 0.75]

# Integration milestones that trigger a ShadowTransition
INTEGRATION_MILESTONES: list[float] = [0.50, 0.80]

# Minimum score for an archetype to become active
ACTIVATION_THRESHOLD: float = 0.38

# Two archetypes within this delta → co-active
CO_ACTIVE_DELTA: float = 0.05
