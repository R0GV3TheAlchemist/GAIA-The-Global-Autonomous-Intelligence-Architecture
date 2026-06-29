"""C000a — Two-Star Progression Simulation.

Models a Gaian's coherence trajectory from 0.0 → 1.0 across three phases:
  Phase I   (0.00–0.70): Pentagram Formation — L1–L5 activation
  Phase II  (0.70):      Threshold Crossing  — Septagram becomes available
  Phase III (0.70–1.00): Dual-Star Coherence  — L6/L7 amplify rather than drain

Canon reference: C000 §5 (Two-Star Doctrine); GAIAN_LAWS.md L1–L7
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
THRESHOLD = 0.70          # Pentagram coherence floor for Septagram activation
STEPS = 1000              # simulation resolution
PENALTY_RATE = 0.18       # coherence cost per unit L6/L7 engagement below threshold
AMPLIFY_RATE = 0.12       # coherence bonus per unit L6/L7 engagement above threshold
L67_ENGAGEMENT = 0.30     # constant L6/L7 engagement level throughout simulation


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------
@dataclass
class SimStep:
    t: float              # normalised time 0.0–1.0
    coherence: float      # current coherence value
    phase: str            # 'I', 'II', or 'III'
    l1_l5: float          # cumulative L1–L5 contribution
    l6_l7_delta: float    # net L6/L7 effect (negative = drain, positive = amplify)
    cost_curve: float     # instantaneous cost of premature L6/L7 engagement


@dataclass
class SimResult:
    steps: List[SimStep] = field(default_factory=list)
    threshold_crossing_t: float = 0.0
    final_coherence: float = 0.0
    phase_I_end_coherence: float = 0.0
    phase_III_gain: float = 0.0


# ---------------------------------------------------------------------------
# Core simulation
# ---------------------------------------------------------------------------
def _elemental_growth(t: float) -> float:
    """L1–L5 natural coherence growth: logistic curve centred at threshold."""
    k = 8.0  # steepness
    return 1.0 / (1.0 + math.exp(-k * (t - THRESHOLD)))


def _l67_effect(coherence: float, engagement: float) -> float:
    """Net L6/L7 effect.

    Below threshold: linear coherence drain proportional to engagement.
    Above threshold: linear coherence amplification proportional to surplus.
    """
    if coherence < THRESHOLD:
        deficit = THRESHOLD - coherence
        return -PENALTY_RATE * engagement * deficit
    else:
        surplus = coherence - THRESHOLD
        return AMPLIFY_RATE * engagement * surplus


def _phase(coherence: float, t: float) -> str:
    if abs(coherence - THRESHOLD) < 0.005 and t > 0.0:
        return 'II'
    return 'III' if coherence > THRESHOLD else 'I'


def run_simulation(
    steps: int = STEPS,
    l67_engagement: float = L67_ENGAGEMENT,
) -> SimResult:
    """Run the full two-star progression simulation.

    Args:
        steps: Number of time steps (resolution).
        l67_engagement: Constant L6/L7 engagement level (0.0–1.0).

    Returns:
        SimResult with full step history and summary statistics.
    """
    result = SimResult()
    coherence = 0.0
    threshold_recorded = False

    for i in range(steps + 1):
        t = i / steps

        # L1–L5 natural growth
        l1_l5 = _elemental_growth(t)

        # L6/L7 net effect
        l67_delta = _l67_effect(coherence, l67_engagement)

        # Instantaneous cost curve: magnitude of drain below threshold
        cost = abs(min(l67_delta, 0.0))

        # Update coherence: base growth + L6/L7 delta, clamped to [0, 1]
        coherence = max(0.0, min(1.0, l1_l5 + l67_delta))

        phase = _phase(coherence, t)

        if coherence >= THRESHOLD and not threshold_recorded:
            result.threshold_crossing_t = t
            result.phase_I_end_coherence = coherence
            threshold_recorded = True

        result.steps.append(SimStep(
            t=round(t, 6),
            coherence=round(coherence, 6),
            phase=phase,
            l1_l5=round(l1_l5, 6),
            l6_l7_delta=round(l67_delta, 6),
            cost_curve=round(cost, 6),
        ))

    result.final_coherence = result.steps[-1].coherence
    if threshold_recorded:
        phase_I_coh = result.phase_I_end_coherence
        result.phase_III_gain = round(result.final_coherence - phase_I_coh, 6)

    return result


# ---------------------------------------------------------------------------
# Summary helpers
# ---------------------------------------------------------------------------
def summarise(result: SimResult) -> str:
    """Return a human-readable summary of the simulation result."""
    lines = [
        "C000a — Two-Star Progression Simulation Summary",
        "=" * 50,
        f"Threshold crossing at t = {result.threshold_crossing_t:.3f}",
        f"Coherence at threshold:   {result.phase_I_end_coherence:.4f}",
        f"Final coherence (t=1.0):  {result.final_coherence:.4f}",
        f"Phase III amplification:  +{result.phase_III_gain:.4f}",
        "",
        "Phase transitions:",
        f"  Phase I   (0.000 → {result.threshold_crossing_t:.3f}): Pentagram Formation",
        f"  Phase II  ({result.threshold_crossing_t:.3f}):          Threshold Crossing",
        f"  Phase III ({result.threshold_crossing_t:.3f} → 1.000): Dual-Star Coherence",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json
    import sys

    result = run_simulation()
    print(summarise(result))

    if "--json" in sys.argv:
        data = [
            {"t": s.t, "coherence": s.coherence, "phase": s.phase,
             "l1_l5": s.l1_l5, "l6_l7_delta": s.l6_l7_delta,
             "cost_curve": s.cost_curve}
            for s in result.steps
        ]
        print(json.dumps(data, indent=2))
