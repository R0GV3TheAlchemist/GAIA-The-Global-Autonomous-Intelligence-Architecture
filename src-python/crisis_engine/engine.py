"""
crisis_engine.engine
====================
CrisisEngine — system-wide crisis detection and escalation.

Aggregates threshold breaches from AffectEngine, ShadowEngine, and
PersonaStabilityEngine to determine if a system-wide crisis state
should be declared.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.9
GAIAN law              : GAIAN_LAWS.md          Law VI  Crisis Precedes Override
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

logger = logging.getLogger("crisis_engine.engine")


class CrisisLevel(Enum):
    NONE     = auto()   # All systems nominal
    WATCH    = auto()   # One threshold approaching breach
    WARNING  = auto()   # One threshold breached
    CRITICAL = auto()   # Multiple thresholds breached — suspend non-essential ops


@dataclass
class EngineConfig:
    """
    Configuration thresholds for CrisisEngine.

    Fields
    ------
    principal_id            : Identity of the governing principal.
    affect_arousal_threshold: AffectState.arousal above this triggers WATCH.
    shadow_load_threshold   : ShadowState.total_load above this triggers WARNING.
    persona_stability_floor : PersonaProfile.stability_score below this triggers CRITICAL.
    """
    principal_id: str = "local-gaian"
    affect_arousal_threshold: float = 0.85
    shadow_load_threshold: float = 0.80
    persona_stability_floor: float = 0.35


class CrisisEngine:
    """
    GAIA crisis detection engine.

    Aggregates signal states from sister engines and computes a CrisisLevel.
    When CRITICAL is reached, emits escalation events to the governance layer
    and suspends non-essential processes via NexusKernel.

    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.9 | GAIAN_LAWS.md Law VI
    """

    def __init__(self, config: Optional[EngineConfig] = None) -> None:
        self.config = config or EngineConfig()
        self._current_level: CrisisLevel = CrisisLevel.NONE
        logger.info("CrisisEngine initialised with config %s", self.config)

    @property
    def current_level(self) -> CrisisLevel:
        """Return the most recently computed CrisisLevel."""
        return self._current_level

    def evaluate(
        self,
        affect_arousal: float,
        shadow_load: float,
        persona_stability: float,
    ) -> CrisisLevel:
        """
        Evaluate current signal states and return the computed CrisisLevel.

        Args:
            affect_arousal    : Current AffectState.arousal value (0.0 – 1.0).
            shadow_load       : Current ShadowState.total_load.
            persona_stability : Current PersonaProfile.stability_score.

        Raises:
            NotImplementedError: Always — stub.
        """
        raise NotImplementedError(
            "CrisisEngine.evaluate not yet implemented. "
            "Expected: check each signal against config thresholds, "
            "compute CrisisLevel (NONE/WATCH/WARNING/CRITICAL), "
            "store in self._current_level, log if changed, return level."
        )
