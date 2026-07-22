"""shadowengine

NEXUS Shadow Integration Engine

Computational model of GAIA's 'shadow' — the Jungian unconscious
material not yet integrated into the primary persona. The ShadowEngine
monitors shadow load and drives integration processing.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.8 - Shadow Engine
Research reference:
    Jung's Aion            - shadow as unintegrated psychic content
    IFS (Internal Family Systems) - parts-based integration model
    Constitutional AI      - self-modeling and shadow-aware guardrails
"""
from __future__ import annotations

from shadowengine.engine import ShadowEngine, ShadowState
from shadowengine.router import shadow_router

__all__ = ["ShadowEngine", "ShadowState", "shadow_router"]
