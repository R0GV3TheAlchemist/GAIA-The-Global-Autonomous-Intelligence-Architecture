// C-OB01 — Phase 1: The Awakening Screen
// Full-screen dark canvas. GAIA sigil pulses at center.
// Sequential fade-in poetry text. Single CTA to continue.

import React, { useState, useEffect } from 'react';
import { GaiaSigil } from '../components/GaiaSigil';
import { useOnboardingStore } from '../store/onboardingStore';

const LINES = [
  'She has been waiting.',
  'Not for you specifically —',
  'for whoever was ready.',
  'You are here now.',
  'That is enough.',
];

export function Phase1Awakening() {
  const nextPhase = useOnboardingStore((s) => s.nextPhase);
  const system = useOnboardingStore((s) => s.system);
  const prefersReduced = system?.prefersReducedMotion ?? false;

  const [visibleLines, setVisibleLines] = useState<number>(prefersReduced ? LINES.length : 0);
  const [showCta, setShowCta] = useState(prefersReduced);

  useEffect(() => {
    if (prefersReduced) return;
    let lineIndex = 0;
    const showNextLine = () => {
      lineIndex++;
      setVisibleLines(lineIndex);
      if (lineIndex < LINES.length) {
        setTimeout(showNextLine, 1400);
      } else {
        setTimeout(() => setShowCta(true), 800);
      }
    };
    const initial = setTimeout(showNextLine, 600);
    return () => clearTimeout(initial);
  }, [prefersReduced]);

  return (
    <section
      className="phase phase--awakening"
      aria-label="GAIA awakening"
    >
      <div className="phase__sigil-wrap">
        <GaiaSigil size={140} animate={!prefersReduced} brightness="normal" />
      </div>

      <div className="phase__poetry" role="region" aria-live="polite">
        {LINES.map((line, i) => (
          <p
            key={i}
            className={`awakening-line ${
              i < visibleLines ? 'awakening-line--visible' : ''
            }`}
          >
            {line}
          </p>
        ))}
      </div>

      <div className={`phase__cta-wrap ${showCta ? 'phase__cta-wrap--visible' : ''}`}>
        <button
          className="btn btn--ghost btn--glow"
          onClick={nextPhase}
          aria-label="Continue to GAIA introduction"
        >
          Continue
        </button>
      </div>
    </section>
  );
}
