"""
schumann
========
Root package for the NEXUS Schumann Resonance Engine.

Aligns GAIA-OS operations with Earth’s electromagnetic resonance
frequency (7.83 Hz fundamental and harmonics).

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 1.4
GAIAN law              : GAIAN_LAWS.md          Law IV  Mesh Sovereignty
"""
from __future__ import annotations

__version__ = "0.1.0"

from schumann.engine import SchumannEngine

__all__ = ["SchumannEngine"]
