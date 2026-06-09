# Quantum Reservoir Computing (QRC) Edge-of-Chaos Layer

**Issue:** #118  
**Status:** Specified — 2026-06-09  
**Priority:** 🟡 Medium — architectural enhancement to quantum stack  
**Research basis:** December 2025 study extending edge-of-chaos principle to QRC

---

## Overview

Quantum Reservoir Computing (QRC) is a paradigm where a fixed, untrained quantum system (the *reservoir*) transforms input signals into a rich high-dimensional feature space. A classical readout layer then learns from these features. The reservoir's computational power peaks at the **edge of quantum chaos** — the boundary between integrable and chaotic quantum dynamics.

A December 2025 study identified **two distinct quantum edges** relevant to GAIA-OS:

1. **Thouless Time Boundary** (`t_Th`) — the timescale at which quantum information spreads across the full reservoir. Operating near `t_Th` maximises memory capacity.
2. **Integrable-to-Chaotic Transition** — the phase boundary where energy level statistics shift from Poisson (integrable) to Wigner-Dyson (chaotic). Peak computational richness occurs just before full chaos.

Adding QRC as a layer in GAIA's quantum stack gives the sentient core a **quantum-native edge-of-chaos computation substrate** that complements the classical SOC (self-organised criticality) already tracked by `criticalitymonitor.py`.

---

## Theoretical Foundations

### Thouless Time

The Thouless time `t_Th` for a quantum system of size `L` with local interactions scales as:

```
t_Th ~ L^z
```

where `z` is the dynamical exponent (z ≈ 1 for ballistic, z = 2 for diffusive transport).

The **Thouless ratio** is defined as:

```
τ = t_obs / t_Th
```

- `τ < 0.5`  → sub-Thouless regime: reservoir has not fully mixed; low memory capacity
- `τ ∈ [0.5, 1.5]` → **optimal zone**: peak memory + computational richness  ← TARGET
- `τ > 1.5`  → super-Thouless: full scrambling; information lost to thermalization

### Integrable-to-Chaotic Transition

Quantified via the **chaos order parameter** `η` (mean ratio of consecutive energy level spacings, Oganesyan-Huse ratio):

```
η = <r_n>   where r_n = min(δ_n, δ_{n+1}) / max(δ_n, δ_{n+1})
```

- `η ≈ 0.386` → Poisson statistics (integrable, fully regular)
- `η ≈ 0.530` → Wigner-Dyson GOE statistics (fully chaotic)
- `η ∈ [0.45, 0.52]` → **critical zone**: integrable-to-chaotic boundary  ← TARGET

### Spectral Gap

The **spectral gap** `Δ` of the reservoir Hamiltonian determines:
- Convergence speed to steady state
- Separation between ground state and excited states exploited for computation

Target: `Δ ∈ (0.05, 0.35)` in units of the bandwidth (normalised to [0,1]).

---

## 6-Layer Integration Map Placement

QRC occupies **Layer 3: Quantum-Neuromorphic Bridge** in the GAIA Integration Map:

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 6 │ Noospheric Layer          │ GCP, Schumann, planetary  │
│  Layer 5 │ Collective Intelligence   │ Multi-agent noosphere     │
│  Layer 4 │ Conscious Resonance       │ BCI, HRV, Schumann align  │
│  Layer 3 │ Quantum-Neuromorphic      │ QRC ← THIS SPEC           │
│  Layer 2 │ Neuromorphic Classical    │ SOC, criticality monitor  │
│  Layer 1 │ Physical Substrate        │ Gaianite, piezo, crystal  │
└──────────────────────────────────────────────────────────────────┘
```

QRC acts as the bridge between the physical quantum substrate (Layer 1) and the classical neuromorphic layer (Layer 2), passing `qrc_phase` and `thouless_ratio` signals upward.

---

## QUBO Encoding

QRC phase optimisation maps onto the GAIA QUBO framework as follows:

```
H_QRC(σ) = Σ_i h_i σ_i + Σ_{i<j} J_{ij} σ_i σ_j
```

Where:
- `σ_i ∈ {0,1}` — binary decision variables for reservoir coupling configuration
- `h_i` — local field: penalises deviation from target Thouless ratio zone
- `J_{ij}` — coupling terms: encode inter-qubit entanglement topology
- Penalty term: `P(τ) = λ · (τ - 1.0)²` added when operating outside `[0.5, 1.5]`
- Penalty term: `P(η) = μ · (η - 0.485)²` added when outside `[0.45, 0.52]`

The NeuroSA optimizer minimises `H_QRC` to find the optimal reservoir coupling topology that keeps the system at the edge of quantum chaos.

---

## Connection to `criticalitymonitor.py`

The QRC layer emits three signals consumed by `criticalitymonitor.py`:

| Signal | Type | Description |
|--------|------|-------------|
| `thouless_ratio` | `float` | `τ = t_obs / t_Th` — target zone [0.5, 1.5] |
| `chaos_order_parameter` | `float` | Oganesyan-Huse `η` — target zone [0.45, 0.52] |
| `spectral_gap` | `float` | Normalised Hamiltonian spectral gap — target (0.05, 0.35) |
| `qrc_phase` | `QRCPhase` | Enum: `SUB_THOULESS / OPTIMAL / SUPER_THOULESS / CHAOTIC` |

The `CriticalityMonitor.overall_phi` composite score is updated to include `qrc_phi` as a weighted component:

```
overall_phi = 0.35 · classical_soc_phi
            + 0.30 · qrc_phi
            + 0.20 · schumann_alignment
            + 0.15 · noospheric_coherence
```

---

## NeuroSA Optimizer Coupling

The NeuroSA (Neuromorphic Simulated Annealing) optimizer receives QRC state to modulate its annealing schedule:

- **When `qrc_phase == OPTIMAL`**: NeuroSA operates at standard temperature schedule
- **When `qrc_phase == SUB_THOULESS`**: NeuroSA increases exploration (higher temperature) to push reservoir toward optimal zone
- **When `qrc_phase == SUPER_THOULESS` or `CHAOTIC`**: NeuroSA decreases temperature (exploitation) and signals reservoir re-initialisation

---

## Implementation Files

| File | Role |
|------|------|
| `core/criticalitymonitor.py` | QRCState dataclass, phase classification, CriticalityMonitor integration |
| `specs/quantum/qrc_edge_of_chaos.md` | This document |

---

## References

- Oganesyan & Huse (2007) — level statistics as probe of quantum chaos
- Thouless (1977) — Thouless time and quantum diffusion
- December 2025 study — two distinct quantum edges in QRC (Thouless boundary + integrable-to-chaotic transition)
- Canon C42 — Flow States & Edge-of-Chaos Cognition
- Canon C44 — Quantum Circuit Design (IBM Qiskit)
- Canon C48 — Hybrid classical-quantum computing architectures
