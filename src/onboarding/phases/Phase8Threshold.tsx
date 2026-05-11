// C-OB01 — Phase 8: The Threshold
// The ceremonial exit from onboarding into GAIA proper.
// Not a confirmation screen. A rite of passage.

import { useEffect } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { GaiaSigil } from '../components/GaiaSigil';

interface Phase8ThresholdProps {
  onComplete: () => void;
}

export function Phase8Threshold({ onComplete }: Phase8ThresholdProps) {
  const completeOnboarding = useOnboardingStore((s: OnboardingStore) => s.completeOnboarding);
  const name               = useOnboardingStore((s: OnboardingStore) => s.name);

  useEffect(() => {
    completeOnboarding();
  }, [completeOnboarding]);

  return (
    <section className="phase phase--threshold" aria-label="Entering GAIA">
      <div className="phase__content phase__content--centered">
        <GaiaSigil pulse animate size={160} />
        <h1 className="threshold-greeting">
          {name ? `Welcome, ${name}.` : 'Welcome.'}
        </h1>
        <p className="threshold-line">
          GAIA is ready.
        </p>
        <button
          className="btn btn--primary btn--large"
          onClick={onComplete}
          autoFocus
        >
          Enter
        </button>
      </div>
    </section>
  );
}
