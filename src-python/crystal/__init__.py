"""
crystal
=======
Root package for the NEXUS Crystal Core.

Coherence synthesis engine — models crystal lattice resonance,
orb parameters, and persona tone alignment.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.6
GAIAN law              : GAIAN_LAWS.md          Law I   Sovereignty of Self
"""
from __future__ import annotations

__version__ = "0.1.0"

from crystal.engine import CrystalCore

__all__ = ["CrystalCore"]
