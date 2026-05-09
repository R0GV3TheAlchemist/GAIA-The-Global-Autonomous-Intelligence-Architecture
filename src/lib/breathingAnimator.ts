/**
 * src/lib/breathingAnimator.ts
 * GAIA-OS — GSAP Breathing Animation Utility
 * Issue #68 Phase 3
 *
 * Manages the ambient breathing / pulse animation on the Viriditas orb
 * and any other element that should inhale/exhale with the user's tier.
 *
 * Uses GSAP (already in package.json) instead of Framer Motion to
 * avoid adding a new dependency. GSAP yoyo tweens are lower overhead
 * for long-running infinite animations than CSS keyframes because they
 * share a single GSAP ticker rather than triggering layout recalc.
 *
 * Breathing rates are read from the Phase 1 CSS token --breathing-rate,
 * so they automatically update when applyAlignmentTheme() injects new
 * token values — no hardcoded values in this file.
 *
 * All animation calls are guarded by prefersReducedMotion().
 *
 * Usage:
 *   breathe(orbElement, 'full');   // start breathing
 *   stopBreathing(orbElement);     // kill on unmount
 */

import gsap from 'gsap';
import type { AlignmentTier } from '../hooks/useAlignment';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface TierMotionVariant {
  scaleMin:    number;  // minimum scale at exhale
  scaleMax:    number;  // maximum scale at inhale
  opacityMin:  number;  // opacity at exhale
  opacityMax:  number;  // opacity at inhale (usually 1)
  ease:        string;  // GSAP ease string
}

// ---------------------------------------------------------------------------
// Tier motion variants
// Each tier has its own breathing character:
//   minimal  — barely perceptible, slow, deeply restorative
//   core     — gentle swell, calming
//   standard — balanced, neutral pulse
//   full     — confident expansion, alive
//   vibrant  — exuberant, radiant pulsing
// ---------------------------------------------------------------------------

export const TIER_MOTION_VARIANTS: Record<AlignmentTier, TierMotionVariant> = {
  minimal: {
    scaleMin:   0.96,
    scaleMax:   1.02,
    opacityMin: 0.72,
    opacityMax: 0.88,
    ease:       'sine.inOut',
  },
  core: {
    scaleMin:   0.95,
    scaleMax:   1.04,
    opacityMin: 0.78,
    opacityMax: 0.92,
    ease:       'sine.inOut',
  },
  standard: {
    scaleMin:   0.94,
    scaleMax:   1.06,
    opacityMin: 0.82,
    opacityMax: 1.0,
    ease:       'power1.inOut',
  },
  full: {
    scaleMin:   0.92,
    scaleMax:   1.08,
    opacityMin: 0.86,
    opacityMax: 1.0,
    ease:       'power2.inOut',
  },
  vibrant: {
    scaleMin:   0.90,
    scaleMax:   1.12,
    opacityMin: 0.88,
    opacityMax: 1.0,
    ease:       'power2.inOut',
  },
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function prefersReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
}

/**
 * Reads --breathing-rate from the live computed style of the document root.
 * Falls back to the standard-tier value (4s) if not available.
 * Returns value in seconds as a number.
 */
function getBreathingRateSeconds(): number {
  if (typeof document === 'undefined') return 4;
  const raw = getComputedStyle(document.documentElement)
    .getPropertyValue('--breathing-rate')
    .trim();
  // Token is expressed as "4s" or "8s" etc.
  const parsed = parseFloat(raw);
  return isNaN(parsed) ? 4 : parsed;
}

// ---------------------------------------------------------------------------
// Active tween registry — keyed by element so we can kill by reference
// ---------------------------------------------------------------------------
const _activeTweens = new WeakMap<Element, gsap.core.Tween>();

// ---------------------------------------------------------------------------
// breathe(element, tier)
//
// Starts (or restarts on tier change) the GSAP breathing tween on the
// given element. The half-period of the tween is breathingRate / 2
// because GSAP yoyo goes to scaleMax then back to scaleMin in one
// repeat cycle, so one full breath = 2 × duration.
// ---------------------------------------------------------------------------
export function breathe(element: Element, tier: AlignmentTier): void {
  if (prefersReducedMotion()) return;

  // Kill any existing tween on this element
  stopBreathing(element);

  const variant       = TIER_MOTION_VARIANTS[tier];
  const breathingSecs = getBreathingRateSeconds();
  const halfPeriod    = breathingSecs / 2;

  const tween = gsap.fromTo(
    element,
    {
      scale:   variant.scaleMin,
      opacity: variant.opacityMin,
    },
    {
      scale:    variant.scaleMax,
      opacity:  variant.opacityMax,
      duration: halfPeriod,
      ease:     variant.ease,
      repeat:   -1,    // infinite
      yoyo:     true,  // reverse on each repeat — creates inhale/exhale
    },
  );

  _activeTweens.set(element, tween);
}

// ---------------------------------------------------------------------------
// stopBreathing(element)
//
// Kills the active tween and resets transform/opacity so the element
// lands in a clean state for the next animation pass.
// ---------------------------------------------------------------------------
export function stopBreathing(element: Element): void {
  const existing = _activeTweens.get(element);
  if (existing) {
    existing.kill();
    gsap.set(element, { clearProps: 'scale,opacity' });
    _activeTweens.delete(element);
  }
}

// ---------------------------------------------------------------------------
// orbTierTransition(element, tier)
//
// Brief celebratory flash when the tier changes — a fast outward pulse
// before the new breathing rhythm settles in. Runs once then hands off
// to breathe().
// ---------------------------------------------------------------------------
export function orbTierTransition(
  element: Element,
  tier:    AlignmentTier,
): void {
  if (prefersReducedMotion()) {
    breathe(element, tier);
    return;
  }

  stopBreathing(element);

  const variant = TIER_MOTION_VARIANTS[tier];

  gsap.timeline()
    .to(element, {
      scale:    variant.scaleMax * 1.15, // overshoot
      opacity:  1,
      duration: 0.35,
      ease:     'power3.out',
    })
    .to(element, {
      scale:    1,
      duration: 0.5,
      ease:     'elastic.out(1, 0.5)',
      onComplete: () => breathe(element, tier), // hand off to steady breathing
    });
}
