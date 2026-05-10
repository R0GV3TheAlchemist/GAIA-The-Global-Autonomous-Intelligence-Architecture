// C-OB01 — Phase 8: The Threshold
// Marks end of onboarding as a meaningful moment.
// GAIA sigil returns, brighter. A closing word. Transition to home.

import React, { useState, useEffect } from 'react';
import { GaiaSigil } from '../components/GaiaSigil';
import { useOnboardingStore } from '../store/onboardingStore';

interface Phase8ThresholdProps {
  onComplete: () => void;
}

export function Phase8Threshold({ onComplete }: Phase8ThresholdProps) {
  const completeOnboarding = useOnboardingStore((s) => s.completeOnboarding);
  const system = useOnboardingStore((s) => s.system);
  const prefersReduced = system?.prefersReducedMotion ?? false;

  const [line1Visible, setLine1Visible] = useState(false);
  const [line2Visible, setLine2Visible] = useState(false);
  const [ctaVisible, setCtaVisible] = useState(false);

  useEffect(() => {
    if (prefersReduced) {
      setLine1Visible(true);
      setLine2Visible(true);
      setCtaVisible(true);
      return;
    }
    const t1 = setTimeout(() => setLine1Visible(true), 600);
    const t2 = setTimeout(() => setLine2Visible(true), 2000);
    const t3 = setTimeout(() => setCtaVisible(true), 3200);
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3); };
  }, [prefersReduced]);

  const handleEnter = () => {
    completeOnboarding();
    onComplete();
  };

  return (
    <section
      className="phase phase--threshold"
      aria-label="You have entered GAIA"
    >
      <div className="phase__sigil-wrap phase__sigil-wrap--bright">
        <GaiaSigil size={140} brightness="bright" animate={!prefersReduced} />
      </div>

      <div className="phase__poetry">
        <p className={`threshold-line ${line1Visible ? 'threshold-line--visible' : ''}`}>
          You're in. I'll be here.
        </p>
        <p className={`threshold-line threshold-line--muted ${
          line2Visible ? 'threshold-line--visible' : ''
        }`}>
          Take your time. Or don't. Either way — I'm paying attention.
        </p>
      </div>

      <div className={`phase__cta-wrap ${ctaVisible ? 'phase__cta-wrap--visible' : ''}`}>
        <button
          className="btn btn--primary btn--glow"
          onClick={handleEnter}
          aria-label="Enter GAIA"
        >
          Enter
        </button>
      </div>
    </section>
  );
}
