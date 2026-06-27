/**
 * reconciliationTypes.ts
 * Canonical type layer for the Automated Reconciliation of Fragmented Processes (ARFP) protocol
 * and the IntegrityIndex computation engine.
 *
 * Build order: this file is compiled first. Nothing in the reconciliation
 * subsystem imports from anywhere else — all other modules import from here.
 *
 * Canon layer : GAIA-OS Core — Integrity & Coherence Engine
 * Spec version : 1.0  (June 27 2026)
 * Depends on   : none
 */

// ---------------------------------------------------------------------------
// 0. Primitives & Shared Vocabulary
// ---------------------------------------------------------------------------

/** ISO-8601 datetime string, always UTC. */
export type ISOTimestamp = string;

/** Unique identifier — UUID v4 string. */
export type ID = string;

/** A value in the closed interval [0, 1]. */
export type Fraction = number;

/** A value in the closed interval [0, 100]. */
export type Score = number;

/** A value in the closed interval [-1, +1]. */
export type SignedUnit = number;

// ---------------------------------------------------------------------------
// 1. Domain
// ---------------------------------------------------------------------------

/**
 * The three domains in which fragmentation can occur.
 * The ReconciliationEngine is domain-agnostic; domain intelligence
 * lives only in FragmentDetector and BridgeStrategies.
 */
export type Domain = 'system' | 'psyche' | 'relational';

// ---------------------------------------------------------------------------
// 2. Fragment
// ---------------------------------------------------------------------------

/**
 * Charge level — the urgency and weight of a fragment.
 * Maps to penalty weights: low=1, medium=2, high=4, critical=8.
 */
export type ChargeLevel = 'low' | 'medium' | 'high' | 'critical';

/** Numeric penalty weight for each charge level. */
export const CHARGE_WEIGHTS: Record<ChargeLevel, number> = {
  low:      1,
  medium:   2,
  high:     4,
  critical: 8,
} as const;

/**
 * The five phases of the ARFP reconciliation lifecycle.
 * Order is non-negotiable — see protocol spec.
 */
export type ReconciliationPhase =
  | 'DETECT'
  | 'DIAGNOSE'
  | 'WITNESS'
  | 'BRIDGE'
  | 'INTEGRATE';

/**
 * Integration stage for psyche-domain fragments.
 * Parallel to the Shadow Engine's archetype stage model.
 */
export type IntegrationStage =
  | 'unmet'       // fragment not yet encountered
  | 'awareness'   // fragment recognised
  | 'engagement'  // active dialogue begun
  | 'embodiment'  // pattern being lived differently
  | 'integrated'; // fragment functioning as ally

/** Continuous value [0,1] mapped from IntegrationStage. */
export const STAGE_DEPTH: Record<IntegrationStage, Fraction> = {
  unmet:       0.00,
  awareness:   0.25,
  engagement:  0.50,
  embodiment:  0.75,
  integrated:  1.00,
} as const;

/** A fragment — any autonomous piece split from a coherent whole. */
export interface Fragment {
  id:          ID;
  domain:      Domain;
  charge:      ChargeLevel;
  phase:       ReconciliationPhase;

  /** Human-readable name surfaced to the principal. */
  label:       string;

  /** Structured description of the fragmentation pattern. */
  description: string;

  /** UTC timestamp of first detection. */
  detected_at: ISOTimestamp;

  /** Age in fractional days, computed at read time. */
  age_days:    number;

  /**
   * Number of times this fragment has completed a full reconciliation
   * cycle and re-emerged. > 2 triggers CALLING escalation regardless
   * of charge level.
   */
  recurrence_count: number;

  /** Psyche-domain only; null for system and relational. */
  integration_stage: IntegrationStage | null;

  /** Archetype ID for psyche-domain fragments; null otherwise. */
  archetype_id: ID | null;

  /** Relational pair ID for relational-domain fragments; null otherwise. */
  relational_pair_id: ID | null;

  /** Arbitrary key-value metadata for domain-specific enrichment. */
  metadata: Record<string, unknown>;
}

/**
 * A compact representation of a fragment used in IntegrityIndex
 * and CALLING payloads — avoids circular import of full Fragment.
 */
export interface FragmentSummary {
  id:                   ID;
  domain:               Domain;
  charge:               ChargeLevel;
  label:                string;
  age_days:             number;
  recurrence_count:     number;
  penalty_contribution: number;
}

// ---------------------------------------------------------------------------
// 3. Diagnosis
// ---------------------------------------------------------------------------

/** Root cause category for a diagnosed fragment. */
export type DiagnosisCategory =
  | 'state_drift'        // system: desired ≠ actual
  | 'process_death'      // system: process stopped unexpectedly
  | 'queue_saturation'   // system: event backlog exceeding capacity
  | 'shadow_autonomous'  // psyche: archetype operating without contact
  | 'reflection_gap'     // psyche: reflect() not called within threshold
  | 'value_action_gap'   // psyche: declared values ≠ logged actions
  | 'goal_conflict'      // psyche: concurrent goals pulling against each other
  | 'rupture_unrepaired' // relational: rupture event without repair
  | 'contact_withdrawal' // relational: engagement falling below threshold
  | 'reciprocity_loss'   // relational: initiation become one-sided
  | 'unknown';           // fallback; triggers human review

/** Output of FragmentDiagnoser for a single fragment. */
export interface Diagnosis {
  fragment_id:      ID;
  category:         DiagnosisCategory;
  confidence:       Fraction;     // 0–1, model confidence in category
  root_signal:      string;       // human-readable description of what triggered detection
  contributing_signals: string[]; // secondary signals that elevated charge
  recommended_strategy: BridgeStrategyName;
  diagnosed_at:     ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 4. Bridge Strategies
// ---------------------------------------------------------------------------

/**
 * Named bridge strategies available per domain.
 * BridgeStrategies.ts implements the handler for each.
 */
export type BridgeStrategyName =
  // System
  | 'state_reconcile'      // re-declare desired state; let controller converge
  | 'process_restart'      // controlled restart with health gate
  | 'queue_drain'          // prioritise queue processing; shed low-priority events
  | 'circuit_reset'        // half-open circuit test before full reset
  // Psyche
  | 'shadow_dialogue'      // structured encounter between ego and archetype fragment
  | 'reflection_prompt'    // surface a targeted reflect() prompt to principal
  | 'value_realignment'    // surface value-action gap; invite conscious renegotiation
  | 'goal_conflict_map'    // visualise conflicting goals; invite prioritisation
  // Relational
  | 'repair_initiation'    // surface rupture; invite principal to initiate repair
  | 'contact_invitation'   // surface withdrawal pattern; invite re-engagement
  | 'reciprocity_rebalance'// surface asymmetry; invite conversation about balance
  // Escalation
  | 'slow_witness'         // canary path: watch fragment without intervention
  | 'calling_escalation';  // hard limit: route to principal attention

/** The output of a bridge attempt. */
export interface BridgeResult {
  fragment_id:    ID;
  strategy:       BridgeStrategyName;
  success:        boolean;
  notes:          string;
  next_phase:     ReconciliationPhase;
  completed_at:   ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 5. Witness Protocol
// ---------------------------------------------------------------------------

/**
 * A Witness record — a read-only, non-intervening observation pass
 * over a fragment. The WITNESS phase is mandatory between DIAGNOSE
 * and BRIDGE; it carries the diagnostic signal the fragment holds.
 */
export interface WitnessRecord {
  fragment_id:     ID;
  observed_charge: ChargeLevel;
  observed_phase:  ReconciliationPhase;

  /**
   * Minimum witness duration in hours before BRIDGE is permitted.
   * Computed as: base_hours * charge_multiplier.
   * charge_multipliers: low=1, medium=2, high=4, critical=8.
   */
  minimum_duration_hours: number;

  /** Key observations recorded during the witness period. */
  observations:    string[];

  started_at:      ISOTimestamp;
  completed_at:    ISOTimestamp | null;
  witness_complete: boolean;
}

// ---------------------------------------------------------------------------
// 6. CALLING
// ---------------------------------------------------------------------------

/**
 * CALLING levels — escalating thresholds for principal attention.
 * Automation has a hard limit; the CALLING is GAIA-OS's refusal
 * to suppress rather than integrate.
 */
export type CallingLevel =
  | 'NOTICE'    // informational; surfaced but not blocking
  | 'PROMPT'    // gentle invitation to engage
  | 'SUMMONS'   // firm; integration paused until acknowledged
  | 'CRITICAL'; // all reconciliation halted; principal must engage

/** Conditions that trigger each CALLING level. */
export const CALLING_THRESHOLDS = {
  NOTICE:   { ii_below: 70, charge: 'low'      as ChargeLevel },
  PROMPT:   { ii_below: 55, charge: 'medium'   as ChargeLevel },
  SUMMONS:  { ii_below: 40, charge: 'high'     as ChargeLevel },
  CRITICAL: { ii_below: 25, charge: 'critical' as ChargeLevel },
} as const;

/** A CALLING issued by CallingIssuer to the principal. */
export interface Calling {
  id:              ID;
  level:           CallingLevel;
  fragment_ids:    ID[];          // fragments triggering this CALLING
  trigger_reason:  string;        // human-readable explanation
  ii_at_issue:     Score;         // IntegrityIndex value when issued
  issued_at:       ISOTimestamp;
  acknowledged_at: ISOTimestamp | null;
  resolved_at:     ISOTimestamp | null;
  resolved:        boolean;
}

// ---------------------------------------------------------------------------
// 7. Reconciliation Memory
// ---------------------------------------------------------------------------

/** Persisted record of a completed reconciliation cycle. */
export interface ReconciliationCycle {
  id:             ID;
  fragment_id:    ID;
  domain:         Domain;
  started_at:     ISOTimestamp;
  completed_at:   ISOTimestamp;
  phases_elapsed: ReconciliationPhase[];
  strategy_used:  BridgeStrategyName;
  outcome:        'integrated' | 'suppressed' | 'escalated' | 'abandoned';
  ii_before:      Score;
  ii_after:       Score;
  notes:          string;
}

/** Full memory envelope for a principal. */
export interface ReconciliationMemory {
  principal_id:    ID;
  cycles:          ReconciliationCycle[];
  active_callings: Calling[];
  last_updated:    ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 8. Sub-Scores (IntegrityIndex components)
// ---------------------------------------------------------------------------

// — 8a. SystemCoherence —

export interface SystemCoherenceMetrics {
  process_liveness_rate:   Fraction;  // PLR
  state_divergence_score:  Fraction;  // SDS  (0=in-sync)
  queue_saturation_index:  Fraction;  // QSI  (0=empty)
  circuit_breaker_health:  Fraction;  // CBH  (1=all closed)
  error_rate:              Fraction;  // ERR  (0=no errors)
}

export interface SystemCoherenceResult {
  score:      Score;            // 0–100
  metrics:    SystemCoherenceMetrics;
  computed_at: ISOTimestamp;
}

// — 8b. ShadowIntegration —

export interface ShadowIntegrationMetrics {
  raw_integration_pct:     Score;       // RI  0–100, from Shadow Engine
  archetype_variance_score: Fraction;   // AVS  (0=uniform, 1=extreme outlier)
  reflection_consistency:  Fraction;    // RC  (decay from last reflect())
  integration_velocity:    SignedUnit;  // IV  (-1 declining → +1 accelerating)
  stage_depth:             Fraction;    // SD  (0=unmet, 1=integrated)
}

export interface ShadowIntegrationResult {
  score:       Score;
  metrics:     ShadowIntegrationMetrics;
  computed_at: ISOTimestamp;
}

// — 8c. CongruenceScore —

export interface CongruenceMetrics {
  vertical_congruence:       Fraction;  // VC  action→value alignment
  horizontal_congruence:     Fraction;  // HC  goal mutual support
  commitment_follow_through: Fraction;  // CFT completion or renegotiation rate
  self_determination_score:  Fraction;  // SDS_c intrinsic vs external motivation
  declared_actual_delta:     Fraction;  // DAD  1=perfect alignment
}

export interface CongruenceResult {
  /** null during cold-start (< 7 days behavioral data). */
  score:          Score | null;
  cold_start:     boolean;
  metrics:        CongruenceMetrics | null;
  data_window_days: number;            // days of behavioral data available
  computed_at:    ISOTimestamp;
}

// — 8d. RelationalResonance —

export interface RelationalPairMetrics {
  pair_id:                  ID;
  engagement_reciprocity:   Fraction;   // ER
  rupture_repair_ratio:     Fraction;   // RRR
  contact_regularity:       Fraction;   // CR  (decay from last interaction)
  resonance_delta:          SignedUnit;  // RD  (-1 declining → +1 accelerating)
  mutual_disclosure_depth:  Fraction;   // MDD
  weight:                   Fraction;   // significance weight in mean
  pair_score:               Score;      // RR for this pair
}

export interface RelationalResonanceResult {
  /** null when no relational pairs configured. */
  score:          Score | null;
  pairs:          RelationalPairMetrics[];
  computed_at:    ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 9. IntegrityIndex
// ---------------------------------------------------------------------------

export type SubScoreName =
  | 'system_coherence'
  | 'shadow_integration'
  | 'congruence'
  | 'relational_resonance';

/** Sub-score weights. Must sum to 1.0. */
export const SUB_SCORE_WEIGHTS: Record<SubScoreName, number> = {
  system_coherence:     0.25,
  shadow_integration:   0.30,
  congruence:           0.25,
  relational_resonance: 0.20,
} as const;

/**
 * Redistributed weights when one or more sub-scores are null.
 * Two absence cases are pre-computed; others are computed at runtime.
 */
export const REDISTRIBUTED_WEIGHTS = {
  /** CS null (cold start): SC 0.33, SI 0.40, RR 0.27 */
  no_congruence: {
    system_coherence:     0.33,
    shadow_integration:   0.40,
    relational_resonance: 0.27,
  },
  /** RR null (no relational pairs): SC 0.33, SI 0.40, CS 0.27 */
  no_relational: {
    system_coherence:     0.33,
    shadow_integration:   0.40,
    congruence:           0.27,
  },
  /** Both CS and RR null: SC 0.45, SI 0.55 */
  no_congruence_no_relational: {
    system_coherence:     0.45,
    shadow_integration:   0.55,
  },
} as const;

/** Fragmentation penalty envelope. */
export interface FragmentationPenalty {
  phi_raw:          number;           // Σ (charge_weight * log2(1 + age_days))
  phi_ceiling:      number;           // configurable ceiling (default 20.0)
  phi_normalised:   number;           // proportional penalty applied to II_base
  active_fragments: FragmentSummary[];
}

/** Temporal views maintained alongside current II. */
export interface IITemporalViews {
  trend_14d:        Score;            // 14-day rolling mean
  trend_90d:        Score;            // 90-day rolling mean (structural baseline)
  volatility_signal: number;          // current - trend_90d
}

/** The full IntegrityIndex envelope returned by IntegrityIndex.ts. */
export interface IntegrityIndex {
  // Core
  value:                Score;        // 0–100, final II after penalty
  fragmentation_index:  Score;        // 100 - value

  // Sub-scores
  sub_scores: {
    system_coherence:     SystemCoherenceResult;
    shadow_integration:   ShadowIntegrationResult;
    congruence:           CongruenceResult;
    relational_resonance: RelationalResonanceResult;
  };

  // Weights actually used (may differ from SUB_SCORE_WEIGHTS if nulls present)
  weights_used: Partial<Record<SubScoreName, number>>;

  // Penalty
  penalty: FragmentationPenalty;

  // Temporal
  temporal: IITemporalViews;

  // Orientation signals
  dominant_strength:  SubScoreName;   // highest non-null sub-score
  dominant_weakness:  SubScoreName;   // lowest non-null sub-score
  calling_proximity:  Fraction;       // 0–1, distance to nearest CALLING threshold

  computed_at: ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 10. Reconciliation Engine — runtime envelopes
// ---------------------------------------------------------------------------

/**
 * Input to ReconciliationEngine.run() for a single principal.
 * The engine is domain-agnostic; all domain awareness is in the handlers.
 */
export interface ReconciliationRequest {
  principal_id:   ID;
  domains:        Domain[];           // which domains to scan this run
  force_full_run: boolean;            // bypass incremental optimisation
  requested_at:   ISOTimestamp;
}

/** The output of a full ReconciliationEngine.run() pass. */
export interface ReconciliationReport {
  principal_id:      ID;
  fragments_detected: FragmentSummary[];
  diagnoses:         Diagnosis[];
  bridge_results:    BridgeResult[];
  callings_issued:   Calling[];
  integrity_index:   IntegrityIndex;
  run_duration_ms:   number;
  completed_at:      ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 11. Configuration
// ---------------------------------------------------------------------------

/**
 * Runtime configuration surface — values sourced from arfp.yaml.
 * All thresholds are here so no magic numbers appear in engine logic.
 */
export interface ARFPConfig {
  // Fragment detection
  high_fragmentation_avs_threshold: number;   // default 2.5
  reflection_gap_days:              number;   // default 5
  repair_window_days:               number;   // default 14

  // Fragmentation penalty
  phi_ceiling:                      number;   // default 20.0

  // Witness protocol
  witness_base_hours:               number;   // default 1.0; multiplied by charge weight

  // Recurrence
  recurrence_calling_threshold:     number;   // default 2; triggers CALLING regardless of charge

  // Integration velocity
  integration_velocity_ceiling:     number;   // default 1.0 (max daily gain %)

  // Temporal
  trend_short_window_days:          number;   // default 14
  trend_long_window_days:           number;   // default 90

  // Cold start
  congruence_cold_start_days:       number;   // default 7

  // Relational decay
  contact_regularity_half_life_days: number;  // default 5 (mirrors reflection_gap_days)
}

/** Default configuration. Override per-principal via arfp.yaml. */
export const DEFAULT_ARFP_CONFIG: ARFPConfig = {
  high_fragmentation_avs_threshold:  2.5,
  reflection_gap_days:               5,
  repair_window_days:                14,
  phi_ceiling:                       20.0,
  witness_base_hours:                1.0,
  recurrence_calling_threshold:      2,
  integration_velocity_ceiling:      1.0,
  trend_short_window_days:           14,
  trend_long_window_days:            90,
  congruence_cold_start_days:        7,
  contact_regularity_half_life_days: 5,
} as const;
