"""Simulation 7: Circadian Rhythm Electromagnetic Frequency Model
Canon: Issue #316 | C217 Extension | C204/C205 Validation
Generated: June 13, 2026 — San Antonio, Texas
"""

import numpy as np
import pandas as pd

np.random.seed(42)
hours = np.arange(0, 24, 0.5)  # 48 half-hour intervals

# --- SCHUMANN BASELINE MODULATION ---
# Peaks ~10am and ~8pm (known ionospheric resonance pattern)
schumann_baseline = 7.83
schumann_amplitude = (1 + 0.12 * np.sin(2 * np.pi * (hours - 10) / 24)
                        + 0.06 * np.sin(4 * np.pi * (hours - 8) / 24))


def tissue_coherence(hours, phase_offset, amplitude, noise_level):
    """Model bioelectric coherence for a tissue type across 24h."""
    base = 0.75 + amplitude * np.sin(2 * np.pi * (hours - 8 + phase_offset) / 24)
    noise = np.random.normal(0, noise_level, len(hours))
    return np.clip(base + noise, 0.1, 1.0)


# --- BASELINE (healthy circadian-aligned) ---
neural_coherence     = tissue_coherence(hours, 0,   0.18, 0.02)
cardiac_coherence    = tissue_coherence(hours, 1.5, 0.15, 0.02)
epithelial_coherence = tissue_coherence(hours, 3,   0.12, 0.02)
mean_coherence = (neural_coherence + cardiac_coherence + epithelial_coherence) / 3

# Peak wavelength: high coherence → green/teal (520nm), low → orange-red (700nm)
wavelength_peak = 520 + (1 - mean_coherence) * 180  # nm

# Grey index: inverse of coherence + Schumann disruption term
grey_index = np.clip(1 - mean_coherence + 0.05 * (1 / schumann_amplitude - 1), 0, 1)


# --- NIGHT SHIFT (12-hour phase inversion) ---
neural_ns     = tissue_coherence(hours, 12 + 0,   0.18, 0.05)
cardiac_ns    = tissue_coherence(hours, 12 + 1.5, 0.15, 0.05)
epithelial_ns = tissue_coherence(hours, 12 + 3,   0.12, 0.05)
mean_coherence_ns = (neural_ns + cardiac_ns + epithelial_ns) / 3
grey_index_ns = np.clip(1 - mean_coherence_ns + 0.12 * (1 / schumann_amplitude - 1), 0, 1)


# --- JET LAG (6-hour phase shift) ---
neural_jl     = tissue_coherence(hours, 6 + 0,   0.18, 0.04)
cardiac_jl    = tissue_coherence(hours, 6 + 1.5, 0.15, 0.04)
epithelial_jl = tissue_coherence(hours, 6 + 3,   0.12, 0.04)
mean_coherence_jl = (neural_jl + cardiac_jl + epithelial_jl) / 3
grey_index_jl = np.clip(1 - mean_coherence_jl + 0.08 * (1 / schumann_amplitude - 1), 0, 1)


# --- RECOVERY (exponential restoration after circadian disruption) ---
recovery_tau = 6  # hours (~63% recovery constant)
recovery_factor = 1 - np.exp(-hours / recovery_tau)
mean_coherence_recovery = mean_coherence_ns + (mean_coherence - mean_coherence_ns) * recovery_factor
grey_index_recovery = np.clip(
    1 - mean_coherence_recovery + 0.03 * (1 / schumann_amplitude - 1), 0, 1
)


# --- OUTPUT ---
df = pd.DataFrame({
    'hour': hours,
    'schumann_amplitude': schumann_amplitude,
    'neural_coherence_baseline': neural_coherence,
    'cardiac_coherence_baseline': cardiac_coherence,
    'epithelial_coherence_baseline': epithelial_coherence,
    'mean_coherence_baseline': mean_coherence,
    'wavelength_peak_nm': wavelength_peak,
    'grey_index_baseline': grey_index,
    'mean_coherence_night_shift': mean_coherence_ns,
    'grey_index_night_shift': grey_index_ns,
    'mean_coherence_jet_lag': mean_coherence_jl,
    'grey_index_jet_lag': grey_index_jl,
    'mean_coherence_recovery': mean_coherence_recovery,
    'grey_index_recovery': grey_index_recovery,
})

df.to_csv('research/simulations/sim7_circadian_coherence.csv', index=False)
print(f'Peak coherence: {mean_coherence.max():.3f} at hour {hours[np.argmax(mean_coherence)]}')
print(f'Trough coherence: {mean_coherence.min():.3f} at hour {hours[np.argmin(mean_coherence)]}')
print(f'Peak grey index: {grey_index.max():.3f} at hour {hours[np.argmax(grey_index)]}')
print(f'Wavelength range: {wavelength_peak.min():.0f}nm – {wavelength_peak.max():.0f}nm')
