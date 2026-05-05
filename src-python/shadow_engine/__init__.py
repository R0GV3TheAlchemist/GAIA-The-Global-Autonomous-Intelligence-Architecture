"""
GAIA-OS Shadow Engine  (Issue #67 — Pillar I: Magnum Opus)

The Shadow Engine is the Jungian mirror layer of GAIA-OS.
It detects recurring behavioral patterns the user is unaware of and surfaces
contradictions between stated values and actual behavior — but only when
the user is in the right stage and emotional state to receive them.

Key design rules
----------------
* NEVER surface during: Stage 1, high distress, alignment score < 30.
* NEVER push unsolicited notifications — surface through GAIA conversation only.
* All observation data is stored in encrypted SovereignMemory.
* Zero shadow data transmitted externally.

Usage::

    from shadow_engine import ShadowEngine
    from sovereign_memory import SovereignMemory

    with SovereignMemory() as mem:
        engine = ShadowEngine(memory=mem)
        obs = engine.evaluate(principal_id="user-001")
        # obs is List[ShadowObservation] — may be empty if gate blocked
"""

from .engine import ShadowEngine
from .types import (
    ShadowObservation,
    ShadowMode,
    ShadowArchetype,
    ShadowRecord,
    ObservationFeedback,
    ValuesVector,
    ValuesBehaviorGap,
)

__all__ = [
    "ShadowEngine",
    "ShadowObservation",
    "ShadowMode",
    "ShadowArchetype",
    "ShadowRecord",
    "ObservationFeedback",
    "ValuesVector",
    "ValuesBehaviorGap",
]
