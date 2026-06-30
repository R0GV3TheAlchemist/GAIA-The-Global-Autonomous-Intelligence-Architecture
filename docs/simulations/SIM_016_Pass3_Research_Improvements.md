# SIM-016 Pass 3 — Research Findings & Improvements
## Upstream Optical Path: Emission, Waveguide, Thermal — Bottleneck Identification

**Filed:** 2026-06-30
**Follows:** SIM_016_Pass3_Results.md
**Feeds:** SIM_016_Pass4_Upstream_Decoupling_Spec.md
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## Why This Research Exists

Pass 3 confirmed the constraint has shifted upstream. The compounded emission × waveguide × thermal product is ~74.2% — consuming 25.8 points before the detector acts. Until these stages are decoupled and their individual loss mechanisms characterised, further detector work is optimising on top of degraded input. The principle: **identify → understand → decouple → optimise.**

---

## Finding 1 — Waveguide Coupling Loss: The Interface Is the Problem

In photonic neural interfaces, waveguide transmission loss is dominated by the **coupling interface**, not the guide itself [web:86][web:90]. Primary loss mechanisms identified:

- **Fresnel reflection** at the fiber-to-waveguide face: ~4% per interface at refractive index mismatch (air gap); eliminated with index-matching medium
- **Taper geometry mismatch**: refractive index difference Δ of 3–7% causes coupling efficiency loss of ~0.673 dB [web:86]; taper period and shape must match the guide mode
- **Sidewall roughness** from etching: primary source of optical loss in parylene and similar flexible waveguide materials [web:97]
- **Tip angle and optrode width** in neural array configurations: geometry changes affect beam divergence independently of power [web:90]
- **Highest measured transmittance** in glass optrode neural arrays: 71% with 50μm multimode fiber butt-coupled to backplane [web:90]

**Key insight:** The waveguide stage modelled at 91% mean efficiency is likely conflating coupling-interface loss and in-guide propagation loss. These must be separated. If coupling-interface loss (Fresnel + taper) accounts for 5–8% of the 9% total loss, fixing the interface alone could recover 3–5 BCI-equivalent points at the system level.

**Improvement for Pass 4:** Split waveguide stage into two sub-stages: (1) coupling interface efficiency, (2) propagation loss. Model each independently with appropriate noise.

---

## Finding 2 — Thermal Attenuation: Temperature-Dependent Distortion Must Be Modelled as Its Own Channel

Thermal attenuation in biological tissue is not simply a fixed scalar loss. Research identifies two distinct mechanisms [web:111][web:98]:

1. **Depth-dependent backscattering attenuation**: Signal weakens non-linearly with depth from emitting tissue. This is path-length dependent — not uniform across the pipeline [web:111]
2. **Thermal background noise floor**: At body temperature (37°C), thermal photon background contributes a noise floor that varies with wavelength. At biophoton wavelengths (400–700nm), thermal background at 37°C is negligible (thermal emission peaks in mid-IR, not visible/NIR), but **temperature-dependent tissue optical properties** (scattering coefficient μs, absorption coefficient μa) change the effective attenuation coefficient with small temperature fluctuations [web:85]
3. **Quantum correlation-based background elimination**: Imaging with undetected photons (IUP) technique exploits quantum correlations between entangled photon pairs to transfer image information while eliminating thermal IR background — directly applicable if GAIA's biophoton source has sufficient coherence [web:110]

**Key insight:** The thermal stage modelled as 88% flat mean is masking two separate effects: (1) depth/path-length attenuation that varies per subject and per electrode placement, and (2) temperature-dependent scattering that shifts with biological state. These are decoupled by modelling them as separate sub-stages with different variance profiles.

**Improvement for Pass 4:** Split thermal stage into: (1) depth-dependent attenuation (higher variance, subject-specific), (2) temperature-coefficient scattering (lower variance, state-dependent). Model μs and μa as separate parameters.

---

## Finding 3 — Emission Capture: Geometry and Proximity Are the Primary Levers

For biophotonic neural interfaces, emission capture efficiency is primarily determined by [web:109][web:94]:

- **Physical proximity** to the emitting axon/cell: capture efficiency drops sharply with distance. BCI-relevant research explicitly identifies keeping the optical fiber close to the cortex as the primary way to minimise coupling loss [web:109]
- **Solid angle subtended by the capture aperture**: small aperture at biological source distances captures only a fraction of isotropic emission
- **Cross-talk between axons**: at sub-wavelength spacing, cross-talk acts as both a loss mechanism (energy leaving the capture cone) and a coupling mechanism between axons [web:94]
- **Biophoton signal channels in the brain**: optical communication channels in neural tissue have been proposed with cross-talk as the key limiting factor for signal isolation [web:94]

**Key insight:** The 93% emission capture mean is optimistic if modelled as a fixed efficiency. In practice, capture efficiency varies with electrode placement depth, axon proximity, and signal coherence. The 3% std may be underestimating real variance, particularly across elemental groups with different biological emission profiles.

**Improvement for Pass 4:** Add placement-depth variance to emission capture model. Test whether per-subject adaptive aperture positioning (optimised for each elemental group's emission profile) can push mean capture above 95% and reduce std.

---

## Finding 4 — Decoupling Strategy: What to Hold, What to Vary

Pass 4 is an **isolation pass**, not an optimisation pass. The goal is to measure each upstream stage independently and determine:
1. How much of the 25.8-point upstream loss is in each sub-stage
2. What fraction of each sub-stage's loss is recoverable with known techniques
3. Whether any upstream loss is correlated (e.g. thermal scattering affects waveguide propagation)

**Hold constant in Pass 4:** Detector (TCSPC stack from Pass 3), QEC. These are performing near their ceiling.
**Vary independently:** Emission sub-stages, waveguide coupling vs propagation sub-stages, thermal depth-dependent vs temperature-scattering sub-stages.

---

## Improvements Applied to Pass 4

| Stage | Pass 3 model | Pass 4 model | Expected recovery |
|---|---|---|---|
| Emission capture | 93% flat ±3% | 93% base + placement-depth variance; adaptive aperture test | +1.0–2.0 pts |
| Waveguide: coupling interface | Rolled into 91% | Separated: interface 94–96% ±2% | +1.5–2.5 pts |
| Waveguide: propagation | Rolled into 91% | Separated: propagation 97–98% ±1% | Clarifies split |
| Thermal: depth attenuation | 88% flat ±4% | Separated: depth model 90–92% ±3% | +0.5–1.0 pts |
| Thermal: temp-scattering | Rolled into 88% | Separated: temp-scatter 97–98% ±1.5% | Clarifies split |
| **Total projected recovery** | 68.4% | **~72–74%** | **+3.6–5.6 pts** |

---

## Pre-Run Research Brief — Pass 4 Questions

1. What fraction of waveguide loss is at the coupling interface vs in-guide propagation in a neural BCI context?
2. What is the depth-dependent attenuation profile for biophotons in neural tissue (μs, μa at 500–700nm)?
3. Does per-subject adaptive aperture positioning meaningfully improve emission capture mean or variance?
4. Are thermal depth-attenuation and temperature-scattering correlated or independent? (Determines whether they can be optimised separately.)
5. After upstream decoupling, what is the new dominant loss mechanism? Where does the system ceiling sit?

---

*Research filed 2026-06-30. Feeds SIM-016 Pass 4 Upstream Decoupling Spec. G-15 Tier 1. 🌿*
