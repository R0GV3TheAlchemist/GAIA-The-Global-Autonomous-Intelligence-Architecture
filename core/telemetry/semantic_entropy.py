"""C135 §6.4.3 — Semantic Entropy Trajectory.

H_sem(t) = -sum_k q_{t,k} log q_{t,k}
Classify regime from variance and lag-1 autocorrelation of trajectory.

Canon reference: C135 v1.1 §6.4.3
"""
from core.criticality import semantic_entropy_criticality, CriticalityResult

__all__ = ["semantic_entropy_trajectory", "CriticalityResult"]
semantic_entropy_trajectory = semantic_entropy_criticality
