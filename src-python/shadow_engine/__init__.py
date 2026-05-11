"""
shadow_engine — public surface

Exports:
    ShadowRecord, ShadowTransition, ArchetypeScore
    ShadowEngine
    get_shadow_state(principal_id) -> ShadowRecord | None
"""

from .types   import ShadowRecord, ShadowTransition, ArchetypeScore
from .engine  import ShadowEngine

_engine: ShadowEngine | None = None


def _get_engine() -> ShadowEngine:
    global _engine
    if _engine is None:
        _engine = ShadowEngine()
    return _engine


async def get_shadow_state(principal_id: str) -> ShadowRecord | None:
    """Return the current ShadowRecord for *principal_id*, or None if not found."""
    return await _get_engine().get_current(principal_id)


__all__ = [
    "ShadowRecord",
    "ShadowTransition",
    "ArchetypeScore",
    "ShadowEngine",
    "get_shadow_state",
]
