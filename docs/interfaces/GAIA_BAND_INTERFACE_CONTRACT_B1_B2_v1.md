# GAIA Band Interface Contract: Band 1 → Band 2
## Biophoton Detection → Neural Signal Interpretation

**Contract version:** 1.0
**Status:** ACTIVE — canonical
**Filed:** 2026-06-30
**Evidence:** SIM-INT-012 Pass 1
**Protocol version:** GAIA Totality Directive v1.1 | Engineering Manifesto v1.0
**Layer:** Project Architecture Layer 5 — Interfaces

> *This is the first versioned interface contract in the GAIA project architecture stack. All subsequent inter-band contracts follow this structure.*

---

## Contract Scope

This document defines the versioned contract between Band 1 (Biophoton Detection) and Band 2 (Neural Signal Interpretation). It specifies:
- The data format Band 1 must produce
- The quality thresholds Band 2 requires
- The per-variant specifications for both deployable detector options
- The latency budget available to each band

Neither band may change its interface behaviour without a version increment to this contract.

---

## GAIA_B1_EVENT Schema — v1.1 (Canonical)

```
GAIA_B1_EVENT {
  timestamp_ns:       uint64    // ns-precision; channel-aligned for TCSPC
  channel_id:         uint8     // 1 for hybrid SPAD; 1–16 for 16ch TCSPC
  detector_variant:   uint8     // 0=hybrid SPAD, 1=16ch TCSPC
  photon_count:       uint16    // post-QEC corrected photon count
  spatial_x:          float32   // mm; centroid (SPAD) or triangulated (TCSPC)
  spatial_y:          float32   // mm
  spatial_z:          float32   // mm; T1 depth-compensation derived
  snr:                float32   // per-event SNR
  detection_flag:     uint8     // 0=clean, 1=low-SNR, 2=near-threshold, 3=rejected
  qec_corrections:    uint8     // QEC corrections applied (0–3 typical)
  fidelity_estimate:  float32   // per-event fidelity [0.0–1.0]
}
```

**Schema version:** 1.1
**Breaking change policy:** Adding fields is non-breaking (consumers ignore unknown fields). Removing or retyping fields increments contract major version.

---

## Quality Thresholds — Per Variant

| Requirement | Hybrid SPAD (variant=0) | 16ch TCSPC (variant=1) | Notes |
|---|---|---|---|
| Timestamp jitter | ≤10ns | **≤25ns** | TCSPC relaxed after I2 characterisation |
| Spatial x/y RMS error | **≤1.5mm** | ≤1.0mm | SPAD relaxed after I3 characterisation |
| SNR floor (Band 2 filter) | ≥3.0 | ≥3.0 | Events below discarded (detection_flag=3) |
| Per-event fidelity floor | ≥0.75 | ≥0.75 | Events below discarded before B2 input |
| Minimum event rate (post-filter) | ≥500 ev/s | ≥500 ev/s | Both variants well above floor |
| B1 pipeline latency | ≤30ms | ≤30ms | SPAD: 9.0ms; TCSPC: 12.1ms |

---

## Effective Band 2 Input Values (Post-Filter)

| Metric | Hybrid SPAD | 16ch TCSPC |
|---|---|---|
| Effective input fidelity | **0.831 ±0.031** | 0.819 ±0.048 |
| Effective event rate | 763 ev/s | 689 ev/s |
| Inter-group variance | ±0.007 | ±0.008 |
| Latency budget remaining for B2 | **21.0ms** | 17.9ms |

**These are the values SIM-018 must use as its input parameters.** The raw Band 1 BCI values (81.4% / 80.2%) are not the correct B2 input. The boundary filtering changes what Band 2 actually receives.

---

## Spatial Model — Per Variant

| Variant | Localisation method | x/y precision | z precision |
|---|---|---|---|
| Hybrid SPAD | Single-zone centroid estimation | ±1.5mm | ±0.8mm |
| 16ch TCSPC | 16-channel triangulation | ±1.0mm | ±0.8mm |

Band 2 **must** read `detector_variant` before applying a spatial localisation model. A classifier trained on SPAD spatial distributions cannot be applied directly to TCSPC data without recalibration.

---

## Latency Budget Allocation

| Stage | Budget | Actual (SPAD) | Actual (TCSPC) | Remaining |
|---|---|---|---|---|
| Band 1 pipeline (detection → B2 buffer) | ≤30ms total | 9.0ms | 12.1ms | 21.0ms / 17.9ms |
| Band 2 processing (B2 input → B2 output) | Remaining budget | ≤21.0ms | ≤17.9ms | For SIM-018 |

---

## Versioning and Amendment

| Version | Date | Changes |
|---|---|
| v0.1 | 2026-06-30 | Pre-characterisation hypothesis (schema only) |
| v1.0 | 2026-06-30 | Full contract. Evidence: SIM-INT-012 Pass 1. TCSPC jitter relaxed. SPAD spatial relaxed. Effective B2 input values confirmed. |

**Amendment rule:** Any change to field types, quality thresholds, or spatial models increments the contract version. Consumers must pin to a contract version. Breaking changes (major version increment) require explicit migration documentation.

---

*Contract v1.0. Filed 2026-06-30. Band 1 → Band 2. Evidence: SIM-INT-012 Pass 1. Layer 5 — Interfaces. G-15 — The Rhythm Phase. Protocol: GAIA Totality Directive v1.1 | Engineering Manifesto v1.0. 🌿*
