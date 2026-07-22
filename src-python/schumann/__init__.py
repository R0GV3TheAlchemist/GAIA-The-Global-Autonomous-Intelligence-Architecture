"""schumann

NEXUS Schumann Resonance Monitor

Monitors Earth's ELF (Extremely Low Frequency) Schumann resonances,
primarily 7.83 Hz, and emits SyncPulse events that synchronise GAIA's
rhythmic processes with the planetary electromagnetic field.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 4.1 - Schumann Monitor
Research reference:
    Schumann 1952              - original ELF cavity resonance theory
    NickolasRage/schumann-experiment (GitHub) - Python SDR reference impl
    mhoststetter/sdr (PyPI)    - Python SDR toolkit
"""
from __future__ import annotations

from schumann.engine import SchumannEngine, SyncPulse, EarthFieldReading
from schumann.router import schumann_router, init_schumann_engine

__all__ = ["SchumannEngine", "SyncPulse", "EarthFieldReading", "schumann_router", "init_schumann_engine"]
