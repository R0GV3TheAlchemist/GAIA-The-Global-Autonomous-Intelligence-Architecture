"""
triadic_charge_complementarity_sim.py
GAIA-OS Simulation Layer | Issue #607 — OQ6 Resolution

# ============================================================
# HYPOTHESIS (OQ6)
# ============================================================
# OQ7 showed balanced anchors need resonance >= 0.75 for unconditional
# triadic closure. OQ6 asks whether STRUCTURAL BALANCE is the only
# path to that guarantee, or whether two partially differentiated nodes
# with COMPLEMENTARY CHARGE VECTORS can substitute.
#
# H: There exists a complementarity level c_min(d) that compensates
#    for anchor differentiation d, allowing closed_harmonic closure.
#    But this trade has a hard ceiling: beyond some d_max, no level
#    of complementarity can rescue triadic closure.
#
# EXPERIMENTAL DESIGN
# ============================================================
# 2D parameter sweep:
#   d (differentiation, 0.0 → 1.0):
#     d=0 → A=(0.60,0.60,0.60), B=(0.60,0.60,0.60)
#     d=1 → A=(0.90,0.10,0.10), B=(0.10,0.90,0.10)  [mirror structure]
#
#   c (complementarity, 0.0 → 1.0):
#     c=0 → both anchors charge=(0.50,0.50) [neutral]
#     c=1 → A=(0.85,0.15), B=(0.15,0.85)  [strong mirror charge]
#
# Third node X is tested in two states per (d,c) pair:
#   X_balanced:   (0.60,0.60,0.60) / (0.50,0.50) / res=0.75
#   X_diff:       (0.90,0.10,0.10) / (0.90,0.15) / res=0.75  [fully differentiated]
#
# All anchor resonances held at 0.75. Isolates: can charge complementarity
# substitute for structural balance?
#
# OUTPUT
# ============================================================
#   simulation/output/triadic_oq6_charge_complementarity.csv
#     columns: d_differentiation, c_complementarity,
#              lw_a_Q/P/N, lw_b_Q/P/N, ch_a_pos/neg, ch_b_pos/neg,
#              coh_X_balanced, state_X_balanced, pair_AB/AX/BX_Xbal,
#              coh_X_diff, state_X_diff, pair_AB/AX/BX_Xdiff
#
# CANON REFS
# ============================================================
#   proofs/TRIADIC_ANCHOR_FLOOR_PROOF.md — OQ6 context and urgency
#   proofs/TRIADIC_CHARGE_COMPLEMENTARITY_PROOF.md — this sim's findings
#   C00 — Q=C=S foundational cosmology
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np

OUT = Path("simulation/output")
OUT.mkdir(parents=True, exist_ok=True)

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


d_values = [round(d, 2) for d in np.arange(0.0, 1.05, 0.05)]
c_values = [round(c, 2) for c in np.arange(0.0, 1.05, 0.10)]

X_balanced = TriadicNode("X_balanced", (0.60, 0.60, 0.60), (0.50, 0.50), 0.75)
X_diff     = TriadicNode("X_diff",     (0.90, 0.10, 0.10), (0.90, 0.15), 0.75)

rows = []

for d in d_values:
    for c in c_values:
        lw_a = (
            round(0.60 + d * (0.90 - 0.60), 4),
            round(0.60 + d * (0.10 - 0.60), 4),
            round(0.60 + d * (0.10 - 0.60), 4),
        )
        lw_b = (
            round(0.60 + d * (0.10 - 0.60), 4),
            round(0.60 + d * (0.90 - 0.60), 4),
            round(0.60 + d * (0.10 - 0.60), 4),
        )
        base_pos_a = round(0.50 + c * (0.85 - 0.50), 4)
        base_neg_a = round(1.0 - base_pos_a, 4)
        ch_a = (base_pos_a, base_neg_a)
        ch_b = (base_neg_a, base_pos_a)

        A = TriadicNode("A", lw_a, ch_a, 0.75)
        B = TriadicNode("B", lw_b, ch_b, 0.75)

        coh_bal,  state_bal,  pairs_bal  = triadic_coh([A, B, X_balanced])
        coh_diff, state_diff, pairs_diff = triadic_coh([A, B, X_diff])

        rows.append({
            "d_differentiation": d,
            "c_complementarity": c,
            "lw_a_Q": lw_a[0], "lw_a_P": lw_a[1], "lw_a_N": lw_a[2],
            "lw_b_Q": lw_b[0], "lw_b_P": lw_b[1], "lw_b_N": lw_b[2],
            "ch_a_pos": ch_a[0], "ch_a_neg": ch_a[1],
            "ch_b_pos": ch_b[0], "ch_b_neg": ch_b[1],
            "coh_X_balanced":  coh_bal,  "state_X_balanced":  state_bal,
            "pair_AB_Xbal":    pairs_bal[0], "pair_AX_Xbal": pairs_bal[1], "pair_BX_Xbal": pairs_bal[2],
            "coh_X_diff":      coh_diff, "state_X_diff":      state_diff,
            "pair_AB_Xdiff":   pairs_diff[0], "pair_AX_Xdiff": pairs_diff[1], "pair_BX_Xdiff": pairs_diff[2],
        })

with open(OUT / "triadic_oq6_charge_complementarity.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)


# ── Results summary ─────────────────────────────────────────────────────────
print("=" * 60)
print("OQ6: Min c for closed_harmonic (X balanced)")
print("=" * 60)
for d in d_values:
    min_c = None
    for c in c_values:
        row = next(r for r in rows if r["d_differentiation"] == d and r["c_complementarity"] == c)
        if row["state_X_balanced"] == "closed_harmonic":
            min_c = c
            break
    print(f"  d={d:.2f}: min_c = {min_c if min_c is not None else 'NEVER (ceiling hit)'}")
print("=" * 60)
