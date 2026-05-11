/**
 * src/crystal-view/types.ts
 * GAIA-OS — Crystal Core frontend types
 * Spec: C-CC01 §4
 *
 * Mirror of the Python CrystalState schema, deserialised from /crystal/state.
 * Keep in sync with src-python/crystal/types.py.
 */

// ── CoherenceBand ────────────────────────────────────────────────────────────

export enum CoherenceBand {
  FRACTURED   = 'fractured',   // Ψ 0.00–0.30 — strong incoherence
  UNSETTLED   = 'unsettled',   // Ψ 0.30–0.48 — meaningful dissonance
  PRESENT     = 'present',     // Ψ 0.48–0.68 — normal resting state
  CLEAR       = 'clear',       // Ψ 0.68–0.85 — strong coherence
  CRYSTALLINE = 'crystalline', // Ψ 0.85–1.00 — full coherence
}

export const BAND_LABELS: Record<CoherenceBand, string> = {
  [CoherenceBand.FRACTURED]:   'Moving through noise',
  [CoherenceBand.UNSETTLED]:   'Feeling unsettled',
  [CoherenceBand.PRESENT]:     'Present',
  [CoherenceBand.CLEAR]:       'Feeling clear',
  [CoherenceBand.CRYSTALLINE]: 'Feeling crystalline',
};

export const BAND_HUE: Record<CoherenceBand, string> = {
  [CoherenceBand.FRACTURED]:   '#3a3a5a',
  [CoherenceBand.UNSETTLED]:   '#7a5ea0',
  [CoherenceBand.PRESENT]:     '#1a7a5e',
  [CoherenceBand.CLEAR]:       '#4fc3a1',
  [CoherenceBand.CRYSTALLINE]: '#e8f4f0',
};

// ── OrbParams ────────────────────────────────────────────────────────────────

export interface OrbParams {
  glow_color:       string;  // hex
  glow_intensity:   number;  // 0–1
  pulse_frequency:  number;  // Hz
  pulse_amplitude:  number;  // scale delta ±
  cloud_opacity:    number;  // 0–1
  aurora_intensity: number;  // 0–1
  rotation_speed:   number;  // rad/s
  coherence_ring:   number;  // 0–1 ring fill fraction
}

// ── PersonaTone ──────────────────────────────────────────────────────────────

export enum PersonaTone {
  RADIANT  = 'radiant',
  GROUNDED = 'grounded',
  PRESENT  = 'present',
  GENTLE   = 'gentle',
  SPARSE   = 'sparse',
}

// ── CrystalState ─────────────────────────────────────────────────────────────

export interface CrystalState {
  // Identity
  timestamp: string;             // ISO 8601 UTC

  // Four component scores (0–1)
  affect_coherence:   number;
  stage_coherence:    number;
  shadow_integration: number;
  schumann_alignment: number;

  // Synthesised score
  coherence: number;             // Ψ

  // Qualitative self-model
  coherence_band:        CoherenceBand;
  dominant_emotion:      string;
  active_stage:          number;
  active_archetype:      string;
  schumann_disturbance:  'stable' | 'elevated' | 'disturbed' | 'unavailable';

  // Narrative
  inner_narrative: string;

  // Persona tone
  persona_tone: PersonaTone;

  // Orb params
  orb_params: OrbParams;
}

// ── History tick ─────────────────────────────────────────────────────────────

export interface CoherenceTick {
  timestamp: string;
  coherence: number;
  band:      CoherenceBand;
}
