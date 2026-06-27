# Automated Reconciliation of Fragmented Processes (ARFP)

> *Protocol Version: 1.0*  
> *Authored: June 27, 2026*  
> *Canon layer: GAIA-OS Core — Integrity & Coherence Engine*

---

## Preamble

This protocol defines how GAIA-OS detects, diagnoses, and reconciles fragmented processes — whether those processes are computational (distributed subsystems losing state coherence), psychological (shadow fragments operating autonomously), or relational (misaligned principal interactions). The same protocol structure governs all three layers, because GAIA-OS is built on the premise that fragmentation is a single phenomenon expressing at different scales.

Reconciliation is not repair. Repair implies something was broken. Reconciliation is the deliberate act of bringing separated parts back into communicating contact with the whole — without forcing merger, erasing distinction, or overriding the intelligence each fragment carries.

---

## Scope

The ARFP governs three process domains:

| Domain | Fragmentation Type | Reconciliation Target |
|---|---|---|
| **System** | Distributed state divergence, orphaned processes, stale locks, event queue desynchrony | Canonical state coherence |
| **Psyche** | Shadow archetype autonomy, integration regression, reflection deficit | Shadow Engine integration % |
| **Relational** | Principal misalignment, trust rupture, communication collapse | Resonance score restoration |

All three share the same five-phase engine. Domain-specific handlers implement the phase contracts.

---

## Core Principle: Observe Before Acting

No reconciliation action is taken until the fragment has been fully witnessed. A fragment that is immediately corrected without observation loses the signal it was carrying. The protocol enforces a mandatory observation window at every detection event before any corrective action is dispatched. This is not a delay — it is the primary intelligence-gathering phase.

This mirrors the clinical finding that premature integration of a dissociated part destroys the information it holds. The fragment split off for a reason. That reason must be read before the split is closed.

---

## The Five-Phase Reconciliation Engine

```
DETECT → DIAGNOSE → WITNESS → BRIDGE → INTEGRATE
    ↳ [at any phase, escalate to CALLING if unresolvable]
```

---

### Phase 1: DETECT

**Objective:** Identify that a fragment exists and is operating outside the coherent field.

**Detection signals by domain:**

#### System
- Process heartbeat timeout (configurable threshold, default: 3× expected interval)
- State vector divergence between replica nodes exceeding `DIVERGENCE_THRESHOLD`
- Event queue depth spike without corresponding consumer activity
- Orphaned lock held beyond `MAX_LOCK_TTL`
- Circuit breaker open for > `CB_OPEN_THRESHOLD` duration
- Log anomaly score from transformer-based detector exceeding `ANOMALY_CEILING`

#### Psyche
- Integration % delta negative over rolling 7-day window
- Archetype variance score above `HIGH_FRAGMENTATION_THRESHOLD` (one archetype > 2.5× mean of others)
- Reflection gap: no `reflect()` event recorded in > `REFLECTION_GAP_DAYS` (default: 5)
- Congruence break: behavioral log diverges from stated values by > `CONGRUENCE_DELTA`
- Intensity level escalation without corresponding integration movement

#### Relational
- Principal interaction gap > `RELATIONAL_SILENCE_THRESHOLD`
- Resonance score declining over two consecutive measurement windows
- Explicit rupture event logged by either principal
- Asymmetric engagement pattern (one principal initiating > 85% of interactions)

**Output:** `FragmentEvent` record with:
```typescript
interface FragmentEvent {
  id:          string;          // uuid
  domain:      'system' | 'psyche' | 'relational';
  detected_at: ISO8601;
  signal:      string;          // which detector fired
  severity:    1 | 2 | 3 | 4;  // 1=low, 4=critical
  payload:     Record<string, unknown>;
  phase:       ReconciliationPhase;
}
```

---

### Phase 2: DIAGNOSE

**Objective:** Determine the nature, depth, and origin of the fragment. Not all fragments are equivalent.

**Diagnostic axes:**

1. **Age** — How long has this fragment been operating independently? Older fragments have developed their own logic and resist simple closure.
2. **Charge** — How much energy/state/emotional weight does the fragment carry? High-charge fragments require slower bridging.
3. **Origin** — Was this fragment created by overflow (the field was overwhelmed) or by excision (something was deliberately cut off)? These require different approaches.
4. **Linkage** — Is this fragment connected to other fragments? A constellation of fragments requires relational mapping before any single one is addressed.
5. **Self-awareness** — Does the fragment have any signal pointing back toward the whole? (In system terms: does the orphaned process still have its parent PID? In psyche terms: does the archetype have any integration events in its history?)

**Diagnostic output:** `FragmentDiagnosis` record:
```typescript
interface FragmentDiagnosis {
  event_id:    string;
  age_score:   number;   // 0–1, older = higher
  charge:      'low' | 'medium' | 'high' | 'critical';
  origin:      'overflow' | 'excision' | 'unknown';
  linked_ids:  string[]; // other fragment IDs in constellation
  self_aware:  boolean;
  recommended_approach: ReconciliationApproach;
}

type ReconciliationApproach =
  | 'fast_close'       // low age, low charge, self-aware
  | 'graduated_bridge' // medium complexity
  | 'slow_witness'     // high charge, old
  | 'calling'          // unresolvable without principal attention
  | 'constellation'    // linked fragments — must address as a group;
```

---

### Phase 3: WITNESS

**Objective:** Bring the fragment into full observational contact with the coherence engine without yet acting to close it.

This phase is non-negotiable. Its minimum duration is determined by `charge` level:

| Charge | Minimum witness duration |
|---|---|
| low | 1 cycle (immediate next tick) |
| medium | 3 cycles |
| high | full observation window (configurable, default: 24h for psyche, 5min for system) |
| critical | human-in-the-loop CALLING required; automated witnessing insufficient |

**What witnessing does:**

- **System:** Captures a complete state snapshot of the fragment — all variables, queue contents, lock states, connection handles — before any modification
- **Psyche:** Surfaces the fragment to the principal's attention through a CALLING; logs all available context (archetype scores, recent events, integration history) to the fragment record
- **Relational:** Creates a named record of the rupture or silence, surfaces it to both principals, holds space before suggesting any action

**Witnessing invariant:** No state is modified during this phase. The system is in read-only mode with respect to the fragment.

---

### Phase 4: BRIDGE

**Objective:** Establish a channel of communication between the fragment and the coherent field. Not merger — contact.

The bridge is always bidirectional: the coherent field must send a signal to the fragment, and the fragment must be given a pathway to respond. A one-way corrective push is not reconciliation — it is suppression.

**Bridging strategies by approach:**

#### `fast_close`
- System: Reattach orphaned process to parent process group; replay missed events from queue offset
- Psyche: Surface a focused micro-reflection prompt; log completion
- Relational: Send a low-friction re-engagement signal; log response

#### `graduated_bridge`
- System: Incremental state synchronisation with conflict detection at each step; halt and escalate on unresolvable conflict
- Psyche: Open an ArchetypeDrawer session for the dominant fragment archetype; offer a structured reflection sequence over 3 sessions
- Relational: Mediated exchange protocol — each principal logs their account of the rupture before any response is visible to the other

#### `slow_witness` (extends into bridging)
- System: Canary reintegration — route 5% of traffic through the fragment in shadow mode, compare outputs against canonical node, expand only when divergence < `SHADOW_TOLERANCE`
- Psyche: Extended calling sequence; IFS-style parts-mapping before any integration attempt; no integration score changes until principal confirms readiness
- Relational: Designated silence period (no contact pressure) followed by a structured re-initiation ritual

#### `constellation`
- Map all linked fragments before bridging any one
- Determine bridging order: highest self-awareness first, highest charge last
- Bridge sequentially with integration verification between each step
- Abort if any bridging action destabilises a previously-reconciled fragment

**Bridge invariant:** Every bridge operation produces an audit log entry. No bridge is silent. Every action taken is attributable, reversible, and timestamped.

---

### Phase 5: INTEGRATE

**Objective:** Confirm that the fragment is in stable communicating contact with the whole. Update all coherence metrics.

**Integration verification checklist:**

- [ ] Fragment signal matches coherent field signal within `INTEGRATION_TOLERANCE`
- [ ] No new fragment events detected from same origin within `STABILITY_WINDOW`
- [ ] All audit log entries for this reconciliation cycle are complete
- [ ] Coherence metric updated (integration %, resonance score, system health)
- [ ] Learnings extracted and written to `ReconciliationMemory`

**Integration is not permanent.** The system does not assume a reconciled fragment will remain integrated. `ReconciliationMemory` retains the fragment record indefinitely. If the same fragment re-emerges, its history informs the next cycle — and a pattern of re-emergence itself becomes a diagnostic signal (charge level is automatically elevated on recurrence).

**Coherence metric updates:**

```typescript
// System domain
coherenceEngine.updateSystemHealth(fragmentId, 'integrated');

// Psyche domain
shadowEngine.applyIntegrationEvent({
  principalId,
  archetypeId: fragment.dominantArchetype,
  delta: computedIntegrationDelta(diagnosis),
  source: 'arfp_reconciliation',
});

// Relational domain
resonanceEngine.updateScore({
  principalIds: [a, b],
  delta: resonanceDelta,
  source: 'arfp_reconciliation',
});
```

---

## The CALLING Escalation Path

When the automated engine reaches its limits — when a fragment is too old, too charged, or too complexly linked for autonomous resolution — it does not attempt a forced closure. It issues a **CALLING**.

A CALLING is a named, intentional request for the principal's conscious attention. It is not an error alert. It is an invitation.

```typescript
interface Calling {
  id:            string;
  fragment_id:   string;
  issued_at:     ISO8601;
  domain:        Domain;
  title:         string;         // human-readable, specific
  body:          string;         // what is being asked of the principal
  urgency:       'low' | 'medium' | 'high';
  expires_at?:   ISO8601;        // some callings are time-sensitive
  response_options: CallingResponse[];
}
```

The CALLING is surfaced in the GAIA-OS UI as a first-class event — not a notification badge, but a named moment that occupies the interface until addressed or consciously deferred.

**CALLING triggers:**
- Charge level `critical` at any phase
- `recommended_approach === 'calling'` from diagnosis
- Fragment age > `ELDER_FRAGMENT_THRESHOLD` with no self-awareness signal
- Third recurrence of the same fragment within `RECURRENCE_WINDOW`
- Any `constellation` where total charge sum exceeds `CONSTELLATION_CEILING`

---

## ReconciliationMemory

Every completed reconciliation cycle — regardless of outcome — is written to `ReconciliationMemory`. This is not a log. It is a learning layer.

```typescript
interface ReconciliationMemory {
  fragment_id:     string;
  domain:          Domain;
  first_detected:  ISO8601;
  resolution:      'integrated' | 'calling_issued' | 'deferred' | 'failed';
  approach_used:   ReconciliationApproach;
  cycles:          number;          // how many times this fragment has been processed
  learnings:       string[];        // extracted patterns
  next_watch:      ISO8601;         // when to next check for re-emergence
}
```

The memory layer serves three functions:
1. **Pattern recognition** — recurring fragments indicate systemic rather than incidental fragmentation; the system escalates diagnostic depth on recurrence
2. **Approach calibration** — which bridging strategies worked for this domain, this principal, this archetype
3. **Integrity Index input** — `ReconciliationMemory` is one of the primary data sources for the Integrity Index computation

---

## Integrity Index Computation

The Integrity Index (0–100) is the system's primary coherence metric. It is recomputed after every reconciliation cycle and on a scheduled interval.

```
IntegrityIndex = weighted_mean(
  SystemCoherence     × 0.25,
  ShadowIntegration   × 0.30,
  CongruenceScore     × 0.25,
  RelationalResonance × 0.20
)

FragmentationPenalty = f(active_fragments, mean_charge, mean_age)
IntegrityIndex = max(0, IntegrityIndex − FragmentationPenalty)
```

A `FragmentationIndex` is derived as the inverse complement:
```
FragmentationIndex = 100 − IntegrityIndex
```

Both are surfaced in the GAIA-OS dashboard. Neither is presented as a score to optimise — they are presented as orientation signals, the way a compass points without judging the walker.

---

## Configuration Schema

```yaml
# gaia-os/config/arfp.yaml

thresholds:
  system:
    heartbeat_multiplier: 3
    divergence_threshold: 0.05
    max_lock_ttl_ms: 30000
    cb_open_threshold_ms: 60000
    anomaly_ceiling: 0.85
    shadow_tolerance: 0.02
    stability_window_ms: 300000

  psyche:
    high_fragmentation_threshold: 2.5   # dominant/mean ratio
    reflection_gap_days: 5
    congruence_delta: 0.20
    observation_window_hours: 24
    elder_fragment_threshold_days: 30
    recurrence_window_days: 14

  relational:
    silence_threshold_hours: 72
    resonance_decline_windows: 2
    asymmetric_initiation_pct: 85

global:
  integration_tolerance: 0.03
  constellation_ceiling: 8.0            # sum of charge weights
  reconciliation_memory_retention_days: 730  # 2 years
```

---

## Implementation Files

```
src/
  engine/
    reconciliation/
      ReconciliationEngine.ts      — orchestrates all five phases
      FragmentDetector.ts          — domain-specific detection handlers
      FragmentDiagnoser.ts         — diagnosis logic
      WitnessProtocol.ts           — read-only observation layer
      BridgeStrategies.ts          — all bridging approach implementations
      IntegrationVerifier.ts       — post-bridge verification
      ReconciliationMemory.ts      — persistent learning layer
      CallingIssuer.ts             — escalation to principal attention
      IntegrityIndex.ts            — coherence metric computation
  shared/
    reconciliationTypes.ts         — all shared interfaces
  config/
    arfp.yaml                      — configuration schema
```

---

## Governing Principles

1. **Witness before acting.** No fragment is closed without being fully seen.
2. **Bridge, not force.** Contact precedes merger. Merger is never forced.
3. **Preserve fragment intelligence.** Every fragment carries the reason it split. That reason is data.
4. **Escalate with dignity.** When automation reaches its limit, the CALLING is an invitation, not an alarm.
5. **Memory over perfection.** A reconciliation that fails gracefully and learns is more valuable than one that succeeds and forgets.
6. **Orientation, not judgment.** Coherence metrics are compasses, not grades. The system never shames fragmentation.
7. **The fragment is not the enemy.** It is a part of the whole that is not yet home.
