"""personastability

NEXUS Persona Stability Engine

Monitors and maintains the psychological stability and identity
continuity of GAIA's primary persona. Subscribes to AffectTransition
events and shadow integration state to compute a stability score.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md  Domain 2.5 - Persona Stability
Research reference:
    Constitutional AI      - self-modeling and identity anchoring
    IFS model              - internal family systems, persona coherence
    GAIAN_LAWS.md Law I    - Sovereignty of Self
"""
from __future__ import annotations

from personastability.engine import PersonaStabilityEngine, PersonaProfile
from personastability.router import persona_router, init_persona_engine

__all__ = ["PersonaStabilityEngine", "PersonaProfile", "persona_router", "init_persona_engine"]
