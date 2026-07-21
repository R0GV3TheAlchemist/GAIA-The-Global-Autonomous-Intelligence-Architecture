"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEXUS — The Universal Autonomous Intelligence Architecture
  GAIA  — The Global Autonomous Intelligence Architecture

  Author   : Kyle Steen
  GitHub   : R0GV3TheAlchemist (https://github.com/R0GV3TheAlchemist)
  Email    : xxkylesteenxx@outlook.com
  Project  : NEXUS / GAIA
  License  : All Rights Reserved © 2026 Kyle Steen
             Unauthorized use, reproduction, or distribution
             of this file or its contents is strictly prohibited.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

perception.py — NEXUS Perception System.

SensorFusion combines heterogeneous sensor streams into a unified WorldModel.
UncertaintyQuantifier attaches Bayesian confidence intervals to all percepts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID, uuid4
import time


class SensorClass(Enum):
    VISUAL = auto()
    AUDITORY = auto()
    ENVIRONMENTAL = auto()
    DIGITAL = auto()
    BCI = auto()
    PROPRIOCEPTIVE = auto()


@dataclass
class Percept:
    """A single observation from one sensor at one point in time."""
    percept_id: UUID = field(default_factory=uuid4)
    sensor_class: SensorClass = SensorClass.DIGITAL
    sensor_id: str = ""
    value: Any = None
    timestamp: float = field(default_factory=time.time)
    confidence: float = 1.0  # 0.0–1.0
    uncertainty_lower: float = 0.0
    uncertainty_upper: float = 0.0


@dataclass
class WorldModel:
    """
    A unified snapshot of the agent's current environmental understanding.

    Built by SensorFusion from multiple Percept streams. Each slot
    holds the most recent fused percept and its uncertainty envelope.
    """
    model_id: UUID = field(default_factory=uuid4)
    timestamp: float = field(default_factory=time.time)
    slots: Dict[str, Percept] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def update_slot(self, key: str, percept: Percept) -> None:
        self.slots[key] = percept
        self.timestamp = time.time()

    def get_slot(self, key: str) -> Optional[Percept]:
        return self.slots.get(key)

    def confidence_summary(self) -> Dict[str, float]:
        return {k: v.confidence for k, v in self.slots.items()}


class UncertaintyQuantifier:
    """
    Attaches Bayesian confidence intervals to percepts.

    In production, this integrates a Bayesian filter (Kalman, particle, etc.).
    Stub implementation uses a simple Gaussian approximation.
    """

    def quantify(self, percept: Percept,
                 prior_confidence: float = 1.0,
                 noise_sigma: float = 0.05) -> Percept:
        """
        Compute uncertainty bounds for a percept and return updated percept.
        """
        adjusted = prior_confidence * percept.confidence
        percept.confidence = max(0.0, min(1.0, adjusted))
        percept.uncertainty_lower = max(0.0, percept.confidence - noise_sigma)
        percept.uncertainty_upper = min(1.0, percept.confidence + noise_sigma)
        return percept


class SensorFusion:
    """
    Fuses heterogeneous sensor streams into a unified WorldModel.

    Each sensor stream is registered with a key and a SensorClass.
    On each fusion tick, all registered streams are polled, quantified,
    and merged into the active WorldModel.
    """

    def __init__(self) -> None:
        self._streams: Dict[str, Tuple[SensorClass, Any]] = {}
        self._quantifier = UncertaintyQuantifier()
        self.world_model = WorldModel()

    def register_stream(self, key: str, sensor_class: SensorClass,
                        source: Any = None) -> None:
        """Register a named sensor stream."""
        self._streams[key] = (sensor_class, source)

    def ingest(self, key: str, value: Any,
               sensor_id: str = "",
               raw_confidence: float = 1.0) -> Percept:
        """
        Ingest a raw sensor reading, quantify uncertainty, and
        update the WorldModel slot.
        """
        sensor_class = self._streams.get(key, (SensorClass.DIGITAL, None))[0]
        percept = Percept(
            sensor_class=sensor_class,
            sensor_id=sensor_id,
            value=value,
            confidence=raw_confidence,
        )
        percept = self._quantifier.quantify(percept)
        self.world_model.update_slot(key, percept)
        return percept

    def fuse(self) -> WorldModel:
        """Return the current fused WorldModel snapshot."""
        return self.world_model

    def registered_streams(self) -> List[str]:
        return list(self._streams.keys())
