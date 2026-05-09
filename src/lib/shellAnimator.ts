/**
 * src/lib/shellAnimator.ts
 * GAIA-OS — Shell Tier Transition Animator
 * Issue #68 Phase 3
 *
 * Animates the .gaia-shell body on alignment tier changes.
 * Triggered when data-alignment-transitioning is set on <html>
 * (set by applyAlignmentTheme in Phase 2).
 *
 * The animation:
 *   1. Reads --animation-speed from the newly-injected tokens
 *   2. Runs a GSAP timeline: brief desaturate → resaturate sweep
 *      + a subtle scale "breath" on the shell body
 *      + a glow pulse on the shell background
 *
 * This file exports a single function: animateShellTierTransition()
 * called by useShellAnimation() hook which mounts a MutationObserver
 * on the <html> element watching for data-alignment-transitioning.
 *
 * Respects prefers-reduced-motion.
 */

import gsap from 'gsap';
import type { AlignmentTier } from '../hooks/useAlignment';

function prefersReducedMotion(): boolean {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
}

/**
 * Reads --animation-speed from the live :root computed style.
 * Returns value in seconds.
 */
function getAnimationSpeedSecs(): number {
  if (typeof document === 'undefined') return 0.4;
  const raw = getComputedStyle(document.documentElement)
    .getPropertyValue('--animation-speed')
    .trim();
  const ms = parseFloat(raw);
  return isNaN(ms) ? 0.4 : ms / 1000;
}

/**
 * animateShellTierTransition(shellEl, tier)
 *
 * Runs a GSAP timeline on the shell root element when a tier transition
 * begins. The animation mirrors the physiological quality of the tier:
 *
 *   minimal / core   — slow fade + gentle scale in
 *   standard         — neutral cross-fade
 *   full / vibrant   — confident expand + brightness flash
 */
export function animateShellTierTransition(
  shellEl: Element,
  tier:    AlignmentTier,
): void {
  if (prefersReducedMotion()) return;

  const speedSecs = getAnimationSpeedSecs();

  // Tier-specific motion character
  const profiles: Record<AlignmentTier, {
    scaleFrom: number;
    scaleTo:   number;
    brightness:number;
    ease:      string;
  }> = {
    minimal:  { scaleFrom: 0.998, scaleTo: 1.000, brightness: 0.85, ease: 'sine.inOut'   },
    core:     { scaleFrom: 0.998, scaleTo: 1.000, brightness: 0.90, ease: 'sine.inOut'   },
    standard: { scaleFrom: 0.999, scaleTo: 1.000, brightness: 0.95, ease: 'power1.inOut' },
    full:     { scaleFrom: 0.999, scaleTo: 1.001, brightness: 1.05, ease: 'power2.out'   },
    vibrant:  { scaleFrom: 0.998, scaleTo: 1.002, brightness: 1.12, ease: 'power3.out'   },
  };

  const p = profiles[tier];

  gsap.timeline()
    // 1. Snap to "from" state instantly
    .set(shellEl, {
      scale:  p.scaleFrom,
      filter: `brightness(${p.brightness}) saturate(0.6)`,
    })
    // 2. Animate to full state over speedSecs
    .to(shellEl, {
      scale:    p.scaleTo,
      filter:   'brightness(1) saturate(1)',
      duration: speedSecs * 3,   // 3× speed token for a slower, graceful sweep
      ease:     p.ease,
    })
    // 3. Gentle settle bounce for full/vibrant
    .to(shellEl, {
      scale:    1,
      duration: speedSecs,
      ease:     'elastic.out(1, 0.6)',
    }, `-=${speedSecs * 0.4}`);
}
