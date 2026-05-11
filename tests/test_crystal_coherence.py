"""
test_crystal_coherence.py
=========================
Unit tests for the Crystal Core coherence formula.

Covers:
  - Each component derivation in isolation (components.py)
  - Composite Ψ formula (coherence.py)
  - Neutral baseline: all components 0.5 → Ψ == 0.5
  - Crystalline ceiling: fully coherent mock → Ψ > 0.85
  - Fractured floor: max volatility + zero stage scores → Ψ < 0.30
  - Shadow Engine unavailable → E defaults to 0.5, no exception
  - Schumann low confidence → H defaults to 0.5, no exception
  - Output always clamped to [0.0, 1.0]
"""

from __future__ import annotations

import pytest

from crystal.components import (
    derive_affect_coherence,
    derive_stage_coherence,
    derive_shadow_integration,
    derive_schumann_alignment,
)
from crystal.coherence import compute_coherence


# ── Helpers ───────────────────────────────────────────────────────────────────

def _affect(arc_stability=0.5, valence_trend=0.0, volatility=0.0):
    return {
        "arc_stability": arc_stability,
        "valence_trend": valence_trend,
        "volatility": volatility,
    }


def _stage(marker_scores=None):
    if marker_scores is None:
        marker_scores = [50.0] * 6
    return {"marker_scores": marker_scores}


def _shadow(integration_progress=0.5, shadow_intensity=0.0):
    return {
        "integration_progress": integration_progress,
        "shadow_intensity": shadow_intensity,
    }


def _schumann(alignment_score=0.5, confidence=0.8):
    return {
        "alignment_score": alignment_score,
        "confidence": confidence,
    }


# ── Affect Coherence ──────────────────────────────────────────────────────────

class TestDeriveAffectCoherence:
    def test_neutral_baseline(self):
        """arc_stability=0.5, valence_trend=0.0, volatility=0.0 → A ≈ 0.667."""
        # valence_trend=0 maps to 0.5; volatility=0 → (1-vol)=1.0
        # A = (0.5 + 0.5 + 1.0) / 3 = 2.0/3 ≈ 0.667
        a = derive_affect_coherence(_affect())
        assert 0.60 < a < 0.75

    def test_perfect_coherence(self):
        """Best possible affect inputs → A close to 1.0."""
        a = derive_affect_coherence(_affect(arc_stability=1.0, valence_trend=1.0, volatility=0.0))
        assert a > 0.90

    def test_worst_coherence(self):
        """Worst possible affect inputs → A close to 0.0."""
        a = derive_affect_coherence(_affect(arc_stability=0.0, valence_trend=-1.0, volatility=1.0))
        assert a < 0.20

    def test_output_clamped(self):
        """Output is always in [0.0, 1.0] even with extreme inputs."""
        a = derive_affect_coherence(_affect(arc_stability=2.0, valence_trend=5.0, volatility=-1.0))
        assert 0.0 <= a <= 1.0

    def test_high_volatility_penalises(self):
        """High volatility should lower coherence vs. zero volatility."""
        a_calm = derive_affect_coherence(_affect(arc_stability=0.7, valence_trend=0.5, volatility=0.0))
        a_volatile = derive_affect_coherence(_affect(arc_stability=0.7, valence_trend=0.5, volatility=0.9))
        assert a_volatile < a_calm


# ── Stage Coherence ───────────────────────────────────────────────────────────

class TestDeriveStageCoherence:
    def test_neutral_baseline(self):
        """Six markers all at 50/100 → S == 0.5."""
        s = derive_stage_coherence(_stage([50.0] * 6))
        assert abs(s - 0.5) < 1e-6

    def test_all_zero(self):
        """All markers at 0 → S == 0.0."""
        s = derive_stage_coherence(_stage([0.0] * 6))
        assert abs(s - 0.0) < 1e-6

    def test_all_max(self):
        """All markers at 100 → S == 1.0."""
        s = derive_stage_coherence(_stage([100.0] * 6))
        assert abs(s - 1.0) < 1e-6

    def test_mixed_markers(self):
        """Mixed marker scores produce correct mean."""
        scores = [0.0, 25.0, 50.0, 75.0, 100.0, 50.0]  # mean = 300/6 = 50 → 0.5
        s = derive_stage_coherence(_stage(scores))
        assert abs(s - 0.5) < 1e-6

    def test_output_clamped(self):
        """Output clamped even if scores exceed 100."""
        s = derive_stage_coherence(_stage([200.0] * 6))
        assert 0.0 <= s <= 1.0


# ── Shadow Integration ────────────────────────────────────────────────────────

class TestDeriveShadowIntegration:
    def test_fully_integrated_no_intensity(self):
        """progress=1.0, intensity=0.0 → E == 1.0."""
        e = derive_shadow_integration(_shadow(1.0, 0.0))
        assert abs(e - 1.0) < 1e-6

    def test_unintegrated_max_intensity(self):
        """progress=0.0, intensity=1.0 → E == 0.0."""
        e = derive_shadow_integration(_shadow(0.0, 1.0))
        assert abs(e - 0.0) < 1e-6

    def test_neutral_default(self):
        """progress=0.5, intensity=0.0 → E == 0.5."""
        e = derive_shadow_integration(_shadow(0.5, 0.0))
        assert abs(e - 0.5) < 1e-6

    def test_unavailable_shadow_defaults_to_half(self):
        """When Shadow Engine is unavailable (None input), E defaults to 0.5."""
        e = derive_shadow_integration(None)
        assert abs(e - 0.5) < 1e-6

    def test_output_clamped(self):
        e = derive_shadow_integration(_shadow(1.5, -0.5))
        assert 0.0 <= e <= 1.0


# ── Schumann Alignment ────────────────────────────────────────────────────────

class TestDeriveSchumannAlignment:
    def test_high_confidence_uses_score(self):
        """confidence >= 0.4 → H == alignment_score."""
        h = derive_schumann_alignment(_schumann(alignment_score=0.8, confidence=0.9))
        assert abs(h - 0.8) < 1e-6

    def test_low_confidence_defaults_to_half(self):
        """confidence < 0.4 → H == 0.5 regardless of alignment_score."""
        h = derive_schumann_alignment(_schumann(alignment_score=0.1, confidence=0.1))
        assert abs(h - 0.5) < 1e-6

    def test_exact_confidence_boundary(self):
        """confidence == 0.4 is ON the boundary → uses score."""
        h = derive_schumann_alignment(_schumann(alignment_score=0.7, confidence=0.4))
        assert abs(h - 0.7) < 1e-6

    def test_unavailable_schumann_defaults_to_half(self):
        """None input (engine unavailable) → H defaults to 0.5."""
        h = derive_schumann_alignment(None)
        assert abs(h - 0.5) < 1e-6


# ── Composite Coherence Ψ ─────────────────────────────────────────────────────

class TestComputeCoherence:
    def test_all_components_half_gives_half(self):
        """
        Spec §13 acceptance criterion:
        compute_coherence() returns exactly 0.5 when all four components are 0.5.
        """
        psi = compute_coherence(
            affect_coherence=0.5,
            stage_coherence=0.5,
            shadow_integration=0.5,
            schumann_alignment=0.5,
        )
        assert abs(psi - 0.5) < 1e-6

    def test_crystalline_on_full_coherence(self):
        """
        Spec §13: compute_coherence() returns > 0.85 (Crystalline) on a
        fully coherent mock input.
        """
        psi = compute_coherence(
            affect_coherence=1.0,
            stage_coherence=1.0,
            shadow_integration=1.0,
            schumann_alignment=1.0,
        )
        assert psi > 0.85

    def test_fractured_on_worst_input(self):
        """
        Spec §13: compute_coherence() returns < 0.30 (Fractured) when
        affect volatility is max and stage scores are all 0.
        """
        psi = compute_coherence(
            affect_coherence=0.0,
            stage_coherence=0.0,
            shadow_integration=0.0,
            schumann_alignment=0.0,
        )
        assert psi < 0.30

    def test_weights_sum_to_one(self):
        """
        Sanity: w_A + w_S + w_E + w_H = 1.0.
        Verified indirectly — if one component is 1.0 and all others 0.0
        the result should equal that component's weight.
        """
        # Weight for Affect = 0.35
        psi_a = compute_coherence(1.0, 0.0, 0.0, 0.0)
        assert abs(psi_a - 0.35) < 1e-6

        # Weight for Stage = 0.30
        psi_s = compute_coherence(0.0, 1.0, 0.0, 0.0)
        assert abs(psi_s - 0.30) < 1e-6

        # Weight for Shadow = 0.20
        psi_e = compute_coherence(0.0, 0.0, 1.0, 0.0)
        assert abs(psi_e - 0.20) < 1e-6

        # Weight for Schumann = 0.15
        psi_h = compute_coherence(0.0, 0.0, 0.0, 1.0)
        assert abs(psi_h - 0.15) < 1e-6

    def test_output_always_clamped(self):
        """Result is always in [0.0, 1.0] even with out-of-range inputs."""
        psi = compute_coherence(2.0, -1.0, 3.0, -0.5)
        assert 0.0 <= psi <= 1.0

    def test_shadow_unavailable_defaults_gracefully(self):
        """
        Spec §13: Shadow Engine unavailable → E = 0.5, no exception.
        Passing shadow_integration=0.5 explicitly models the default.
        """
        try:
            psi = compute_coherence(
                affect_coherence=0.7,
                stage_coherence=0.6,
                shadow_integration=0.5,  # default when #67 unavailable
                schumann_alignment=0.8,
            )
        except Exception as exc:
            pytest.fail(f"Unexpected exception with shadow default: {exc}")
        assert 0.0 <= psi <= 1.0

    def test_schumann_unavailable_defaults_gracefully(self):
        """
        Spec §13: Schumann stream unavailable → H = 0.5, no exception.
        """
        try:
            psi = compute_coherence(
                affect_coherence=0.6,
                stage_coherence=0.6,
                shadow_integration=0.5,
                schumann_alignment=0.5,  # default when confidence < 0.4
            )
        except Exception as exc:
            pytest.fail(f"Unexpected exception with schumann default: {exc}")
        assert 0.0 <= psi <= 1.0
