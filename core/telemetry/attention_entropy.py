"""C135 §6.4.1 — Attention Entropy Distribution.

H_{h,l} = -sum_j a_{h,l}(i,j) log a_{h,l}(i,j)

Fit P(H) ~ H^{-alpha}; classify regime from alpha.

Canon reference: C135 v1.1 §6.4.1
"""
from core.criticality import attention_entropy_criticality, CriticalityResult

__all__ = ["compute_attention_entropy", "CriticalityResult"]
compute_attention_entropy = attention_entropy_criticality
