/**
 * OrbParams.ts
 * 8-field visual contract from the Crystal Core engine (C-CC01).
 * The Python sidecar derives these from Ψ on every tick.
 * GaianOrb.setParams() consumes this directly — no mood lookup needed.
 */

export interface OrbParams {
  /** Primary glow / atmosphere colour — hex string, e.g. '#4f98a3' */
  primaryColor: string;
  /** Secondary aurora / cloud tint — hex string */
  secondaryColor: string;
  /** Breathing pulse rate in Hz (0.08 Fractured → 0.42 Crystalline) */
  pulseRate: number;
  /** Atmosphere glow radius multiplier (1.0 = neutral) */
  glowRadius: number;
  /** Aurora curtain intensity 0–1 */
  auroraIntensity: number;
  /** Earth rotation speed in radians/frame */
  rotationSpeed: number;
  /** Coherence ring opacity 0–1 (drawn as canvas overlay) */
  coherenceRingOpacity: number;
  /** Human-readable band label, e.g. 'Coherent' */
  bandLabel: CoherenceBandLabel;
}

export type CoherenceBandLabel =
  | 'Fractured'
  | 'Fragmented'
  | 'Coherent'
  | 'Resonant'
  | 'Crystalline';

/**
 * Derive OrbParams from a raw coherence score Ψ ∈ [0, 1].
 * Used as a fallback when the sidecar is unavailable.
 */
export function orbParamsFromPsi(psi: number): OrbParams {
  const clamped = Math.max(0, Math.min(1, psi));

  // Colour interpolation across bands
  // Fractured → Fragmented → Coherent → Resonant → Crystalline
  const BAND_COLORS: Array<{ min: number; primary: string; secondary: string }> = [
    { min: 0.00, primary: '#7a3030', secondary: '#5a2020' }, // Fractured
    { min: 0.30, primary: '#7a6030', secondary: '#5a4820' }, // Fragmented
    { min: 0.50, primary: '#1a7a5e', secondary: '#155f4a' }, // Coherent
    { min: 0.70, primary: '#4f98a3', secondary: '#2a7a87' }, // Resonant
    { min: 0.85, primary: '#a0d4e8', secondary: '#7ab8d0' }, // Crystalline
  ];

  let primary   = BAND_COLORS[0].primary;
  let secondary = BAND_COLORS[0].secondary;
  for (const band of BAND_COLORS) {
    if (clamped >= band.min) {
      primary   = band.primary;
      secondary = band.secondary;
    }
  }

  let bandLabel: CoherenceBandLabel;
  if      (clamped < 0.30) bandLabel = 'Fractured';
  else if (clamped < 0.50) bandLabel = 'Fragmented';
  else if (clamped < 0.70) bandLabel = 'Coherent';
  else if (clamped < 0.85) bandLabel = 'Resonant';
  else                     bandLabel = 'Crystalline';

  return {
    primaryColor:          primary,
    secondaryColor:        secondary,
    pulseRate:             0.08 + clamped * 0.34,      // 0.08 → 0.42 Hz
    glowRadius:            0.8  + clamped * 0.6,       // 0.80 → 1.40
    auroraIntensity:       clamped * 0.95,             // 0.00 → 0.95
    rotationSpeed:         0.0003 + clamped * 0.0018,  // slow → alive
    coherenceRingOpacity:  clamped,                    // directly maps
    bandLabel,
  };
}
