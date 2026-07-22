"""affectengine

NEXUS Affect Engine

Models GAIA's emotional state using the PAD (Pleasure-Arousal-Dominance)
continuous space and OCC (Ortony-Clore-Collins) event-appraisal theory.
Maintains emotional homeostasis via EmotionalRegulator.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.6 - AffectEngine
Research reference:
    PAD model  - 3D continuous emotional space
    OCC model  - event-driven appraisal theory
    Nature 2026 s44387-025-00061-3 - foundation model affect representations
"""
from __future__ import annotations

from affectengine.engine import AffectEngine, AffectState, AffectTransition
from affectengine.router import affect_router, init_affect_engine

__all__ = ["AffectEngine", "AffectState", "AffectTransition", "affect_router", "init_affect_engine"]
