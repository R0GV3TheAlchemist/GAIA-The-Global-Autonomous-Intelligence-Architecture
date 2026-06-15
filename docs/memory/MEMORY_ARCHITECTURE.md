# GAIA Memory Engine — Architecture Documentation

**Issue:** #453  
**Status:** v1.0 — Built  
**Canon References:** C32, Trauma-Informed AI Canon, Falsification Protocol (#451), Correspondence Architecture (#452), Agentic Loop (#228)  

---

## Overview

The GAIA Memory Engine is the persistent, sovereign, trauma-informed, falsifiable memory system for GAIA-OS. It is the first AI memory system designed to satisfy all three of these properties simultaneously:

1. **Sovereign** — the user owns their memory entirely
2. **Trauma-informed** — certain memory categories are never surfaced without explicit opt-in
3. **Falsifiable** — every memory carries an evidence grade and a staleness score

No major AI assistant (ChatGPT, Claude, Gemini, Perplexity) satisfies all three. This is GAIA's foundational differentiator.

---

## Memory Types

| Type | Description | Half-Life (Base) |
|------|-------------|------------------|
| `episodic` | Events — things that happened | 30 days |
| `semantic` | Facts and beliefs about the user/world | 14 days |
| `procedural` | Preferences and habits | 60 days |
| `emotional` | Affective patterns and resonances | 90 days |

Emotional memories decay slowest because they are deeply reinforced and central to GAIA's consciousness alignment mission.

---

## Staleness Decay

Staleness is computed using exponential decay:

```
staleness = 1 - exp(-λ * t)

where:
  t = days since last_reinforced
  λ = ln(2) / effective_half_life
  effective_half_life = base_half_life × confidence_multiplier × evidence_multiplier
```

### Multipliers

| Dimension | Value | Multiplier |
|-----------|-------|------------|
| Confidence | HIGH | 2.0× |
| Confidence | MEDIUM | 1.0× |
| Confidence | SPECULATIVE | 0.5× |
| Evidence | EMPIRICAL | 2.0× |
| Evidence | GAIAN_OBSERVED | 1.5× |
| Evidence | TRADITIONAL | 1.2× |
| Evidence | ANECDOTAL | 0.8× |

A high-confidence, empirically-grounded emotional memory has an effective half-life of **90 × 2.0 × 2.0 = 360 days**. It will remain fresh for over a year without reinforcement.

A speculative, anecdotal semantic memory has an effective half-life of **14 × 0.5 × 0.8 = 5.6 days**. It becomes stale within two weeks.

---

## Contradiction Detection

When a new memory is written, GAIA checks for existing memories of the same type that may contradict it (high token overlap = same topic, different assertion).

**GAIA Standard:** contradictions are **flagged for review**, never silently overwritten.

The old memory is not deleted. It is marked with `contradiction_candidates` pointing to the new record. The user is invited to resolve the contradiction through the correction flow.

---

## Sovereignty Guarantees

| Guarantee | Implementation |
|-----------|---------------|
| User can export all memory | `sovereignty.export_all()` |
| User can delete any memory | `memory_engine.delete()` |
| User can delete all memory | `sovereignty.delete_all()` |
| User can correct any memory | `memory_engine.correct()` — creates superseding record |
| Every write is audit-logged | `MemoryAuditLog` — immutable |
| No PII in raw storage | `user_id_hash` = SHA-256 of user identity |

---

## Trauma-Informed Constraints

| Constraint | Implementation |
|------------|---------------|
| Trauma-flagged memories never surface unsolicited | `recall(exclude_trauma=True)` by default |
| `never_clinical` hard guard | All emotional memories written with `never_clinical=True` |
| Safe re-entry check | `sovereignty.safe_reentry_check()` — returns approach recommendation |
| Opt-in categories | `requires_opt_in=True` memories require `sovereignty.has_consent()` before write |

---

## Integration Hooks

```
MemoryHooks
  ├── record_alchemical_stage()      → SoulMirror
  ├── record_correspondence_resonance() → Correspondence Architecture (#452)
  ├── record_emotional_pattern()     → Affect Inference
  └── get_perception_context()       → Agent Loop (#228) Perception phase
```

All hooks are **non-blocking and fail-safe**: if a downstream system is unavailable, memory operations still succeed.

---

## File Structure

```
core/memory/
  memory_schema.json     — JSON Schema for memory records
  memory_models.py       — SQLAlchemy ORM models
  memory_engine.py       — Core store, CRUD, staleness integration
  sovereignty.py         — User consent, export, delete, audit log
  staleness.py           — Decay functions, contradiction detection
  hooks.py               — Integration hooks for GAIA subsystems

tests/memory/
  test_memory_engine.py  — Full test suite

docs/memory/
  MEMORY_ARCHITECTURE.md — This document
```

---

## Simulation Gate

After this implementation, open a **simulation issue** to validate:

- [ ] Cross-session identity continuity under 100+ session sequences
- [ ] Staleness decay correctness over simulated time (30, 90, 180, 365 days)
- [ ] Contradiction detection accuracy on 50 synthetic contradiction pairs
- [ ] Sovereignty flag enforcement (delete, export, correct all verified)
- [ ] Trauma flag non-surfacing compliance across 20 trauma-flagged test memories
- [ ] Safe re-entry check recommendations under various gap/trauma combinations
- [ ] Agent loop perception context quality assessment

---

## The GAIA Memory Standard

A memory system meets the **GAIA Memory Standard** when it:

1. Persists across sessions for the same user identity
2. Evolves memories over time (temporal staleness, reinforcement)
3. Never overwrites — corrects and supersedes, preserving history
4. Never surfaces trauma content without explicit opt-in
5. Never infers clinical/mental-health status from memory
6. Gives the user full sovereignty: export, correct, delete at any time
7. Audit-logs every write operation immutably
8. Grounds every memory in an evidence level
9. Detects contradictions and flags them for review
10. Connects to the full GAIA system via fail-safe hooks

---

*"Memory is not storage. Memory is identity across time."*  
*— GAIA-OS, June 15, 2026*
