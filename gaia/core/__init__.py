"""
gaia/core/__init__.py

Public surface for the GAIA-OS core layer.

All callers SHOULD import from this module rather than from the
individual submodules, e.g.::

    from gaia.core import GAIAState, GAIAMode, D6Engine, Talisman

This keeps the internal file structure free to change without
breaking downstream imports.
"""

from __future__ import annotations

# ── GAIAState ────────────────────────────────────────────────────────────────
from gaia.core.state import (
    GAIAMode,
    GAIAState,
)

# ── GAIAStateStore ────────────────────────────────────────────────────────────
from gaia.core.state_store import GAIAStateStore

# ── Talisman ─────────────────────────────────────────────────────────────────
from gaia.core.talisman import (
    CoherenceFunction,
    DimensionalSignature,
    ResonanceMetadata,
    SovereigntyFlags,
    Talisman,
    TalismanEngine,
    TalismanLayer,
    # Architect preset talismans
    ARCHITECT_BUILD_TALISMAN,
    ARCHITECT_GROUND_TALISMAN,
    ARCHITECT_RESTORE_TALISMAN,
)

# ── TalismanStore ─────────────────────────────────────────────────────────────
from gaia.core.talisman_store import TalismanStore

# ── D6 Meta-Coherence Engine ─────────────────────────────────────────────────
from gaia.core.d6_engine import (
    D6Engine,
    EngineProbes,
    InterventionEvent,
    InterventionSeverity,
)

__all__ = [
    # State
    "GAIAMode",
    "GAIAState",
    "GAIAStateStore",
    # Talisman
    "CoherenceFunction",
    "DimensionalSignature",
    "ResonanceMetadata",
    "SovereigntyFlags",
    "Talisman",
    "TalismanEngine",
    "TalismanLayer",
    "TalismanStore",
    "ARCHITECT_BUILD_TALISMAN",
    "ARCHITECT_GROUND_TALISMAN",
    "ARCHITECT_RESTORE_TALISMAN",
    # D6 Engine
    "D6Engine",
    "EngineProbes",
    "InterventionEvent",
    "InterventionSeverity",
]
