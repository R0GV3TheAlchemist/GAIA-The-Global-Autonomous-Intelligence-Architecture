// C-OB01 — Phase 1: Awakening
// Refactor #366: receives onComplete prop; no longer calls nextPhase() internally.
// The router owns all navigation. This phase owns only its own UI.

import { useEffect, useState, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';

const LINES = [
  'Initialising sensory matrix…',
  'Calibrating context engine…',
  'GAIA is waking.',
];

const LINE_DELAY = 900;   // ms between each line
const CTA_AFTER  = 600;  // ms after last line before Continue appears

interface Phase1AwakeningProps {
  onComplete: () => void;
}

export function Phase1Awakening({ onComplete }: Phase1AwakeningProps) {
  const name = useOnboardingStore((s: OnboardingStore) => s.name);

  const [visibleCount, setVisibleCount] = useState(0);
  const [showCta,      setShowCta]      = useState(false);

  useEffect(() => {
    LINES.forEach((_, i) => {
      setTimeout(() => setVisibleCount((n) => n + 1), i * LINE_DELAY);
    });
    setTimeout(() => setShowCta(true), LINES.length * LINE_DELAY + CTA_AFTER);
  }, []);

  const handleContinue = useCallback(() => onComplete(), [onComplete]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.key === 'Enter' || e.key === ' ') && showCta) {
        const tag = (document.activeElement as HTMLElement)?.tagName;
        if (tag !== 'BUTTON') handleContinue();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showCta, handleContinue]);

  return (
    <section className="phase phase--awakening phase--enter" aria-label="Awakening">
      <div className="phase__content">
        <div className="awakening-lines" aria-live="polite">
          {LINES.slice(0, visibleCount).map((line) => (
            <p key={line} className="awakening-line">{line}</p>
          ))}
        </div>

        {showCta && (
          <div className="phase__cta">
            <button
              className="btn btn--primary"
              onClick={handleContinue}
              autoFocus
            >
              {name ? `Continue, ${name}` : 'Continue'}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
