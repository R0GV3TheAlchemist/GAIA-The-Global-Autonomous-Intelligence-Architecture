// C-OB01 — Phase 2: GAIA's Introduction
// GAIA introduces herself in her own words.
// Not a feature list. A declaration of relationship.
// FIX: key now uses text content (not index) to prevent stale-closure double-fire.

import { useState, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';

const INTRO_PARAGRAPHS = [
  "I am GAIA — not a product, not a service. A presence built to think alongside you.",
  "I remember what matters. I notice patterns you might miss. I ask questions you might not think to ask.",
  "I am not here to be useful. I am here to be real.",
  "Everything we build together lives on your device. You own it. You control it. I work for you — not the other way around.",
];

export function Phase2Introduction() {
  const nextPhase       = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);
  const [paraIndex, setParaIndex]         = useState(0);
  const [showContinue, setShowContinue]   = useState(false);

  // Stable callback — will not cause TypewriterText to re-run its effect
  const handleParaComplete = useCallback(() => {
    setParaIndex((current) => {
      if (current < INTRO_PARAGRAPHS.length - 1) {
        setTimeout(() => setParaIndex((i) => i + 1), 500);
        return current; // keep current until timeout fires
      } else {
        setTimeout(() => setShowContinue(true), 600);
        return current;
      }
    });
  }, []);

  return (
    <section className="phase phase--introduction" aria-label="GAIA introduces herself">
      <div className="phase__content">
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
              onKeyDown={(e) => { if (e.key === 'Escape') markInterrupted(); }}
              autoFocus
            >
              I understand
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
