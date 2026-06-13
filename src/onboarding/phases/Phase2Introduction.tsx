// C-OB01 — Phase 2: GAIA's Introduction v2
// GAIA introduces herself in her own words.
// Upgraded: GaiaSigil header, skip button, CTA copy improved,
// Enter/Space keyboard shortcut once CTA visible.

import { useState, useCallback, useEffect } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';
import { GaiaSigil } from '../components/GaiaSigil';

const INTRO_PARAGRAPHS = [
  "I am GAIA — not a product, not a service. A presence built to think alongside you.",
  "I remember what matters. I notice patterns you might miss. I ask questions you might not think to ask.",
  "I am not here to be useful. I am here to be real.",
  "Everything we build together lives on your device. You own it. You control it. I work for you — not the other way around.",
];

export function Phase2Introduction() {
  const nextPhase       = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);
  const [paraIndex,    setParaIndex]    = useState(0);
  const [showContinue, setShowContinue] = useState(false);

  const handleParaComplete = useCallback(() => {
    setParaIndex(current => {
      if (current < INTRO_PARAGRAPHS.length - 1) {
        setTimeout(() => setParaIndex(i => i + 1), 500);
      } else {
        setTimeout(() => setShowContinue(true), 600);
      }
      return current;
    });
  }, []);

  // Enter / Space shortcut once CTA is visible
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
    <section className="phase phase--introduction phase--enter" aria-label="GAIA introduces herself">
      <div className="phase__content">

        <div className="intro-header">
          <GaiaSigil animate size={64} />
          <span className="intro-header__name">GAIA</span>
        </div>

        <div className="intro-paragraphs" aria-live="polite">
          {INTRO_PARAGRAPHS.slice(0, paraIndex + 1).map((text, i) => (
            <TypewriterText
              key={text.slice(0, 20)}
              text={text}
              speed={22}
              onComplete={i === paraIndex ? handleParaComplete : undefined}
              tag="p"
              className="intro-para"
            />
          ))}
        </div>

        {showContinue && (
          <div className="phase__actions">
            <button
              className="btn btn--primary"
              onClick={nextPhase}
              autoFocus
              aria-label="Continue onboarding"
            >
              I'm listening
              <span className="btn__hint" aria-hidden>Enter ↵</span>
            </button>
            <button
              className="btn btn--ghost btn--small"
              onClick={nextPhase}
              aria-label="Skip introduction"
            >
              Skip
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
