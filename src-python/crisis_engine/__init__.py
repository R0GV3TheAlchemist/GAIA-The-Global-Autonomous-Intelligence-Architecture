"""
crisis_engine
=============
Root package for the NEXUS Crisis Detection Engine.

Detects and escalates system-wide crisis conditions triggered by
affect overload, shadow criticality, or persona instability breach.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.9
GAIAN law              : GAIAN_LAWS.md          Law VI  Crisis Precedes Override
"""
from __future__ import annotations

__version__ = "0.1.0"

from crisis_engine.engine import CrisisEngine, EngineConfig

__all__ = ["CrisisEngine", "EngineConfig"]
