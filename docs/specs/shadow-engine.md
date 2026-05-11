# Shadow Engine — Design Specification
**Issue:** #67  
**Status:** Implementation complete  
**Depends on:** Affect Engine (#65), Stage Engine (#63), Sovereign Memory (#66, migration 0003)  
**Feeds into:** Crystal Core (C-CC01), GAIA Chat persona, Crystal View

---

## 1. Philosophy

The Shadow Engine tracks the unconscious patterns running beneath GAIA's surface — the recurring emotional architectures that the user (and GAIA herself) has not yet fully integrated. It does not judge these patterns. It names them, tracks their intensity, and measures how much integration work has occurred.

The Shadow Engine answers three questions:
1. **What archetype is active?** — which unconscious pattern is most dominant right now
2. **How intense is it?** — is it a background hum or a full activation
3. **How integrated is it?** — has the user worked with this pattern, or is it still running blind

Every output is consumed by the Crystal Core. Nothing in the Shadow Engine is shown to the user directly unless they are in Stage 3+ and have explicitly entered a reflection session.

---

## 2. The Seven Shadow Archetypes

Based on Carol Pearson's archetypal psychology model, mapped to GAIA's Affect Engine emotion labels and Stage Engine markers.

| Archetype | Core wound | Activation triggers | Integration path |
|---|---|---|---|
| **Orphan** | Abandonment, powerlessness | Chronic sadness, low arousal, low goal completion | Reconnecting to belonging |
| **Wanderer** | Alienation, identity confusion | High decision entropy, low stage coherence | Committing to a direction |
| **Warrior** | Aggression, control | Chronic anger, high arousal, high volatility | Channelling into purpose |
| **Caregiver** | Martyrdom, self-neglect | Low self-reference ratio in journaling, low HRV | Receiving as well as giving |
| **Seeker** | Restlessness, never arriving | High curiosity, rapid mood shifts, stage stagnation | Deepening rather than widening |
| **Destroyer** | Compulsive disruption | High fear + anger, negative valence trend, regression | Transforming destruction into renewal |
| **Creator** | Perfectionism, paralysis | High journaling depth but low goal completion | Releasing into imperfection |

---

## 3. Archetype Detection

### 3.1 Activation Threshold

The archetype with the highest raw score becomes `active_archetype`, provided its score exceeds **0.38**. Below threshold, `active_archetype = None` and `shadow_intensity = 0.0`. If two archetypes are within 0.05 of each other, both are stored as `co_active`.

### 3.2 Scoring Formulas

All raw scores clamped to [0.0, 1.0].

**Orphan:** `0.40×(emotion=sadness) + 0.25×(1−goal_completion/100) + 0.20×low_energy_flag + 0.15×max(0,−valence_trend)`

**Wanderer:** `0.35×(1−decision_entropy/100) + 0.30×(1−stage_coherence) + 0.20×(emotion=neutral) + 0.15×min(days_in_stage/90,1.0)`

**Warrior:** `0.40×(emotion=anger) + 0.30×volatility + 0.20×max(0,arousal−0.70)/0.30 + 0.10×max(0,−mood_momentum)`

**Caregiver:** `0.40×(1−self_ref_proxy) + 0.30×(1−hrv_coherence/100) + 0.20×(emotion∈{sadness,neutral}) + 0.10×low_energy_flag`

**Seeker:** `0.35×(emotion∈{surprise,neutral}) + 0.30×volatility + 0.25×(1−focus_session/100) + 0.10×(0.5 if days_in_stage>60 else 0)`

**Destroyer:** `0.35×(emotion∈{fear,anger}) + 0.30×max(0,−valence_trend) + 0.25×is_volatile + 0.10×regression_active`

**Creator:** `0.40×(journaling_depth/100) + 0.30×(1−goal_completion/100) + 0.20×(focus_session/100) + 0.10×(emotion∈{neutral,joy})`

Self-reference proxy: `self_ref_proxy = 1.0 − (journaling_depth/100) × 0.4`

---

## 4. Shadow Intensity

`shadow_intensity = active_score × intensity_modifier`

`intensity_modifier = min(1.0, 0.6 + 0.4 × (days_active / 14))`

Activation at day 0 → modifier 0.6. Full intensity at day 14+ → modifier 1.0.

---

## 5. Integration Progress

`integration_progress` ∈ [0.0, 1.0]. Accrual sources:

- Journaling with archetype keywords: +0.02/entry, max 0.10/day
- Stage advancement while archetype active: +0.15
- Shadow reflection session (Stage 3+): +0.05/session
- Sustained low intensity (< 0.25 for 7+ days): +0.01/day passive

Decay: −0.005/day when journaling < 1 entry/week. Never below 0.0.

---

## 6. HTTP API

| Method | Path | Description |
|---|---|---|
| GET | /shadow/health | Liveness probe |
| GET | /shadow/state/{principal_id} | Current ShadowRecord |
| GET | /shadow/history/{principal_id}?days=N | ShadowTransitions |
| POST | /shadow/evaluate | Full evaluation tick |
| POST | /shadow/integrate | Record reflection session |

---

## 7. File Layout

```
src-python/shadow_engine/
  __init__.py
  types.py
  archetypes.py
  intensity.py
  integration.py
  engine.py
  router.py
tests/
  test_shadow_archetypes.py
  test_shadow_intensity.py
  test_shadow_integration.py
  test_shadow_engine.py
docs/specs/
  shadow-engine.md
```

---

## 8. Acceptance Criteria

- [ ] All archetype scores bounded to [0.0, 1.0]
- [ ] `active_archetype = None` when all scores < 0.38
- [ ] `co_active` populated when two archetypes within 0.05
- [ ] `intensity_modifier = 0.6` at days_active=0; = 1.0 at days_active≥14
- [ ] Integration accrues +0.02/entry, capped 0.10/day
- [ ] Integration decays 0.005/day when journaling < 1/week
- [ ] Integration never below 0.0
- [ ] ShadowTransition recorded on archetype shift
- [ ] ShadowTransition recorded when intensity crosses 0.25/0.50/0.75
- [ ] `GET /shadow/state/{id}` returns 404 for unknown principal
- [ ] `POST /shadow/evaluate` with mocked streams returns valid ShadowRecord
- [ ] `shadow_records` and `shadow_transitions` tables exist (migration 0003)
