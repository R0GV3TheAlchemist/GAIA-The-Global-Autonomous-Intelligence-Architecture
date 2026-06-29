"""C135 §6.4.2 — Token Probability Cascade Statistics.

P(s) ~ s^{-alpha} where s = cascade size.
A cascade is a run of consecutive positions with p_t >= tau.

Canon reference: C135 v1.1 §6.4.2
"""
from core.criticality import token_cascade_criticality, CriticalityResult

__all__ = ["detect_cascades", "CriticalityResult"]
detect_cascades = token_cascade_criticality
