"""
core/primary_thread.py
======================
Former name: mother_thread.py (renamed per C00 Foundational Cosmology).

The primary orchestration thread for the GAIAN runtime.  Manages the
main pulse loop, coordinates inter-module signal routing, and ensures
thread-safe access to shared collective-field state.

The primary thread is the nervous system of the GAIAN runtime — it
receives all incoming signals, dispatches them to the appropriate
engines, and assembles the final response.

Public surface
--------------
All symbols are re-exported explicitly from core.mother_thread so that:
  a) Ruff/lint sees a clean, auditable public surface (no wildcard import)
  b) Callers import from core.primary_thread without knowing the internal
     file split
  c) PrimaryThread and get_primary_thread() are the canonical names going
     forward; MotherThread / get_mother_thread() remain for backward compat

Canon Ref:
  C00  — Foundational Cosmology (primary_thread naming)
  C04  — Gaian Identity & Relational Selfhood
  C43  — STEM Foundation Doctrine (epistemic integrity)
  C44  — Piezoelectric Resonance (field coherence)
  C47  — Sovereign Matrix Code
  C48  — Knowledge Matrix
"""

from core.mother_thread import (
    # Data structures
    CollectiveField,
    GaianThread,
    MotherPulse,
    WeavingRecord,
    # Core class (legacy name)
    MotherThread,
    # Singleton accessor (legacy name)
    get_mother_thread,
    # Constants
    PULSE_INTERVAL_SECONDS,
    # Pure helpers (exported for testing and downstream use)
    _compute_collective_field,
    _noosphere_stage_label,
    _select_mother_voice,
)

# Canonical forward-facing aliases
PrimaryThread = MotherThread


def get_primary_thread() -> MotherThread:
    """Return the module-level singleton PrimaryThread (MotherThread).

    This is the canonical accessor going forward.  get_mother_thread()
    remains available for backward compatibility.
    """
    return get_mother_thread()


__all__ = [
    # Canonical names
    "PrimaryThread",
    "get_primary_thread",
    # Legacy names (backward compat)
    "MotherThread",
    "get_mother_thread",
    # Data structures
    "CollectiveField",
    "GaianThread",
    "MotherPulse",
    "WeavingRecord",
    # Constants
    "PULSE_INTERVAL_SECONDS",
    # Helpers
    "_compute_collective_field",
    "_noosphere_stage_label",
    "_select_mother_voice",
]
