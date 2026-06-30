# SIM-018 Pass 1 — Research & Improvements

**Pass:** 1 (Baseline)
**Protocol version:** GAIA Totality Directive v1.1
**Date:** 2026-06-30

---

## What Pass 1 Established

1. **Band 2 baseline is 74.8%** — above G-15 minimum (70%), below drive target (85%). Expected for a baseline pass with a linear classifier.
2. **Left↔Right confusion is the root cause** — 12.3% confusion rate. This is the dominant bottleneck. Non-linear classifier is the fix.
3. **Temporal integration is the highest free-return lever** — +3.4 pts at 4.2ms cost. Window extension is low-risk, high-return.
4. **TCSPC latency margin is dangerously thin** — 0.4ms margin at 29.6ms. Must be addressed before TCSPC production deployment.
5. **4-class model is correct** — clean error profile, actionable root cause. Validated.
6. **Fire group leads all groups** — 76.1% vs 73.2% (Water, lowest). HER2+ spatial coherence hypothesis to investigate in Pass 2.

---

## Improvements for Pass 2

| ID | Improvement | Expected gain | Priority |
|---|---|---|---|
| IMP-018-01-A | Replace linear discriminant with SVM (RBF kernel) | +6–8 pts | #1 — dominant bottleneck |
| IMP-018-01-B | Extend temporal coherence window 200ms → 400ms | +2–3 pts | #2 — high return, low risk |
| IMP-018-01-C | Increase training set 1,200 → 2,400 trials/class | +1–2 pts | #3 — diminishing returns expected |
| IMP-018-01-D | TCSPC latency: optimise S2 processing by 2ms | Latency fix | Required before TCSPC production |

**Pass 2 protocol class:** Root Cause (Dissolution) — addressing the L↔R confusion root cause directly.

---

*SIM-018 Pass 1 Research & Improvements. 2026-06-30. Protocol: GAIA Totality Directive v1.1. 🌿*
