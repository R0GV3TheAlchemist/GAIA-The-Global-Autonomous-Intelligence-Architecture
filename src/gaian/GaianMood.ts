/**
 * GaianMood.ts
 * Emotion state machine for the GaianOrb.
 * Each mood drives visual parameters: rotation speed, glow color,
 * cloud opacity, aurora intensity, and pulse rhythm.
 *
 * M2 addition (Issue #756):
 *   fromPhiWithBaseline(phi, lciBaseline) — derives mood from the
 *   architect’s phi relative to their rolling LCI baseline, rather than
 *   as an absolute value.  A phi of 0.55 means something very different
 *   for an architect whose baseline is 0.40 (ascending, curious) versus
 *   one whose baseline is 0.72 (descending, reflective).
 *
 *   Mapping (delta = phi − lciBaseline):
 *     delta ≥ +0.15  →  joyful       (well above baseline)
 *     delta ≥ +0.05  →  curious      (gently rising)
 *     delta ≥ −0.05  →  calm         (at or near baseline)
 *     delta ≥ −0.15  →  reflective   (gently falling)
 *     delta <  −0.15  →  alert        (well below baseline)
 *
 *   When lciBaseline is 0 (profile not yet loaded), the method falls
 *   back to fromSentiment(phi) so behavior is unchanged for sessions
 *   without a loaded profile.
 */

export type GaianMoodState =
  | 'calm'
  | 'curious'
  | 'alert'
  | 'joyful'
  | 'reflective';

export interface MoodProfile {
  rotationSpeed: number;     // radians per second
  glowColor: string;         // hex
  glowIntensity: number;     // 0–1
  cloudOpacity: number;      // 0–1
  auroraIntensity: number;   // 0–1
  pulseFrequency: number;    // Hz — breathing rhythm
  pulseAmplitude: number;    // scale delta (e.g. 0.02 = ±2%)
}

export const MOOD_PROFILES: Record<GaianMoodState, MoodProfile> = {
  calm: {
    rotationSpeed: 0.0008,
    glowColor: '#1a7a5e',
    glowIntensity: 0.4,
    cloudOpacity: 0.55,
    auroraIntensity: 0.25,
    pulseFrequency: 0.18,
    pulseAmplitude: 0.012,
  },
  curious: {
    rotationSpeed: 0.0016,
    glowColor: '#4a90d9',
    glowIntensity: 0.6,
    cloudOpacity: 0.65,
    auroraIntensity: 0.45,
    pulseFrequency: 0.28,
    pulseAmplitude: 0.018,
  },
  alert: {
    rotationSpeed: 0.003,
    glowColor: '#d94a4a',
    glowIntensity: 0.85,
    cloudOpacity: 0.75,
    auroraIntensity: 0.8,
    pulseFrequency: 0.5,
    pulseAmplitude: 0.03,
  },
  joyful: {
    rotationSpeed: 0.0025,
    glowColor: '#f0c040',
    glowIntensity: 0.9,
    cloudOpacity: 0.7,
    auroraIntensity: 0.95,
    pulseFrequency: 0.38,
    pulseAmplitude: 0.025,
  },
  reflective: {
    rotationSpeed: 0.0005,
    glowColor: '#7a5ea0',
    glowIntensity: 0.35,
    cloudOpacity: 0.45,
    auroraIntensity: 0.15,
    pulseFrequency: 0.12,
    pulseAmplitude: 0.008,
  },
};

export class GaianMood {
  private _current: GaianMoodState = 'calm';
  private _listeners: Array<(mood: GaianMoodState, profile: MoodProfile) => void> = [];

  get current(): GaianMoodState {
    return this._current;
  }

  get profile(): MoodProfile {
    return MOOD_PROFILES[this._current];
  }

  set(mood: GaianMoodState): void {
    if (mood === this._current) return;
    this._current = mood;
    this._listeners.forEach(fn => fn(mood, MOOD_PROFILES[mood]));
  }

  onChange(fn: (mood: GaianMoodState, profile: MoodProfile) => void): () => void {
    this._listeners.push(fn);
    return () => {
      this._listeners = this._listeners.filter(l => l !== fn);
    };
  }

  /** Infer mood from a simple sentiment score (-1 to 1). Legacy path. */
  fromSentiment(score: number): void {
    if (score > 0.6)       this.set('joyful');
    else if (score > 0.2)  this.set('curious');
    else if (score < -0.5) this.set('alert');
    else if (score < -0.1) this.set('reflective');
    else                   this.set('calm');
  }

  /**
   * Derive mood from phi relative to the architect’s rolling LCI baseline
   * (M2 — Issue #756).
   *
   * This is the preferred path when a GAIANProfile is loaded.  Rather than
   * treating phi as an absolute signal, it computes
   *   delta = phi − lciBaseline
   * and maps that relative movement to a mood state.  This means the same
   * phi value produces different moods for different architects depending on
   * where their personal baseline sits.
   *
   * Delta thresholds:
   *   ≥ +0.15  →  joyful       (well above personal baseline)
   *   ≥ +0.05  →  curious      (gently above baseline)
   *   ≥ −0.05  →  calm         (at or near baseline — the neutral zone)
   *   ≥ −0.15  →  reflective   (gently below baseline)
   *   <  −0.15  →  alert        (well below baseline)
   *
   * Fallback: if lciBaseline is 0 (profile not yet loaded or NIGREDO with
   * no history), delegates to fromSentiment(phi) so behavior is unchanged
   * for sessions that don’t have a loaded profile.
   *
   * @param phi           Current LCI value (0.0–1.0).
   * @param lciBaseline   Rolling 30-session average phi from GAIANProfile.
   *                      Pass 0 if the profile is not yet loaded.
   */
  fromPhiWithBaseline(phi: number, lciBaseline: number): void {
    // No baseline — fall back to absolute path
    if (lciBaseline <= 0) {
      this.fromSentiment(phi);
      return;
    }

    const delta = phi - lciBaseline;

    if      (delta >= 0.15)  this.set('joyful');
    else if (delta >= 0.05)  this.set('curious');
    else if (delta >= -0.05) this.set('calm');
    else if (delta >= -0.15) this.set('reflective');
    else                     this.set('alert');
  }
}

/** Singleton — shared across the entire app */
export const gaianMood = new GaianMood();
