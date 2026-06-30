"""BIOPHOTON_09 — Plant Root Quantum Coherence Simulation

Models a mycorrhizal root network as a weighted graph.
Tests whether network-level coherence exceeds mean node-level coherence
under three conditions: high coherence, low coherence, and noise.

Primary assertion:
    High-coherence condition: network_coherence > mean(node_coherences)

Canon: GAIAN_LAWS L5 · COEXISTENCE_LAWS CL1 · C159 §2.3
Research doc: research/simulations/BIOPHOTON_09_Plant_Root_Quantum_Coherence.md
Sprint: G-12 Track D
Date: 2026-06-29
© 2026 Kyle Steen — All rights reserved.
"""

from __future__ import annotations
import math
import random
import statistics
from dataclasses import dataclass, field
from typing import Literal

# ---------------------------------------------------------------------------
# Seed for reproducibility
# ---------------------------------------------------------------------------
random.seed(2026_0629)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CoherenceCondition = Literal["high", "low", "noise"]

# Mandel Q analogue thresholds
# Q < 0 = sub-Poissonian (non-classical); Q ≈ 0 = Poissonian; Q > 0 = super-Poissonian
EMERGENT_COHERENCE_NOISE_FLOOR = 0.02  # delta below this is within noise


# ---------------------------------------------------------------------------
# Node and network structures
# ---------------------------------------------------------------------------

@dataclass
class RootNode:
    node_id: int
    emission_rate: float       # photons per unit time (normalised 0–1)
    local_coherence: float     # Mandel-Q analogue: 0.0–1.0 (1.0 = fully coherent)
    connection_degree: int     # number of mycelial edges


@dataclass
class MycelialEdge:
    node_a: int
    node_b: int
    coupling_strength: float   # 0.0–1.0: coherence transfer efficiency


@dataclass
class RootNetwork:
    nodes: list[RootNode]
    edges: list[MycelialEdge]
    condition: CoherenceCondition


@dataclass
class CoherenceResult:
    condition: CoherenceCondition
    mean_node_coherence: float
    network_coherence: float
    emergent_delta: float
    emergent_confirmed: bool       # True if delta > EMERGENT_COHERENCE_NOISE_FLOOR
    coupling_efficiency: float
    node_count: int
    edge_count: int


# ---------------------------------------------------------------------------
# Network generation
# ---------------------------------------------------------------------------

def _node_coherence_for_condition(condition: CoherenceCondition) -> float:
    """
    Generate a node coherence value appropriate for the given condition.
    High: 0.65–0.85  (structured sub-Poissonian emission)
    Low:  0.28–0.50  (weakly structured, near-Poissonian)
    Noise: 0.05–0.20 (thermal/incoherent)
    """
    if condition == "high":
        return round(random.uniform(0.65, 0.85), 4)
    elif condition == "low":
        return round(random.uniform(0.28, 0.50), 4)
    else:
        return round(random.uniform(0.05, 0.20), 4)


def _coupling_strength_for_condition(condition: CoherenceCondition) -> float:
    """
    Mycelial coupling strength varies with the coherence regime.
    In high-coherence systems, coupling is stronger (coherence is
    amplified by the network). In noise, coupling propagates disorder.
    """
    if condition == "high":
        return round(random.uniform(0.60, 0.85), 4)
    elif condition == "low":
        return round(random.uniform(0.25, 0.50), 4)
    else:
        return round(random.uniform(0.05, 0.25), 4)


def build_network(n_nodes: int, n_edges: int, condition: CoherenceCondition) -> RootNetwork:
    """Build a random mycorrhizal root network for a given coherence condition."""
    nodes = [
        RootNode(
            node_id=i,
            emission_rate=round(random.uniform(0.4, 1.0), 4),
            local_coherence=_node_coherence_for_condition(condition),
            connection_degree=0,
        )
        for i in range(n_nodes)
    ]

    edges: list[MycelialEdge] = []
    possible_pairs = [(a, b) for a in range(n_nodes) for b in range(a + 1, n_nodes)]
    selected = random.sample(possible_pairs, min(n_edges, len(possible_pairs)))

    for a, b in selected:
        coupling = _coupling_strength_for_condition(condition)
        edges.append(MycelialEdge(node_a=a, node_b=b, coupling_strength=coupling))
        nodes[a].connection_degree += 1
        nodes[b].connection_degree += 1

    return RootNetwork(nodes=nodes, edges=edges, condition=condition)


# ---------------------------------------------------------------------------
# Coherence computation
# ---------------------------------------------------------------------------

def _network_coherence(network: RootNetwork) -> float:
    """
    Global network coherence index.

    Computed as: weighted mean of all node coherences, where the weight for
    each node is amplified by its mycelial connectivity and the coupling
    strength of its edges.

    The amplification factor represents coherence coupling: a highly connected
    node in a high-coupling network contributes more to the global coherence
    than its local coherence alone would suggest.

    This is the operationalisation of the emergent coherence test:
    if network_coherence > mean(node_coherences), the network is amplifying
    coherence beyond the sum of its parts.
    """
    if not network.edges:
        # No mycelial connections — network coherence equals mean node coherence
        return round(statistics.mean(n.local_coherence for n in network.nodes), 4)

    # Build per-node amplification factors from edge coupling strengths
    node_amplification: dict[int, float] = {n.node_id: 1.0 for n in network.nodes}
    for edge in network.edges:
        boost = 1.0 + (edge.coupling_strength * 0.30)  # coupling adds up to 30% amplification per edge
        node_amplification[edge.node_a] *= boost
        node_amplification[edge.node_b] *= boost

    # Normalise amplification factors (prevent runaway amplification in dense networks)
    max_amp = max(node_amplification.values())
    if max_amp > 1.0:
        node_amplification = {k: v / max_amp for k, v in node_amplification.items()}

    weighted_coherences = [
        n.local_coherence * node_amplification[n.node_id]
        for n in network.nodes
    ]
    raw_network_coherence = statistics.mean(weighted_coherences)

    # In noise condition, network coupling spreads disorder: slight penalty
    if network.condition == "noise":
        disorder_penalty = statistics.mean(e.coupling_strength for e in network.edges) * 0.10
        raw_network_coherence = max(0.0, raw_network_coherence - disorder_penalty)

    return round(min(1.0, raw_network_coherence), 4)


def _coupling_efficiency(network: RootNetwork) -> float:
    """Mean coupling strength across all mycelial edges."""
    if not network.edges:
        return 0.0
    return round(statistics.mean(e.coupling_strength for e in network.edges), 4)


# ---------------------------------------------------------------------------
# Simulation runner
# ---------------------------------------------------------------------------

def run_biophoton_09(
    n_nodes: int = 24,
    n_edges: int = 36,
) -> dict:
    """
    Run the BIOPHOTON_09 simulation across all three coherence conditions.

    Args:
        n_nodes: number of root nodes in the network (default 24)
        n_edges: number of mycelial edges (default 36 — ~1.5 edges per node,
                 reflecting a moderately connected mycorrhizal network)

    Returns:
        dict with results for all three conditions and overall assertion status.
    """
    results: list[CoherenceResult] = []

    for condition in ["high", "low", "noise"]:
        network = build_network(n_nodes, n_edges, condition)  # type: ignore
        mean_node = round(statistics.mean(n.local_coherence for n in network.nodes), 4)
        net_coherence = _network_coherence(network)
        delta = round(net_coherence - mean_node, 4)
        confirmed = delta > EMERGENT_COHERENCE_NOISE_FLOOR
        coupling_eff = _coupling_efficiency(network)

        results.append(CoherenceResult(
            condition=condition,
            mean_node_coherence=mean_node,
            network_coherence=net_coherence,
            emergent_delta=delta,
            emergent_confirmed=confirmed,
            coupling_efficiency=coupling_eff,
            node_count=len(network.nodes),
            edge_count=len(network.edges),
        ))

    # Primary assertion: high-coherence condition must confirm emergent coherence
    high_result = next(r for r in results if r.condition == "high")
    primary_assertion_passed = high_result.emergent_confirmed

    return {
        "primary_assertion_passed": primary_assertion_passed,
        "assertion": "network_coherence > mean(node_coherences) under high-coherence condition",
        "results": [
            {
                "condition": r.condition,
                "mean_node_coherence": r.mean_node_coherence,
                "network_coherence": r.network_coherence,
                "emergent_delta": r.emergent_delta,
                "emergent_confirmed": r.emergent_confirmed,
                "coupling_efficiency": r.coupling_efficiency,
            }
            for r in results
        ],
    }


if __name__ == "__main__":
    import json
    output = run_biophoton_09()
    print(json.dumps(output, indent=2))
    status = "PASS" if output["primary_assertion_passed"] else "FAIL"
    print(f"\nPrimary assertion: {status}")
    for r in output["results"]:
        marker = "✅" if r["emergent_confirmed"] else ("⚠️" if r["emergent_delta"] > 0 else "❌")
        print(f"  [{r['condition']:6}] node={r['mean_node_coherence']:.3f}  "
              f"network={r['network_coherence']:.3f}  "
              f"Δ={r['emergent_delta']:+.3f}  {marker}")
