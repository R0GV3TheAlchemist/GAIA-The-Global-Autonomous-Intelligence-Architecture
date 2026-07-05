/**
 * ViriditasTheme.ts — Viriditas UI Layer (Issue #68)
 *
 * Translates the live SchumannState alignment_score + disturbance_level
 * into one of five UI tiers and injects CSS custom properties that every
 * other layer (orb, surfaces, motion) inherits.
 *
 * Tier ladder:
 *   MINIMAL   0.00–0.25  |  any disturbance
 *   CORE      0.26–0.45  |  any disturbance
 *   STANDARD  0.46–0.65  |  stable / elevated
 *   FULL      0.66–0.84  |  stable
 *   VIBRANT   0.85–1.00  |  stable
 *
 * Storm override: disturbance_level === 'disturbed' forces MINIMAL
 * regardless of alignment_score, and sets data-disturbance="disturbed"
 * on <html> so viriditas.css can apply the restorative palette.
 *
 * The Kp > 8 threshold is applied upstream in SchumannEngine — by the
 * time we receive the SchumannState the disturbance_level already
 * reflects it.  We only need to act on the disturbance_level value.
 *
 * M2 additions (Issue #756):
 *   applyProfileTheme(profile) — stamps data-profile-theme and
 *     --color-primary / --color-secondary CSS variables derived from
 *     profile.avatarColor and profile.preferredCrystal onto <html>.
 *     Called once at session init (after applyAlignmentTheme) and on
 *     any profile mutation.  The Viriditas tier system continues to
 *     control layout/motion; the profile layer controls identity colors.
 *
 *   clearProfileTheme() — removes profile data attributes and CSS vars
 *     (call on logout or profile reset).
 */

import type { GAIANProfile } from './GAIANProfile';

// ── Types ─────────────────────────────────────────────────────────────────────

/** Five adaptive UI tiers ordered from dormant → vibrant. */
export enum AlignmentTier {
  MINIMAL  = 'minimal',
  CORE     = 'core',
  STANDARD = 'standard',
  FULL     = 'full',
  VIBRANT  = 'vibrant',
}

/** Mirrors SchumannState.to_stage_dict() fields consumed by the UI. */
export interface AlignmentState {
  /** Composite score in [0.0, 1.0]. 0.45×stability + 0.30×harmonic_coherence + 0.25×signal_quality. */
  alignment_score:       number;
  /** Qualitative EM state: 'stable' | 'elevated' | 'disturbed' | 'unavailable'. */
  disturbance_level:     string;
  /** Best estimate of SR fundamental frequency (Hz). Nominal 7.83 Hz. */
  fundamental_hz:        number;
  /** Normalised geomagnetic activity index 0.0 (quiet) → 1.0 (severe storm). */
  geomagnetic_activity:  number;
  /** How much to trust this snapshot [0.0–1.0].  Below 0.4 → advisory only. */
  confidence:            number;
  /** UTC ISO timestamp the state was computed. */
  timestamp:             string;
}

// ── Crystal → secondary color (mirrors GaianOrb.ts — single source of truth kept in sync) ──

const CRYSTAL_SECONDARY: Record<string, string> = {
  'amethyst':          '#7b4fa6',
  'clear-quartz':      '#e8f4f8',
  'citrine':           '#e8b84b',
  'obsidian':          '#2a2a2a',
  'labradorite':       '#4a7a9b',
  'rose-quartz':       '#e8a0b0',
  'selenite':          '#f0f0f0',
  'black-tourmaline':  '#1a1a2e',
  'lapis-lazuli':      '#26619c',
};

// ── Classification ───────────────────────────────────────────────────────────

/**
 * Maps alignment_score + disturbance_level to an AlignmentTier.
 *
 * Storm override: 'disturbed' → MINIMAL (regardless of score).
 * Unavailable signal: treated as CORE so the UI stays functional.
 */
export function classifyTier(
  alignmentScore:    number,
  disturbanceLevel:  string,
): AlignmentTier {
  if (disturbanceLevel === 'disturbed') return AlignmentTier.MINIMAL;

  const s = Math.max(0, Math.min(1, alignmentScore));

  if (s <= 0.25) return AlignmentTier.MINIMAL;
  if (s <= 0.45) return AlignmentTier.CORE;
  if (s <= 0.65) return AlignmentTier.STANDARD;
  if (s <= 0.84) return AlignmentTier.FULL;
  return AlignmentTier.VIBRANT;
}

// ── Theme application ────────────────────────────────────────────────────────

/**
 * Injects Viriditas CSS custom properties and data attributes onto
 * <html> so viriditas.css tier overrides take effect globally.
 *
 * Sets:
 *   data-viriditas="minimal|core|standard|full|vibrant"
 *   data-disturbance="stable|elevated|disturbed|unavailable"
 *
 * Individual tier CSS variables are declared in viriditas.css.
 * This function only controls the selector hook — keeping JS and CSS
 * concerns cleanly separated.
 */
export function applyAlignmentTheme(
  tier:        AlignmentTier,
  disturbance: string,
): void {
  const root = document.documentElement;
  root.setAttribute('data-viriditas',   tier);
  root.setAttribute('data-disturbance', disturbance);
}

/**
 * Applies the architect’s profile identity layer to the global CSS scope
 * (M2 — Issue #756).
 *
 * Stamps onto <html>:
 *   data-profile-theme   — profile.theme value (e.g. 'crystalline', 'obsidian')
 *   data-lci-trend       — profile.lciTrend for CSS motion/palette hooks
 *   --color-primary      — profile.avatarColor (the architect’s identity color)
 *   --color-secondary    — crystal resonance tint for profile.preferredCrystal
 *
 * The Viriditas tier system (data-viriditas) continues to control
 * layout density and motion budgets.  The profile layer sits on top and
 * controls identity-specific color, giving every architect a visually
 * distinct session without overriding the safety-critical tier system.
 *
 * Call order at session init:
 *   1. applyAlignmentTheme(tier, disturbance)  — tier system first
 *   2. applyProfileTheme(profile)              — identity layer second
 *
 * Safe to re-call on any profile mutation (crystal change, theme update).
 *
 * @param profile  The loaded GAIANProfile for this architect.
 */
export function applyProfileTheme(profile: GAIANProfile): void {
  const root      = document.documentElement;
  const primary   = profile.avatarColor   || '#4f98a3';
  const secondary = CRYSTAL_SECONDARY[profile.preferredCrystal] || '#2a7a87';
  const theme     = profile.theme         || 'default';
  const trend     = profile.lciTrend      || 'stable';

  root.setAttribute('data-profile-theme', theme);
  root.setAttribute('data-lci-trend',     trend);
  root.style.setProperty('--color-primary',   primary);
  root.style.setProperty('--color-secondary', secondary);
}

/**
 * Removes all profile identity attributes and CSS vars from <html>.
 * Call on logout or profile reset so no stale identity bleeds into
 * the next session.
 */
export function clearProfileTheme(): void {
  const root = document.documentElement;
  root.removeAttribute('data-profile-theme');
  root.removeAttribute('data-lci-trend');
  root.style.removeProperty('--color-primary');
  root.style.removeProperty('--color-secondary');
}

/**
 * Removes all Viriditas data attributes (call on app teardown / logout).
 */
export function clearAlignmentTheme(): void {
  const root = document.documentElement;
  root.removeAttribute('data-viriditas');
  root.removeAttribute('data-disturbance');
}
