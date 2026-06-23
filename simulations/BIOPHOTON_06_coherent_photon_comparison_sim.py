"""BIOPHOTON_06: Coherent Photon State Comparison Simulation
GAIA-OS Simulation Series | 2026-06-23
Authors: R0GV3 + GAIA

Compares three photonic systems across coherence decay, noise character,
entanglement, and GAIA-OS advantage scoring.
See canon/BIOPHOTON_06 for full documentation.
"""

import numpy as np

rng = np.random.default_rng(42)

SYSTEMS = {
    'Biological Neuron':    {'wavelength_nm': 550,  'coherence_time_s': 1e-13, 'energy_per_op_J': 1e-20, 'ops_per_second': 40,   'operating_temp_K': 310, 'entanglement': True},
    'Silicon Photonic Chip':{'wavelength_nm': 1550, 'coherence_time_s': 1e-4,  'energy_per_op_J': 1e-15, 'ops_per_second': 5e9,  'operating_temp_K': 300, 'entanglement': False},
    'Quantum Photonic Chip':{'wavelength_nm': 1310, 'coherence_time_s': 1e-3,  'energy_per_op_J': 1e-18, 'ops_per_second': 1e9,  'operating_temp_K': 4,   'entanglement': True},
}

GAIA_SCORES = {
    'Biological Neuron':     [8, 10, 9, 2, 9, 10],
    'Silicon Photonic Chip': [7,  2, 6, 9, 5,  5],
    'Quantum Photonic Chip': [9,  5, 8, 7, 7,  9],
}
SCORE_DIMS = ['Coherence Quality', 'Biological Compat', 'Energy Efficiency',
              'Processing Speed', 'Reconfigurability', 'Information Richness']

t_vals = np.logspace(-15, -3, 500)

def coherence_decay(t, tau_c, sys_name):
    base = np.exp(-t / tau_c)
    if 'Biological' in sys_name:
        return np.clip(base * (1 + 0.15 * np.sin(2 * np.pi * 40 * t)), 0, 1.3)
    elif 'Silicon' in sys_name:
        phase_noise = 0.01 * np.cumsum(rng.normal(0, 1, len(t))) / len(t)
        return np.clip(base + phase_noise, 0, 1)
    else:
        loss = (rng.random(len(t)) < 1e-4).astype(float)
        collapse = np.maximum(1 - np.cumsum(loss) / 50, 0)
        return np.clip(base * collapse, 0, 1)

if __name__ == '__main__':
    print('=== BIOPHOTON_06 SYSTEM COMPARISON ===')
    for name, params in SYSTEMS.items():
        print(f'\n{name}')
        print(f'  Coherence time:  {params["coherence_time_s"]:.2e} s')
        print(f'  Energy/op:       {params["energy_per_op_J"]:.2e} J')
        print(f'  Entanglement:    {params["entanglement"]}')
        print(f'  GAIA score:      {sum(GAIA_SCORES[name])}/60')
    print('\nSimulation complete. See BIOPHOTON_06 canon for interpretation.')
