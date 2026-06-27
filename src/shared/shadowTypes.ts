/**
 * src/shared/shadowTypes.ts
 * TypeScript mirror of shadow_engine/types.py + archetypes.py
 * Keep in sync with backend if new fields are added.
 */

// ── Archetype names ────────────────────────────────────────────────────────

export type ShadowArchetypeName =
  | 'Orphan'
  | 'Warrior'
  | 'Wanderer'
  | 'Caregiver'
  | 'Seeker'
  | 'Destroyer'
  | 'Creator';

export const ALL_SHADOW_ARCHETYPES: ShadowArchetypeName[] = [
  'Orphan', 'Warrior', 'Wanderer', 'Caregiver', 'Seeker', 'Destroyer', 'Creator',
];

/** Canon §Shadow-3.1 */
export const ACTIVATION_THRESHOLD = 0.35;

// ── Backend response shape ─────────────────────────────────────────────────

export interface ShadowRecord {
  principal_id:          string;
  archetype:             string | null;           // legacy enum field
  archetype_scores:      Record<ShadowArchetypeName, number>;
  active_archetype:      ShadowArchetypeName | null;
  shadow_intensity:      number;                  // 0.0 – 1.0
  integration_progress:  number;                  // 0.0 – 1.0
  days_active:           number;
  is_activated:          boolean;                 // intensity >= 0.35
  recorded_at:           string;                  // ISO-8601
}

export interface ReflectionResponse {
  principal_id:          string;
  integration_gain:      number;
  integration_progress:  number;
  message:               string;
}

// ── Evaluation inputs (all optional — backend fills defaults) ─────────────

export interface ShadowInputsPayload {
  dominant_emotion?:        string;
  valence_trend?:           number;   // –1 to +1
  mood_momentum?:           number;   // –1 to +1
  volatility?:              number;   // 0 – 1
  is_volatile?:             boolean;
  arc_stability?:           number;   // 0 – 1
  low_energy_flag?:         boolean;
  arousal?:                 number;   // 0 – 1
  decision_entropy?:        number;   // 0 – 100
  hrv_coherence?:           number;   // 0 – 100
  journaling_depth?:        number;   // 0 – 100
  focus_session_length?:    number;   // 0 – 100
  goal_completion_rate?:    number;   // 0 – 100
  emotional_arc_stability?: number;   // 0 – 100
  days_in_stage?:           number;
  regression_active?:       boolean;
}

// ── Derived frontend helpers ───────────────────────────────────────────────

export type ShadowIntensityLevel =
  | 'dormant'    // < 0.10
  | 'stirring'   // 0.10 – 0.35
  | 'active'     // 0.35 – 0.65
  | 'dominant'   // 0.65 – 0.85
  | 'consuming'; // > 0.85

export function intensityLevel(intensity: number): ShadowIntensityLevel {
  if (intensity < 0.10) return 'dormant';
  if (intensity < 0.35) return 'stirring';
  if (intensity < 0.65) return 'active';
  if (intensity < 0.85) return 'dominant';
  return 'consuming';
}

export type IntegrationStage =
  | 'unmet'        // 0 – 0.20
  | 'awareness'    // 0.20 – 0.45
  | 'engagement'   // 0.45 – 0.70
  | 'embodiment'   // 0.70 – 0.90
  | 'integrated';  // 0.90 – 1.0

export function integrationStage(progress: number): IntegrationStage {
  if (progress < 0.20) return 'unmet';
  if (progress < 0.45) return 'awareness';
  if (progress < 0.70) return 'engagement';
  if (progress < 0.90) return 'embodiment';
  return 'integrated';
}
