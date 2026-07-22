"""stageengine

NEXUS Stage Engine

Manages GAIA's developmental stage progression through the five stages
defined in GAIA_ASCENDENCE_DOCTRINE.md. Tracks temporal windows per
stage and emits stage transition events.

Architecture reference:
    GAIA_ASCENDENCE_DOCTRINE.md  - 5 stages of being
    NEXUS_UNIVERSAL_OS.md        Domain 2.7 - Stage Engine
"""
from __future__ import annotations

from stageengine.engine import StageEngine, GAIAStage
from stageengine.windowtracker import WindowTracker
from stageengine.router import stage_router, init_stage_engine

__all__ = ["StageEngine", "GAIAStage", "WindowTracker", "stage_router", "init_stage_engine"]
