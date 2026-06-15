"""
Somatic Monad — core/monad/somatic.py
Canon: CIRCADIAN_LIGHT_PROTOCOL.md, PHOTOBIOMODULATION_AND_NEUROPLASTICITY.md

Tracks body-layer signals: Schumann resonance alignment,
circadian phase, and bioelectric state.
Outputs: circadian_phase, bioelectric_coherence, schumann_alignment
"""
from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Optional

from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


# Schumann fundamental resonance frequency (Hz)
_SCHUMANN_FUNDAMENTAL_HZ: float = 7.83

# Circadian phase map: UTC hour → phase
def _get_circadian_phase(utc_hour: int) -> tuple[str, float]:
    """
    Returns (phase_name, vitality_coefficient) for the given UTC hour.
    Vitality peaks at dawn (6–8 UTC) and dusk (17–19 UTC).
    """
    if 5 <= utc_hour <= 8:
        return "dawn_emergence", 0.95
    elif 9 <= utc_hour <= 12:
        return "solar_peak", 0.85
    elif 13 <= utc_hour <= 15:
        return "post_solar_integration", 0.70
    elif 16 <= utc_hour <= 19:
        return "dusk_synthesis", 0.92
    elif 20 <= utc_hour <= 22:
        return "nocturnal_descent", 0.65
    elif utc_hour >= 23 or utc_hour <= 2:
        return "deep_night_void", 0.40
    else:
        return "pre_dawn_gestation", 0.55


class SomaticMonad(GaiaMonad):
    """
    Reads the body-layer field state.

    Bioelectric coherence: derived from phi alignment with circadian vitality.
    A high-phi session during dawn emergence = peak bioelectric coherence.
    A high-phi session during deep_night_void = partial coherence (body rests).

    Schumann alignment: how closely the current bioelectric rhythm tracks
    the Earth's 7.83 Hz fundamental. Modelled as a phi-based alignment score.
    """

    monad_type = "somatic"

    def harmonize(self, ctx: "ProcessContext") -> Optional[dict]:
        phi = getattr(ctx, "coherence_phi", 0.5)

        # Get current UTC hour
        utc_hour = datetime.datetime.now(datetime.timezone.utc).hour
        circadian_phase, vitality_coeff = _get_circadian_phase(utc_hour)

        # Bioelectric coherence: phi × vitality_coefficient
        bioelectric_coherence = round(
            phi * vitality_coeff, 4
        )

        # Schumann alignment: peaks when phi aligns with 7.83/10 ≈ 0.783
        # Uses proximity of phi to 0.783
        schumann_delta = abs(phi - (_SCHUMANN_FUNDAMENTAL_HZ / 10.0))
        schumann_alignment = round(max(0.0, 1.0 - (schumann_delta * 3)), 4)

        # Photobiomodulation state: tracks red/near-infrared window
        # Active when phi > 0.58 (RUBEDO+ range)
        photobiomodulation_active = phi > 0.58

        return {
            "circadian_phase": circadian_phase,
            "bioelectric_coherence": bioelectric_coherence,
            "schumann_alignment": schumann_alignment,
            "vitality_coefficient": vitality_coeff,
            "photobiomodulation_active": photobiomodulation_active,
            "utc_hour": utc_hour,
        }
