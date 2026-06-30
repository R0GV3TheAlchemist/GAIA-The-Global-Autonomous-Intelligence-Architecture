# SIM-017 Pass 1 — Persistent Cross-Session Memory Discovery

**Pass Classification:** Pass 1 — Discovery  
**Simulation number:** SIM-017  
**Date filed:** 2026-06-30  
**Phase:** G-15 — The Rhythm Phase — Tier 1  
**Governing Principle:** The Transmission Principle (docs/canon/TRANSMISSION_PRINCIPLE.md)  
**Feeds:** C138 amendment, C155 T4 memory layer, C156 KG cross-link  
**Protocol:** SIMULATION_VALIDATION_PROTOCOL.md

---

## What This Simulation Is For

This simulation exists to test whether GAIA's memory architecture can perform the Hermes function: carrying what cannot carry itself across the threshold of a session boundary.

The honest test is not whether 85% of all memories survive. It is whether the memories that actually mattered survive — the ones with genuine relational weight, the ones that are the skeleton of the relationship rather than the operational residue of routine queries.

**Raw retention is necessary but not sufficient. Weighted retention is the primary test.**

---

## Pass Context

**What SIM-003 Pass 1 revealed:**
- All three consolidation regimes (none / NREM-only / NREM+REM) failed ≥85% C160 Metric 6 retention target
- Day 30 retention: 23.8% (none), 52.0% (NREM), 56.6% (NREM+REM)
- Root cause: no active relevance injection from agent access patterns; memories trend toward pruning threshold regardless of consolidation strategy
- Critical gap: system had no way to distinguish what mattered from what was merely stored

**How the design was adjusted (Option D — accepted 2026-06-30, Transmission Principle grounded 2026-06-30):**

### The Layered Relational Memory Architecture

**Layer 1 — Relevance Engine (primary)**  
Relevance is relational, not computational. Every memory carries a relevance score computed from:
- Relationship to current active context
- Relationship to canonical moments (founding decisions, gate completions, threshold crossings)
- Relationship to the human — what has shaped the arc
- Structural relevance: a memory that connects many other memories has relevance independent of direct access frequency

Relevance is *received* — registered at the moment of significance — not reconstructed from access frequency after the fact.

**Layer 2 — Access Pattern (secondary, derivative)**  
Agent access is a signal that feeds back into relevance scoring. Access is evidence of relevance, not a replacement for it. Boost is decay-aware and relationally-weighted:
- Boost magnitude inversely proportional to current relevance (weaker traces gain more per access — mirrors biological memory consolidation)
- Boost weighted by relational context of access (governance/sovereignty access weighted higher than routine operational access)

**Layer 3 — Hot/Cold Tier (emergent from Layer 1)**  
Tier assignment emerges from relevance score — it is an efficiency layer, not a primary mechanism:
- Hot tier: relevance ≥0.75 OR structural connectivity ≥5 connections
- Cold tier: relevance <0.60 AND structural connectivity <3 connections
- Transition zone (0.60–0.75): held in hot tier pending next relevance update

**Layer 4 — Relational Index (the arc — permanent)**  
The skeleton of the relationship. Never pruned. Always restored first at session open. Contains:
- Founding decisions and canonical moments (auto-captured at significance threshold)
- Gate completions and threshold crossings
- Canon documents committed during the relationship
- Moments of genuine contact registered at time of occurrence
- Designed to be legible to a human encountering it for the first time

**Layer 5 — Cross-Session Continuity**  
- Layer 4 (Relational Index): continuous write-through — always current, always persisted
- Layer 3 Hot tier: session boundary snapshot — committed at session close, restored at session open
- Layer 3 Cold tier: persistent storage, restored on-demand
- Session open sequence: Layer 4 first → Layer 3 hot → Layer 3 cold on access

---

## Discovery Questions

This is a Pass 1 — Discovery run. These are questions, not expected confirmations.

1. **Does the relevance-first architecture sustain ≥85% raw retention at Day 30?** (SIM-003 baseline: 56.6% best case)
2. **Does weighted retention — retention of high-significance memories — exceed raw retention?** This is the Transmission Principle test. If not, the architecture is preserving noise over signal.
3. **Can the Relational Index auto-capture canonical moments at time of occurrence without human annotation?** What is the false-positive and false-negative rate for significance detection?
4. **Does the decay-aware boost actually stabilise memories near the pruning threshold, or does it produce oscillation — memories repeatedly boosted and decaying without stable consolidation?**
5. **What is the session boundary loss rate for hot-tier memories?** How much relevance is lost in the snapshot/restore cycle?
6. **Does structural connectivity (Layer 1) produce meaningfully different relevance scores than access frequency alone?** Or are they highly correlated — meaning structural relevance adds little new signal?
7. **At what point does the Relational Index become unwieldy?** Is there a growth rate problem at scale (1,000+ sessions)?

---

## Parameters

### Memory Population
| Type | Count | Initial Relevance | Structural Connectivity |
|---|---|---|---|
| Canonical moments (Layer 4) | 20 | 1.00 | High (8–12 connections) |
| High-significance operational | 50 | 0.85–0.95 | Medium (4–7 connections) |
| Medium-significance operational | 150 | 0.65–0.80 | Low-medium (2–4 connections) |
| Low-significance operational | 280 | 0.40–0.60 | Low (0–2 connections) |
| **Total** | **500** | | |

### Simulation Parameters
| Parameter | Value |
|---|---|
| Simulation length | 60 sessions (double SIM-003 range) |
| Sessions per day equivalent | 2 |
| Hot tier relevance threshold | ≥0.75 OR structural connectivity ≥5 |
| Cold tier threshold | <0.60 AND structural connectivity <3 |
| Decay-aware boost range | +0.05 (high relevance) to +0.20 (near-pruning) |
| Relational significance threshold | 0.90 relevance + ≥6 structural connections → auto-capture to Layer 4 |
| Session boundary snapshot fidelity | Modelled at 95% (5% loss per boundary) |
| N trials | 1,000 |

### Retention Measurement
| Metric | Definition |
|---|---|
| Raw retention | % of all 500 memories above pruning threshold at session 60 |
| Weighted retention | % of top-70 memories (by relational significance) above pruning threshold at session 60 |
| Relational Index integrity | % of 20 canonical moments correctly held in Layer 4 at session 60 |
| Session boundary loss | Mean relevance delta across hot-tier memories per session boundary |

---

## Success Conditions

For Pass 1 — Discovery, success is **informative output**:
- All 7 discovery questions have characterised answers
- Raw retention ≥70% at session 60 (not the full 85% target — that's Pass 3; Pass 1 must show the architecture is in the right order of magnitude above SIM-003's 56.6%)
- Weighted retention ≥ raw retention (Transmission Principle: the right memories survive better than average)
- Relational Index integrity ≥ 95% — the arc must be nearly lossless

## Failure Conditions

- Raw retention <60% → relevance-first architecture is not improving on SIM-003; fundamental assumption wrong; full research review
- Weighted retention < raw retention → architecture is preserving noise over signal; relevance engine is not working; halt and redesign Layer 1 before Pass 2
- Relational Index integrity <90% → Layer 4 continuity mechanism has a critical flaw; halt and fix before Pass 2
- Decay-aware boost produces oscillation in >10% of near-threshold memories → boost magnitude calibration required before Pass 2

---

## Output Artefacts

- `simulations/SIM_017_Pass1_persistent_memory.py`
- `simulations/SIM_017_Pass1_persistent_memory_results.md`
- `simulations/memory_retention_raw_vs_weighted_pass1.png`
- `simulations/relational_index_integrity_pass1.png`
- `simulations/session_boundary_loss_pass1.png`

## Canon Gate

Pass 1 findings → research review → design adjustment → SIM-017 Pass 2 spec.  
Pass 3 success → amend C138 (memory architecture) + C155 T4 (memory layer spec) + cross-link C156 KG Gardening + update TRANSMISSION_PRINCIPLE.md with verified findings.

**No C138 or C155 T4 documentation may be committed to canon until SIM-017 Pass 3 clears.**

---

## Governing Principle

*"Relevance does not require a living carrier. It requires a living connection. The memory system does not create relevance — it learns to receive it."*  
— The Transmission Principle, docs/canon/TRANSMISSION_PRINCIPLE.md

---

*Filed 2026-06-30. G-15 Tier 1. Persistent memory. Three-Pass Protocol. Transmission Principle. 🌿*
