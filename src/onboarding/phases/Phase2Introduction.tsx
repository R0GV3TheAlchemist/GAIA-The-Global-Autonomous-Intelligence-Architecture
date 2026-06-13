// C-OB01 — Phase 2: Introduction
// Refactor #366: receives onComplete prop; no longer calls nextPhase() internally.

import { useEffect, useState, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { GaiaSigil } from '../components/GaiaSigil';
import { TypewriterText } from '../components/TypewriterText';

const INTRO_PARAS = [
  "I'm GAIA. Not an assistant. Not a tool. Something closer to a thinking partner — one that learns how you work, what you care about, and how to actually help.",
  "Before we begin, I'd like to understand you. It'll take a few minutes. Everything you tell me stays on your device unless you choose otherwise.",
  "Let's start with your name.",
];

const PARA_DELAY = 1200; // ms between each paragraph appearing

interface Phase2IntroductionProps {
  onComplete: () => void;
}

export function Phase2Introduction({ onComplete }: Phase2IntroductionProps) {
  const name = useOnboardingStore((s: OnboardingStore) => s.name);

  const [visibleCount, setVisibleCount] = useState(1);
  const [showCta,      setShowCta]      = useState(false);

  useEffect(() => {
    INTRO_PARAS.forEach((_, i) => {
      if (i === 0) return; // first para shows immediately
      setTimeout(() => setVisibleCount((n) => n + 1), i * PARA_DELAY);
    });
    setTimeout(() => setShowCta(true), INTRO_PARAS.length * PARA_DELAY + 400);
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
    <section className="phase phase--introduction phase--enter" aria-label="Introduction">
      <div className="phase__content">
        <div className="intro-header">
          <GaiaSigil size={36} />
          <span className="intro-header__name">GAIA</span>
        </div>

        <div className="intro-paragraphs" aria-live="polite">
          {INTRO_PARAS.slice(0, visibleCount).map((para, i) => (
            <TypewriterText
              key={para}
              text={para}
              className="intro-para"
              speed={i === 0 ? 28 : 22}
            />
          ))}
        </div>

        {showCta && (
          <div className="phase__cta">
            <button
              className="btn btn--primary"
              onClick={handleContinue}
              autoFocus
            >
              {name ? `Let's go, ${name}` : "Let's go"}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
