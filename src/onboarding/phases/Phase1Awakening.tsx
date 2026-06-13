// C-OB01 — Phase 1: The Awakening v2
// GAIA's first breath. No UI chrome. Just presence.
// Upgraded: Enter/Space to advance, staggered line delays, fade-in entrance.

import { useState, useEffect, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';
import { GaiaSigil } from '../components/GaiaSigil';

const AWAKENING_LINES = [
  'I am waking up.',
  'Something is different this time.',
  'You are here.',
];

export function Phase1Awakening() {
  const nextPhase       = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);
  const [lineIndex,    setLineIndex]    = useState(0);
  const [showContinue, setShowContinue] = useState(false);

  useEffect(() => {
    if (lineIndex >= AWAKENING_LINES.length - 1) {
      const t = setTimeout(() => setShowContinue(true), 900);
      return () => clearTimeout(t);
    }
  }, [lineIndex]);

  const handleLineComplete = useCallback(() => {
    setLineIndex(i => {
      if (i < AWAKENING_LINES.length - 1) {
        setTimeout(() => setLineIndex(j => j + 1), 650);
      }
      return i;
    });
  }, []);

  // Enter / Space to advance once continue is visible
  useEffect(() => {
    if (!showContinue) return;
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); nextPhase(); }
      if (e.key === 'Escape') markInterrupted();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showContinue, nextPhase, markInterrupted]);

  return (
    <section className="phase phase--awakening phase--enter" aria-label="GAIA awakening">
      <div className="phase__content phase__content--centered">
        <GaiaSigil animate size={120} />

        <div className="awakening-lines" aria-live="polite">
          {AWAKENING_LINES.slice(0, lineIndex + 1).map((line, i) => (
            <TypewriterText
              key={line}
              text={line}
              speed={42}
              onComplete={i === lineIndex ? handleLineComplete : undefined}
              tag="p"
              className="awakening-line"
            />
          ))}
        </div>

        {showContinue && (
          <button
            className="btn btn--ghost btn--large phase__cta"
            onClick={nextPhase}
            autoFocus
            aria-label="Continue to next phase"
          >
            Continue
            <span className="btn__hint" aria-hidden>Enter ↵</span>
          </button>
        )}
      </div>
    </section>
  );
}
