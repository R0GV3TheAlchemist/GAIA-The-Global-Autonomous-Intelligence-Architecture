"""
Shadow Engine — Orchestrator  (Issue #67)

ShadowEngine ties together:
  - RecurringThemeDetector
  - BehavioralLoopDetector
  - ContradictionDetector
  - ArchetypeClassifier
  - ShadowTimingGate
  - SovereignMemory (read episodes, store observations and shadow_records)

The evaluate() method is the single entry point.  It returns a list of
ShadowObservations that are ALLOWED to be surfaced (gate passed).  The
caller (GAIA conversation layer) decides HOW to present them — never
unsolicited push notifications.
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from typing import List, Optional

from .detectors import (
    RecurringThemeDetector,
    BehavioralLoopDetector,
    ContradictionDetector,
    ArchetypeClassifier,
)
from .timing_gate import ShadowTimingGate
from .types import (
    ShadowObservation,
    ShadowRecord,
    ShadowArchetype,
    ShadowMode,
    STAGE_TO_MODE,
    ValuesVector,
    ValuesBehaviorGap,
    ObservationFeedback,
)

logger = logging.getLogger(__name__)


def _now_ms() -> int:
    return int(time.time() * 1000)


class ShadowEngine:
    """
    Main Shadow Engine orchestrator.

    Args:
        memory           — open SovereignMemory instance (required for production)
        theme_detector   — override RecurringThemeDetector (for testing)
        loop_detector    — override BehavioralLoopDetector (for testing)
        contradiction    — override ContradictionDetector (for testing)
        archetype        — override ArchetypeClassifier (for testing)
        gate             — override ShadowTimingGate (for testing)
        episode_days     — lookback window in days for episode retrieval (default 90)
        alignment_score  — current Schumann alignment score (default 50 if not provided)
    """

    def __init__(
        self,
        memory=None,
        theme_detector   : Optional[RecurringThemeDetector] = None,
        loop_detector    : Optional[BehavioralLoopDetector]  = None,
        contradiction    : Optional[ContradictionDetector]   = None,
        archetype        : Optional[ArchetypeClassifier]     = None,
        gate             : Optional[ShadowTimingGate]        = None,
        episode_days     : int   = 90,
        alignment_score  : float 