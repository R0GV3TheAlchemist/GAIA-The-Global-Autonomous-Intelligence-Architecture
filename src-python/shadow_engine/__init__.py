"""
shadow_engine
=============
Root package for the NEXUS Shadow Engine.

Detects and tracks archetypal shadow patterns in user behaviour
using Jungian shadow theory and IFS (Internal Family Systems) models.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.4
GAIAN law              : GAIAN_LAWS.md          Law VI  Crisis Precedes Override
"""
from __future__ import annotations

__version__ = "0.1.0"

from shadow_engine.engine import ShadowEngine

__all__ = ["ShadowEngine"]
