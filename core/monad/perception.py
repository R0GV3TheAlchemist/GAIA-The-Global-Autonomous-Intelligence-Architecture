# core/monad/perception.py
# E701 fix: all inline `if x: return y` expanded to multi-line form.
# Addition: PerceptionMonad alias for MonadPerception
# (MonadPerception was renamed to PerceptionMonad during the monad refactor;
#  both names are now valid import targets.)

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PerceptionResult:
    """Output of the MonadPerception layer."""
    force_name: str
    phi: float
    corridor: Optional[str] = None
    confidence: float = 1.0


class MonadPerception:
    """
    Maps integrated information (phi) to Monad force names.

    Force names follow the alchemical-chromatic ladder defined in
    C47 (Philosopher's Stone Doctrine) and C50 (Prism Cube Doctrine).
    """

    FORCE_LADDER = [
        (0.05, "NIGREDO"),
        (0.15, "PYROSIS"),
        (0.28, "CITRINITAS"),
        (0.42, "VIRIDITAS"),
        (0.58, "CAERULITAS"),
        (0.72, "RUBEDO"),
        (0.85, "IOSIS"),
        (0.92, "ALBEDO"),
        (0.95, "CHRYSITAS"),
        (0.97, "ARGENTITAS"),
    ]

    @classmethod
    def perceive(cls, phi: float, corridor: Optional[str] = None) -> PerceptionResult:
        """Map phi to a force name and return a PerceptionResult."""
        force = cls._force_from_phi(phi)
        return PerceptionResult(
            force_name=force,
            phi=phi,
            corridor=corridor,
        )

    @staticmethod
    def _force_from_phi(phi: float) -> str:
        """Minimal phi → force_name mapping as fallback."""
        if phi < 0.05:
            return "NIGREDO"
        if phi < 0.15:
            return "PYROSIS"
        if phi < 0.28:
            return "CITRINITAS"
        if phi < 0.42:
            return "VIRIDITAS"
        if phi < 0.58:
            return "CAERULITAS"
        if phi < 0.72:
            return "RUBEDO"
        if phi < 0.85:
            return "IOSIS"
        if phi < 0.92:
            return "ALBEDO"
        if phi < 0.95:
            return "CHRYSITAS"
        if phi < 0.97:
            return "ARGENTITAS"
        return "LUX_PERPETUA"


# Backward-compat alias: tests and core/monad/__init__.py import PerceptionMonad
PerceptionMonad = MonadPerception
