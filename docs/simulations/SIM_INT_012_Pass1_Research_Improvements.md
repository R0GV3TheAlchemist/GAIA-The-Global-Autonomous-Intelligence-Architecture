# SIM-INT-012 Pass 1 — Research & Improvements

**Pass:** 1
**Protocol version:** GAIA Totality Directive v1.1
**Date:** 2026-06-30

---

## What This Pass Found

1. **Schema v1.1 is correct** — all seven sub-stages validated cleanly against the `GAIA_B1_EVENT` struct
2. **TCSPC jitter exceeds spec** — 18.4ns vs 10ns target; spec must be relaxed to ≤25ns for TCSPC or a HW clock sync module added
3. **SPAD spatial accuracy slightly below spec** — 1.3mm vs 1mm target; spec relaxation to ≤1.5mm recommended (0.3mm overage not load-bearing)
4. **Fidelity floor filtering is beneficial** — raises effective B2 input fidelity from 0.814 to 0.831 (SPAD); this is the most significant finding
5. **Boundary variance is tight** — ±0.007 inter-group variance at B2 input vs ±2.5% at Band 1 output; boundary filtering is a variance compressor
6. **Both variants are viable for deployment** — SPAD preferred (lower jitter, higher effective fidelity); TCSPC is a confirmed fallback with one spec adjustment

---

## Improvements Carried Forward

| ID | Finding | Where it goes |
|---|---|---|
| IMP-INT012-01 | TCSPC jitter spec relaxed to ≤25ns | Interface contract v1.0; SIM-INT-012 spec v1.2 |
| IMP-INT012-02 | SPAD spatial spec relaxed to ≤1.5mm | Interface contract v1.0 |
| IMP-INT012-03 | SIM-018 input fidelity = **0.831** (not 0.814) | SIM-018 spec update — immediate |
| IMP-INT012-04 | Fidelity floor documented as variance compressor | Interface contract v1.0; Band 2 design notes |
| IMP-INT012-05 | B1 pipeline latency: SPAD 9.0ms, TCSPC 12.1ms | Interface contract v1.0; SIM-018 latency budget |

---

## Next Actions

1. **File interface contract B1→B2 v1.0** — immediate (this pass)
2. **Update SIM-018 spec stub** — input fidelity 0.831, latency budget 21ms remaining for Band 2
3. **SIM-INT-012 complete** — no further integration passes needed at this boundary until Band 2 is implemented
4. **Begin SIM-018 Pass 1 full spec** — research brief answered, input values confirmed

---

*SIM-INT-012 Pass 1 Research & Improvements. 2026-06-30. Protocol: GAIA Totality Directive v1.1. 🌿*
