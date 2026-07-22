"""
affect_engine
=============
Root package for the NEXUS Affect Engine.

Models the emotional-affective state of the GAIA-OS user using a
PAD (Pleasure-Arousal-Dominance) / OCC-aligned signal space.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.2
GAIAN law              : GAIAN_LAWS.md          Law V   Emotional Sovereignty
Ethics reference       : ETHICS.md              Commitment 4  Affective Transparency
"""
from __future__ import annotations

__version__ = "0.1.0"

from affect_engine.engine import AffectEngine

__all__ = ["AffectEngine"]
