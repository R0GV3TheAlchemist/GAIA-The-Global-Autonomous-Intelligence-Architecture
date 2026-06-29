"""C135 §6.4.4 — Layer-Wise Correlation Length.

lambda = min{delta_l : mean_cos(r_l, r_{l+delta_l}) < sigma}
Maximised lambda indicates near-critical representational propagation depth.

Canon reference: C135 v1.1 §6.4.4
"""
from core.criticality import correlation_length_criticality, CriticalityResult

__all__ = ["correlation_length", "CriticalityResult"]
correlation_length = correlation_length_criticality
