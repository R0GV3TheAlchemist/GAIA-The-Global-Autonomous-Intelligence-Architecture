"""
triadic_anchor_floor_sim.py
GAIA-OS Simulation Layer | Issue #607 — OQ7 Resolution

# ============================================================
# HYPOTHESIS (OQ7)
# ============================================================
# OQ3 showed two balanced nodes hold triadic closure unconditionally
# when anchor resonance = 0.75. OQ7 asks whether that guarantee
# survives anchor resonance degradation.
#
# H: The two-balanced unconditional result is load-conditional.
#    There exists an anchor resonance floor R_floor below which
#    the balanced pair can no longer hold closure regardless of
#    the third node's differentiation level.
#
# EXPERIMENTAL DESIGN
# ============================================================
# 2D parameter sweep:
#   - R_anchor: resonance of BALANCED_A and BALANCED_B (both degraded together)
#     Range: 0.30 to 0.75 in steps of 0.05
#   - t: differentiation of third node X from fully balanced (t=0)
#     to fully electronic-like (t=1.0) in steps of 0.05
#
# For each (R_anchor, t) pair, triadic coherence and closure state
# are computed using identical scoring to triadic_field_sim.py.
# The floor R_floor is defined as the minimum R_anchor at which
# the triad achieves closed_harmonic at t=0 (all three nodes balanced).
#
# OUTPUT
# ============================================================
#   simulation/output/triadic_oq7_anchor_floor.csv
#     columns: anchor_resonance, t_differentiation, triadic_coherence,
#              closure_state, pair_AB, pair_AX, pair_BX
#
# CANON REFS
# ============================================================
#   proofs/TRIADIC_FIELD_FOLLOWUP_PROOF.md — OQ7 definition
#   proofs/TRIADIC_ANCHOR_FLOOR_PROOF.md   — findings (this sim)
#   simulation/triadic_field_followup_sim.py — parent sim
#   C00 — Q=C=S foundational cosmology
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, List

import numpy as np

OUT = Path("simulation/output")
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants (identical to all triadic sims) ──────────────────────────────
W_ANGULAR   = 0.50
W_CHARGE    = 0.30
W_RESONANCE = 0.20
HARMONIC_THRESHOLD = 0.60
PARTIAL_THRESHOLD  = 0.35


@dataclass
class TriadicNode:
    name: str
    layer_weights: Tuple[float, float, float]
    charge: Tuple[float, float]
    resonance: float


def _cosine(a, b) -> float:
    va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
    denom = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / denom) if denom else 0.0


def pairwise_coherence(a: TriadicNode, b: TriadicNode) -> float:
    angular_score   = (_cosine(a.layer_weights, b.layer_weights) + 1) / 2
    charge_term     = (1 - _cosine(a.charge, b.charge)) / 2
    resonance_score = a.resonance * b.resonance
    return W_ANGULAR * angular_score + W_CHARGE * charge_term + W_RESONANCE * resonance_score


def triadic_coh(nodes: List[TriadicNode]):
    scores = [
        pairwise_coherence(nodes[0], nodes[1]),
        pairwise_coherence(nodes[0], nodes[2]),
        pairwise_coherence(nodes[1], nodes[2]),
    ]
    mean = float(np.mean(scores))
    state = (
        "closed_harmonic" if mean >= HARMONIC_THRESHOLD else
        "partially_open"  if mean >= PARTIAL_THRESHOLD  else
        "unstable"
    )
    return round(mean, 4), state, [round(s, 4) for s in scores]


# ── 2D sweep ─────────────────────────────────────────────────────────────
anchor_resonances = [round(r, 2) for r in np.arange(0.30, 0.80, 0.05)]
t_values          = [round(t, 2) for t in np.arange(0.0, 1.05, 0.05)]

rows = []
floor_map = {}  # R_anchor → first t where closure is lost (None = never lost)

for R in anchor_resonances:
    A = TriadicNode("BALANCED_A", (0.60, 0.60, 0.60), (0.70, 0.30), R)
    B = TriadicNode("BALANCED_B", (0.60, 0.60, 0.60), (0.30, 0.70), R)
    floor_map[R] = None
    for t in t_values:
        lw = (
            round(0.60 + t * (0.90 - 0.60), 4),
            round(0.60 + t * (0.10 - 0.60), 4),
            round(0.60 + t * (0.10 - 0.60), 4),
        )
        ch = (
            round(0.50 + t * (0.90 - 0.50), 4),
            round(0.50 + t * (0.15 - 0.50), 4),
        )
        X = TriadicNode(f"X_t{t}", lw, ch, 0.75)
        coh, state, pairs = triadic_coh([A, B, X])
        if floor_map[R] is None and state != "closed_harmonic":
            floor_map[R] = t
        rows.append({
            "anchor_resonance":   R,
            "t_differentiation":  t,
            "triadic_coherence":  coh,
            "closure_state":      state,
            "pair_AB":            pairs[0],
            "pair_AX":            pairs[1],
            "pair_BX":            pairs[2],
        })

with open(OUT / "triadic_oq7_anchor_floor.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)


# ── Results summary ─────────────────────────────────────────────────────────
print("=" * 58)
print("OQ7 ANCHOR FLOOR — RESULTS")
print("=" * 58)
for R, t_loss in sorted(floor_map.items()):
    note = "NEVER LOST" if t_loss is None else f"lost at t={t_loss}"
    print(f"  R_anchor={R:>4} | {note}")
critical = [R for R, t in floor_map.items() if t is None]
if critical:
    print(f"\nR_floor = {min(critical)} — minimum anchor resonance for unconditional closure.")
print("=" * 58)
