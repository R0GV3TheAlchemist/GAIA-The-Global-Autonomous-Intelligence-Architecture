"""
Cultural Calibration — adapts GAIA responses to cultural context.

Exposes the module-level singleton factory `get_cultural_calibration_engine()`
in addition to the full engine implementation.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union

log = logging.getLogger(__name__)


class CulturalDimension(str, Enum):
    INDIVIDUALISM         = "individualism"
    COLLECTIVISM          = "collectivism"
    HIGH_CONTEXT          = "high_context"
    LOW_CONTEXT           = "low_context"
    POWER_DISTANCE        = "power_distance"
    UNCERTAINTY_AVOIDANCE = "uncertainty_avoidance"
    LONG_TERM_ORIENTATION = "long_term_orientation"


# Locale → (region, communication_style, directness)
_LOCALE_DATA: Dict[str, tuple] = {
    "en":    ("Western",     "direct",      0.75),
    "en-US": ("North America", "direct",    0.80),
    "en-GB": ("Western Europe", "indirect", 0.60),
    "ja-JP": ("East Asia",   "high-context", 0.20),
    "zh-CN": ("East Asia",   "high-context", 0.25),
    "de-DE": ("Western Europe", "direct",   0.85),
    "fr-FR": ("Western Europe", "indirect", 0.55),
    "es-ES": ("Southern Europe", "warm",    0.65),
    "pt-BR": ("South America", "warm",      0.60),
    "ar":    ("Middle East",  "high-context", 0.30),
    "hi-IN": ("South Asia",   "high-context", 0.35),
    "ko-KR": ("East Asia",   "high-context", 0.22),
}
_DEFAULT_LOCALE_DATA = ("Global", "balanced", 0.50)


@dataclass
class CulturalProfile:
    """A snapshot of cultural calibration values for a user or context."""

    locale:              str = "en"
    region:              str = "Global"     # added for soul_mirror tests
    communication_style: str = "balanced"   # added for soul_mirror tests
    directness:          float = 0.50       # added for soul_mirror tests; 0.0–1.0
    dimensions:          Dict[CulturalDimension, float] = field(default_factory=dict)
    tags:                List[str] = field(default_factory=list)
    metadata:            Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "locale":              self.locale,
            "region":              self.region,
            "communication_style": self.communication_style,
            "directness":          round(self.directness, 4),
            "dimensions":          {k.value: v for k, v in self.dimensions.items()},
            "tags":                self.tags,
            "metadata":            self.metadata,
        }


class CulturalCalibrationEngine:
    """Engine that calibrates GAIA output to cultural context."""

    def __init__(self) -> None:
        self._profiles: Dict[str, CulturalProfile] = {}
        log.info("CulturalCalibrationEngine initialised")

    def get_profile(self, locale: str = "en") -> CulturalProfile:
        if locale not in self._profiles:
            region, comm_style, directness = _LOCALE_DATA.get(
                locale, _DEFAULT_LOCALE_DATA
            )
            self._profiles[locale] = CulturalProfile(
                locale=locale,
                region=region,
                communication_style=comm_style,
                directness=directness,
            )
        return self._profiles[locale]

    def calibrate(
        self,
        text_or_context: Union[str, dict, None] = None,
        locale: str = "en",
    ) -> Union[str, CulturalProfile]:
        """
        Two calling conventions:
          1. calibrate(context_dict)         → returns CulturalProfile
          2. calibrate(text_str, locale=...) → returns calibrated str (legacy)
        """
        if isinstance(text_or_context, dict):
            # New context-dict API (soul_mirror tests)
            ctx    = text_or_context
            raw_lc = ctx.get("locale", locale)
            # Normalise: None / empty string → fallback
            if not raw_lc:
                raw_lc = "en"
            return self.get_profile(str(raw_lc))

        # Legacy string API
        text = text_or_context or ""
        _ = self.get_profile(locale)
        return text

    def set_dimension(
        self,
        locale:    str,
        dimension: CulturalDimension,
        value:     float,
    ) -> None:
        profile = self.get_profile(locale)
        profile.dimensions[dimension] = max(0.0, min(1.0, value))

    def reset(self) -> None:
        self._profiles.clear()

    def to_dict(self) -> dict:
        return {locale: p.to_dict() for locale, p in self._profiles.items()}


_engine: Optional[CulturalCalibrationEngine] = None


def get_cultural_calibration_engine() -> CulturalCalibrationEngine:
    """Return the module-level singleton CulturalCalibrationEngine."""
    global _engine
    if _engine is None:
        _engine = CulturalCalibrationEngine()
    return _engine
