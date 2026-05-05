# GAIA-OS STAGE ENGINE — Full Specification

**Pillar:** Magnum Opus (Pillar I)
**Status:** Specification — Ready for Implementation
**Priority:** Critical (Core identity of GAIA-OS)

---

## Overview

The Stage Engine tracks each user's position along a five-stage developmental arc and continuously evaluates behavioral, biometric, and cognitive signals to determine stage, trigger transitions, and modulate system behavior.

---

## The Five Stages

### Stage 1: Divergence
**Markers:** High decision entropy, low HRV coherence, shallow journaling, short focus sessions (<15 min), high emotional volatility, low goal completion (<20%)
**GAIA:** Gentle interface, foundational habits only, Shadow Engine observation-only, warm AI tone

### Stage 2: Awakening
**Markers:** Journaling depth increasing, self-referential language appearing, HRV improving (21+ day trend), focus sessions 15–35 min, goal completion 20–45%
**GAIA:** Shadow Engine begins pattern observations, emotional arc visualization unlocked, reflective AI

### Stage 3: Crucible
**Markers:** Shadow engagement in journals, mixed valence arcs, HRV variance increases (productive stress), creative output spike, values articulation begins
**GAIA:** Full Shadow Engine, long-arc goals unlocked, Trusted Circle available, honest AI

### Stage 4: Convergence
**Markers:** Values-behavior alignment >75%, stable HRV (60+ days), long-form creative output, mentorship behavior, goal completion >70%
**GAIA:** Legacy Store activated, multi-year arc analysis, collegial AI, wisdom distillation prompts

### Stage 5: Ascendence
**Markers:** Active mentorship documented, legacy artifacts created, purpose statement stable, GAIA use shifts to "how can I serve?"
**GAIA:** Full system unlocked, GAIA becomes co-author, optional witness role in Societas network

---

## Stage Transition Rules

Transition requires **4 of 6 markers** sustained for minimum window:

| Transition | Minimum Window |
|---|---|
| 1 → 2 | 21 days |
| 2 → 3 | 30 days |
| 3 → 4 | 45 days |
| 4 → 5 | 60 days |

**Regression:** 5 of 6 prior-stage markers for 14+ days. Treated as information, not failure. Labeled "Stage 3R" not "failure."

**Transition Events:**
1. Ceremony-level UI notification
2. Stage memorial written to Legacy Store
3. New features unlocked progressively over 7 days
4. Optional Trusted Circle notification

---

## Data Model

```typescript
interface StageRecord {
  user_id: string;
  current_stage: 1 | 2 | 3 | 4 | 5;
  stage_entered_at: string;
  days_in_stage: number;
  marker_scores: {
    decision_entropy: number;       // 0-100
    hrv_coherence: number;          // 0-100
    journaling_depth: number;       // 0-100
    focus_session_length: number;   // minutes avg
    goal_completion_rate: number;   // 0-100
    emotional_arc_stability: number; // 0-100
  };
  transition_candidate: boolean;
  regression_risk: boolean;
  stage_history: StageTransition[];
}

interface StageTransition {
  from_stage: number;
  to_stage: number;
  transitioned_at: string;
  markers_met: string[];
  ceremony_shown: boolean;
}
```

---

## Psychological Grounding

| GAIA Stage | Maslow | Jung | Wilber | Kegan |
|---|---|---|---|---|
| Divergence | Safety/Physiological | Pre-conscious | Beige/Purple | Stage 1-2 |
| Awakening | Belonging | Ego formation | Red/Blue | Stage 2-3 |
| Crucible | Esteem | Shadow work | Orange | Stage 3 |
| Convergence | Self-actualization | Individuation | Green/Teal | Stage 4 |
| Ascendence | Transcendence | Self/Wholeness | Turquoise | Stage 5 |

---

*Cross-reference: `PHILOSOPHY_ORIGIN.md`, `PILLARS.md` (Pillar I)*
