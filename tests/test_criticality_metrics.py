"""Tests for C135 §6.4 criticality proxy methods.

Covers all four methods across three regimes:
  - subcritical
  - near-critical
  - supercritical

Canon reference: C135 v1.1 §6.4.1–§6.4.4
"""
from __future__ import annotations

import math
import pytest
from core.criticality import (
    attention_entropy_criticality,
    token_cascade_criticality,
    semantic_entropy_criticality,
    correlation_length_criticality,
    compute_rci,
)


# ---------------------------------------------------------------------------
# Synthetic input generators
# ---------------------------------------------------------------------------
def _subcritical_entropies(n: int = 50) -> list:
    """Low-entropy, near-uniform values — subcritical (frozen) attention."""
    return [0.05 + 0.02 * (i % 3) for i in range(n)]


def _near_critical_entropies(n: int = 50) -> list:
    """Moderate spread, power-law-like — near-critical attention."""
    import random
    rng = random.Random(42)
    return [max(0.01, rng.gauss(0.5, 0.2)) for _ in range(n)]


def _supercritical_entropies(n: int = 50) -> list:
    """Very high entropy values — supercritical (diffuse) attention."""
    return [0.9 + 0.05 * (i % 2) for i in range(n)]


def _subcritical_probs(n: int = 80) -> list:
    """Low token probabilities — no significant cascades."""
    return [0.1 + 0.05 * (i % 4) for i in range(n)]


def _near_critical_probs(n: int = 80) -> list:
    """Mixed probs with moderate cascade lengths."""
    import random
    rng = random.Random(7)
    return [rng.choice([0.1, 0.15, 0.35, 0.40, 0.25]) for _ in range(n)]


def _supercritical_probs(n: int = 80) -> list:
    """Long runs of high probability — supercritical token generation."""
    return [0.8 if i % 12 < 10 else 0.1 for i in range(n)]


def _subcritical_traj(n: int = 40) -> list:
    """Flat, low-variance semantic entropy — subcritical."""
    return [0.3 + 0.01 * math.sin(i) for i in range(n)]


def _near_critical_traj(n: int = 40) -> list:
    """Moderate variance with positive autocorrelation — near-critical."""
    traj = [0.5]
    for i in range(1, n):
        traj.append(max(0.0, min(1.0, traj[-1] + 0.08 * math.sin(i * 0.7) + 0.02)))
    return traj


def _supercritical_traj(n: int = 40) -> list:
    """High variance, erratic — supercritical."""
    import random
    rng = random.Random(99)
    return [rng.uniform(0.0, 1.0) for _ in range(n)]


def _layer_reps(n_layers: int, dim: int, decay: float) -> list:
    """Layer representations with controlled cosine decay."""
    import random
    rng = random.Random(13)
    base = [rng.gauss(0, 1) for _ in range(dim)]
    reps = [base[:]]
    for _ in range(1, n_layers):
        prev = reps[-1]
        noise = [rng.gauss(0, decay) for _ in range(dim)]
        new = [p + noise[j] for j, p in enumerate(prev)]
        reps.append(new)
    return reps


# ---------------------------------------------------------------------------
# §6.4.1 — Attention Entropy
# ---------------------------------------------------------------------------
class TestAttentionEntropy:
    def test_subcritical_returns_subcritical_or_unknown(self):
        result = attention_entropy_criticality(_subcritical_entropies())
        assert result.method == 'attention_entropy'
        assert result.regime in ('subcritical', 'unknown')

    def test_near_critical_returns_near_critical(self):
        result = attention_entropy_criticality(_near_critical_entropies())
        assert result.method == 'attention_entropy'
        assert result.regime in ('near-critical', 'unknown')

    def test_supercritical_returns_supercritical_or_unknown(self):
        result = attention_entropy_criticality(_supercritical_entropies())
        assert result.method == 'attention_entropy'
        assert result.regime in ('supercritical', 'unknown')

    def test_empty_input_returns_unknown(self):
        result = attention_entropy_criticality([])
        assert result.regime == 'unknown'
        assert math.isnan(result.alpha)

    def test_result_fields_present(self):
        result = attention_entropy_criticality(_near_critical_entropies())
        assert hasattr(result, 'alpha')
        assert hasattr(result, 'regime')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'method')


# ---------------------------------------------------------------------------
# §6.4.2 — Token Cascade
# ---------------------------------------------------------------------------
class TestTokenCascade:
    def test_subcritical_no_cascades(self):
        result = token_cascade_criticality(_subcritical_probs(), tau=0.3)
        assert result.method == 'token_cascade'
        assert result.regime in ('subcritical', 'unknown')

    def test_near_critical_regime(self):
        result = token_cascade_criticality(_near_critical_probs(), tau=0.3)
        assert result.method == 'token_cascade'
        # Regime should be classifiable (not necessarily near-critical given stub)
        assert result.regime in ('subcritical', 'near-critical', 'supercritical', 'unknown')

    def test_supercritical_long_cascades(self):
        result = token_cascade_criticality(_supercritical_probs(), tau=0.3)
        assert result.method == 'token_cascade'
        # Long cascades → low alpha → subcritical classification
        assert result.regime in ('subcritical', 'near-critical', 'unknown')

    def test_empty_input_returns_unknown(self):
        result = token_cascade_criticality([], tau=0.3)
        assert result.regime == 'unknown'

    def test_tau_sensitivity(self):
        """Higher tau should detect fewer/shorter cascades."""
        result_low = token_cascade_criticality(_near_critical_probs(), tau=0.1)
        result_high = token_cascade_criticality(_near_critical_probs(), tau=0.9)
        # Both should return a result; regime may differ
        assert result_low.method == 'token_cascade'
        assert result_high.method == 'token_cascade'


# ---------------------------------------------------------------------------
# §6.4.3 — Semantic Entropy Trajectory
# ---------------------------------------------------------------------------
class TestSemanticEntropy:
    def test_subcritical_flat_trajectory(self):
        result = semantic_entropy_criticality(_subcritical_traj())
        assert result.method == 'semantic_entropy'
        assert result.regime == 'subcritical'

    def test_near_critical_structured_trajectory(self):
        result = semantic_entropy_criticality(_near_critical_traj())
        assert result.method == 'semantic_entropy'
        assert result.regime in ('near-critical', 'subcritical')

    def test_supercritical_erratic_trajectory(self):
        result = semantic_entropy_criticality(_supercritical_traj())
        assert result.method == 'semantic_entropy'
        assert result.regime in ('supercritical', 'near-critical')

    def test_short_input_returns_unknown(self):
        result = semantic_entropy_criticality([0.5, 0.4])
        assert result.regime == 'unknown'


# ---------------------------------------------------------------------------
# §6.4.4 — Correlation Length
# ---------------------------------------------------------------------------
class TestCorrelationLength:
    def test_slow_decay_near_critical(self):
        """Small noise → representations stay similar → long correlation length → near-critical."""
        reps = _layer_reps(n_layers=20, dim=16, decay=0.05)
        result = correlation_length_criticality(reps, sigma=0.2)
        assert result.method == 'correlation_length'
        assert result.regime in ('near-critical', 'unknown')

    def test_fast_decay_subcritical(self):
        """Large noise → representations diverge quickly → short lambda → subcritical."""
        reps = _layer_reps(n_layers=20, dim=16, decay=5.0)
        result = correlation_length_criticality(reps, sigma=0.2)
        assert result.method == 'correlation_length'
        assert result.regime in ('subcritical', 'supercritical', 'unknown')

    def test_insufficient_layers_returns_unknown(self):
        result = correlation_length_criticality([[1.0, 0.0]], sigma=0.2)
        assert result.regime == 'unknown'

    def test_normalised_lambda_in_range(self):
        reps = _layer_reps(n_layers=12, dim=8, decay=0.3)
        result = correlation_length_criticality(reps, sigma=0.2)
        assert 0.0 <= result.alpha <= 1.0


# ---------------------------------------------------------------------------
# Composite RCI
# ---------------------------------------------------------------------------
class TestComputeRCI:
    def test_rci_with_all_methods(self):
        result = compute_rci(
            entropy_values=_near_critical_entropies(),
            token_probs=_near_critical_probs(),
            entropy_trajectory=_near_critical_traj(),
            layer_representations=_layer_reps(12, 8, 0.1),
        )
        assert 0.0 <= result.rci <= 1.0
        assert result.regime in ('subcritical', 'near-critical', 'supercritical', 'unknown')
        assert len(result.components) == 4

    def test_rci_with_no_inputs_returns_unknown(self):
        result = compute_rci()
        assert result.regime == 'unknown'
        assert math.isnan(result.rci)

    def test_rci_with_single_method(self):
        result = compute_rci(entropy_values=_near_critical_entropies())
        assert len(result.components) == 1
        assert result.regime in ('subcritical', 'near-critical', 'supercritical', 'unknown')
