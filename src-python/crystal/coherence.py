"""
crystal/coherence.py
Computes the composite coherence score Ψ from the four live-stream inputs.

Ψ = w_A·A + w_S·S + w_E·E + w_H·H

Weights (from spec C-CC01 §3.1):
  Affect    w_A = 0.35
  Stage     w_S = 0.30
  Shadow    w_E = 0.20
  Schumann  w_H = 0.15

API (current)
-------------
compute_coherence(
    *,
    arc_stability,        # float [0,1]  – from affect stream
    valence_trend,        # float [-1,1] – from affect stream
    volatility,           # float [0,1]  – from affect stream
    marker_scores,        # dict[str,float] [0,100] – from stage stream
    integration_progress, # float [0,1]  – from shadow stream
    shadow_intensity,     # float [0,1]  – from shadow stream
    shadow_available,     # bool
    schumann_alignment,   # float [0,1]  – raw score from schumann stream
    schumann_confidence,  # float [0,1]  – confidence tag from schumann stream
    schumann_available,   # bool
) -> tuple[float, float, float, float, float]
   (psi, A, S, E, H)
"""

from __future__ import annotations

from typing import Optional

# Weights — must sum to 1.0
W_AFFECT   = 0.35
W_STAGE    = 0.30
W_SHADOW   = 0.20
W_SCHUMANN = 0.15

assert abs(W_AFFECT + W_STAGE + W_SHADOW + W_SCHUMANN - 1.0) < 1e-9, \
    "Crystal Core weights must sum to 1.0"

# Stage marker keys and their normalisation denominator
_MARKER_KEYS = [
    "decision_entropy",
    "hrv_coherence",
    "journaling_depth",
    "focus_session_length",
    "goal_completion_rate",
    "emotional_arc_stability",
]


def _clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def _derive_affect_coherence(
    arc_stability: float,
    valence_trend: float,
    volatility: float,
) -> float:
    """
    A = arc_stability weighted by valence trend bonus, penalised by volatility.

    arc_stability  already in [0,1].
    valence_trend  in [-1,1]  → shift to [0,1] for blending.
    volatility     in [0,1]   → high volatility lowers coherence.
    """
    trend_bonus   = (valence_trend + 1.0) / 2.0      # [-1,1] → [0,1]
    raw           = 0.60 * arc_stability + 0.25 * trend_bonus + 0.15 * (1.0 - volatility)
    return _clamp(raw)


def _derive_stage_coherence(marker_scores: dict) -> float:
    """
    S = mean of the normalised marker scores.
    Values are assumed to be in [0,100]; normalise to [0,1].
    Missing keys default to 50.0 (neutral).
    """
    if not marker_scores:
        return 0.5
    values = [float(marker_scores.get(k, 50.0)) / 100.0 for k in _MARKER_KEYS]
    return _clamp(sum(values) / len(values))


def _derive_shadow_integration(
    integration_progress: float,
    shadow_intensity: float,
    shadow_available: bool,
) -> float:
    """
    E = integration_progress dampened by shadow_intensity.
    When shadow data is unavailable → neutral 0.5.
    """
    if not shadow_available:
        return 0.5
    raw = integration_progress * (1.0 - 0.5 * shadow_intensity)
    return _clamp(raw)


def _derive_schumann_alignment(
    schumann_alignment: float,
    schumann_confidence: float,
    schumann_available: bool,
    confidence_threshold: float = 0.3,
) -> float:
    """
    H = schumann_alignment gated by confidence.
    Low confidence or unavailable stream → neutral 0.5.
    """
    if not schumann_available:
        return 0.5
    if schumann_confidence < confidence_threshold:
        return 0.5
    return _clamp(schumann_alignment)


def compute_coherence(
    *,
    arc_stability: float = 0.5,
    valence_trend: float = 0.0,
    volatility: float = 0.0,
    marker_scores: Optional[dict] = None,
    integration_progress: float = 0.5,
    shadow_intensity: float = 0.0,
    shadow_available: bool = True,
    schumann_alignment: float = 0.5,
    schumann_confidence: float = 0.0,
    schumann_available: bool = True,
) -> tuple[float, float, float, float, float]:
    """
    Compute Ψ and all four component scores from raw stream fields.

    Parameters
    ----------
    arc_stability         : emotional arc stability   [0, 1]
    valence_trend         : valence trend direction   [-1, 1]
    volatility            : emotional volatility      [0, 1]
    marker_scores         : stage marker dict         {key: 0-100}
    integration_progress  : shadow work progress      [0, 1]
    shadow_intensity      : active shadow pressure    [0, 1]
    shadow_available      : shadow stream online
    schumann_alignment    : HRV–Schumann alignment    [0, 1]
    schumann_confidence   : stream confidence         [0, 1]
    schumann_available    : schumann stream online

    Returns
    -------
    (psi, A, S, E, H) — all floats in [0.0, 1.0]
    """
    A = _derive_affect_coherence(arc_stability, valence_trend, volatility)
    S = _derive_stage_coherence(marker_scores or {})
    E = _derive_shadow_integration(integration_progress, shadow_intensity, shadow_available)
    H = _derive_schumann_alignment(schumann_alignment, schumann_confidence, schumann_available)

    psi = W_AFFECT * A + W_STAGE * S + W_SHADOW * E + W_SCHUMANN * H
    return _clamp(psi), A, S, E, H
