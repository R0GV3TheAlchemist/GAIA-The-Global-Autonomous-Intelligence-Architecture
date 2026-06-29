"""GAIA Telemetry — C135 §6.4 Criticality Proxy Methods.

Exports:
    compute_attention_entropy   — C135 §6.4.1
    detect_cascades             — C135 §6.4.2
    semantic_entropy_trajectory — C135 §6.4.3
    correlation_length          — C135 §6.4.4
    compute_rci                 — composite Relative Criticality Index

Canon reference: C135 v1.1 §6.4
"""
from core.criticality import (
    attention_entropy_criticality as compute_attention_entropy,
    token_cascade_criticality as detect_cascades,
    semantic_entropy_criticality as semantic_entropy_trajectory,
    correlation_length_criticality as correlation_length,
    compute_rci,
    CriticalityResult,
    RCIResult,
)

__all__ = [
    "compute_attention_entropy",
    "detect_cascades",
    "semantic_entropy_trajectory",
    "correlation_length",
    "compute_rci",
    "CriticalityResult",
    "RCIResult",
]
