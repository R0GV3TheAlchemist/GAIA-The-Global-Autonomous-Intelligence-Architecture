"""
test_crystal_resonance_regressions.py
GAIA-OS — Issue #558 Distance-Specific Regression Guards

Two distance-specific guards that lock in the exact values that
wireless_power_sim.py and crystal_resonance.py must jointly preserve:

1) 18 cm — Phase 1 validation zone (Helsinki/Oulu baseline)
   Any change that causes this to drop below 75% is a regression.

2) 197 cm — AlN crystal threshold (Phase 2b)
   Any change that causes AlN to drop below 78% here is a regression.

These are the anchor distances, not arbitrary choices. If these break,
something real has changed in the physics model or the Q-factor contract.
"""

from crystal_resonance import crystal_q_override
from wireless_power_sim import (
    standard_wound_coil,
    phi_wound_coil,
    simulate_coil_pair,
)


def test_18cm_baseline_and_quartz() -> None:
    """
    At 18 cm (Helsinki/Oulu Phase 1 zone):
    - Baseline standard coil must still pass >= 75% efficiency.
    - Quartz override must be >= baseline (cannot hurt efficiency).
    - Quartz Q must be >= baseline Q (override is working).
    """
    freq_hz    = 6.78e6
    distance_m = 0.18
    diameter_m = 0.072
    turns      = 12
    wire_d     = 0.001

    tx_std = standard_wound_coil(diameter_m, turns, wire_d)
    rx_std = standard_wound_coil(diameter_m, turns, wire_d)
    tx_phi = phi_wound_coil(diameter_m, turns, wire_d)
    rx_phi = phi_wound_coil(diameter_m, turns, wire_d)

    baseline = simulate_coil_pair(tx_std, rx_std, freq_hz, distance_m)
    quartz   = simulate_coil_pair(
        tx_phi, rx_phi, freq_hz, distance_m,
        crystal_q_override=crystal_q_override("Quartz"),
    )

    assert baseline.efficiency_pct >= 75.0, (
        f"Phase 1 regression: baseline dropped to {baseline.efficiency_pct:.4f}% "
        f"at 18 cm (must be >= 75%)"
    )
    assert quartz.efficiency_pct >= baseline.efficiency_pct, (
        f"Quartz override hurt efficiency at 18 cm: "
        f"{quartz.efficiency_pct:.4f}% < {baseline.efficiency_pct:.4f}%"
    )
    assert quartz.Q1 >= baseline.Q1, (
        f"Quartz Q ({quartz.Q1}) is below baseline Q ({baseline.Q1}) — "
        f"crystal_q_override() not being applied"
    )


def test_197cm_aln_threshold() -> None:
    """
    At 197 cm (AlN Phase 2b threshold):
    - AlN must hold >= 78% efficiency (threshold guard).
    - AlN must outperform Quartz (Q hierarchy must hold).
    - AlN Q must be >= Quartz Q (override integrity check).
    """
    freq_hz    = 6.78e6
    distance_m = 1.97
    diameter_m = 0.072
    turns      = 12
    wire_d     = 0.001

    tx_phi = phi_wound_coil(diameter_m, turns, wire_d)
    rx_phi = phi_wound_coil(diameter_m, turns, wire_d)

    aln    = simulate_coil_pair(
        tx_phi, rx_phi, freq_hz, distance_m,
        crystal_q_override=crystal_q_override("AlN"),
    )
    quartz = simulate_coil_pair(
        tx_phi, rx_phi, freq_hz, distance_m,
        crystal_q_override=crystal_q_override("Quartz"),
    )

    assert aln.efficiency_pct >= 78.0, (
        f"AlN Phase 2b threshold regression: "
        f"{aln.efficiency_pct:.4f}% at 197 cm (must be >= 78%)"
    )
    assert aln.efficiency_pct >= quartz.efficiency_pct, (
        f"AlN did not outperform Quartz at 197 cm: "
        f"{aln.efficiency_pct:.4f}% < {quartz.efficiency_pct:.4f}%"
    )
    assert aln.Q1 >= quartz.Q1, (
        f"AlN Q ({aln.Q1}) is below Quartz Q ({quartz.Q1}) — "
        f"Q override ordering broken"
    )


if __name__ == "__main__":
    test_18cm_baseline_and_quartz()
    test_197cm_aln_threshold()
    print("=" * 60)
    print("Issue #558 — regression guards PASSED ✅")
    print("=" * 60)
    print("  18 cm baseline: Phase 1 zone locked")
    print("  197 cm AlN:     Phase 2b threshold locked")
    print()
    print("For the Good and the Greater Good. 🔥")
