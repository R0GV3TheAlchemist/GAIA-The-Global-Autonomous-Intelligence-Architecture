"""
simulation/gaia_state_day_sim.py

GAIAState Day Simulation — 96-tick (15-minute interval) episode.

Purpose:
  Validate that D6 mode transitions are sane over a realistic day arc.
  Verify that BUILD only appears when conditions genuinely support it.
  Verify that stress spikes trigger RECOVER and system recovers afterward.
  This is the simulation proof required by Issue #576 and Issue #568.

Usage:
  python simulation/gaia_state_day_sim.py

  Outputs (saved to simulation/output/):
    - gaia_state_day_sim.csv   — full tick-by-tick data
    - gaia_state_day_sim.png   — multi-panel plot

Canon anchors:
  - Issue #576 (GAIAState)
  - Issue #568 (D6 Meta-Coherence Engine)
  - Issue #153 (BiometricCoherenceEngine — personal_coherence arc)
  - Issue #435 (NoosphericConsciousnessEngine — planetary_coherence arc)

For the Good and the Greater Good.
"""

from __future__ import annotations

import csv
import math
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Allow running as a script from repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from gaia.core.state import GAIAState, GAIAOperationalMode
from gaia.core.d6_engine import D6Inputs, compute_next_state

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TICKS = 96          # 96 × 15 min = 24 hours
TICK_MINUTES = 15


# ── Synthetic signal generators ───────────────────────────────────────────────

def personal_coherence_arc(tick: int) -> float:
    """Simulate a realistic Architect day:
    - Groggy start (low coherence around tick 0–8)
    - Morning rise (tick 8–24)
    - Peak midday (tick 24–40)
    - Post-lunch dip (tick 40–48)
    - Recovery and late-afternoon build (tick 48–64)
    - Late-night work session with declining coherence (tick 64–80)
    - Depletion / pre-sleep low (tick 80–96)
    Plus: a stress spike event at tick 55–60 (simulating a late-session crisis).
    """
    t = tick / TICKS
    # Base circadian: peaks around tick 30 (~7.5h in), dips at end
    base = 0.45 + 0.35 * math.sin(math.pi * t)  # 0.45 → peak ~0.80 → 0.45
    # Morning ramp-up modifier
    morning_ramp = max(0.0, min(1.0, (tick - 4) / 20)) * 0.15
    # Late-night decline
    night_decline = -0.25 * max(0.0, (tick - 70) / 26)
    # Stress spike dip at ticks 55–62
    stress_dip = -0.35 if 55 <= tick <= 62 else 0.0
    value = base + morning_ramp + night_decline + stress_dip
    return max(0.10, min(1.0, value))


def energy_arc(tick: int) -> float:
    """Energy mirrors coherence but with slower recovery and sharper evening drop."""
    t = tick / TICKS
    base = 0.50 + 0.30 * math.sin(math.pi * t * 0.9)
    evening_drop = -0.30 * max(0.0, (tick - 60) / 36)
    return max(0.08, min(1.0, base + evening_drop))


def stress_arc(tick: int) -> float:
    """Low morning stress, building through the day, spike at ticks 55–62."""
    t = tick / TICKS
    base = 0.15 + 0.25 * t  # slowly rises
    spike = 0.55 if 55 <= tick <= 62 else 0.0
    return max(0.05, min(1.0, base + spike))


def entropy_arc(tick: int) -> float:
    """Entropy rises as work accumulates; spikes during the stress event."""
    t = tick / TICKS
    base = 0.20 + 0.40 * t
    spike = 0.25 if 55 <= tick <= 65 else 0.0
    return max(0.10, min(0.95, base + spike))


def planetary_coherence_arc(tick: int) -> float:
    """Planetary coherence: slow wave, brief turbulence mid-afternoon."""
    t = tick / TICKS
    base = 0.55 + 0.15 * math.cos(2 * math.pi * t)
    turbulence = -0.20 if 45 <= tick <= 55 else 0.0
    return max(0.20, min(1.0, base + turbulence))


# ── Simulation loop ───────────────────────────────────────────────────────────

def run_simulation() -> list[dict]:
    records = []
    start = datetime(2026, 6, 17, 6, 0, 0, tzinfo=timezone.utc)
    state = GAIAState(
        coherence=personal_coherence_arc(0),
        energy=energy_arc(0),
        stress=stress_arc(0),
        entropy=entropy_arc(0),
        personal_coherence=personal_coherence_arc(0),
        planetary_coherence=planetary_coherence_arc(0),
    )

    for tick in range(TICKS):
        ts = start + timedelta(minutes=tick * TICK_MINUTES)

        # Update probe values on state
        state.personal_coherence = personal_coherence_arc(tick)
        state.energy = energy_arc(tick)
        state.stress = stress_arc(tick)
        state.entropy = entropy_arc(tick)
        state.planetary_coherence = planetary_coherence_arc(tick)
        state.coherence = (state.personal_coherence + state.planetary_coherence) / 2.0

        inputs = D6Inputs(current_state=state)
        decision = compute_next_state(inputs)
        state = decision.next_state

        record = {
            "tick": tick,
            "timestamp": ts.strftime("%H:%M"),
            "mode": state.mode.value,
            "personal_coherence": round(state.personal_coherence, 3),
            "energy": round(state.energy, 3),
            "stress": round(state.stress, 3),
            "entropy": round(state.entropy, 3),
            "planetary_coherence": round(state.planetary_coherence, 3),
            "coherence": round(state.coherence, 3),
            "learning_rate": round(state.learning_rate, 3),
            "exploration_rate": round(state.exploration_rate, 3),
            "conservation_rate": round(state.conservation_rate, 3),
            "interventions": " | ".join(decision.interventions) if decision.interventions else "",
            "rationale": decision.rationale,
        }
        records.append(record)

    return records


def save_csv(records: list[dict]) -> Path:
    csv_path = OUTPUT_DIR / "gaia_state_day_sim.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)
    print(f"CSV saved → {csv_path}")
    return csv_path


def save_plot(records: list[dict]) -> Path:
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        print("matplotlib not installed — skipping plot. Run: pip install matplotlib")
        return Path()

    MODE_COLORS = {
        "build":      "#22c55e",
        "discovery":  "#3b82f6",
        "validation": "#f59e0b",
        "reflect":    "#a855f7",
        "recover":    "#ef4444",
        "protect":    "#f97316",
        "offline":    "#6b7280",
    }

    ticks = [r["tick"] for r in records]
    times = [r["timestamp"] for r in records]
    modes = [r["mode"] for r in records]
    pc = [r["personal_coherence"] for r in records]
    en = [r["energy"] for r in records]
    st = [r["stress"] for r in records]
    ent = [r["entropy"] for r in records]
    pl = [r["planetary_coherence"] for r in records]

    fig, axes = plt.subplots(3, 1, figsize=(16, 12), sharex=True)
    fig.suptitle(
        "GAIA-OS — GAIAState Day Simulation (96 ticks × 15 min)\n"
        "Issue #576 + #568 — D6 Meta-Coherence Engine Proof",
        fontsize=14, fontweight="bold", y=0.98
    )
    fig.patch.set_facecolor("#0f172a")
    for ax in axes:
        ax.set_facecolor("#1e293b")
        ax.tick_params(colors="#94a3b8")
        ax.spines[:].set_color("#334155")

    # ── Panel 1: Mode timeline (coloured spans) ───────────────────────────────
    ax1 = axes[0]
    prev_mode = modes[0]
    span_start = 0
    for i, m in enumerate(modes + [None]):
        if m != prev_mode:
            color = MODE_COLORS.get(prev_mode, "#ffffff")
            ax1.axvspan(span_start, i, alpha=0.85, color=color)
            span_start = i
            prev_mode = m
    ax1.set_ylim(0, 1)
    ax1.set_yticks([])
    ax1.set_ylabel("Mode", color="#e2e8f0")
    legend_patches = [
        mpatches.Patch(color=c, label=m) for m, c in MODE_COLORS.items()
    ]
    ax1.legend(handles=legend_patches, loc="upper right", ncol=4,
               fontsize=8, facecolor="#1e293b", labelcolor="#e2e8f0")
    ax1.set_title("Operational Mode", color="#e2e8f0", fontsize=10)

    # ── Panel 2: Coherence, Energy, Planetary ─────────────────────────────────
    ax2 = axes[1]
    ax2.plot(ticks, pc, color="#22c55e", linewidth=2, label="personal_coherence")
    ax2.plot(ticks, en, color="#3b82f6", linewidth=2, label="energy")
    ax2.plot(ticks, pl, color="#a855f7", linewidth=1.5, linestyle="--", label="planetary_coherence")
    ax2.axhline(0.70, color="#22c55e", linestyle=":", alpha=0.5, linewidth=1)
    ax2.axhline(0.40, color="#f59e0b", linestyle=":", alpha=0.5, linewidth=1)
    ax2.axhline(0.30, color="#ef4444", linestyle=":", alpha=0.5, linewidth=1)
    ax2.set_ylim(0, 1.05)
    ax2.set_ylabel("Score [0–1]", color="#e2e8f0")
    ax2.legend(loc="upper right", fontsize=8, facecolor="#1e293b", labelcolor="#e2e8f0")
    ax2.set_title("Coherence & Energy", color="#e2e8f0", fontsize=10)

    # ── Panel 3: Stress & Entropy ─────────────────────────────────────────────
    ax3 = axes[2]
    ax3.plot(ticks, st, color="#ef4444", linewidth=2, label="stress")
    ax3.plot(ticks, ent, color="#f97316", linewidth=2, label="entropy")
    ax3.axhline(0.80, color="#ef4444", linestyle=":", alpha=0.5, linewidth=1, label="recover_threshold")
    ax3.axhline(0.60, color="#f97316", linestyle=":", alpha=0.5, linewidth=1, label="validation_threshold")
    ax3.set_ylim(0, 1.05)
    ax3.set_ylabel("Score [0–1]", color="#e2e8f0")
    ax3.set_xlabel("Tick (15-min intervals)", color="#e2e8f0")
    ax3.legend(loc="upper left", fontsize=8, facecolor="#1e293b", labelcolor="#e2e8f0")
    ax3.set_title("Stress & Entropy", color="#e2e8f0", fontsize=10)

    # X-axis: show hour labels every 8 ticks (2h)
    tick_positions = list(range(0, TICKS, 8))
    tick_labels = [times[i] for i in tick_positions]
    for ax in axes:
        ax.set_xticks(tick_positions)
    axes[2].set_xticklabels(tick_labels, rotation=45, ha="right", color="#94a3b8", fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plot_path = OUTPUT_DIR / "gaia_state_day_sim.png"
    plt.savefig(str(plot_path), dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close()
    print(f"Plot saved  → {plot_path}")
    return plot_path


if __name__ == "__main__":
    print("Running GAIA-OS Day Simulation (96 ticks × 15 min)...")
    records = run_simulation()
    save_csv(records)
    save_plot(records)

    # Print a quick mode summary
    from collections import Counter
    mode_counts = Counter(r["mode"] for r in records)
    print("\nMode distribution over 24h:")
    for mode, count in sorted(mode_counts.items(), key=lambda x: -x[1]):
        hours = count * TICK_MINUTES / 60
        print(f"  {mode:<12} {count:>3} ticks  ({hours:.1f}h)")

    # Show stress-spike RECOVER window
    recover_ticks = [r for r in records if r["mode"] == "recover"]
    if recover_ticks:
        print(f"\nRECOVER window: ticks {recover_ticks[0]['tick']}–{recover_ticks[-1]['tick']} "
              f"({recover_ticks[0]['timestamp']}–{recover_ticks[-1]['timestamp']})")
    print("\nSimulation complete. For the Good and the Greater Good. ❤️")
