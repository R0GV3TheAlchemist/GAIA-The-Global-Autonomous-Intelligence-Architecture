"""
persona_stability
=================
Root package for the NEXUS Persona Stability Engine.

Prevents identity drift using Oxford/Anthropic Constitutional-AI-aligned
anchor injection and stability scoring.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.5
GAIAN law              : GAIAN_LAWS.md          Law I   Sovereignty of Self
"""
from __future__ import annotations

__version__ = "0.1.0"

from persona_stability.engine import PersonaStabilityEngine

__all__ = ["PersonaStabilityEngine"]
