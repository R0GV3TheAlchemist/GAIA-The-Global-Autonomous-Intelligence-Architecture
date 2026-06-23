"""
triadic_field_followup_sim.py
GAIA-OS Simulation Layer | Issue #607 — Triadic Closure Follow-Up

# ============================================================
# HYPOTHESIS
# ============================================================
# Three open questions from TRIADIC_FIELD_PROOF.md are resolved here:
#
#   OQ2: What is the minimum gate resonance required for GATE_QCS
#        to elevate a partial triad to closed_harmonic closure?
#        H: There exists a resonance threshold R_min below which
#           the gate becomes a neutral drag rather than an anchor.
#
#   OQ3: Can a partially differentiated node substitute for the gate?
#        H: There is a differentiation threshold below which a node
#           behaves gate-like (absorbs polarity without destabilizing).
#           Two balanced nodes absorb one differentiated node (Config 07),
#           but where exactly is the tipping point?
#
#   OQ4: Is NEUTRONIC a proto-gate if its resonance is elevated?
#        NEUTRONIC has net charge ≈ -0.05 (nearly neutral).
#        H: Elevating NEUTRONIC resonance from 0.70 toward 0.90
#           will allow it to substitute for GATE_QCS and push the
#           pure E+P+N triad closer to closed_harmonic.
#
# SCHEMA OVERVIEW
# ============================================================
# Inherits TriadicNode, pairwise_coherence, and triadic_coherence
# directly from triadic_field_sim.py. No schema changes.
# All thresholds and weights are identical for cross-sim comparability.
#
# Experiments:
#   EXP-A: Gate resonance sweep (0.10 → 0.95 in 0.05 steps)
#          Best partial triad: BALANCED_A–BALANCED_B (from triadic_field_sim)
#          Gate replaces BALANCED_C. Measure triadic coherence vs gate resonance.
#
#   EXP-B: Differentiation gradient
#          Node X varies from fully balanced (0.60,0.60,0.60) to fully
#          differentiated (0.90,0.10,0.10). Triadic coherence of
#          BALANCED_A + BALANCED_B + X is measured at each step.
#          Find the differentiation threshold where closure is lost.
#
#   EXP-C: NEUTRONIC resonance sweep (0.40 → 0.95 in 0.05 steps)
#          Triad: ELECTRONIC + PROTONIC + NEUTRONIC (pure Q=C=S, worst triad).
#          Measure whether elevating NEUTRONIC resonance rescues closure.
#
# OUTPUTS
# ============================================================
#   simulation/output/triadic_followup_gate_sweep.csv
#   simulation/output/triadic_followup_diff_gradient.csv
#   simulation/output/triadic_followup_neutronic_sweep.csv
#
# CANON REFS
# ============================================================
#   proofs/TRIADIC_FIELD_PROOF.md   — open questions OQ2, OQ3, OQ4
#   proofs/COLOR_ATOMIZATION_PROOF.md — polarity field algebra origin
#   C00 — Q=C=S foundational cosmology
#   simulation/SIMULATION_SCHEMA.md
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np

OUT = Path("simulation/output")
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants (identical to triadic_field_sim for cross-sim comparability) ───
W_ANGULAR   = 0.50
W_CHARGE    = 0.30
W_RESONANCE = 0.20

HARMONIC_THRESHOLD = 0.60
PARTIAL_THRESHOLD  = 0.35


# ── Node definition (inherited schema) ───────────────────────────────────────
@dataclass
class TriadicNode:
    name: str
    layer_weights: Tuple[float, float, float]
    charge: Tuple[float, float]
    resonance: float


# ── Scoring (identical functions to triadic_field_sim) ────────────────────────
def _cosine(a: Tuple, b: Tuple) -> float:
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


# ── Baseline nodes (from triadic_field_sim node library) ─────────────────────
BALANCED_A  = TriadicNode("BALANCED_A",  (0.60, 0.60, 0.60), (0.70, 0.30), 0.75)
BALANCED_B  = TriadicNode("BALANCED_B",  (0.60, 0.60, 0.60), (0.30, 0.70), 0.75)
BALANCED_C  = TriadicNode("BALANCED_C",  (0.60, 0.60, 0.60), (0.50, 0.50), 0.72)
ELECTRONIC  = TriadicNode("ELECTRONIC",  (0.90, 0.10, 0.10), (0.90, 0.15), 0.85)
PROTONIC    = TriadicNode("PROTONIC",    (0.10, 0.90, 0.10), (0.15, 0.90), 0.80)
NEUTRONIC   = TriadicNode("NEUTRONIC",   (0.10, 0.10, 0.90), (0.50, 0.55), 0.70)


# ── EXP-A: Gate resonance sweep ──────────────────────────────────────────────
# Baseline: BALANCED_A + BALANCED_B + BALANCED_C = 0.6304 (closed_harmonic)
# Gate replaces BALANCED_C. Sweep gate resonance from 0.10 to 0.95.
gate_sweep_rows = []
threshold_resonance = None
prev_state = None

for r in np.arange(0.10, 1.00, 0.05):
    r = round(float(r), 2)
    gate = TriadicNode("GATE_QCS", (0.57, 0.57, 0.57), (0.50, 0.50), r)
    coh, state, pairs = triadic_coh([BALANCED_A, BALANCED_B, gate])
    if prev_state == "partially_open" and state == "closed_harmonic" and threshold_resonance is None:
        threshold_resonance = r
    gate_sweep_rows.append({
        "gate_resonance": r,
        "triadic_coherence": coh,
        "closure_state": state,
        "pair_AB": pairs[0],
        "pair_AG": pairs[1],
        "pair_BG": pairs[2],
    })
    prev_state = state

with open(OUT / "triadic_followup_gate_sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(gate_sweep_rows[0].keys()))
    w.writeheader()
    w.writerows(gate_sweep_rows)


# ── EXP-B: Differentiation gradient ──────────────────────────────────────────
# Node X: layer_weights interpolate from balanced (0.60,0.60,0.60) → differentiated (0.90,0.10,0.10)
# Charge interpolates: balanced (0.50,0.50) → strongly positive (0.90,0.15)
# Resonance held constant at 0.75. Triad: BALANCED_A + BALANCED_B + X
diff_rows = []
closure_lost_at = None

for t in np.arange(0.0, 1.05, 0.05):
    t = round(float(t), 2)
    lw = (
        round(0.60 + t * (0.90 - 0.60), 4),
        round(0.60 + t * (0.10 - 0.60), 4),
        round(0.60 + t * (0.10 - 0.60), 4),
    )
    ch = (
        round(0.50 + t * (0.90 - 0.50), 4),
        round(0.50 + t * (0.15 - 0.50), 4),
    )
    node_x = TriadicNode(f"X_t{t}", lw, ch, 0.75)
    coh, state, pairs = triadic_coh([BALANCED_A, BALANCED_B, node_x])
    if closure_lost_at is None and state != "closed_harmonic" and t > 0:
        closure_lost_at = t
    diff_rows.append({
        "t": t,
        "layer_e": lw[0], "layer_p": lw[1], "layer_n": lw[2],
        "charge_pos": ch[0], "charge_neg": ch[1],
        "triadic_coherence": coh,
        "closure_state": state,
        "pair_AB": pairs[0], "pair_AX": pairs[1], "pair_BX": pairs[2],
    })

with open(OUT / "triadic_followup_diff_gradient.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(diff_rows[0].keys()))
    w.writeheader()
    w.writerows(diff_rows)


# ── EXP-C: NEUTRONIC resonance sweep ─────────────────────────────────────────
# Triad: ELECTRONIC + PROTONIC + NEUTRONIC (Config 01, worst: 0.4821)
# Sweep NEUTRONIC resonance from 0.40 to 0.95. Does it rescue closure?
neut_rows = []
neut_threshold = None

for r in np.arange(0.40, 1.00, 0.05):
    r = round(float(r), 2)
    neut = TriadicNode("NEUTRONIC", (0.10, 0.10, 0.90), (0.50, 0.55), r)
    coh, state, pairs = triadic_coh([ELECTRONIC, PROTONIC, neut])
    if neut_threshold is None and state == "closed_harmonic":
        neut_threshold = r
    neut_rows.append({
        "neutronic_resonance": r,
        "triadic_coherence": coh,
        "closure_state": state,
        "pair_EP": pairs[0], "pair_EN": pairs[1], "pair_PN": pairs[2],
    })

with open(OUT / "triadic_followup_neutronic_sweep.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(neut_rows[0].keys()))
    w.writeheader()
    w.writerows(neut_rows)


# ── RESULTS SUMMARY ──────────────────────────────────────────────────────────
print("=" * 60)
print("TRIADIC FIELD FOLLOW-UP — RESULTS SUMMARY")
print("=" * 60)
print(f"EXP-A  Gate R_min for closed_harmonic : {threshold_resonance}")
print(f"EXP-B  Differentiation closure lost at: {closure_lost_at} (None = never lost)")
print(f"EXP-C  NEUTRONIC proto-gate threshold : {neut_threshold} (None = not reached)")
if neut_threshold is None:
    max_coh = max(r["triadic_coherence"] for r in neut_rows)
    print(f"       Max E+P+N coherence in sweep   : {max_coh}")
    print("       OQ4 FALSIFIED: resonance alone cannot rescue E+P+N triad.")
print("=" * 60)
