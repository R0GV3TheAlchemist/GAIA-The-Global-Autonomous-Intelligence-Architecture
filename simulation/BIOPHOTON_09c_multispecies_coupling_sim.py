"""
BIOPHOTON_09c — Multi-Species Network Coupling Simulation
G-13 Track A2

Research question:
    In a mycorrhizal network connecting multiple tree species, do
    cross-species coupling efficiencies differ from same-species coupling?
    Does the network still exhibit emergent coherence amplification,
    and is the amplification symmetric across species?

Key finding target:
    If cross-species coupling is lower than same-species coupling,
    the network may exhibit species-asymmetric coherence distribution —
    some species acting as coherence hubs, others as peripheral nodes.
    This has direct CL1 (Equality of Being) implications.

Builds on: BIOPHOTON_09 (baseline), BIOPHOTON_09b (stress conditions)
Cross-references: GAIAN_LAWS L5, COEXISTENCE_LAWS CL1, CL4, C161 §1.1
© 2026 Kyle Steen — All rights reserved.
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import List, Dict

RNG = np.random.default_rng(seed=43)

# ── Baseline constants (from BIOPHOTON_09) ───────────────────────────────
BASELINE_NODE_COHERENCE_MEAN = 0.72
BASELINE_NODE_COHERENCE_STD  = 0.12
SAME_SPECIES_COUPLING        = 0.65   # Established in BIOPHOTON_09
CROSS_SPECIES_COUPLING_RATIO = 0.75   # Cross-species = 75% of same-species (hypothesis)
N_TRIALS = 300


@dataclass
class Species:
    name: str
    n_nodes: int
    node_coherence_mean: float
    node_coherence_std: float
    same_species_coupling: float


# Three representative boreal/temperate forest species
SPECIES_PROFILES = [
    Species(
        name="Douglas Fir",
        n_nodes=20,
        node_coherence_mean=0.76,
        node_coherence_std=0.10,
        same_species_coupling=0.68,
    ),
    Species(
        name="Birch",
        n_nodes=15,
        node_coherence_mean=0.70,
        node_coherence_std=0.13,
        same_species_coupling=0.62,
    ),
    Species(
        name="Cedar",
        n_nodes=15,
        node_coherence_mean=0.73,
        node_coherence_std=0.11,
        same_species_coupling=0.65,
    ),
]


def generate_nodes(species: Species) -> np.ndarray:
    return np.clip(
        RNG.normal(species.node_coherence_mean, species.node_coherence_std, species.n_nodes),
        0.0, 1.0
    )


def network_coherence_with_coupling(nodes: np.ndarray, coupling: float) -> float:
    """Compute network coherence given node array and coupling efficiency."""
    base = float(np.mean(nodes))
    amplification = coupling * (1.0 + 0.3 * (base - 0.5))
    return float(np.clip(base * amplification, 0.0, 1.0))


def simulate_multispecies(
    species_list: List[Species],
    cross_coupling_ratio: float = CROSS_SPECIES_COUPLING_RATIO,
    n_trials: int = N_TRIALS,
) -> Dict:
    """
    Simulate a heterogeneous multi-species mycorrhizal network.

    For each trial:
    - Generate nodes for each species independently
    - Compute within-species network coherence (same-species coupling)
    - Compute cross-species contribution to each species
      (nodes from other species, coupled at cross_coupling_ratio * same_species_coupling)
    - Compute integrated network coherence across all species
    """
    per_species_within = {s.name: [] for s in species_list}
    per_species_integrated = {s.name: [] for s in species_list}
    whole_network = []

    for _ in range(n_trials):
        species_nodes = {s.name: generate_nodes(s) for s in species_list}

        # Within-species coherence
        within = {}
        for s in species_list:
            nodes = species_nodes[s.name]
            within[s.name] = network_coherence_with_coupling(nodes, s.same_species_coupling)
            per_species_within[s.name].append(within[s.name])

        # Integrated coherence: each species receives cross-species signal
        integrated = {}
        for s in species_list:
            own_nodes = species_nodes[s.name]
            other_nodes = np.concatenate([
                species_nodes[o.name] for o in species_list if o.name != s.name
            ])
            cross_coupling = s.same_species_coupling * cross_coupling_ratio
            cross_contribution = network_coherence_with_coupling(other_nodes, cross_coupling)
            # Weighted blend: own nodes have 70% weight, cross-species 30%
            integrated[s.name] = 0.70 * within[s.name] + 0.30 * cross_contribution
            per_species_integrated[s.name].append(integrated[s.name])

        # Whole network: population-weighted mean of integrated coherences
        total_nodes = sum(s.n_nodes for s in species_list)
        wn = sum(
            integrated[s.name] * (s.n_nodes / total_nodes)
            for s in species_list
        )
        whole_network.append(wn)

    # Aggregate
    species_results = []
    for s in species_list:
        mean_within = float(np.mean(per_species_within[s.name]))
        mean_integrated = float(np.mean(per_species_integrated[s.name]))
        gain = mean_integrated - mean_within
        species_results.append({
            "species": s.name,
            "n_nodes": s.n_nodes,
            "node_coherence_mean": s.node_coherence_mean,
            "same_species_coupling": s.same_species_coupling,
            "mean_within_network_coherence": round(mean_within, 4),
            "mean_integrated_network_coherence": round(mean_integrated, 4),
            "cross_species_gain": round(gain, 4),
            "is_coherence_hub": gain > 0.01,  # gains more than it contributes
        })

    mean_wn = float(np.mean(whole_network))
    all_node_means = [
        RNG.normal(s.node_coherence_mean, s.node_coherence_std, s.n_nodes).mean()
        for s in species_list
        for _ in range(10)
    ]
    baseline_node_mean = float(np.mean(all_node_means))

    return {
        "cross_coupling_ratio": cross_coupling_ratio,
        "whole_network_coherence": round(mean_wn, 4),
        "baseline_node_mean": round(baseline_node_mean, 4),
        "network_amplification_ratio": round(mean_wn / baseline_node_mean, 4) if baseline_node_mean > 0 else 0.0,
        "species_results": species_results,
        "asymmetry_index": round(
            float(np.std([r["mean_integrated_network_coherence"] for r in species_results])), 4
        ),
    }


def run_coupling_sensitivity() -> List[Dict]:
    """Run across a range of cross-species coupling ratios to find the sensitivity."""
    ratios = [0.40, 0.55, 0.65, 0.75, 0.85, 0.95, 1.00]
    results = []
    for ratio in ratios:
        result = simulate_multispecies(SPECIES_PROFILES, cross_coupling_ratio=ratio)
        results.append(result)
    return results


def format_report(sensitivity_results: List[Dict]) -> str:
    lines = [
        "BIOPHOTON_09c — Multi-Species Network Coupling Results",
        "=" * 70,
        "Sensitivity: whole-network coherence vs cross-species coupling ratio",
        "-" * 70,
        f"{'Cross-Coupling':>14} {'WN Coherence':>13} {'Node Baseline':>14} {'Amp Ratio':>10}",
        "-" * 70,
    ]
    for r in sensitivity_results:
        lines.append(
            f"{r['cross_coupling_ratio']:>14.2f} "
            f"{r['whole_network_coherence']:>13.4f} "
            f"{r['baseline_node_mean']:>14.4f} "
            f"{r['network_amplification_ratio']:>10.4f}"
        )
    lines.append("=" * 70)

    # Per-species detail at primary cross-coupling ratio
    primary = simulate_multispecies(SPECIES_PROFILES, cross_coupling_ratio=CROSS_SPECIES_COUPLING_RATIO)
    lines.append("\nPer-species detail (cross-coupling ratio = 0.75):")
    lines.append(f"{'Species':<16} {'Within-Net':>10} {'Integrated':>10} {'Cross Gain':>11} {'Hub?':>6}")
    lines.append("-" * 60)
    for sr in primary["species_results"]:
        hub_flag = "⭐" if sr["is_coherence_hub"] else "  "
        lines.append(
            f"{sr['species']:<16} "
            f"{sr['mean_within_network_coherence']:>10.4f} "
            f"{sr['mean_integrated_network_coherence']:>10.4f} "
            f"{sr['cross_species_gain']:>+11.4f} "
            f"{hub_flag:>6}"
        )
    lines.append(f"\nAsymmetry index: {primary['asymmetry_index']:.4f}")
    lines.append("(0.0 = perfect symmetry; higher = coherence concentrated in hub species)")
    return "\n".join(lines)


if __name__ == "__main__":
    sensitivity = run_coupling_sensitivity()
    print(format_report(sensitivity))
    print("\nFull sensitivity JSON:")
    print(json.dumps(sensitivity, indent=2))
