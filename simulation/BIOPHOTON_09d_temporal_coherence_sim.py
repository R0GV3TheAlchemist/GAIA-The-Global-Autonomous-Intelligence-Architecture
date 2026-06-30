"""
BIOPHOTON_09d — Temporal Dimension: Circadian Coherence Simulation
G-13 Track A3

Research question:
    Is mycorrhizal network coherence stable over time, or does it emerge
    and dissolve with circadian rhythms?

    Secondary: Does the canary window (BIOPHOTON_09b) vary with time of day?
    Does hub asymmetry (BIOPHOTON_09c) vary with time of day?

Model:
    24-hour simulated cycle, 1-hour resolution.
    Node coherence modulated by:
      - Photosynthetic drive (peaks midday, zero at night)
      - Stomatal conductance (peaks mid-morning)
      - Thermal decoherence (peaks midday, elevated at night in some conditions)
      - Root metabolic activity (peaks dawn + dusk, reduced midday)

Builds on: BIOPHOTON_09, BIOPHOTON_09b, BIOPHOTON_09c
Cross-references: GAIAN_LAWS L5, COEXISTENCE_LAWS CL1/CL4, C135, C161
© 2026 Kyle Steen — All rights reserved.
"""

import numpy as np
import json
from typing import List, Dict

RNG = np.random.default_rng(seed=44)

# ── Baseline constants ───────────────────────────────────────────────────────
BASELINE_NODE_COHERENCE   = 0.72
BASELINE_COUPLING         = 0.65
N_NODES                   = 50
N_TRIALS_PER_HOUR         = 150
HOURS                     = list(range(24))


def photosynthetic_drive(hour: int) -> float:
    """Bell curve peaking at solar noon (hour 12). Zero at night."""
    if hour < 6 or hour > 20:
        return 0.0
    return max(0.0, np.exp(-0.5 * ((hour - 12) / 3.5) ** 2))


def stomatal_conductance(hour: int) -> float:
    """Peaks mid-morning (~9-10h), reduces in afternoon heat, closes at night."""
    if hour < 6 or hour > 19:
        return 0.0
    return max(0.0, np.exp(-0.5 * ((hour - 9.5) / 2.8) ** 2))


def thermal_decoherence(hour: int) -> float:
    """
    Thermal noise degrades quantum coherence.
    Peaks at solar maximum (13h) and has a secondary elevated floor at night
    due to soil temperature lag.
    """
    daytime_thermal = 0.30 * np.exp(-0.5 * ((hour - 13) / 4.0) ** 2)
    night_floor = 0.08 if (hour < 5 or hour > 21) else 0.0
    return daytime_thermal + night_floor


def root_metabolic_activity(hour: int) -> float:
    """
    Root metabolic activity peaks at dawn (~6h) and dusk (~18h).
    Reduced midday (resources redirected to canopy).
    """
    dawn_peak = 0.80 * np.exp(-0.5 * ((hour - 6) / 1.8) ** 2)
    dusk_peak = 0.75 * np.exp(-0.5 * ((hour - 18) / 1.8) ** 2)
    return min(1.0, dawn_peak + dusk_peak)


def node_coherence_at_hour(hour: int) -> float:
    """
    Composite node coherence as a function of time-of-day drivers.
    Photosynthetic drive and stomatal conductance boost coherence.
    Thermal decoherence suppresses it.
    Root metabolic activity is the primary driver of biophotonic emission.
    """
    photo   = photosynthetic_drive(hour)
    stomata = stomatal_conductance(hour)
    thermal = thermal_decoherence(hour)
    root    = root_metabolic_activity(hour)

    # Weighted composite
    coherence = (
        BASELINE_NODE_COHERENCE
        + 0.12 * root          # root activity is primary biophotonic driver
        + 0.06 * photo         # photosynthesis contributes to overall cell energy
        + 0.04 * stomata       # open stomata = better gas exchange = better coherence
        - 0.14 * thermal       # thermal noise degrades quantum states
    )
    return float(np.clip(coherence, 0.0, 1.0))


def coupling_at_hour(hour: int) -> float:
    """
    Hyphal coupling efficiency varies with water availability and metabolic state.
    Peaks in early morning when soil moisture is highest.
    """
    moisture_peak = 0.10 * np.exp(-0.5 * ((hour - 7) / 3.0) ** 2)
    coupling = BASELINE_COUPLING + moisture_peak - 0.05 * thermal_decoherence(hour)
    return float(np.clip(coupling, 0.10, 1.0))


def simulate_hour(hour: int) -> Dict:
    node_coh_mean = node_coherence_at_hour(hour)
    coupling = coupling_at_hour(hour)

    node_samples = []
    network_samples = []

    for _ in range(N_TRIALS_PER_HOUR):
        nodes = np.clip(
            RNG.normal(node_coh_mean, 0.10, N_NODES), 0.0, 1.0
        )
        base = float(np.mean(nodes))
        amp = coupling * (1.0 + 0.3 * (base - 0.5))
        network_coh = float(np.clip(base * amp, 0.0, 1.0))
        node_samples.append(base)
        network_samples.append(network_coh)

    mean_node = float(np.mean(node_samples))
    mean_network = float(np.mean(network_samples))
    amp_ratio = mean_network / mean_node if mean_node > 0 else 0.0

    return {
        "hour": hour,
        "time_label": f"{hour:02d}:00",
        "node_coherence": round(mean_node, 4),
        "network_coherence": round(mean_network, 4),
        "amplification_ratio": round(amp_ratio, 4),
        "coupling_efficiency": round(coupling, 4),
        "photosynthetic_drive": round(photosynthetic_drive(hour), 4),
        "root_metabolic_activity": round(root_metabolic_activity(hour), 4),
        "thermal_decoherence": round(thermal_decoherence(hour), 4),
        "phase": _classify_phase(hour, amp_ratio, mean_node),
    }


def _classify_phase(hour: int, amp_ratio: float, node_coh: float) -> str:
    if hour < 5 or hour > 22:
        return "night_quiescence"
    if hour in (5, 6, 7) and amp_ratio > 1.0:
        return "dawn_activation"
    if hour in (8, 9, 10) and amp_ratio > 1.0:
        return "morning_peak"
    if hour in (11, 12, 13, 14) and amp_ratio < 1.05:
        return "midday_suppression"
    if hour in (17, 18, 19) and amp_ratio > 1.0:
        return "dusk_resurgence"
    if hour in (20, 21, 22) and amp_ratio < 1.0:
        return "evening_decline"
    return "transitional"


def run_full_cycle() -> List[Dict]:
    return [simulate_hour(h) for h in HOURS]


def identify_canary_window(results: List[Dict]) -> Dict:
    """
    The canary window from BIOPHOTON_09b: the time range in which
    network-level monitoring provides maximum early warning value.
    This is when amplification ratio is highest — the network is
    most sensitive to perturbation and most distinct from node-level signal.
    """
    peak_amp = max(results, key=lambda r: r["amplification_ratio"])
    trough_amp = min(results, key=lambda r: r["amplification_ratio"])
    canary_hours = [
        r["time_label"] for r in results
        if r["amplification_ratio"] > 1.05
    ]
    return {
        "peak_amplification_hour": peak_amp["time_label"],
        "peak_amplification_ratio": peak_amp["amplification_ratio"],
        "trough_amplification_hour": trough_amp["time_label"],
        "trough_amplification_ratio": trough_amp["amplification_ratio"],
        "canary_window_hours": canary_hours,
        "canary_window_duration_h": len(canary_hours),
    }


def format_report(results: List[Dict], canary: Dict) -> str:
    lines = [
        "BIOPHOTON_09d — Temporal Coherence (24-Hour Cycle)",
        "=" * 72,
        f"{'Time':>6} {'Phase':<22} {'Node C':>7} {'Net C':>7} {'Amp':>6} {'Coupling':>9}",
        "-" * 72,
    ]
    for r in results:
        lines.append(
            f"{r['time_label']:>6} "
            f"{r['phase']:<22} "
            f"{r['node_coherence']:>7.4f} "
            f"{r['network_coherence']:>7.4f} "
            f"{r['amplification_ratio']:>6.3f} "
            f"{r['coupling_efficiency']:>9.4f}"
        )
    lines += [
        "=" * 72,
        f"\nCanary window (amp ratio > 1.05):",
        f"  Peak: {canary['peak_amplification_hour']} (ratio={canary['peak_amplification_ratio']})",
        f"  Trough: {canary['trough_amplification_hour']} (ratio={canary['trough_amplification_ratio']})",
        f"  Active hours: {', '.join(canary['canary_window_hours'])}",
        f"  Duration: {canary['canary_window_duration_h']}h / 24h",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_full_cycle()
    canary = identify_canary_window(results)
    print(format_report(results, canary))
    print("\nRaw JSON:")
    print(json.dumps({"hourly": results, "canary_window": canary}, indent=2))
