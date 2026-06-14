"""
core/monad
GAIA-OS Monad Layer — Public API

The Monad is the irreducible, self-contained unit of GAIA-OS.
Each subsystem is a Monad. Pre-Established Harmony is the synchronisation loop.

See docs/canon/monad.md for philosophical and technical foundations.
See Issue #398 — The Monad and the Variety of Monads.
"""

from .base import GaiaMonad, MonadState
from .registry import MonadRegistry, MonadType, get_monad_registry
from .simulation import MonadSimulation, SimulationReport

__all__ = [
    "GaiaMonad",
    "MonadState",
    "MonadRegistry",
    "MonadType",
    "get_monad_registry",
    "MonadSimulation",
    "SimulationReport",
]
