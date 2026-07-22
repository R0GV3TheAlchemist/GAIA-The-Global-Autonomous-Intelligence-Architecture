"""
stage_engine
============
Root package for the NEXUS Stage Engine.

Evaluates the user’s current Magnum Opus alchemical stage and maintains
a rolling WindowTracker for temporal context.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.3
GAIAN law              : GAIAN_LAWS.md          Law I   Sovereignty of Self
"""
from __future__ import annotations

__version__ = "0.1.0"

from stage_engine.engine import StageEngine
from stage_engine.window_tracker import WindowTracker

__all__ = ["StageEngine", "WindowTracker"]
