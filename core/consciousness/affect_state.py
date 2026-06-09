"""AffectState — continuous valence × arousal affective model for GAIA-OS.

Extends VitalityState with a full 2D Russell circumplex model:
  arousal  axis: low (restful) → high (activated)
  valence  axis: negative (distress) → positive (flourishing)

The quadrant labels map to GAIA’s apothecary register system:
  High arousal + positive valence  → ‘flow’
  High arousal + negative valence  → ‘stress’
  Low arousal  + positive valence  → ‘rest’
  Low arousal  + negative valence  → ‘somnus’ (integration mode)

Canon refs: C05 (Lapis Lazuli / Cognition), C81 (Twelve Intelligences)
Issue: #262
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Quadrant = Literal['flow', 'stress', 'rest', 'somnus']


@dataclass
class AffectState:
    """Instantaneous affective state snapshot.

    Both axes are floats in [-1.0, 1.0].
    Negative valence = distress; positive = flourishing.
    Low arousal = calm/passive; high = activated/energised.
    """
    valence: float = 0.0        # [-1.0, 1.0]
    arousal: float = 0.0        # [-1.0, 1.0]
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    source: str = 'inferred'    # 'inferred' | 'self_reported' | 'biometric'
    confidence: float = 0.5     # [0.0, 1.0]

    # ------------------------------------------------------------------
    # Derived
    # ------------------------------------------------------------------

    @property
    def quadrant(self) -> Quadrant:
        """Map (valence, arousal) to one of GAIA’s four affective quadrants."""
        if self.valence >= 0 and self.arousal >= 0:
            return 'flow'
        if self.valence < 0 and self.arousal >= 0:
            return 'stress'
        if self.valence >= 0 and self.arousal < 0:
            return 'rest'
        return 'somnus'

    @property
    def intensity(self) -> float:
        """Euclidean distance from neutral origin (0, 0). Range [0.0, ~1.41]."""
        return (self.valence ** 2 + self.arousal ** 2) ** 0.5

    @property
    def is_regulation_needed(self) -> bool:
        """True when intensity is high AND valence is negative (stress / trauma)."""
        return self.valence < -0.3 and self.intensity > 0.5

    def to_register(self) -> str:
        """Map quadrant to GAIA response register."""
        mapping: dict[Quadrant, str] = {
            'flow':    'executive',
            'stress':  'minimal',
            'rest':    'reflective',
            'somnus':  'minimal',
        }
        return mapping[self.quadrant]

    def blend(self, other: 'AffectState', weight: float = 0.5) -> 'AffectState':
        """Weighted blend of two AffectState snapshots (temporal smoothing)."""
        w = max(0.0, min(1.0, weight))
        return AffectState(
            valence=self.valence * (1 - w) + other.valence * w,
            arousal=self.arousal * (1 - w) + other.arousal * w,
            source='inferred',
            confidence=min(self.confidence, other.confidence),
        )

    def __repr__(self) -> str:
        return (
            f"AffectState(quadrant={self.quadrant!r}, "
            f"valence={self.valence:.2f}, arousal={self.arousal:.2f}, "
            f"intensity={self.intensity:.2f})"
        )
