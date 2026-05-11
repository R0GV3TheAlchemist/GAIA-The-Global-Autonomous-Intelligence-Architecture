// C-OB01 — Phase 1: The Awakening
// GAIA's first breath. No UI chrome. Just presence.
// Typewriter text, a slow sigil pulse, and a single action.

import { useState, useEffect } from 'react';
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
  const [lineIndex, setLineIndex]       = useState(0);
  const [showContinue, setShowContinue] = useState(false);

  useEffect(() => {
    if (lineIndex >= AWAKENING_LINES.length - 1) {
      const t = setTimeout(() => setShowContinue(true), 800);
      return () => clearTimeout(t);
    }
  }, [lineIndex]);

  const handleLineComplete = () => {
    if (lineIndex < AWAKENING_LINES.length - 1) {
      setTimeout(() => setLineIndex((i) => i + 1), 600);
    }
  };

  return (
    <section className="phase phase--awakening" aria-label="GAIA awakening">
      <div className="phase__content phase__content--centered">
        <GaiaSigil animate size={120} />
        <div className="awakening-lines" aria-live="polite">
          <TypewriterText
            key={AWAKENING_LINES[lineIndex]}
            text={AWAKENING_LINES[lineIndex]}
            speed={40}
            onComplete={handleLineComplete}
            tag="p"
            className="awakening-line"
          />
        </div>
        {showContinue && (
          <button
            className="btn btn--ghost btn--large"
            onClick={nextPhase}
            onKeyDown={(e) => { if (e.key === 'Escape') markInterrupted(); }}
            autoFocus
          >
            Continue
          </button>
        )}
      </div>
    </section>
  );
}
