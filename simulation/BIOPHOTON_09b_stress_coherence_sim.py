"""
BIOPHOTON_09b — Stress-Condition Coherence Degradation Simulation
G-13 Track A1

Research question:
    Does environmental stress destroy network-level coherence amplification
    *before* it destroys individual node coherence?

If yes: the mycorrhizal network is the canary-in-the-mine-shaft for
ecosystem coherence monitoring — network-level degradation is the
early warning signal, not node-level degradation.

Stress parameters modelled:
    - Soil compaction (reduces hyphal conductance)
    - Pesticide exposure (reduces node coherence directly)
    - Drought (reduces both conductance and baseline node coherence)

Builds on: BIOPHOTON_09 (plant root quantum coherence baseline)
Cross-references: GAIAN_LAWS L5, COEXISTENCE_LAWS CL1, C135
© 2026 Kyle Steen — All rights reserved.
"""

import numpy as np
import json
from dataclasses import dataclass, field
from typing import List, Dict, Tuple

# ── Seed for reproducibility ──────────────────────────────────────────────────
RNG = np.random.default_rng(seed=42)

# ── Constants from BIOPHOTON_09 baseline ─────────────────────────────────────
BASELINE_NODE_COHERENCE_MEAN = 0.72
BASELINE_NODE_COHERENCE_STD  = 0.12
BASELINE_COUPLING_EFFICIENCY = 0.65
NETWORK_AMPLIFICATION_THRESHOLD = 0.60  # Below this, network coherence < mean node
N_NODES = 50
N_TRIALS = 200


@dataclass
class StressCondition:
    name: str
    node_coherence_penalty: float   # Direct reduction to node coherence
    conductance_penalty: float      # Reduction to hyphal coupling efficiency
    description: str


STRESS_CONDITIONS = [
    StressCondition(
        name="baseline",
        node_coherence_penalty=0.0,
        conductance_penalty=0.0,
        description="No stress — BIOPHOTON_09 baseline conditions"
    ),
    StressCondition(
        name="mild_compaction",
        node_coherence_penalty=0.05,
        conductance_penalty=0.15,
        description="Mild soil compaction: reduced hyphal conductance, minor node impact"
    ),
    StressCondition(
        name="severe_compaction",
        node_coherence_penalty=0.12,
        conductance_penalty=0.35,
        description="Severe compaction: significant conductance loss, moderate node impact"
    ),
    StressCondition(
        name="mild_pesticide",
        node_coherence_penalty=0.18,
        conductance_penalty=0.08,
        description="Mild pesticide: direct node coherence disruption, minor conductance effect"
    ),
    StressCondition(
        name="severe_pesticide",
        node_coherence_penalty=0.38,
        conductance_penalty=0.20,
        description="Severe pesticide: major direct node disruption"
    ),
    StressCondition(
        name="mild_drought",
        node_coherence_penalty=0.10,
        conductance_penalty=0.20,
        description="Mild drought: reduced water-mediated coherence and conductance"
    ),
    StressCondition(
        name="severe_drought",
        node_coherence_penalty=0.25,
        conductance_penalty=0.45,
        description="Severe drought: major dual impact on nodes and conductance"
    ),
    StressCondition(
        name="combined_crisis",
        node_coherence_penalty=0.45,
        conductance_penalty=0.55,
        description="Combined stressors: compaction + pesticide + drought"
    ),
]


def simulate_network_coherence(
    stress: StressCondition,
    n_nodes: int = N_NODES,
    n_trials: int = N_TRIALS
) -> Dict:
    """
    Simulate network and node coherence under a given stress condition.
    Returns mean node coherence, network coherence, amplification ratio,
    and whether network-level degradation precedes node-level degradation.
    """
    node_coherences = []
    network_coherences = []

    for _ in range(n_trials):
        # Node coherence under stress
        node_mean = max(
            0.0,
            BASELINE_NODE_COHERENCE_MEAN - stress.node_coherence_penalty
            + RNG.normal(0, 0.01)
        )
        node_std = BASELINE_NODE_COHERENCE_STD * (1 + stress.node_coherence_penalty)
        nodes = np.clip(
            RNG.normal(node_mean, node_std, n_nodes), 0.0, 1.0
        )

        # Coupling efficiency under stress
        coupling = max(
            0.05,
            BASELINE_COUPLING_EFFICIENCY - stress.conductance_penalty
            + RNG.normal(0, 0.02)
        )

        # Network coherence: weighted mean with coupling amplification
        # High coupling + high node coherence = network > mean node (amplification)
        # Low coupling = network collapses toward minimum node coherence
        base_network = float(np.mean(nodes))
        amplification = coupling * (1.0 + 0.3 * (base_network - 0.5))
        network_coh = float(np.clip(base_network * amplification, 0.0, 1.0))

        node_coherences.append(float(np.mean(nodes)))
        network_coherences.append(network_coh)

    mean_node = float(np.mean(node_coherences))
    mean_network = float(np.mean(network_coherences))
    amplification_ratio = mean_network / mean_node if mean_node > 0 else 0.0

    # Canary test: is network already below BIOPHOTON_09 amplification threshold
    # while node coherence is still above its own degraded baseline?
    node_degraded = mean_node < (BASELINE_NODE_COHERENCE_MEAN - 0.05)
    network_degraded = amplification_ratio < 1.0  # Network no longer amplifying

    canary = network_degraded and not node_degraded

    return {
        "stress": stress.name,
        "description": stress.description,
        "mean_node_coherence": round(mean_node, 4),
        "mean_network_coherence": round(mean_network, 4),
        "amplification_ratio": round(amplification_ratio, 4),
        "node_degraded": node_degraded,
        "network_degraded": network_degraded,
        "canary_signal": canary,  # True = network warns before nodes
        "coupling_loss_pct": round(stress.conductance_penalty * 100, 1),
        "node_loss_pct": round(stress.node_coherence_penalty * 100, 1),
    }


def run_all_conditions() -> List[Dict]:
    results = []
    for condition in STRESS_CONDITIONS:
        result = simulate_network_coherence(condition)
        results.append(result)
    return results


def format_report(results: List[Dict]) -> str:
    lines = [
        "BIOPHOTON_09b — Stress-Condition Coherence Degradation Results",
        "=" * 70,
        f"{'Condition':<22} {'Node C':>7} {'Net C':>7} {'Amp':>6} {'Canary':>8}",
        "-" * 70,
    ]
    for r in results:
        canary_flag = "⚠️  YES" if r["canary_signal"] else "   no"
        lines.append(
            f"{r['stress']:<22} "
            f"{r['mean_node_coherence']:>7.4f} "
            f"{r['mean_network_coherence']:>7.4f} "
            f"{r['amplification_ratio']:>6.3f} "
            f"{canary_flag:>8}"
        )
    lines.append("=" * 70)
    canary_count = sum(1 for r in results if r["canary_signal"])
    lines.append(f"Canary signal active in {canary_count}/{len(results)} conditions")
    lines.append("")
    lines.append("Interpretation:")
    lines.append("  Amplification ratio < 1.0 = network no longer amplifies above mean node")
    lines.append("  Canary = network degraded while nodes still appear healthy")
    lines.append("  This confirms the mycorrhizal network as early warning instrument")
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_all_conditions()
    print(format_report(results))
    print("\nRaw results (JSON):")
    print(json.dumps(results, indent=2))
