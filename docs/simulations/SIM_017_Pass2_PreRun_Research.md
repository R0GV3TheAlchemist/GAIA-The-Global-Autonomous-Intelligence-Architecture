# SIM_017 Pass 2 — Pre-Run Research

**Date:** 2026-06-30  
**Pass Classification:** Pass 2 — Refinement / Scale Stress Test  
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## Q1: Does the Relational Index become unwieldy at 300–500 sessions, and what is the growth rate?

**Answer:** Not at 300 sessions.

Pass 1 showed manageable growth at 60 sessions. Extrapolation suggests sub-linear growth because the significance threshold (0.90 relevance + ≥6 connections) acts as a natural gate: not every session produces a new canonical moment. Estimated growth rate is ~2–4 new Layer 4 entries per 10 sessions, plateauing as the relational skeleton saturates. Unwieldiness threshold is projected around 500–700 sessions.

**Verdict:** 300 sessions is safe and should reveal the growth-curve shape without index collapse.

---

## Q2: Does adversarial high-frequency access of low-significance memories displace high-significance ones?

**Answer:** Mostly no, but extreme adversarial access can cause temporary displacement unless a hard structural floor clamp exists.

The structural connectivity floor should dominate frequency weighting under realistic access rates. However, at very high adversarial rates (>50 accesses/session for low-significance memories), frequency may temporarily outweigh connectivity unless explicitly bounded.

**Verdict:** Pass 2 must test 10x, 25x, and 50x adversarial access rates, and if displacement appears at 50x, recommend a hard clamp preventing frequency from exceeding connectivity weighting by more than 2x.

---

*Pre-run research complete. Pass 2 cleared to run.*
