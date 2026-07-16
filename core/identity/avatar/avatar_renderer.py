"""
core/identity/avatar/avatar_renderer.py

AvatarRenderer — projects an AvatarProfile into a rendered expression state.

Design:
- Reads the profile’s mode and traits to produce a RenderedState.
- RenderedState is a snapshot used by the response pipeline to modulate
  tone, verbosity, citation depth, and boundary assertion.
- Stateless: the renderer holds no mutable state; call render() freely.
- Extensible via trait_modifiers: register callables that mutate the
  base state dict before it is frozen into a RenderedState.

Canon Refs: C04 (Expression), C07 (Modulation)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from .avatar_profile import AvatarProfile, ExpressionMode


# ---------------------------------------------------------------------------
# RenderedState
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RenderedState:
    """
    Immutable snapshot of how an avatar should express itself right now.

    Fields
    ------
    avatar_id       Source profile id.
    mode            Active ExpressionMode at render time.
    voice           Voice descriptor string.
    verbosity       Float [0, 1] — 0 = minimal, 1 = expansive.
    citation_depth  Float [0, 1] — 0 = none, 1 = deep sourcing.
    boundary_level  Float [0, 1] — 0 = open, 1 = maximum assertion.
    affect          String label for the dominant emotional tone.
    active_traits   Dict of trait_name → intensity for traits above threshold.
    rendered_at     Unix timestamp.
    """
    avatar_id: str
    mode: ExpressionMode
    voice: str
    verbosity: float
    citation_depth: float
    boundary_level: float
    affect: str
    active_traits: Dict[str, float]
    rendered_at: float = field(default_factory=time.time)
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "avatar_id": self.avatar_id,
            "mode": self.mode.value,
            "voice": self.voice,
            "verbosity": self.verbosity,
            "citation_depth": self.citation_depth,
            "boundary_level": self.boundary_level,
            "affect": self.affect,
            "active_traits": dict(self.active_traits),
            "rendered_at": self.rendered_at,
            "extra": dict(self.extra),
        }


# ---------------------------------------------------------------------------
# Mode-default parameter tables
# ---------------------------------------------------------------------------

_MODE_DEFAULTS: Dict[ExpressionMode, Dict[str, Any]] = {
    ExpressionMode.NEUTRAL: {
        "verbosity": 0.5,
        "citation_depth": 0.5,
        "boundary_level": 0.3,
        "affect": "balanced",
    },
    ExpressionMode.GUARDIAN: {
        "verbosity": 0.4,
        "citation_depth": 0.6,
        "boundary_level": 0.85,
        "affect": "protective",
    },
    ExpressionMode.SCHOLAR: {
        "verbosity": 0.75,
        "citation_depth": 0.95,
        "boundary_level": 0.2,
        "affect": "analytic",
    },
    ExpressionMode.HERALD: {
        "verbosity": 0.85,
        "citation_depth": 0.4,
        "boundary_level": 0.2,
        "affect": "expressive",
    },
    ExpressionMode.WITNESS: {
        "verbosity": 0.2,
        "citation_depth": 0.3,
        "boundary_level": 0.1,
        "affect": "receptive",
    },
    ExpressionMode.SOVEREIGN: {
        "verbosity": 0.6,
        "citation_depth": 0.7,
        "boundary_level": 1.0,
        "affect": "authoritative",
    },
}

# Trait names that directly modulate render parameters
_TRAIT_MODULATIONS: Dict[str, Dict[str, float]] = {
    "curiosity":    {"verbosity": +0.15, "citation_depth": +0.10},
    "directness":   {"verbosity": -0.10, "boundary_level": +0.10},
    "warmth":       {"boundary_level": -0.10},
    "precision":    {"citation_depth": +0.15},
    "caution":      {"boundary_level": +0.15, "verbosity": -0.05},
    "openness":     {"boundary_level": -0.15},
    "authority":    {"boundary_level": +0.20},
    "creativity":   {"verbosity": +0.10},
}


# ---------------------------------------------------------------------------
# AvatarRenderer
# ---------------------------------------------------------------------------

class AvatarRenderer:
    """
    Projects an AvatarProfile into a RenderedState.

    Parameters
    ----------
    trait_threshold : float
        Traits with intensity below this value are excluded from
        active_traits and ignored for modulation.
    extra_modifiers : list of callables
        Each callable receives the mutable params dict and the profile,
        and may mutate params in-place before the state is frozen.
    """

    def __init__(
        self,
        trait_threshold: float = 0.2,
        extra_modifiers: Optional[List[Callable[[Dict[str, Any], AvatarProfile], None]]] = None,
    ) -> None:
        self.trait_threshold = trait_threshold
        self.extra_modifiers: List[Callable[[Dict[str, Any], AvatarProfile], None]] = (
            extra_modifiers or []
        )

    def render(self, profile: AvatarProfile) -> RenderedState:
        """Produce a RenderedState from *profile*."""
        # Start from mode defaults
        defaults = _MODE_DEFAULTS.get(profile.mode, _MODE_DEFAULTS[ExpressionMode.NEUTRAL])
        params: Dict[str, Any] = {
            "verbosity":      defaults["verbosity"],
            "citation_depth": defaults["citation_depth"],
            "boundary_level": defaults["boundary_level"],
            "affect":         defaults["affect"],
            "extra":          {},
        }

        # Apply trait modulations
        active_traits: Dict[str, float] = {}
        for trait in profile.traits:
            if trait.intensity < self.trait_threshold:
                continue
            active_traits[trait.name] = trait.intensity
            modulations = _TRAIT_MODULATIONS.get(trait.name, {})
            for param, delta in modulations.items():
                if param in params and isinstance(params[param], float):
                    params[param] = max(0.0, min(1.0, params[param] + delta * trait.intensity))

        # Run any registered extra modifiers
        for modifier in self.extra_modifiers:
            modifier(params, profile)

        return RenderedState(
            avatar_id=profile.id,
            mode=profile.mode,
            voice=profile.voice,
            verbosity=round(params["verbosity"], 4),
            citation_depth=round(params["citation_depth"], 4),
            boundary_level=round(params["boundary_level"], 4),
            affect=params["affect"],
            active_traits=active_traits,
            extra=params["extra"],
        )

    def register_modifier(
        self,
        fn: Callable[[Dict[str, Any], AvatarProfile], None],
    ) -> None:
        """Register an additional modifier function."""
        self.extra_modifiers.append(fn)
