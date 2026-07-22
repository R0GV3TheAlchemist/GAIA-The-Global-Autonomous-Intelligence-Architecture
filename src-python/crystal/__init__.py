"""crystal

NEXUS Crystal Lattice Simulation Module

Models periodic crystal structures and phonon propagation within
the NEXUS architecture. Provides CrystalCore engine and router.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 4.2 - Crystal Simulation
Research reference:
    pymatgen (pymatgen.org)  - periodic crystal structure library
    ASE                      - Atomic Simulation Environment
    phonopy                  - phonon calculation toolkit
"""
from __future__ import annotations

from crystal.engine import CrystalCore, CrystalNode, CrystalLattice
from crystal.router import crystal_router, init_crystal_core

__all__ = ["CrystalCore", "CrystalNode", "CrystalLattice", "crystal_router", "init_crystal_core"]
