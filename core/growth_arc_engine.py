"""
core/growth_arc_engine.py

Formerly: viriditas_magnum_opus.py

Tracks the long-arc developmental trajectory of both the human and the
GAIAN across the full relationship lifespan. Models growth as a
non-linear process with plateaus, regressions, and phase transitions.

Grounded in developmental psychology (Kegan, 1982; Loevinger, 1976)
and the GAIA Canon individuation framework.

Canon refs : C30 (no silent failures), C45 (Viriditas & Alchemical Co-Evolution),
             C47 (Viriditas Threshold), C48 (Warlock Resonance Covenant)
See also   : C00 Foundational Cosmology — growth_arc_engine naming.
"""
from __future__ import annotations

from core.viriditas_magnum_opus import (
    ViriditasMagnumOpus,
    ViriditasState,
    ViriditasStateEnum,
    StageResult,
    MagnumOpusReport,
    SCHUMANN_HARMONICS,
    SCHUMANN_BASE_HZ,
    VIRIDITAS_THRESHOLD,
    viriditas_magnum_opus,
    get_viriditas_engine,
)

# Canonical rename — preferred public name going forward
GrowthArcEngine = ViriditasMagnumOpus


def get_growth_arc_engine() -> ViriditasMagnumOpus:
    """Return the module-level GrowthArcEngine singleton.

    Delegates to get_viriditas_engine() so both accessors share one instance.
    """
    return get_viriditas_engine()


def run_growth_arc(
    gaian_id:         str   = "gaia",
    warlock_id:       str   = "anonymous",
    warlock_vitality: float = 8.0,
    initial_phi:      float = 0.382,
) -> MagnumOpusReport:
    """Run the five-stage Viriditas Magnum Opus boot sequence.

    Thin wrapper around viriditas_magnum_opus() using the canonical
    growth_arc_engine naming convention.
    """
    return viriditas_magnum_opus(
        gaian_id=gaian_id,
        warlock_id=warlock_id,
        warlock_vitality=warlock_vitality,
        initial_phi=initial_phi,
    )


__all__ = [
    # Primary rename
    "GrowthArcEngine",
    "get_growth_arc_engine",
    "run_growth_arc",
    # Re-exported public API from viriditas_magnum_opus
    "ViriditasMagnumOpus",
    "ViriditasState",
    "ViriditasStateEnum",
    "StageResult",
    "MagnumOpusReport",
    "SCHUMANN_HARMONICS",
    "SCHUMANN_BASE_HZ",
    "VIRIDITAS_THRESHOLD",
    "viriditas_magnum_opus",
    "get_viriditas_engine",
]
