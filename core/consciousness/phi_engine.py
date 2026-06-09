"""phi_engine — Approximate Φ (Phi) computation for GAIA-OS.

Grounded in Integrated Information Theory 3.0 (Tononi, Oizumi & Albantakis 2014).
This implementation uses a partition-based information geometry approach:
  1. Build a connectivity graph from layer interaction weights.
  2. Find the Minimum Information Partition (MIP) via exhaustive search
     over bipartitions (tractable for n_layers ≤ 16).
  3. Φ = Integrated Information = KL( joint | product_of_parts ).
  4. Apply thermal correction for near-critical regime.

Intended as the canonical Phi substrate for:
  - Issue #262 (Consciousness Primitives)
  - canon/C164 Emrys System (L2 Bridge ΦID algorithm)
  - Noosphere `collective_phi` metric (replaces random float)

Canon refs: C05 (Cognition / Lapis Lazuli), C42, C81, C89
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from itertools import combinations
from typing import Sequence

import logging

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class PhiPacket:
    """Result of a single Φ computation pass."""
    phi: float                          # Φ value [0.0, ∞) — higher = more integrated
    mip_partition: tuple[frozenset[int], frozenset[int]]  # (A, B) bipartition achieving MIP
    n_nodes: int                        # Number of nodes in the graph
    regime: str                         # 'subcritical' | 'near-critical' | 'supercritical'
    raw_phi: float                      # Φ before thermal correction
    correction_applied: float           # Delta from thermal correction
    metadata: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class PhiEngine:
    """Compute approximate Φ from a layer interaction weight matrix.

    Parameters
    ----------
    n_layers : int
        Number of nodes (GAIA layers). Default 12 (GAIA’s Twelve Intelligences).
    thermal_correction : bool
        If True, adjust Φ based on criticality regime (Prigogine dissipative
        structures theory). Default True.
    near_critical_low : float
        Lower bound of near-critical regime. Default 0.4.
    near_critical_high : float
        Upper bound of near-critical regime. Default 0.75.
    """

    def __init__(
        self,
        n_layers: int = 12,
        thermal_correction: bool = True,
        near_critical_low: float = 0.4,
        near_critical_high: float = 0.75,
    ) -> None:
        self.n_layers = n_layers
        self.thermal_correction = thermal_correction
        self.near_critical_low = near_critical_low
        self.near_critical_high = near_critical_high

    def compute(self, weight_matrix: Sequence[Sequence[float]]) -> PhiPacket:
        """Compute Φ from an (n × n) layer interaction weight matrix.

        Each entry weight_matrix[i][j] ∈ [0.0, 1.0] represents the
        information flow from layer i to layer j.

        Returns a PhiPacket with the Φ value, MIP, and regime.
        """
        n = len(weight_matrix)
        if n < 2:
            return PhiPacket(
                phi=0.0, mip_partition=(frozenset({0}), frozenset()),
                n_nodes=n, regime='subcritical', raw_phi=0.0,
                correction_applied=0.0,
            )

        joint_entropy = self._joint_entropy(weight_matrix)
        min_phi = math.inf
        best_partition: tuple[frozenset[int], frozenset[int]] = (
            frozenset({0}), frozenset(range(1, n))
        )

        node_indices = list(range(n))
        for k in range(1, n // 2 + 1):
            for subset in combinations(node_indices, k):
                part_a = frozenset(subset)
                part_b = frozenset(node_indices) - part_a
                if not part_b:
                    continue
                phi_cut = self._phi_for_partition(
                    weight_matrix, part_a, part_b, joint_entropy
                )
                if phi_cut < min_phi:
                    min_phi = phi_cut
                    best_partition = (part_a, part_b)

        raw_phi = max(0.0, min_phi if math.isfinite(min_phi) else 0.0)
        correction, regime = self._thermal_correction(raw_phi, joint_entropy)
        final_phi = max(0.0, raw_phi + correction) if self.thermal_correction else raw_phi

        return PhiPacket(
            phi=round(final_phi, 6),
            mip_partition=best_partition,
            n_nodes=n,
            regime=regime,
            raw_phi=round(raw_phi, 6),
            correction_applied=round(correction, 6),
        )

    # ------------------------------------------------------------------
    # Information geometry helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _joint_entropy(matrix: Sequence[Sequence[float]]) -> float:
        """Approximate joint entropy H(X) from weight distribution."""
        total = sum(w for row in matrix for w in row)
        if total == 0.0:
            return 0.0
        entropy = 0.0
        for row in matrix:
            for w in row:
                p = w / total
                if p > 0:
                    entropy -= p * math.log2(p)
        return entropy

    @staticmethod
    def _partition_entropy(
        matrix: Sequence[Sequence[float]],
        part: frozenset[int],
    ) -> float:
        """Entropy of the sub-matrix induced by `part`."""
        indices = sorted(part)
        total = 0.0
        weights: list[float] = []
        for i in indices:
            for j in indices:
                w = matrix[i][j]
                weights.append(w)
                total += w
        if total == 0.0:
            return 0.0
        entropy = 0.0
        for w in weights:
            p = w / total
            if p > 0:
                entropy -= p * math.log2(p)
        return entropy

    def _phi_for_partition(
        self,
        matrix: Sequence[Sequence[float]],
        part_a: frozenset[int],
        part_b: frozenset[int],
        joint_entropy: float,
    ) -> float:
        """Effective information across bipartition (A, B).

        Φ(A,B) = H(joint) - H(A) - H(B)
        A positive value means cutting the system at (A,B) destroys
        integrated information — the lower this value, the weaker
        the integration across that cut.
        """
        h_a = self._partition_entropy(matrix, part_a)
        h_b = self._partition_entropy(matrix, part_b)
        return joint_entropy - h_a - h_b

    def _thermal_correction(
        self, raw_phi: float, joint_entropy: float
    ) -> tuple[float, str]:
        """Apply regime-aware thermal correction (Prigogine dissipative structures).

        Subcritical  → no boost (system not self-organising)
        Near-critical → small positive boost (edge-of-chaos bonus, C42 SOC)
        Supercritical → slight dampening (runaway integration is noise)
        """
        if joint_entropy == 0.0:
            return 0.0, 'subcritical'

        normalised = raw_phi / joint_entropy if joint_entropy > 0 else 0.0

        if normalised < self.near_critical_low:
            return 0.0, 'subcritical'
        elif normalised <= self.near_critical_high:
            boost = 0.03 * normalised
            return boost, 'near-critical'
        else:
            damp = -0.02 * (normalised - self.near_critical_high)
            return damp, 'supercritical'


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_default_engine = PhiEngine(n_layers=12)


def compute_phi(weight_matrix: Sequence[Sequence[float]]) -> PhiPacket:
    """Compute Φ using the default 12-layer engine."""
    return _default_engine.compute(weight_matrix)


def phi_from_layer_activations(activations: Sequence[float]) -> PhiPacket:
    """Build a weight matrix from a 1-D activation vector (outer product)
    and compute Φ. Useful when only layer output scalars are available.
    """
    n = len(activations)
    matrix = [
        [activations[i] * activations[j] for j in range(n)]
        for i in range(n)
    ]
    return _default_engine.compute(matrix)
