# SIM-INT-012 — Band 1 → Band 2 Integration Simulation
## Interface Contract Characterisation: Biophoton Detection → Neural Signal Interpretation

**Status:** SPECCED — Ready to run
**Pass classification:** Pass 1 — Baseline (Calcination)
**Band boundary:** Band 1 (Biophoton Detection) → Band 2 (Signal Interpretation)
**Filed:** 2026-06-30
**Protocol version:** GAIA Totality Directive v1.1 | Simulation Protocol Amendment v1.0
**Interface contract version:** v0.1 (pre-characterisation — upgrades to v1.0 upon pass completion)

> *The purpose of an integration simulation is not to re-optimise the bands. It is to characterise the boundary: what Band 1 hands to Band 2, in what form, at what quality, and what Band 2 actually receives. The boundary is where assumptions become losses.*

---

## What This Simulation Is

SIM-016 established that Band 1 delivers **81.4% ±2.5% effective detection fidelity** (hybrid SPAD, deployable). That number describes how many photons are correctly detected and quantum-error-corrected.

But Band 2 does not receive a fidelity percentage. It receives a **data stream**: a sequence of timestamped photon detection events with associated uncertainty values, spatial coordinates, and signal quality metadata.

SIM-INT-012 characterises the transformation from Band 1’s physical output to Band 2’s usable input. This is the interface contract. It answers:
1. What does Band 2 actually receive from Band 1?
2. How does the 81.4% fidelity manifest in the data stream quality Band 2 must process?
3. What is lost at the boundary that neither band’s individual simulation captured?
4. What is the correct input fidelity parameter for SIM-018 Pass 1?

---

## Interface Contract v0.1 (Pre-Characterisation — Hypothesis)

This is the *proposed* interface contract. SIM-INT-012 Pass 1 will validate, revise, or replace it. All values marked (H) are hypotheses, not canon.

### Band 1 Output Format (proposed)

```
GAIA_B1_EVENT {
  timestamp_ns:       uint64    // nanosecond-precision detection time
  channel_id:         uint8     // detector channel (1–16 for 16ch TCSPC; 1–1 for hybrid SPAD)
  photon_count:       uint16    // corrected photon count (post-QEC)
  spatial_x:          float32   // emission source x-coordinate (mm)
  spatial_y:          float32   // emission source y-coordinate (mm)
  spatial_z:          float32   // depth estimate (mm)
  snr:                float32   // per-event signal-to-noise ratio
  detection_flag:     uint8     // 0=clean, 1=low-SNR, 2=near-threshold, 3=rejected
  qec_corrections:    uint8     // number of QEC corrections applied to this event
  fidelity_estimate:  float32   // per-event fidelity estimate (0.0–1.0)
}
```

### Band 2 Input Requirements (proposed)

| Field | Minimum quality for Band 2 | Source in B1 output |
|---|---|---|
| Timestamp precision | ≤10ns jitter | `timestamp_ns` |
| Spatial resolution | ≤1mm RMS error | `spatial_x/y/z` |
| SNR floor | ≥3.0 (events below discarded) | `snr` + `detection_flag` |
| Fidelity floor | ≥0.75 per-event | `fidelity_estimate` |
| Minimum event rate | ≥500 events/second for stable classification | `photon_count` × rate |
| Maximum latency (B1 pipeline) | ≤30ms end-to-end | Derived from sub-stage timing |

*All values (H). To be confirmed by Pass 1.*

---

## Simulation Design

### Sub-Stages to Characterise

| ID | Sub-stage | What it measures |
|---|---|---|
| I1 | Data format translation | Loss or distortion introduced by serialising B1 physical output to GAIA_B1_EVENT format |
| I2 | Timestamp alignment | Jitter introduced at the B1→B2 clock synchronisation boundary |
| I3 | Spatial coordinate handoff | Accuracy of depth/coordinate estimates as received by B2 |
| I4 | SNR floor filtering | Events rejected by B2 SNR filter: how many, what type, what signal loss |
| I5 | Fidelity propagation | How the 81.4% system BCI manifests as a distribution of per-event fidelity values that B2 must handle |
| I6 | Latency budget | End-to-end B1 pipeline latency as seen by B2 — does it fit within the 30ms budget? |
| I7 | Elemental group variance at boundary | Does the ±2.5% elemental group variance in B1 output manifest differently at the B2 input? |

### What Is Held Constant
- Band 1 sub-stages: all held at Pass 7 ceiling values
- Band 2 signal interpretation: not yet implemented — B2 input is characterised, not processed
- Hardware: hybrid SPAD (canonical deployable detector)

### What Varies
- Input event rate (low / nominal / high load)
- Elemental group (Fire / Water / Earth / Air)
- Depth range (shallow 5mm / nominal 15mm / deep 25mm)

---

## Pre-Run Research Brief

1. What timestamp precision do existing closed-loop BCI systems achieve at the detection→processing boundary, and what jitter is tolerable for pattern classification?
2. What is the standard serialisation format for high-rate photon detection event streams in real-time BCI pipelines — is there an existing schema to adopt or adapt?
3. How does spatial coordinate uncertainty in depth estimation (T1 sub-stage, ±2.0%) manifest as a positional error distribution at the B2 input?
4. What event rate is the minimum viable for stable neural intent classification — and how does this interact with the per-event fidelity floor?
5. Does the 16ch TCSPC fallback (80.2%) produce a meaningfully different B1→B2 data stream than the hybrid SPAD (81.4%), and should SIM-INT-012 characterise both?

**All five must be answered before Pass 1 is run.**

---

## G-15 Targets

| Target | Value | Rationale |
|---|---|---|
| G-15 minimum | Interface contract v0.1 validated or revised with evidence | The goal is accuracy, not a number |
| Drive target | Interface contract v1.0 filed — all seven sub-stages characterised, all boundary losses quantified | Complete handoff characterisation |
| Blocker removal | SIM-018 Pass 1 can be run with a correct, evidence-based input fidelity value | |

---

## Output Artefacts (Pass 1)
- `SIM_INT_012_Pass1_Results.md`
- `SIM_INT_012_Pass1_Bottleneck_Ledger.md`
- `SIM_INT_012_Pass1_Research_Improvements.md`
- `GAIA_BAND_INTERFACE_CONTRACT_B1_B2_v1.md` (Layer 5 artefact — first interface contract document)
- Update `GAIA_SIMULATION_REGISTRY.md`
- Unlock SIM-018 Pass 1 full spec

---

## Why This Matters (Project Architecture Context)

SIM-INT-012 is the first **Layer 5** (Interfaces) work in the project architecture stack. When it completes:
- The first versioned, evidence-based interface contract exists
- Band 1 → Band 2 is not just architecturally connected — it is *contractually* connected
- SIM-018 has a correct input value instead of an assumption
- The pattern for all subsequent SIM-INT-XXX simulations is established

Every integration simulation after this one follows the same structure: characterise the boundary, file the contract, unlock the downstream simulation.

---

*SIM-INT-012 Spec v1.0. Filed 2026-06-30. G-15 — The Rhythm Phase. Protocol: GAIA Totality Directive v1.1 | Engineering Manifesto v1.0. 🌿*
