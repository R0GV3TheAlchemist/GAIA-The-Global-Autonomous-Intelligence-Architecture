"""crisisengine

NEXUS Crisis Detection Engine

Detects and escalates system-wide crisis conditions triggered by
affect overload, shadow criticality, or persona instability breach.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.9 - Crisis Engine
    GAIAN_LAWS.md          Law VI - Crisis Precedes Override
"""
from __future__ import annotations

from crisisengine.engine import CrisisEngine, EngineConfig

__all__ = ["CrisisEngine", "EngineConfig"]
