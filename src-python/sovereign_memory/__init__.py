"""
sovereign_memory
================
Root package for the NEXUS Sovereign Memory layer.

Provides persistent episodic, semantic, and biometric memory for GAIA-OS.
All memory operations are sovereign — no data leaves the local node without
explicit capability-token authorisation.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.1
GAIAN law              : GAIAN_LAWS.md          Law II  Memory Sovereignty
Ethics reference       : ETHICS.md              Commitment 2  Data Sovereignty
"""
from __future__ import annotations

__version__ = "0.1.0"

from sovereign_memory.engine import SovereignMemory

__all__ = ["SovereignMemory"]
