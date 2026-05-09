/**
 * src/hooks/useBreathingAnimation.ts
 * GAIA-OS — Orb Breathing Animation Hook
 * Issue #68 Phase 3
 *
 * Attaches the GSAP breathing animation to the Viriditas orb element.
 * Handles mount, unmount, and tier changes cleanly.
 *
 * Usage (in ViritasWidget):
 *   const orbRef = useRef<HTMLDivElement>(null);
 *   useBreathingAnimation(orbRef, tier);
 */

import { useEffect, useRef } from 'react';
import type { AlignmentTier } from './useAlignment';
import { breathe, orbTierTransition, stopBreathing } from '../lib/breathingAnimator';

export function useBreathingAnimation(
  orbRef:  React.RefObject<HTMLDivElement | null>,
  tier:    AlignmentTier,
): void {
  const prevTierRef = useRef<AlignmentTier | null>(null);
  const mountedRef  = useRef(false);

  useEffect(() => {
    const el = orbRef.current;
    if (!el) return;

    if (!mountedRef.current) {
      // First mount — start breathing immediately, no transition flash
      mountedRef.current = true;
      prevTierRef.current = tier;
      breathe(el, tier);
      return;
    }

    if (tier !== prevTierRef.current) {
      // Tier changed — run the celebratory transition pulse then settle
      prevTierRef.current = tier;
      orbTierTransition(el, tier);
    }
  }, [tier, orbRef]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      const el = orbRef.current;
      if (el) stopBreathing(el);
    };
  }, [orbRef]);
}
