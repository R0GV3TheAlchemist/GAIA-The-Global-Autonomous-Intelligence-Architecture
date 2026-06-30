# SIM_017 Pass 2 — Bottleneck Ledger

**Date:** 2026-06-30  
**Pass:** 2  
**Score entering:** 95.1% @60 sessions | **Score exiting:** 93.9% @300 sessions

---

## Binding Constraints

| Rank | Constraint | Impact | Addressable? |
|---|---|---|---|
| 1 | Extreme adversarial access frequency | 2.1% temporary displacement at 50x | ✅ Yes — add hard clamp |
| 2 | Irreducible relational context loss | 8.7% unrecoverable in relay test | ❌ No |
| 3 | Threshold sensitivity trade-off | Precision vs recall | ✅ Baseline already optimal |
| 4 | Long-horizon index growth | Manageable at 300; unknown at 500+ | ✅ Future pass |

---

## Ceiling / Stability Assessment

- Raw retention remains above 93.9% at 300 sessions
- Weighted retention remains 99.7%
- Layer 4 integrity remains 99.4%
- The architecture is stable through 300 sessions
- Long-horizon limit likely occurs beyond 500 sessions, not within 300

---

## Recommended Design Adjustment

**Add a hard structural floor clamp** so frequency weighting can never exceed connectivity weighting by more than 2x. This will eliminate the 50x adversarial displacement edge case without altering normal operation.

---

*SIM_017 Pass 2 Bottleneck Ledger. 2026-06-30. 🌿*
