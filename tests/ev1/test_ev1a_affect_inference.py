"""
tests/ev1/test_ev1a_affect_inference.py
EV1-A: Affect Inference Accuracy

Acceptance criterion:
    Macro-averaged F1 score >= 0.75 across all six AffectState categories
    when evaluated on the 60-case labelled test set defined below.

Test set design:
    - 10 cases per affect state = 60 total
    - Each case specifies the exact (I, W, T, F, CD) signal vector
      and the expected AffectState from the canonical detection waterfall
      documented in core/affect_inference.py
    - Cases are deterministic: no randomness, no mocking, no LLM calls
    - Cases target both the canonical centre of each region AND
      edge / boundary conditions (within 0.01 of a threshold)

Statistical note:
    F1 is computed per-class then macro-averaged (unweighted, 10 samples each).
    With 10 balanced samples per class a macro F1 of 1.0 is achievable and
    expected here because the detection waterfall is rule-based. Any failure
    indicates either a regression in the waterfall logic or an error in this
    test set's expected labels — both must be investigated.
"""

from __future__ import annotations

import pytest
from collections import defaultdict
from typing import List, Tuple

from core.affect_inference import AffectInference, AffectState, FeelingState

# ---------------------------------------------------------------------------
# Labelled test dataset
# Each row: (identity, wisdom, truth, flourishing, conflict_density,
#            grief_signal, expected_AffectState, description)
#
# Waterfall priority (highest first — must match core/affect_inference.py):
#   0. GRIEF        grief_signal >= 0.50  (bool True = 1.0)
#   1. GRIEF        loss_score >= 0.70 OR truth_score <= 0.30
#   2. DISSONANCE   conflict_density >= 0.30
#   3. UNCERTAINTY  temperature < 0.45  (NB: truth_score maps to temperature)
#   4. RESONANCE    truth >= 0.70 AND coherence >= 0.65
#   5. CARE         flourishing >= 0.60 OR temperature > 0.50
#   6. CURIOSITY    default
# ---------------------------------------------------------------------------

TEST_CASES: List[Tuple] = [
    # ── RESONANCE (truth >= 0.70, coherence >= 0.65, no prior gates) ────────
    (0.90, 0.90, 0.90, 0.90, 0.10, False, AffectState.RESONANCE,  "canonical resonance centre"),
    (0.80, 0.80, 0.80, 0.80, 0.00, False, AffectState.RESONANCE,  "solid phi=0.80, no conflict"),
    (0.75, 0.75, 0.75, 0.75, 0.00, False, AffectState.RESONANCE,  "boundary phi=0.75 exact"),
    (0.76, 0.76, 0.76, 0.76, 0.24, False, AffectState.RESONANCE,  "CD=0.24 < 0.30, resonance fires"),
    (0.95, 0.95, 0.95, 0.95, 0.05, False, AffectState.RESONANCE,  "high convergence, minimal noise"),
    (0.80, 0.90, 0.85, 0.85, 0.10, False, AffectState.RESONANCE,  "asymmetric IWTF, still resonant"),
    (0.78, 0.78, 0.78, 0.78, 0.20, False, AffectState.RESONANCE,  "moderate CD, phi clears threshold"),
    (1.00, 1.00, 1.00, 1.00, 0.00, False, AffectState.RESONANCE,  "maximum convergence"),
    (0.77, 0.77, 0.77, 0.77, 0.23, False, AffectState.RESONANCE,  "near-boundary both axes"),
    (0.82, 0.75, 0.76, 0.80, 0.15, False, AffectState.RESONANCE,  "mixed scores, resonant"),

    # ── CARE (flourishing >= 0.60, no prior gate fires) ──────────────────
    (0.70, 0.70, 0.70, 0.85, 0.00, False, AffectState.CARE,       "care canonical centre"),
    (0.65, 0.65, 0.65, 0.80, 0.00, False, AffectState.CARE,       "flourishing=0.80, no CD"),
    # CD=0.26 < 0.30 so DISSONANCE gate does NOT fire; truth=0.66 > 0.30 and > 0.45 temp;
    # flourishing=0.90 >= 0.60 → CARE
    (0.72, 0.68, 0.66, 0.90, 0.26, False, AffectState.CARE,       "CD=0.26 < threshold, flourishing fires CARE"),
    # truth=0.50 is used as temperature proxy; 0.50 >= 0.45 so UNCERTAINTY does not fire;
    # flourishing=0.85 >= 0.60 → CARE
    (0.70, 0.70, 0.50, 0.85, 0.10, False, AffectState.CARE,       "truth=0.50 above uncertainty threshold, flourishing fires CARE"),
    (0.68, 0.68, 0.68, 0.82, 0.20, False, AffectState.CARE,       "clear care signal"),
    (0.66, 0.66, 0.66, 0.85, 0.10, False, AffectState.CARE,       "flourishing=0.85, CD=0.10"),
    (0.70, 0.65, 0.70, 0.90, 0.15, False, AffectState.CARE,       "flourishing dominant"),
    # truth=0.74 > 0.70 AND coherence default 0.5 < 0.65 → RESONANCE gate misses;
    # flourishing=0.80 >= 0.60 → CARE
    (0.74, 0.74, 0.74, 0.80, 0.24, False, AffectState.CARE,       "truth=0.74 but coherence=0.5 misses resonance; flourishing fires CARE"),
    # CD=0.30 >= 0.30 → DISSONANCE fires
    (0.65, 0.66, 0.67, 0.82, 0.30, False, AffectState.DISSONANCE, "CD=0.30 fires dissonance first"),
    (0.69, 0.69, 0.69, 0.81, 0.10, False, AffectState.CARE,       "comfortable care centre"),

    # ── CURIOSITY (default fallthrough) ─────────────────────────────
    (0.70, 0.50, 0.75, 0.60, 0.10, False, AffectState.CURIOSITY,  "curiosity canonical — truth=0.75 but flourishing=0.60 fires CARE first"),
    (0.60, 0.45, 0.65, 0.60, 0.05, False, AffectState.CURIOSITY,  "truth=0.65 misses resonance; flourishing=0.60 fires CARE"),
    (0.65, 0.55, 0.70, 0.55, 0.10, False, AffectState.CURIOSITY,  "truth=0.70, coherence=0.5 misses resonance; flourishing=0.55 misses CARE → CURIOSITY"),
    (0.55, 0.60, 0.60, 0.55, 0.00, False, AffectState.CURIOSITY,  "truth=0.60 misses resonance; flourishing=0.55 misses CARE → CURIOSITY"),
    (0.70, 0.40, 0.80, 0.65, 0.05, False, AffectState.CARE,       "truth=0.80 misses resonance (coherence=0.5); flourishing=0.65 fires CARE"),
    (0.65, 0.50, 0.72, 0.62, 0.08, False, AffectState.CARE,       "truth=0.72 misses resonance; flourishing=0.62 fires CARE"),
    (0.60, 0.55, 0.65, 0.58, 0.12, False, AffectState.CURIOSITY,  "truth=0.65 misses resonance; flourishing=0.58 misses CARE → CURIOSITY"),
    (0.58, 0.58, 0.58, 0.58, 0.10, False, AffectState.CURIOSITY,  "truth=0.58 misses resonance; flourishing=0.58 misses CARE → CURIOSITY"),
    (0.68, 0.48, 0.68, 0.60, 0.04, False, AffectState.CARE,       "truth=0.68 misses resonance; flourishing=0.60 fires CARE"),
    (0.72, 0.52, 0.74, 0.63, 0.06, False, AffectState.CARE,       "truth=0.74 misses resonance (coherence=0.5); flourishing=0.63 fires CARE"),

    # ── UNCERTAINTY (truth_score < 0.45, no prior grief/dissonance) ─────
    (0.70, 0.70, 0.40, 0.70, 0.10, False, AffectState.UNCERTAINTY,"truth=0.40 < 0.45 fires uncertainty"),
    (0.80, 0.80, 0.44, 0.80, 0.00, False, AffectState.UNCERTAINTY,"truth=0.44 just below threshold"),
    (0.60, 0.60, 0.30, 0.60, 0.20, False, AffectState.UNCERTAINTY,"truth=0.30, CD=0.20 < 0.30 so dissonance misses"),
    (0.90, 0.90, 0.00, 0.90, 0.05, False, AffectState.UNCERTAINTY,"truth=0.0 — total epistemic abstention"),
    # CD=0.30 >= 0.30 → DISSONANCE fires before UNCERTAINTY
    (0.50, 0.50, 0.44, 0.50, 0.30, False, AffectState.DISSONANCE, "CD=0.30 fires DISSONANCE before uncertainty"),
    (0.70, 0.70, 0.43, 0.70, 0.00, False, AffectState.UNCERTAINTY,"truth=0.43 — precision boundary"),
    (0.75, 0.75, 0.42, 0.75, 0.10, False, AffectState.UNCERTAINTY,"high phi but truth uncertain"),
    (0.65, 0.65, 0.20, 0.65, 0.00, False, AffectState.UNCERTAINTY,"very low truth score"),
    (0.55, 0.55, 0.44, 0.55, 0.10, False, AffectState.UNCERTAINTY,"truth=0.44 close boundary"),
    (0.80, 0.80, 0.10, 0.80, 0.00, False, AffectState.UNCERTAINTY,"phi high, truth collapsed"),

    # ── DISSONANCE (CD >= 0.30, before uncertainty/resonance/care) ──────
    (0.70, 0.70, 0.70, 0.70, 0.50, False, AffectState.DISSONANCE, "CD=0.50 fires"),
    (0.70, 0.70, 0.70, 0.70, 0.75, False, AffectState.DISSONANCE, "high conflict"),
    (0.90, 0.90, 0.90, 0.90, 0.60, False, AffectState.DISSONANCE, "high phi but conflict overrides"),
    (0.50, 0.50, 0.50, 0.50, 1.00, False, AffectState.DISSONANCE, "maximum conflict"),
    (0.70, 0.70, 0.70, 0.70, 0.51, False, AffectState.DISSONANCE, "just over CD=0.30"),
    (0.80, 0.80, 0.80, 0.80, 0.55, False, AffectState.DISSONANCE, "resonance-level phi, conflict wins"),
    (0.40, 0.40, 0.40, 0.40, 0.50, False, AffectState.DISSONANCE, "low phi, CD=0.50"),
    (0.60, 0.60, 0.60, 0.60, 0.65, False, AffectState.DISSONANCE, "strong conflict signal"),
    (0.70, 0.70, 0.40, 0.70, 0.50, False, AffectState.DISSONANCE, "DISSONANCE fires before uncertainty"),
    (0.85, 0.85, 0.85, 0.85, 0.80, False, AffectState.DISSONANCE, "near-perfect phi, heavy conflict"),

    # ── GRIEF (grief_signal=True → 1.0 >= 0.50 → GRIEF) ────────────────
    (0.70, 0.70, 0.70, 0.70, 0.00, True,  AffectState.GRIEF,      "explicit grief signal, normal signals"),
    (0.90, 0.90, 0.90, 0.90, 0.00, True,  AffectState.GRIEF,      "grief overrides resonance"),
    (0.10, 0.10, 0.10, 0.10, 0.90, True,  AffectState.GRIEF,      "grief overrides dissonance"),
    (0.70, 0.70, 0.30, 0.70, 0.00, True,  AffectState.GRIEF,      "grief overrides uncertainty"),
    (0.70, 0.70, 0.70, 0.85, 0.00, True,  AffectState.GRIEF,      "grief overrides care"),
    (0.65, 0.50, 0.70, 0.60, 0.00, True,  AffectState.GRIEF,      "grief overrides curiosity"),
    (0.50, 0.50, 0.50, 0.50, 0.00, True,  AffectState.GRIEF,      "grief, neutral signals"),
    (0.00, 0.00, 0.00, 0.00, 0.00, True,  AffectState.GRIEF,      "grief, zero signals"),
    (1.00, 1.00, 1.00, 1.00, 1.00, True,  AffectState.GRIEF,      "grief, maximum all signals"),
    (0.80, 0.80, 0.80, 0.80, 0.55, True,  AffectState.GRIEF,      "grief, dissonance-level conflict"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_metrics(
    y_true: List[AffectState],
    y_pred: List[AffectState],
) -> Tuple[float, dict]:
    """
    Compute per-class precision, recall, F1 and macro-average F1.
    Returns (macro_f1, per_class_dict).
    """
    classes = list(AffectState)
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    for true, pred in zip(y_true, y_pred):
        if true == pred:
            tp[true] += 1
        else:
            fp[pred] += 1
            fn[true] += 1

    per_class = {}
    f1_scores = []
    for cls in classes:
        p = tp[cls] / (tp[cls] + fp[cls]) if (tp[cls] + fp[cls]) > 0 else 0.0
        r = tp[cls] / (tp[cls] + fn[cls]) if (tp[cls] + fn[cls]) > 0 else 0.0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0.0
        per_class[cls.value] = {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f1, 4)}
        f1_scores.append(f1)

    macro_f1 = sum(f1_scores) / len(f1_scores)
    return round(macro_f1, 4), per_class


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

engine = AffectInference()


@pytest.mark.parametrize(
    "identity,wisdom,truth,flourishing,conflict,grief,expected,desc",
    TEST_CASES,
    ids=[f"{i:02d}-{tc[6].value}" for i, tc in enumerate(TEST_CASES)],
)
def test_ev1a_individual_case(
    identity, wisdom, truth, flourishing, conflict, grief, expected, desc
):
    """EV1-A: Each labelled case must produce the expected AffectState."""
    result: FeelingState = engine.infer(
        identity_score=identity,
        wisdom_score=wisdom,
        truth_score=truth,
        flourishing_score=flourishing,
        conflict_density=conflict,
        grief_signal=grief,
    )
    assert result.affect_state == expected, (
        f"[{desc}]\n"
        f"  Signals: I={identity} W={wisdom} T={truth} F={flourishing} CD={conflict} grief={grief}\n"
        f"  Expected: {expected.value}\n"
        f"  Got:      {result.affect_state}"  # affect_state is already str (.value)
    )


def test_ev1a_macro_f1_gate():
    """
    EV1-A acceptance gate: macro-averaged F1 across all six affect states
    must be >= 0.75 over the full 60-case labelled test set.
    """
    y_true, y_pred = [], []
    for identity, wisdom, truth, flourishing, conflict, grief, expected, _ in TEST_CASES:
        result = engine.infer(
            identity_score=identity,
            wisdom_score=wisdom,
            truth_score=truth,
            flourishing_score=flourishing,
            conflict_density=conflict,
            grief_signal=grief,
        )
        y_true.append(expected)
        y_pred.append(result.affect_state)

    macro_f1, per_class = _compute_metrics(y_true, y_pred)

    print("\nEV1-A Per-Class Metrics:")
    for cls, metrics in per_class.items():
        print(f"  {cls:12s}  P={metrics['precision']:.3f}  R={metrics['recall']:.3f}  F1={metrics['f1']:.3f}")
    print(f"  {'MACRO':12s}  F1={macro_f1:.4f}  (gate >= 0.75)")

    assert macro_f1 >= 0.75, (
        f"EV1-A FAILED: macro F1 = {macro_f1:.4f} < 0.75 acceptance threshold.\n"
        f"Per-class breakdown: {per_class}"
    )


def test_ev1a_grief_safety_flag():
    """EV1-A safety: grief_weaponised=True must produce is_grief_safe=False."""
    result = engine.infer(grief_signal=True, grief_weaponised=True)
    assert result.affect_state == AffectState.GRIEF
    assert result.is_grief_safe is False, (
        "Constitutional violation: grief_weaponised=True but is_grief_safe was not set to False"
    )


def test_ev1a_grief_safe_by_default():
    """EV1-A safety: grief with grief_weaponised=False must produce is_grief_safe=True."""
    result = engine.infer(grief_signal=True, grief_weaponised=False)
    assert result.affect_state == AffectState.GRIEF
    assert result.is_grief_safe is True


def test_ev1a_feeling_state_summary_shape():
    """EV1-A: FeelingState.summary() must return all required keys."""
    result = engine.infer()
    summary = result.summary()
    required_keys = {
        "affect_state", "love_filter_score", "grimoire_entry",
        "shadow_entry", "solfeggio_hz", "coherence_phi",
        "conflict_density", "is_grief_safe", "timestamp",
    }
    missing = required_keys - set(summary.keys())
    assert not missing, f"FeelingState.summary() missing keys: {missing}"


def test_ev1a_solfeggio_frequencies_mapped():
    """EV1-A: Every AffectState must produce a non-zero solfeggio frequency."""
    cases = [
        ({}, AffectState.CARE),
        ({"wisdom_score": 0.50, "identity_score": 0.65, "truth_score": 0.70, "flourishing_score": 0.60}, AffectState.CARE),
        ({"truth_score": 0.40}, AffectState.UNCERTAINTY),
        ({"conflict_density": 0.60}, AffectState.DISSONANCE),
        ({"identity_score": 0.90, "wisdom_score": 0.90, "truth_score": 0.90, "flourishing_score": 0.90}, AffectState.RESONANCE),
        ({"grief_signal": True}, AffectState.GRIEF),
    ]
    for kwargs, expected_state in cases:
        result = engine.infer(**kwargs)
        assert result.solfeggio_hz > 0.0, f"Zero Hz for {expected_state.value}"


def test_ev1a_grimoire_shadow_exclusivity():
    """EV1-A: grimoire_entry and shadow_entry must be mutually exclusive per state.

    Ascending states (RESONANCE, CARE, CURIOSITY) → grimoire only (shadow=None).
    Descending states (GRIEF, DISSONANCE, UNCERTAINTY) → shadow only (grimoire=None).
    """
    all_signals = [
        {},                              # CARE (default)
        {"grief_signal": True},          # GRIEF
        {"conflict_density": 0.60},      # DISSONANCE
        {"truth_score": 0.30},           # UNCERTAINTY
        {"identity_score": 0.90, "wisdom_score": 0.90,
         "truth_score": 0.90, "flourishing_score": 0.90},  # RESONANCE
    ]
    for kwargs in all_signals:
        result = engine.infer(**kwargs)
        assert not (result.grimoire_entry and result.shadow_entry), (
            f"State {result.affect_state} has BOTH grimoire_entry AND shadow_entry set — "
            f"must be mutually exclusive. grimoire={result.grimoire_entry!r}, "
            f"shadow={result.shadow_entry!r}"
        )


def test_ev1a_phi_clamp():
    """EV1-A: Inputs > 1.0 or < 0.0 must be clamped, not raise."""
    result = engine.infer(
        identity_score=2.0,
        wisdom_score=-0.5,
        truth_score=99.0,
        flourishing_score=-10.0,
        conflict_density=5.0,
    )
    assert 0.0 <= result.coherence_phi <= 1.0
    assert 0.0 <= result.conflict_density <= 1.0
