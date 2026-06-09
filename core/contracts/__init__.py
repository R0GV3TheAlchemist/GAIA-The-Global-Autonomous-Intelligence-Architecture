"""
core/contracts/__init__.py

Layer 0 - Contracts (Shared Types)

This package is the single source of truth for all cross-layer shared
symbols: dataclasses, enums, protocols, and constants that are imported
by more than one layer.

Architectural rule:
    - core/contracts imports NOTHING from the rest of core/
    - Every other layer MAY import from core.contracts
    - This prevents circular imports by making shared types dependency-free

Current exports:
    AffectInput     - affect inference input signals (from affect_inference)
    AffectState     - canonical GAIA affect state enum (from affect_inference)
    FeelingState    - rich affect inference result (from affect_inference)

See ARCHITECTURE.md for the full 7-layer dependency graph.
"""

from core.affect_inference import AffectInput, AffectState, FeelingState

__all__ = [
    "AffectInput",
    "AffectState",
    "FeelingState",
]
