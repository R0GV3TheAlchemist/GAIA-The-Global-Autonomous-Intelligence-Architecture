"""GAIA-OS Numerology package.

Public surface:
  NumerologyService  — stateless computation + persistence service
  NumerologyEngine   — pure-function calculation core (no DB)
"""
from gaia.numerology.engine import NumerologyEngine
from gaia.numerology.service import NumerologyService

__all__ = ["NumerologyEngine", "NumerologyService"]
