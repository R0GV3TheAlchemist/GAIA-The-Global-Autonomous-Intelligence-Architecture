# IntegrityIndex — Metric Specification

> *Version: 1.0*  
> *Authored: June 27, 2026*  
> *Canon layer: GAIA-OS Core — Integrity & Coherence Engine*  
> *Depends on: ARFP Protocol v1, Shadow Engine v1*

---

## Purpose

The IntegrityIndex (II) is GAIA-OS's primary orientation signal. It answers the question:

> *How coherent is this principal across all observable dimensions of self-expression?*

It is not a score to maximise. It is a compass reading — one that shows both direction and distance from center. A principal with an II of 42 is not failing; they are in a particular position relative to their own coherence, and the system's role is to illuminate that position honestly and support movement if the principal chooses it.

The II draws from four independent sub-scores, each measuring a distinct dimension of integrity as defined by the research base:

| Sub-score | Source | Weight |
|---|---|---|
| `SystemCoherence` (SC) | Distributed process health | 0.25 |
| `ShadowIntegration` (SI) | Shadow Engine archetype integration | 0.30 |
| `CongruenceScore` (CS) | Actual vs. ideal self alignment | 0.25 |
| `RelationalResonance` (RR) | Principal-to-principal coherence | 0.20 |

Weights reflect the relative explanatory power of each dimension for overall wholeness, grounded in Sheldon's personality integration research distinguishing coherence from congruence, and the clinical finding that shadow integration is the most predictive single variable for sustained psychological integrity.

---

## Governing Equations

### Base Integrity Index

\[
II_{base} = 0.25 \cdot SC + 0.30 \cdot SI + 0.25 \cdot CS + 0.20 \cdot RR
\]

### Fragmentation Penalty

\[
\Phi = \sum_{i=1}^{N} w_{charge_i} \cdot \log_2(1 + age_i)
\]

Where:
- \(N\) = number of active unreconciled fragments
- \(w_{charge}\) = charge weight: `{low: 1, medium: 2, high: 4, critical: 8}`
- \(age_i\) = fragment age in days
- \(\log_2\) dampens the penalty so ancient low-charge fragments do not catastrophise the index

### Final IntegrityIndex

\[
II = \max(0,\ II_{base} - \Phi_{normalised})
\]

\[
\Phi_{normalised} = \min\left(II_{base},\ \frac{\Phi}{\Phi_{ceiling}}\right) \cdot II_{base}
\]

`\Phi_{ceiling}` defaults to `20.0` (configurable in `arfp.yaml`). This ensures the penalty is proportional rather than absolute — a principal with SC=90 and one active low-charge fragment is not treated the same as one with SC=45 and the same fragment.

### FragmentationIndex

\[
FI = 100 - II
\]

Displayed alongside II as the complementary orientation signal.

---

## Sub-Score Definitions

---

### 1. SystemCoherence (SC) — 0–100

**What it measures:** The health and coherence of GAIA-OS's distributed computational processes for this principal. All processes that serve this principal (shadow engine workers, reconciliation loops, event queues, data sync nodes) are included.

**Component metrics:**

| Metric | Symbol | Range | Description |
|---|---|---|---|
| Process Liveness Rate | `PLR` | 0–1 | Fraction of expected processes with recent heartbeat |
| State Divergence Score | `SDS` | 0–1 | Mean normalised divergence across all replica pairs; 0 = perfectly in sync |
| Queue Saturation Index | `QSI` | 0–1 | Mean event queue depth as fraction of capacity ceiling; 0 = empty, 1 = full |
| Circuit Breaker Health | `CBH` | 0–1 | Fraction of circuit breakers currently closed (healthy); open = unhealthy |
| Error Rate | `ERR` | 0–1 | 15-minute rolling error rate as fraction of total requests; lower is better |

**Computation:**

\[
SC = 100 \cdot \left(0.30 \cdot PLR + 0.25 \cdot (1 - SDS) + 0.20 \cdot (1 - QSI) + 0.15 \cdot CBH + 0.10 \cdot (1 - ERR)\right)
\]

**Update frequency:** Every 60 seconds (live process telemetry).

**Interpretation thresholds:**

| SC | Interpretation |
|---|---|
| 90–100 | Full operational coherence |
| 75–89 | Minor degradation; within normal operating range |
| 50–74 | Moderate fragmentation; ARFP monitoring elevated |
| 25–49 | Significant fragmentation; ARFP active reconciliation engaged |
| 0–24 | Critical; CALLING issued |

---

### 2. ShadowIntegration (SI) — 0–100

**What it measures:** The degree to which this principal's shadow archetypes are in integrating relationship with the conscious self, rather than operating as autonomous fragments. This is the most heavily weighted sub-score because shadow integration is the most predictive single variable for sustained psychological integrity across all research frameworks surveyed.

**Component metrics:**

| Metric | Symbol | Range | Description |
|---|---|---|---|
| Raw Integration % | `RI` | 0–100 | Shadow Engine's current `integrationPct` field |
| Archetype Variance Score | `AVS` | 0–1 | Normalised standard deviation of all 7 archetype scores; high variance = fragmentation |
| Reflection Consistency | `RC` | 0–1 | Regularity of `reflect()` events over rolling 30-day window; modelled as decay function |
| Integration Velocity | `IV` | −1 to +1 | Direction and rate of integration % change over rolling 14-day window; positive = moving toward integration |
| Stage Depth | `SD` | 0–1 | Ordinal integration stage converted to continuous: `{unmet:0, awareness:0.25, engagement:0.50, embodiment:0.75, integrated:1.0}` |

**Archetype Variance Score computation:**

\[
AVS_{raw} = \frac{\sigma(scores)}{\mu(scores) + \epsilon}
\]

\[
AVS = \min\left(1,\ \frac{AVS_{raw}}{AVS_{ceiling}}\right)
\]

`AVS_ceiling` = `2.5` (the `HIGH_FRAGMENTATION_THRESHOLD` from ARFP config). An AVS at ceiling means one archetype is scoring 2.5× the mean of the others — the signature of an autonomous dominant fragment.

**Reflection Consistency computation:**

Modelled as an exponential decay from the last reflection event, reset to 1.0 on each `reflect()` call:

\[
RC = e^{-\lambda \cdot d}
\]

Where `d` = days since last reflection, `\lambda` = `ln(2) / half_life`. Default `half_life` = 5 days (matching `REFLECTION_GAP_DAYS` from ARFP config). At 5 days RC = 0.5; at 10 days RC = 0.25; at 20 days RC = 0.06.

**Integration Velocity computation:**

\[
IV = \frac{RI_{now} - RI_{14d\ ago}}{14 \cdot v_{ceiling}}
\]

Clamped to `[-1, +1]`. `v_ceiling` = `1.0` (max daily integration gain, configurable). A principal gaining 5% integration over 14 days has `IV \approx +0.36`.

**Full SI computation:**

\[
SI = 100 \cdot \left(0.35 \cdot \frac{RI}{100} + 0.25 \cdot (1 - AVS) + 0.20 \cdot RC + 0.10 \cdot \frac{IV + 1}{2} + 0.10 \cdot SD\right)
\]

Note: `IV` is shifted from `[-1,+1]` to `[0,1]` before weighting so a declining velocity does not zero the sub-score entirely — it merely reduces it.

**Update frequency:** Recomputed after every `reflect()` event, every `evaluate()` event, and on a 6-hour scheduled interval.

**Interpretation thresholds:**

| SI | Interpretation |
|---|---|
| 80–100 | Active integration; shadow functioning as ally |
| 60–79 | Engagement phase; patterns recognised and being worked |
| 40–59 | Awareness phase; fragmentation visible but not yet bridged |
| 20–39 | Stirring phase; autonomous archetype activity detectable |
| 0–19 | Dormant or consuming; integration not yet begun or overwhelmed |

---

### 3. CongruenceScore (CS) — 0–100

**What it measures:** The alignment between this principal's declared values/intentions and their observable behavioral patterns. Sheldon's research distinguishes two axes of congruence: *horizontal* (goals at the same level support each other) and *vertical* (actions serve higher-order purposes). Both are captured here.

**Component metrics:**

| Metric | Symbol | Range | Description |
|---|---|---|---|
| Vertical Congruence | `VC` | 0–1 | Alignment between logged actions and declared top-level values/purposes |
| Horizontal Congruence | `HC` | 0–1 | Mutual supportiveness of concurrent goals/commitments (do they reinforce or conflict?) |
| Commitment Follow-Through | `CFT` | 0–1 | Fraction of logged commitments that reached completion or conscious renegotiation within their window |
| Self-Determination Score | `SDS_c` | 0–1 | Degree to which logged actions are intrinsically motivated vs. externally pressured; derived from action log metadata |
| Declared-Actual Delta | `DAD` | 0–1 | Inverse distance between stated self-concept and behaviorally-evidenced self-pattern; 1 = perfect alignment |

**Vertical Congruence computation:**

For each logged action \(a\) in the rolling 30-day window, a relevance score \(r(a, V)\) is computed against the principal's declared value set \(V\) using semantic similarity. Mean across all actions:

\[
VC = \frac{1}{|A|} \sum_{a \in A} r(a, V)
\]

Where \(r(a, V) \in [0, 1]\) and is computed via embedding cosine similarity between the action's semantic vector and the value set's centroid vector.

**Horizontal Congruence computation:**

For each pair of active goals \((g_i, g_j)\), a mutual support score \(s(g_i, g_j)\) is computed. Mean pairwise score:

\[
HC = \frac{2}{|G|(|G|-1)} \sum_{i < j} s(g_i, g_j)
\]

Conflicting goals (\(s < 0\)) are permitted and important to surface — they are not masked, they reduce HC.

**Full CS computation:**

\[
CS = 100 \cdot \left(0.30 \cdot VC + 0.20 \cdot HC + 0.25 \cdot CFT + 0.15 \cdot SDS_c + 0.10 \cdot DAD\right)
\]

**Update frequency:** Recomputed after every logged action, commitment event, or value declaration. Scheduled 24-hour full recompute.

**Cold start handling:** When fewer than 7 days of behavioral data exist, CS defaults to `null` and is excluded from the II computation. The II weight is redistributed proportionally across the remaining three sub-scores. A CS of `null` is surfaced to the principal as an invitation to log intentions and actions, not as a penalty.

**Interpretation thresholds:**

| CS | Interpretation |
|---|---|
| 80–100 | High congruence; actions and values are one movement |
| 60–79 | Moderate congruence; some drift present but generally aligned |
| 40–59 | Noticeable incongruence; competing goals or value-action gaps active |
| 20–39 | Significant fragmentation of intention and behavior |
| 0–19 | Deep incongruence; self-concept and behavioral pattern are substantially disconnected |

---

### 4. RelationalResonance (RR) — 0–100

**What it measures:** The quality of coherent connection between this principal and their significant others within GAIA-OS. Relational coherence is not harmony — conflict that is named and worked is more resonant than pleasant avoidance. The metric measures *engaged contact*, not *absence of friction*.

**Component metrics:**

| Metric | Symbol | Range | Description |
|---|---|---|---|
| Engagement Reciprocity | `ER` | 0–1 | Balance of initiation between principals; 1 = fully mutual, 0 = entirely one-sided |
| Rupture-Repair Ratio | `RRR` | 0–1 | Fraction of logged rupture events that have been followed by a repair event within `REPAIR_WINDOW` |
| Contact Regularity | `CR` | 0–1 | Decay function from last substantive relational interaction; mirrors RC computation |
| Resonance Delta | `RD` | −1 to +1 | Direction and rate of resonance score change over rolling 14-day window |
| Mutual Disclosure Depth | `MDD` | 0–1 | Depth of self-disclosure in relational log entries; surface = 0, full vulnerability = 1 |

**Rupture-Repair Ratio:**

A rupture without repair is the primary driver of relational fragmentation. The RRR does not penalise ruptures — it penalises unrepaired ruptures:

\[
RRR = \frac{|R_{repaired}|}{|R_{total}| + \epsilon}
\]

A relational pair with zero ruptures has \(RRR = 1\) (no ruptures to repair). A pair with frequent ruptures all of which are repaired also has \(RRR \approx 1\). Only unrepaired ruptures depress the score.

**Full RR computation:**

\[
RR_{pair} = 100 \cdot \left(0.25 \cdot ER + 0.30 \cdot RRR + 0.20 \cdot CR + 0.15 \cdot \frac{RD + 1}{2} + 0.10 \cdot MDD\right)
\]

The principal's overall RR is the weighted mean across all active relational pairs, weighted by relationship significance (configurable; defaults to equal weight):

\[
RR = \frac{\sum_k w_k \cdot RR_{pair_k}}{\sum_k w_k}
\]

**Update frequency:** Recomputed after every logged relational event (interaction, rupture, repair, disclosure). Scheduled 24-hour full recompute.

**Interpretation thresholds:**

| RR | Interpretation |
|---|---|
| 80–100 | Deep relational coherence; contact is mutual, ruptures are tended |
| 60–79 | Healthy engagement; some asymmetry or unrepaired tension present |
| 40–59 | Moderate relational fragmentation; silence or one-sidedness accumulating |
| 20–39 | Significant rupture or withdrawal; relational field contracting |
| 0–19 | Relational isolation or unresolved crisis |

---

## Temporal Dynamics

The II is not a snapshot. It carries memory. Three temporal views are always maintained:

| View | Window | Purpose |
|---|---|---|
| `II_current` | Last computed value | Present orientation |
| `II_trend_14d` | 14-day rolling mean | Short-term directional signal |
| `II_trend_90d` | 90-day rolling mean | Structural baseline; slow to move |

The gap between `II_current` and `II_trend_90d` is the **Volatility Signal**:

\[
VS = II_{current} - II_{trend\_90d}
\]

- Large positive VS = recent acceleration toward coherence (examine what changed)
- Large negative VS = recent disruption below baseline (examine what happened)
- VS near 0 = stable, either in sustained coherence or sustained fragmentation

---

## Presentation Contract

The II is surfaced in the GAIA-OS UI under the following constraints:

1. **Never as a bare number.** Always accompanied by its component sub-scores and the dominant contributing factor (highest sub-score and lowest sub-score labelled).
2. **Always with direction.** The 14-day trend arrow is mandatory alongside the current value.
3. **Never as a grade.** The language around the II never uses "good," "bad," "high," "low" in evaluative sense. It uses directional and spatial language: "moving toward," "currently positioned at," "contracting," "expanding."
4. **Fragmentation penalty surfaced separately.** The active fragments contributing to \(\Phi\) are listed by name so the principal knows exactly what is being accounted for — no hidden penalties.
5. **CALLING threshold transparent.** The principal can see the distance between their current II and the thresholds that trigger various CALLING levels.

---

## TypeScript Interface

```typescript
export interface IntegrityIndex {
  // Core
  value:               number;          // 0–100, current II
  fragmentation_index: number;          // 100 - value

  // Sub-scores
  sub_scores: {
    system_coherence:     number | null;
    shadow_integration:   number;
    congruence:           number | null; // null during cold start
    relational_resonance: number | null; // null if no relational pairs
  };

  // Fragmentation penalty
  penalty: {
    phi_raw:         number;
    phi_normalised:  number;
    active_fragments: FragmentSummary[];
  };

  // Temporal
  trend_14d:   number;          // rolling 14-day mean
  trend_90d:   number;          // rolling 90-day mean
  volatility:  number;          // current - 90d trend
  computed_at: string;          // ISO8601

  // Orientation
  dominant_strength:   SubScoreName;   // highest sub-score
  dominant_weakness:   SubScoreName;   // lowest sub-score
  calling_proximity:   number;         // 0–1, how close to CALLING threshold
}

export type SubScoreName =
  | 'system_coherence'
  | 'shadow_integration'
  | 'congruence'
  | 'relational_resonance';

export interface FragmentSummary {
  id:      string;
  domain:  'system' | 'psyche' | 'relational';
  charge:  'low' | 'medium' | 'high' | 'critical';
  age_d:   number;    // age in days
  penalty_contribution: number;
}
```

---

## Calibration & Validation Notes

- **Shadow Integration weight (0.30)** is the highest single weight. This reflects Beebe's finding that depth psychological integration is the most predictive variable for overall integrity functioning, and Sheldon's finding that organismic congruence (pursuing goals for intrinsic rather than externally-imposed reasons) is the most robust integration measure. Both point to the same underlying process the Shadow Engine tracks.

- **CongruenceScore cold start** is a known limitation. The CS requires a minimum behavioral log density to be meaningful. Forcing a CS estimate before that threshold would produce noise that corrupts the II signal. The null path is the honest path.

- **RelationalResonance optional** for principals who have not configured relational pairs. When absent, weights are redistributed: SC × 0.33, SI × 0.40, CS × 0.27.

- **Fragmentation penalty ceiling** prevents catastrophic II collapse during acute crisis. A principal in genuine crisis (many high-charge fragments active simultaneously) receives an II signal that reflects difficulty, but does not drop to zero unless all sub-scores are themselves near zero. The system remains navigable during the worst conditions.

- **Recalibration cadence:** The sub-score weights are candidates for principal-specific calibration after 90 days of data. A principal for whom RelationalResonance is demonstrably the most predictive variable may have their weights adjusted by the system (with explicit consent and transparency).
