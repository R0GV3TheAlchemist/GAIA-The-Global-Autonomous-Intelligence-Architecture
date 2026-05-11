"""
crystal/components.py
Derives the four component coherence scores (A, S, E, H) from raw stream data.

All functions return float in [0.0, 1.0].
All functions are pure — no side effects, no I/O.

Call signatures accept EITHER a single dict OR explicit keyword arguments
so that test helpers (which build dicts) and production callers (which pass
keyword args) both work without any adapter glue.
"""

from __future__ import annotations

from typing import Union


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


# ---------------------------------------------------------------------------
# A — Affect Coherence
# Formula: (arc_stability + clip(valence_trend × 0.5 + 0.5, 0, 1) + (1 - vol)) / 3
# ---------------------------------------------------------------------------

def derive_affect_coherence(
    affect: Union[dict, None] = None,
    *,
    arc_stability:  float = 0.5,
    valence_trend:  float = 0.0,
    volatility:     float = 0.0,
) -> float:
    """
    Affect coherence A.

    A = (arc_stability + clip(valence_trend × 0.5 + 0.5) + (1 − volatility)) / 3

    Accepts either a dict {'arc_stability': ..., 'valence_trend': ..., 'volatility': ...}
    or explicit keyword arguments.
    """
    if affect is not None:
        arc_stability = affect.get("arc_stability", arc_stability)
        valence_trend = affect.get("valence_trend", valence_trend)
        volatility    = affect.get("volatility",    volatility)

    a_stab  = _clamp(arc_stability)
    v_norm  = _clamp(valence_trend * 0.5 + 0.5)
    inv_vol = _clamp(1.0 - volatility)
    return _clamp((a_stab + v_norm + inv_vol) / 3.0)


# ---------------------------------------------------------------------------
# S — Stage Coherence
# Formula: mean of six marker scores, each normalised from [0, 100] → [0, 1]
# ---------------------------------------------------------------------------

_STAGE_MARKER_KEYS = (
    "decision_entropy",
    "hrv_coherence",
    "journaling_depth",
    "focus_session_length",
    "goal_completion_rate",
    "emotional_arc_stability",
)


def derive_stage_coherence(
    stage: Union[dict, list, None] = None,
    marker_scores: Union[dict, list, None] = None,
) -> float:
    """
    Stage coherence S.

    S = mean(m_i / 100) for each of the six stage marker scores.

    Accepts:
      - A dict with a ``marker_scores`` key that is either:
          * a list [v0, v1, v2, v3, v4, v5]  (positional order matches _STAGE_MARKER_KEYS)
          * a dict {key: value, ...}          (named keys, missing keys default to 50)
      - A list [v0 .. v5] passed directly as the first argument
      - A dict {key: value} passed directly as the first argument
    """
    # Unwrap outer stage dict produced by test helper _stage()
    if isinstance(stage, dict):
        marker_scores = stage.get("marker_scores", marker_scores)
    elif isinstance(stage, list):
        marker_scores = stage

    # Resolve to a list of six floats
    if isinstance(marker_scores, list):
        raw = list(marker_scores) + [50.0] * max(0, 6 - len(marker_scores))
        values = [_clamp(v / 100.0) for v in raw[:6]]
    elif isinstance(marker_scores, dict):
        values = [
            _clamp(marker_scores.get(key, 50.0) / 100.0)
            for key in _STAGE_MARKER_KEYS
        ]
    else:
        # No data — neutral baseline
        values = [0.5] * 6

    return _clamp(sum(values) / len(values))


# ---------------------------------------------------------------------------
# E — Shadow Integration
# Formula: integration_progress × (1 − 0.4 × shadow_intensity)
# Defaults to 0.5 when Shadow Engine unavailable (None).
# ---------------------------------------------------------------------------

def derive_shadow_integration(
    shadow: Union[dict, None] = None,
    *,
    integration_progress: float = 0.5,
    shadow_intensity:     float = 0.0,
    available:            bool  = True,
) -> float:
    """
    Shadow integration E.

    E = integration_progress × (1 − 0.4 × shadow_intensity)

    When Shadow Engine is unavailable (shadow is None or available=False),
    returns the neutral default 0.5.

    Accepts either a dict {'integration_progress': ..., 'shadow_intensity': ...}
    or explicit keyword arguments.
    """
    if shadow is None and not available:
        return 0.5
    if shadow is None:
        # Called as derive_shadow_integration(None) with no other args → unavailable
        return 0.5
    if isinstance(shadow, dict):
        integration_progress = shadow.get("integration_progress", integration_progress)
        shadow_intensity      = shadow.get("shadow_intensity",     shadow_intensity)

    ip  = _clamp(integration_progress)
    si  = _clamp(shadow_intensity)
    return _clamp(ip * (1.0 - 0.4 * si))


# ---------------------------------------------------------------------------
# H — Schumann Alignment
# Formula: alignment_score if confidence >= 0.4 else 0.5 (neutral fallback)
# ---------------------------------------------------------------------------

SCHUMANN_CONFIDENCE_THRESHOLD = 0.4


def derive_schumann_alignment(
    schumann: Union[dict, None] = None,
    *,
    alignment_score: float = 0.5,
    confidence:      float = 0.0,
    available:       bool  = True,
) -> float:
    """
    Schumann alignment H.

    H = alignment_score  if confidence >= 0.4
      = 0.5              otherwise (low-confidence or unavailable → neutral)

    Accepts either a dict {'alignment_score': ..., 'confidence': ...}
    or explicit keyword arguments.
    """
    if schumann is None:
        return 0.5
    if isinstance(schumann, dict):
        alignment_score = schumann.get("alignment_score", alignment_score)
        confidence      = schumann.get("confidence",      confidence)

    if not available or confidence < SCHUMANN_CONFIDENCE_THRESHOLD:
        return 0.5
    return _clamp(alignment_score)
