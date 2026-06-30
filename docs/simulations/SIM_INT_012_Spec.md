# SIM-INT-012 — Band 1 → Band 2 Integration Simulation
## Interface Contract Characterisation: Biophoton Detection → Neural Signal Interpretation

**Status:** COMPLETE — Pass 1 done
**Pass classification:** Pass 1 — Baseline (Calcination)
**Band boundary:** Band 1 → Band 2
**Filed:** 2026-06-30
**Spec version:** 1.1 (detector_variant field added after Q5 analysis)
**Protocol version:** GAIA Totality Directive v1.1 | Simulation Protocol Amendment v1.0 | Engineering Manifesto v1.0

---

## Pre-Run Research Brief — Resolved

| Q | Question | Answer | Trust level |
|---|---|---|---|
| Q1 | Timestamp jitter tolerance | ≤10ns — well-established for TCSPC-class systems | High — run with hypothesis |
| Q2 | Serialisation format | GAIA_B1_EVENT custom schema — cleaner than legacy BCI formats | High — run with hypothesis |
| Q3 | Spatial coordinate uncertainty | T1 ±2.0% bounded, well-characterised; straightforward propagation | High — run with hypothesis |
| Q4 | Minimum event rate | 500 events/s working floor — load-bearing only in SIM-018 | Medium — working assumption |
| Q5 | TCSPC vs SPAD stream differences | Structurally compatible but semantically different — spatial model and timestamp alignment differ; `detector_variant` field required | Worked through — schema updated |

---

## GAIA_B1_EVENT Schema (v1.1 — Final)

```
GAIA_B1_EVENT {
  timestamp_ns:       uint64    // nanosecond-precision, channel-aligned for TCSPC
  channel_id:         uint8     // 1 for hybrid SPAD; 1–16 for 16ch TCSPC
  detector_variant:   uint8     // 0=hybrid SPAD, 1=16ch TCSPC
  photon_count:       uint16    // corrected photon count (post-QEC)
  spatial_x:          float32   // emission source x-coordinate (mm)
  spatial_y:          float32   // emission source y-coordinate (mm)
  spatial_z:          float32   // depth estimate (mm)
  snr:                float32   // per-event signal-to-noise ratio
  detection_flag:     uint8     // 0=clean, 1=low-SNR, 2=near-threshold, 3=rejected
  qec_corrections:    uint8     // number of QEC corrections applied
  fidelity_estimate:  float32   // per-event fidelity estimate (0.0–1.0)
}
```

Schema version: **v1.1**. The `detector_variant` field was added after structured Q5 analysis confirming that spatial localisation model and timestamp alignment burden differ materially between variants.

---

*Spec v1.1. SIM-INT-012. 2026-06-30. 🌿*
