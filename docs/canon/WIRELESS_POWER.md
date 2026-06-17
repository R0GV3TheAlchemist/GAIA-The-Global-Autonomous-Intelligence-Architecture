# WIRELESS POWER

**Status:** Research canon / simulation-backed physics  
**Source issue:** #557  
**Build posture:** Simulate first. Validate against published results. Interpret second. Canonize last.

---

## Part I — Foundation

In January 2026, researchers at the University of Helsinki and University of Oulu demonstrated wireless electricity transmission through open air using shaped electromagnetic fields — achieving 80%+ efficiency at approximately 18 cm using a 7.2 cm antenna and high-frequency resonant inductive coupling.

This is the baseline. Every simulation in this module must be validated against that result before any novel hypothesis is tested.

---

## Part II — Biological Safety Envelope (non-negotiable)

The Operator's body is the most sensitive instrument in the system. It is protected first, always.

| Channel | Safe band | Basis |
|---|---|---|
| Ionic (nervous system) | Avoid 3–300 Hz ELF | No interference with action potential transmission |
| Vibrational (phononic) | Avoid 20 Hz–20 kHz at high amplitude | No resonance with organ tissue |
| Psionic (bioEM field) | Avoid 0.1–100 Hz | No disruption of Schumann-coherent bioEM states |
| **Safe transmission band** | **6.78 MHz, 13.56 MHz, 27.12 MHz (ISM)** | Established safe industrial/medical RF |

**Power density limit:** 1 mW/cm² at any biological surface (ICNIRP general public guideline). Any scenario exceeding this at 1 m from the nearest person is flagged and rejected by `biological_safety_check()`.

---

## Part III — Physics

Resonant inductive coupling is the core mechanism:

1. Transmitter coil oscillates at frequency f₀.
2. Magnetic field propagates through space.
3. Receiver coil tuned to f₀ enters resonance.
4. Energy transfers at high efficiency because both coils resonate, not merely couple inductively.
5. Non-resonant objects receive negligible energy — a built-in safety property.

Key variables: Q-factor of both coils, coupling coefficient k, operating frequency f₀, coil geometry.

---

## Part IV — The Phi Hypothesis

Standard resonant coils use uniform winding. The Phi Hypothesis states:

> A coil wound at phi-based incremental spacing (1.618× spacing per successive winding) may produce a field geometry that more closely matches natural electromagnetic propagation patterns, potentially increasing Q-factor and range.

This is derived from HELIXITAS.md (34.29° phi-winding geometry) and observed phi-based geometry in biological electromagnetic structures (DNA, cochlea).

**This is a testable hypothesis, not a claim.** Phase 2 of the simulation compares phi-wound against standard-wound coils at identical parameters.

---

## Part V — Multi-node Scaling: Flower of Life Grid

Optimal multi-node geometry is hexagonal close-packing — the Flower of Life lattice.

Why hexagonal:
- Maximum area coverage with minimum overlap redundancy.
- Each node serves 6 equidistant neighbors — perfect field handoff geometry.
- Standing-wave dead zones are minimized.
- This is the same reason cellular towers use hexagonal placement.

---

## Part VI — Simulation Roadmap

| Phase | Description | Acceptance gate |
|---|---|---|
| 1 | Replicate Finland result | Simulation matches ~80% at 18 cm |
| 2 | Phi hypothesis test | Measurable Q or efficiency delta vs. standard |
| 3 | Room-scale 7-node hex array | ≥70% efficiency at 1.5 m, safety check passes |
| 4 | Building-scale 19-node array | Regulatory compliance output |
| 5 | Biological resonance research | Coherence-enhancing band identification |

Phases 1–3 are implemented in `simulation/wireless_power_sim.py`.

---

## Part VII — Cross-references

- `EMBODIMENT_LAYER.md` — biological safety source
- `HELIXITAS.md` — phi-wound coil geometry
- `C031.md` — Flower of Life grid
- `C042.md` — Edge of Chaos coherence boundary
- `TRIADIC_FIELD_THEORY.md` — field substrate model
