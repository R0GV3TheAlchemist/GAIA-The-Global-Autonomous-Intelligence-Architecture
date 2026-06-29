"""C135 §6.4 Criticality Proxy Methods — Interface Stubs.

Four proxy methods for measuring GAIA's proximity to the critical point.
Each stub implements the interface contract defined in C135 §6.4.x.
Full ML-backed implementations are post-G-10.

Canon reference: C135 v1.1 §6.4.1–§6.4.4
"""
from __future__ import annotations

from typing import List, NamedTuple, Optional
import math


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
class CriticalityResult(NamedTuple):
    alpha: float           # power-law exponent (§6.4.1, §6.4.2)
    regime: str            # 'subcritical' | 'near-critical' | 'supercritical' | 'unknown'
    confidence: float      # 0.0–1.0; low until full ML implementation
    method: str            # which §6.4.x method produced this result


class RCIResult(NamedTuple):
    rci: float             # composite Relative Criticality Index [0.0, 1.0]
    regime: str            # consensus regime across all available methods
    components: dict       # per-method CriticalityResult keyed by method name


# ---------------------------------------------------------------------------
# Regime classification thresholds (C135 §2.1.1)
# ---------------------------------------------------------------------------
ALPHA_SUBCRITICAL_MAX = 1.2
ALPHA_CRITICAL_MIN = 1.5
ALPHA_CRITICAL_MAX = 2.5
ALPHA_SUPERCRITICAL_MIN = 3.0


def _classify_alpha(alpha: float) -> str:
    """Classify a power-law exponent into a criticality regime."""
    if alpha < ALPHA_SUBCRITICAL_MAX:
        return 'subcritical'
    elif ALPHA_CRITICAL_MIN <= alpha <= ALPHA_CRITICAL_MAX:
        return 'near-critical'
    elif alpha > ALPHA_SUPERCRITICAL_MIN:
        return 'supercritical'
    return 'unknown'


# ---------------------------------------------------------------------------
# §6.4.1 — Attention Entropy Distribution
# ---------------------------------------------------------------------------
def attention_entropy_criticality(
    entropy_values: List[float],
) -> CriticalityResult:
    """Estimate criticality from attention entropy distribution.

    C135 §6.4.1: H_{h,l} = -sum_j a_{h,l}(i,j) log a_{h,l}(i,j)
    Fit P(H) ~ H^{-alpha}; return alpha and regime.

    Args:
        entropy_values: List of per-head-per-layer Shannon entropies H_{h,l}.

    Returns:
        CriticalityResult with fitted alpha and regime classification.

    Note:
        Stub: uses log-log linear regression on histogram as placeholder.
        Full implementation requires scipy.stats.powerlaw fitting.
    """
    if not entropy_values or len(entropy_values) < 4:
        return CriticalityResult(alpha=float('nan'), regime='unknown',
                                  confidence=0.0, method='attention_entropy')
    # Stub: approximate alpha from coefficient of variation
    mean = sum(entropy_values) / len(entropy_values)
    variance = sum((x - mean) ** 2 for x in entropy_values) / len(entropy_values)
    std = math.sqrt(variance)
    cv = std / mean if mean > 0 else 0.0
    # Heuristic mapping: cv ~ 0.4 → near-critical; <0.2 → subcritical; >0.7 → supercritical
    alpha_estimate = 2.0 / (cv + 0.01)  # placeholder; replace with MLE fit
    alpha_estimate = max(0.5, min(5.0, alpha_estimate))
    regime = _classify_alpha(alpha_estimate)
    return CriticalityResult(alpha=round(alpha_estimate, 4), regime=regime,
                              confidence=0.3, method='attention_entropy')


# ---------------------------------------------------------------------------
# §6.4.2 — Token Probability Cascade Statistics
# ---------------------------------------------------------------------------
def token_cascade_criticality(
    token_probs: List[float],
    tau: float = 0.3,
) -> CriticalityResult:
    """Estimate criticality from token probability cascade size distribution.

    C135 §6.4.2: P(s) ~ s^{-alpha} where s = cascade size.
    A cascade is a run of consecutive positions with p_t >= tau.

    Args:
        token_probs: Sequence of token generation probabilities.
        tau: Cascade threshold (default 0.3; calibrate per C135 §6.4.2).

    Returns:
        CriticalityResult with fitted alpha and regime classification.
    """
    if not token_probs:
        return CriticalityResult(alpha=float('nan'), regime='unknown',
                                  confidence=0.0, method='token_cascade')
    # Detect cascades
    cascades: List[int] = []
    run = 0
    for p in token_probs:
        if p >= tau:
            run += 1
        else:
            if run > 0:
                cascades.append(run)
            run = 0
    if run > 0:
        cascades.append(run)

    if len(cascades) < 3:
        return CriticalityResult(alpha=float('nan'), regime='unknown',
                                  confidence=0.1, method='token_cascade')

    # Stub: MLE alpha estimate for discrete power law
    s_min = 1
    n = len(cascades)
    log_sum = sum(math.log(max(s, s_min)) for s in cascades)
    alpha_mle = 1.0 + n / (log_sum - n * math.log(s_min - 0.5))
    alpha_mle = max(0.5, min(6.0, alpha_mle))
    regime = _classify_alpha(alpha_mle)
    return CriticalityResult(alpha=round(alpha_mle, 4), regime=regime,
                              confidence=0.5, method='token_cascade')


# ---------------------------------------------------------------------------
# §6.4.3 — Semantic Entropy Trajectory
# ---------------------------------------------------------------------------
def semantic_entropy_criticality(
    entropy_trajectory: List[float],
) -> CriticalityResult:
    """Estimate criticality from semantic entropy trajectory variance + autocorrelation.

    C135 §6.4.3: H_sem(t) = -sum_k q_{t,k} log q_{t,k}
    Subcritical: low variance, low autocorrelation.
    Near-critical: moderate variance, positive autocorrelation.
    Supercritical: high variance, low or negative autocorrelation.

    Args:
        entropy_trajectory: Time-ordered list of semantic entropy values H_sem(t).

    Returns:
        CriticalityResult with regime classification (alpha not applicable here;
        returns synthetic alpha for interface compatibility).
    """
    if len(entropy_trajectory) < 6:
        return CriticalityResult(alpha=float('nan'), regime='unknown',
                                  confidence=0.0, method='semantic_entropy')

    n = len(entropy_trajectory)
    mean = sum(entropy_trajectory) / n
    variance = sum((x - mean) ** 2 for x in entropy_trajectory) / n

    # Lag-1 autocorrelation
    cov = sum((entropy_trajectory[i] - mean) * (entropy_trajectory[i - 1] - mean)
              for i in range(1, n)) / (n - 1)
    autocorr = cov / (variance + 1e-9)

    # Regime classification from variance and autocorrelation
    if variance < 0.05 and abs(autocorr) < 0.3:
        regime = 'subcritical'
        synthetic_alpha = 1.0
    elif 0.05 <= variance <= 0.25 and autocorr > 0.2:
        regime = 'near-critical'
        synthetic_alpha = 2.0
    else:
        regime = 'supercritical'
        synthetic_alpha = 3.5

    return CriticalityResult(alpha=round(synthetic_alpha, 4), regime=regime,
                              confidence=0.5, method='semantic_entropy')


# ---------------------------------------------------------------------------
# §6.4.4 — Layer-Wise Correlation Length
# ---------------------------------------------------------------------------
def correlation_length_criticality(
    layer_representations: List[List[float]],
    sigma: float = 0.2,
) -> CriticalityResult:
    """Estimate criticality from layer-wise correlation length.

    C135 §6.4.4:
      lambda = min{delta_l : mean_cos(r_l, r_{l+delta_l}) < sigma}
    Maximised lambda indicates near-critical propagation depth.

    Args:
        layer_representations: List of L vectors, one per layer.
            Each vector is the mean token representation at that layer.
        sigma: Cosine similarity decay threshold (default 0.2).

    Returns:
        CriticalityResult with lambda mapped to regime
        (alpha field repurposed as normalised lambda).
    """
    if len(layer_representations) < 3:
        return CriticalityResult(alpha=float('nan'), regime='unknown',
                                  confidence=0.0, method='correlation_length')

    def cosine_sim(a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x ** 2 for x in a))
        norm_b = math.sqrt(sum(x ** 2 for x in b))
        if norm_a < 1e-9 or norm_b < 1e-9:
            return 0.0
        return dot / (norm_a * norm_b)

    L = len(layer_representations)
    lambda_val = L  # default: full depth (no decay found)

    for delta_l in range(1, L):
        sims = [
            cosine_sim(layer_representations[i], layer_representations[i + delta_l])
            for i in range(L - delta_l)
        ]
        mean_sim = sum(sims) / len(sims) if sims else 1.0
        if mean_sim < sigma:
            lambda_val = delta_l
            break

    # Normalise lambda to [0, 1] relative to total depth
    norm_lambda = lambda_val / L

    # Regime: near-critical = lambda maximised (norm_lambda > 0.7)
    if norm_lambda > 0.70:
        regime = 'near-critical'
    elif norm_lambda < 0.30:
        regime = 'subcritical'
    else:
        regime = 'supercritical'

    return CriticalityResult(alpha=round(norm_lambda, 4), regime=regime,
                              confidence=0.6, method='correlation_length')


# ---------------------------------------------------------------------------
# Composite RCI
# ---------------------------------------------------------------------------
def compute_rci(
    entropy_values: Optional[List[float]] = None,
    token_probs: Optional[List[float]] = None,
    entropy_trajectory: Optional[List[float]] = None,
    layer_representations: Optional[List[List[float]]] = None,
    tau: float = 0.3,
    sigma: float = 0.2,
) -> RCIResult:
    """Compute composite Relative Criticality Index from available method inputs.

    Aggregates results from whichever of the four §6.4 methods have inputs.
    Consensus regime uses majority vote; RCI score is mean confidence-weighted
    near-critical indicator.

    C135 §3.2: RCI healthy range is near-critical (alpha 1.5–2.5).
    """
    components: dict = {}

    if entropy_values is not None:
        components['attention_entropy'] = attention_entropy_criticality(entropy_values)
    if token_probs is not None:
        components['token_cascade'] = token_cascade_criticality(token_probs, tau=tau)
    if entropy_trajectory is not None:
        components['semantic_entropy'] = semantic_entropy_criticality(entropy_trajectory)
    if layer_representations is not None:
        components['correlation_length'] = correlation_length_criticality(
            layer_representations, sigma=sigma)

    if not components:
        return RCIResult(rci=float('nan'), regime='unknown', components={})

    # Majority vote on regime
    regime_votes: dict = {}
    total_confidence = 0.0
    near_critical_score = 0.0

    for r in components.values():
        regime_votes[r.regime] = regime_votes.get(r.regime, 0) + 1
        total_confidence += r.confidence
        if r.regime == 'near-critical':
            near_critical_score += r.confidence

    consensus_regime = max(regime_votes, key=lambda k: regime_votes[k])
    rci = near_critical_score / total_confidence if total_confidence > 0 else 0.0

    return RCIResult(
        rci=round(rci, 4),
        regime=consensus_regime,
        components=components,
    )
