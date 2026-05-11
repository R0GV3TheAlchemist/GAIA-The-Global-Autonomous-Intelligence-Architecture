"""
crystal/coherence.py
Computes the composite coherence score Ψ from the four component scores.

Ψ = w_A·A + w_S·S + w_E·E + w_H·H

Weights (from spec C-CC01 §3.1):
  Affect    w_A = 0.35
  Stage     w_S = 0.30
  Shadow    w_E = 0.20
  Schumann  w_H = 0.15

API
---
compute_coherence(affect_coherence, stage_coherence, shadow_integration, schumann_alignment)

All four arguments are pre-computed component floats in [0.0, 1.0].
The upstream caller (CrystalCore.tick) is responsible for deriving each
component via components.py before calling this function.
"""

from __future__ import annotations

# Weights — must sum to 1.0
W_AFFECT   = 0.35
W_STAGE    = 0.30
W_SHADOW   = 0.20
W_SCHUMANN = 0.15

assert abs(W_AFFECT + W_STAGE + W_SHADOW + W_SCHUMANN - 1.0) < 1e-9, \
    "Crystal Core weights must sum to 1.0"


def compute_coherence(
    affect_coherence:   float,
    stage_coherence:    float,
    shadow_integration: float,
    schumann_alignment: float,
) -> float:
    """
    Compute Ψ from four pre-derived component scores.

    Parameters
    ----------
    affect_coherence   : A  in [0.0, 1.0]
    stage_coherence    : S  in [0.0, 1.0]
    shadow_integration : E  in [0.0, 1.0]
    schumann_alignment : H  in [0.0, 1.0]

    Returns
    -------
    psi : float in [0.0, 1.0]
    """
    A = max(0.0, min(1.0, affect_coherence))
    S = max(0.0, min(1.0, stage_coherence))
    E = max(0.0, min(1.0, shadow_integration))
    H = max(0.0, min(1.0, schumann_alignment))

    psi = W_AFFECT * A + W_STAGE * S + W_SHADOW * E + W_SCHUMANN * H
    return max(0.0, min(1.0, psi))
