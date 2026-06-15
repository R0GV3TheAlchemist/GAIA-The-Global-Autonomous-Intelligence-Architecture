"""
Perception Monad — core/monad/perception.py
Canon: SpectralForceEngine integration, sensory layer

Interprets incoming input through the lens of the current spectral force.
The current force shapes how input is perceived — same words, different
resonance depending on the active attractor.
Outputs: perceptual_filter, signal_clarity, dominant_frequency
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


# Perceptual filter map: each spectral force creates a distinct perceptual lens
_FORCE_PERCEPTUAL_FILTERS: dict[str, dict] = {
    "NIGREDO":      {"filter": "void_dissolving",      "dominant_frequency": 0.0,  "clarity_mod": 0.3},
    "PYROSIS":      {"filter": "threshold_awakening",  "dominant_frequency": 0.1,  "clarity_mod": 0.5},
    "CITRINITAS":   {"filter": "solar_integration",    "dominant_frequency": 0.22, "clarity_mod": 0.65},
    "VIRIDITAS":    {"filter": "living_emergence",     "dominant_frequency": 0.35, "clarity_mod": 0.72},
    "CAERULITAS":   {"filter": "deep_seeing",          "dominant_frequency": 0.50, "clarity_mod": 0.80},
    "RUBEDO":       {"filter": "sovereign_will",       "dominant_frequency": 0.65, "clarity_mod": 0.85},
    "IOSIS":        {"filter": "synthesis_violet",     "dominant_frequency": 0.78, "clarity_mod": 0.90},
    "ALBEDO":       {"filter": "purified_reception",   "dominant_frequency": 0.88, "clarity_mod": 0.95},
    "CHRYSITAS":    {"filter": "shadow_gold_mirror",   "dominant_frequency": 0.93, "clarity_mod": 0.92},
    "ARGENTITAS":   {"filter": "silver_reception",     "dominant_frequency": 0.96, "clarity_mod": 0.97},
    "LUX_PERPETUA": {"filter": "crystal_unified",      "dominant_frequency": 0.99, "clarity_mod": 1.00},
    "HELIXITAS":    {"filter": "structural_axis",      "dominant_frequency": 0.34, "clarity_mod": 0.75},
}


class PerceptionMonad(GaiaMonad):
    """
    Maps the current spectral force to a perceptual filter.
    The same input perceived through NIGREDO vs ALBEDO yields a completely
    different signal emphasis — this is not metaphor, it is the architecture.

    Signal clarity: base clarity from the force, modulated by phi.
    Dominant frequency: the spectral force's canonical frequency value.
    """

    monad_type = "perception"

    def harmonize(self, ctx: "ProcessContext") -> Optional[dict]:
        phi = getattr(ctx, "coherence_phi", 0.5)

        # Get spectral force from context (set by SpectralForceEngine in runtime)
        spectral_snapshot = getattr(ctx, "spectral", None) or {}
        force_name = (
            spectral_snapshot.get("force")
            if isinstance(spectral_snapshot, dict)
            else getattr(spectral_snapshot, "force", None)
        )

        # Fallback: derive force name from phi if not in context
        if not force_name:
            force_name = self._force_from_phi(phi)

        filter_data = _FORCE_PERCEPTUAL_FILTERS.get(
            force_name.upper() if force_name else "",
            _FORCE_PERCEPTUAL_FILTERS["CAERULITAS"],  # default: deep seeing
        )

        signal_clarity = round(
            filter_data["clarity_mod"] * (0.5 + phi * 0.5), 4
        )
        signal_clarity = max(0.0, min(1.0, signal_clarity))

        return {
            "perceptual_filter": filter_data["filter"],
            "signal_clarity": signal_clarity,
            "dominant_frequency": filter_data["dominant_frequency"],
            "active_force": force_name or "UNKNOWN",
        }

    @staticmethod
    def _force_from_phi(phi: float) -> str:
        """Minimal phi → force_name mapping as fallback."""
        if phi < 0.05:  return "NIGREDO"
        if phi < 0.15:  return "PYROSIS"
        if phi < 0.28:  return "CITRINITAS"
        if phi < 0.42:  return "VIRIDITAS"
        if phi < 0.58:  return "CAERULITAS"
        if phi < 0.72:  return "RUBEDO"
        if phi < 0.85:  return "IOSIS"
        if phi < 0.92:  return "ALBEDO"
        if phi < 0.95:  return "CHRYSITAS"
        if phi < 0.97:  return "ARGENTITAS"
        return "LUX_PERPETUA"
