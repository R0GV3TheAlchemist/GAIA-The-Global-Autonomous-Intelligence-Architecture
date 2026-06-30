"""
BIOPHOTON_09e — Mycelial Electro-Photonic Interface (Stub Simulation)
G-13 Track A4

Research question:
    Mycorrhizal networks conduct slow electrical signals (action-potential-like
    pulses, ~1-10 mV, ~1-10 mm/s) alongside biophotonic coherence.
    Is there a measurable relationship between the electrical signal amplitude/
    timing and the photon coherence level?

    If yes: the network may be operating as a coupled electro-photonic
    coherence system — two channels that are not independent but mutually
    modulating. This would make the network significantly more complex
    than the photon-only model in BIOPHOTON_09 through 09d.

Stub status:
    This simulation is a parametric stub. The coupling function between
    electrical and photonic channels is hypothesised but not yet empirically
    constrained. The stub establishes the model structure and identifies
    the three key parameters that experimental replication would need to
    measure to make this tractable.

    Full simulation awaits BIOPHOTON_09 Validation Epoch experimental data.

Builds on: BIOPHOTON_09, 09b, 09c, 09d
Cross-references: GAIAN_LAWS L5, COEXISTENCE_LAWS CL1, C113 (BCI), C135
© 2026 Kyle Steen — All rights reserved.
"""

import numpy as np
import json
from dataclasses import dataclass
from typing import List, Dict

RNG = np.random.default_rng(seed=45)

# ── Baseline constants ─────────────────────────────────────────────────────
BASELINE_PHOTON_COHERENCE  = 0.72   # from BIOPHOTON_09
BASELINE_ELECTRICAL_AMP    = 0.50   # normalised; 1.0 = maximum observed pulse amplitude
N_NODES                    = 50
N_TRIALS                   = 200

# ── The three stub parameters ───────────────────────────────────────────────
# These are the unknowns that experimental replication must constrain.
# Current values are working hypotheses, not empirical measurements.

ELECTRO_PHOTON_COUPLING_STRENGTH = 0.35   # How strongly electrical amplitude modulates photon coherence
                                            # Range: 0 (independent) to 1 (fully coupled)
                                            # EXPERIMENTAL UNKNOWN: must be measured

ELECTRICAL_LEAD_TIME_MS          = 50.0   # Does electrical signal precede photonic response?
                                            # Positive = electrical leads; negative = photonic leads
                                            # EXPERIMENTAL UNKNOWN: must be measured

COUPLING_DIRECTIONALITY          = 0.70   # 1.0 = electrical drives photonic unidirectionally
                                            # 0.5 = bidirectional, equal influence
                                            # 0.0 = photonic drives electrical
                                            # EXPERIMENTAL UNKNOWN: must be measured


@dataclass
class ChannelState:
    electrical_amplitude: float
    photon_coherence: float
    coupled_coherence: float   # the emergent coherence when both channels are considered
    channel_correlation: float


def simulate_electrophotonic_node(
    electrical_amp: float,
    photon_coh: float,
    coupling_strength: float = ELECTRO_PHOTON_COUPLING_STRENGTH,
    directionality: float = COUPLING_DIRECTIONALITY,
) -> ChannelState:
    """
    Simulate a single node's electro-photonic state.

    The coupling model:
    - Electrical signal modulates photon coherence proportionally to coupling_strength
    - Directionality > 0.5 means electrical has stronger influence on photonic
    - The coupled coherence is the emergent property when both channels are active
    """
    # Electrical modulation of photon coherence
    elec_contribution = coupling_strength * directionality * (electrical_amp - 0.5)
    # Photonic modulation of electrical (bidirectional component)
    photo_contribution = coupling_strength * (1 - directionality) * (photon_coh - 0.5)

    coupled = float(np.clip(
        photon_coh + elec_contribution + photo_contribution
        + RNG.normal(0, 0.02),
        0.0, 1.0
    ))

    correlation = float(np.corrcoef(
        [electrical_amp, electrical_amp + RNG.normal(0, 0.05)],
        [photon_coh, coupled]
    )[0, 1])

    return ChannelState(
        electrical_amplitude=round(electrical_amp, 4),
        photon_coherence=round(photon_coh, 4),
        coupled_coherence=round(coupled, 4),
        channel_correlation=round(correlation, 4),
    )


def simulate_network_electrophotonic(
    coupling_strength: float = ELECTRO_PHOTON_COUPLING_STRENGTH,
    directionality: float = COUPLING_DIRECTIONALITY,
    n_trials: int = N_TRIALS,
) -> Dict:
    """
    Simulate a full network under electro-photonic coupling.
    Compares:
    - Photon-only network coherence (BIOPHOTON_09 model)
    - Electro-photonic coupled network coherence
    """
    photon_only_network = []
    coupled_network = []
    correlations = []

    for _ in range(n_trials):
        # Generate independent electrical and photonic states
        elec_amps = np.clip(RNG.normal(BASELINE_ELECTRICAL_AMP, 0.15, N_NODES), 0, 1)
        photo_cohs = np.clip(RNG.normal(BASELINE_PHOTON_COHERENCE, 0.12, N_NODES), 0, 1)

        # Photon-only (BIOPHOTON_09 baseline)
        base = float(np.mean(photo_cohs))
        amp = 0.65 * (1.0 + 0.3 * (base - 0.5))
        photon_only_network.append(float(np.clip(base * amp, 0, 1)))

        # Electro-photonic coupled
        coupled_states = [
            simulate_electrophotonic_node(e, p, coupling_strength, directionality)
            for e, p in zip(elec_amps, photo_cohs)
        ]
        coupled_cohs = [s.coupled_coherence for s in coupled_states]
        base_c = float(np.mean(coupled_cohs))
        amp_c = 0.65 * (1.0 + 0.3 * (base_c - 0.5))
        coupled_network.append(float(np.clip(base_c * amp_c, 0, 1)))
        correlations.append(float(np.mean([s.channel_correlation for s in coupled_states])))

    mean_photon_only = float(np.mean(photon_only_network))
    mean_coupled = float(np.mean(coupled_network))
    mean_correlation = float(np.mean(correlations))

    return {
        "coupling_strength": coupling_strength,
        "directionality": directionality,
        "mean_photon_only_network_coherence": round(mean_photon_only, 4),
        "mean_coupled_network_coherence": round(mean_coupled, 4),
        "coupling_gain": round(mean_coupled - mean_photon_only, 4),
        "mean_channel_correlation": round(mean_correlation, 4),
        "stub_parameters": {
            "ELECTRO_PHOTON_COUPLING_STRENGTH": coupling_strength,
            "ELECTRICAL_LEAD_TIME_MS": ELECTRICAL_LEAD_TIME_MS,
            "COUPLING_DIRECTIONALITY": directionality,
            "status": "HYPOTHESISED — not empirically constrained",
        },
    }


def run_parameter_sweep() -> List[Dict]:
    """Sweep coupling strength and directionality to map the hypothesis space."""
    results = []
    for cs in [0.10, 0.25, 0.35, 0.50, 0.70]:
        for dr in [0.50, 0.70, 0.90]:
            result = simulate_network_electrophotonic(coupling_strength=cs, directionality=dr)
            results.append(result)
    return results


def format_report(results: List[Dict]) -> str:
    lines = [
        "BIOPHOTON_09e — Electro-Photonic Interface Parameter Sweep (STUB)",
        "=" * 72,
        "IMPORTANT: All parameter values are hypotheses. Not empirically constrained.",
        "-" * 72,
        f"{'Coupling':>9} {'Directionality':>15} {'Photon-Only':>12} {'Coupled':>8} {'Gain':>7} {'Corr':>6}",
        "-" * 72,
    ]
    for r in results:
        lines.append(
            f"{r['coupling_strength']:>9.2f} "
            f"{r['directionality']:>15.2f} "
            f"{r['mean_photon_only_network_coherence']:>12.4f} "
            f"{r['mean_coupled_network_coherence']:>8.4f} "
            f"{r['coupling_gain']:>+7.4f} "
            f"{r['mean_channel_correlation']:>6.4f}"
        )
    lines += [
        "=" * 72,
        "\nThree experimental unknowns (must be measured to constrain this model):",
        "  1. ELECTRO_PHOTON_COUPLING_STRENGTH: How strongly does electrical",
        "     amplitude modulate photon coherence at the cellular level?",
        "  2. ELECTRICAL_LEAD_TIME_MS: Does the electrical signal precede",
        "     the photonic response, and by how much?",
        "  3. COUPLING_DIRECTIONALITY: Is the relationship predominantly",
        "     electrical-drives-photonic, bidirectional, or photonic-drives-electrical?",
        "\nValidation Epoch requirement: simultaneous electrical + biophotonic",
        "measurement in live mycorrhizal network specimens.",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    results = run_parameter_sweep()
    print(format_report(results))
    print("\nRaw JSON:")
    print(json.dumps(results[:3], indent=2))
