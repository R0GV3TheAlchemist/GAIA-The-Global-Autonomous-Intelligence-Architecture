"""
simulation/wireless_power_viz.py

Queue 3 — Field geometry visualizations.

Requires wireless_power_sim.py to have been run first to generate CSV files.

Outputs to simulation/output/:
  wireless_efficiency_curve.png   — efficiency vs. distance (phase 1 + 2)
  wireless_room_heatmap.png       — 2D power density heat map with safety overlay (phase 3)
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUT = Path("simulation/output")


def plot_efficiency_curve():
    p1 = pd.read_csv(OUT / "wireless_phase1_validation.csv")
    p2 = pd.read_csv(OUT / "wireless_phase2_phi_hypothesis.csv")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), facecolor="#08111f")

    # Phase 1 — Finland replication
    ax1 = axes[0]
    ax1.set_facecolor("#0f172a")
    ax1.plot(p1["distance_m"] * 100, p1["efficiency_pct"], color="#38bdf8", lw=2, label="Standard coil")
    ax1.axvline(18, color="#fbbf24", lw=1.5, linestyle="--", label="Finland baseline (18 cm)")
    ax1.axhline(80, color="#4ade80", lw=1.0, linestyle=":", label="Target 80%")
    ax1.set_xlabel("Distance (cm)", color="#cbd5e1")
    ax1.set_ylabel("Efficiency (%)", color="#cbd5e1")
    ax1.set_title("Phase 1 — Finland Validation", color="white")
    ax1.tick_params(colors="#94a3b8")
    ax1.legend(facecolor="#1e293b", labelcolor="white", fontsize=8)
    ax1.grid(alpha=0.15)

    # Phase 2 — Phi vs standard
    ax2 = axes[1]
    ax2.set_facecolor("#0f172a")
    for variant, color, label in [("standard", "#38bdf8", "Standard"), ("phi", "#a78bfa", "Phi-wound (φ)")]:
        sub = p2[p2["variant"] == variant]
        ax2.plot(sub["distance_m"] * 100, sub["efficiency_pct"], color=color, lw=2, label=label)
    ax2.set_xlabel("Distance (cm)", color="#cbd5e1")
    ax2.set_ylabel("Efficiency (%)", color="#cbd5e1")
    ax2.set_title("Phase 2 — Phi Hypothesis", color="white")
    ax2.tick_params(colors="#94a3b8")
    ax2.legend(facecolor="#1e293b", labelcolor="white", fontsize=8)
    ax2.grid(alpha=0.15)

    fig.suptitle("GAIA Queue 3 — Resonant Wireless Power Simulation", color="white", fontsize=14)
    fig.savefig(OUT / "wireless_efficiency_curve.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Wrote: {OUT / 'wireless_efficiency_curve.png'}")


def plot_room_heatmap():
    df = pd.read_csv(OUT / "wireless_phase3_room_scale.csv")
    pivot_eff = df.pivot_table(index="point_y", columns="point_x", values="efficiency_pct")
    pivot_safe = df.pivot_table(index="point_y", columns="point_x", values="safety_pass")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), facecolor="#08111f")

    ax1 = axes[0]
    ax1.set_facecolor("#0f172a")
    im = ax1.imshow(pivot_eff.values, origin="lower", cmap="plasma",
                    extent=[pivot_eff.columns.min(), pivot_eff.columns.max(),
                            pivot_eff.index.min(), pivot_eff.index.max()])
    cb = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cb.set_label("Efficiency (%)", color="#cbd5e1")
    cb.ax.yaxis.set_tick_params(color="#94a3b8")
    plt.setp(cb.ax.get_yticklabels(), color="#cbd5e1")
    ax1.set_title("Phase 3 — Room Efficiency Heatmap", color="white")
    ax1.set_xlabel("x (m)", color="#cbd5e1"); ax1.set_ylabel("y (m)", color="#cbd5e1")
    ax1.tick_params(colors="#94a3b8")

    ax2 = axes[1]
    ax2.set_facecolor("#0f172a")
    safe_vals = pivot_safe.values.astype(float)
    im2 = ax2.imshow(safe_vals, origin="lower", cmap="RdYlGn", vmin=0, vmax=1,
                     extent=[pivot_safe.columns.min(), pivot_safe.columns.max(),
                             pivot_safe.index.min(), pivot_safe.index.max()])
    ax2.set_title("Phase 3 — Biological Safety Overlay", color="white")
    ax2.set_xlabel("x (m)", color="#cbd5e1"); ax2.set_ylabel("y (m)", color="#cbd5e1")
    ax2.tick_params(colors="#94a3b8")
    safe_patch = mpatches.Patch(color="green", label="Safe (≤1 mW/cm²)")
    danger_patch = mpatches.Patch(color="red", label="Exceeds limit")
    ax2.legend(handles=[safe_patch, danger_patch], facecolor="#1e293b", labelcolor="white", fontsize=8)

    fig.suptitle("GAIA Queue 3 — Room Scale Wireless Power (7-node Flower of Life array)", color="white", fontsize=13)
    fig.savefig(OUT / "wireless_room_heatmap.png", dpi=180, bbox_inches="tight", facecolor=fig.get_facecolor())
    print(f"Wrote: {OUT / 'wireless_room_heatmap.png'}")


if __name__ == "__main__":
    plot_efficiency_curve()
    plot_room_heatmap()
    print("Visualization complete.")
