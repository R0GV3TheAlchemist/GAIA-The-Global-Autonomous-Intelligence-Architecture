"""crisisengine.engine

GAIA Crisis Detection and Escalation Engine

Aggregates threshold breach signals from AffectEngine, ShadowEngine,
and PersonaStabilityEngine to compute a system-wide CrisisLevel.
When CRITICAL is reached, escalation events are emitted to the
Governance layer and NexusKernel suspends non-essential processes.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.9
    GAIAN_LAWS.md          Law VI - Crisis Precedes Override
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum, auto

logger = logging.getLogger("crisisengine.engine")


class CrisisLevel(Enum):
    """System-wide crisis severity levels."""
    NONE = auto()      # All systems nominal
    WATCH = auto()     # One threshold approaching breach
    WARNING = auto()   # One threshold breached
    CRITICAL = auto()  # Multiple thresholds breached — suspend non-essential ops


@dataclass
class EngineConfig:
    """Configuration thresholds for CrisisEngine.

    Fields:
        affect_arousal_threshold:   AffectState.arousal above this triggers WATCH.
        shadow_load_threshold:      ShadowState.total_load above this triggers WARNING.
        persona_stability_floor:    PersonaProfile.stability_score below this triggers CRITICAL.
    """
    affect_arousal_threshold: float = 0.85
    shadow_load_threshold: float = 0.80
    persona_stability_floor: float = 0.35


class CrisisEngine:
    """GAIA crisis detection engine.

    Aggregates signal states from AffectEngine, ShadowEngine,
    PersonaStabilityEngine and computes a CrisisLevel.

    When CRITICAL is reached:
        - Emits escalation event to Governance layer.
        - Requests NexusKernel to suspend non-essential processes.

    Reference:
        GAIAN_LAWS.md Law VI - Crisis state must be declared before override.
        NEXUS_UNIVERSAL_OS.md Domain 2.9.
    """

    def __init__(self, config: EngineConfig | None = None) -> None:
        self.config = config or EngineConfig()
        self._current_level: CrisisLevel = CrisisLevel.NONE
        logger.info("CrisisEngine initialised with config: %s.", self.config)

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
        """Evaluate current signal states and return the computed CrisisLevel.

        Args:
            affect_arousal:    Current AffectState.arousal value [0.0, 1.0].
            shadow_load:       Current ShadowState.total_load.
            persona_stability: Current PersonaProfile.stability_score.

        Returns:
            The computed CrisisLevel.

        Raises:
            NotImplementedError: Aggregation logic not yet implemented.
                Expected: check each signal against config thresholds,
                compute CrisisLevel NONE/WATCH/WARNING/CRITICAL,
                store in self._current_level, log if changed, return level.
        """
        raise NotImplementedError(
            "CrisisEngine.evaluate() not yet implemented. "
            "Expected: threshold evaluation across affect_arousal, shadow_load, "
            "persona_stability -> CrisisLevel.NONE/WATCH/WARNING/CRITICAL."
        )
