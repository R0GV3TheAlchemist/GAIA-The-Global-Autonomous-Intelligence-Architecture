// C-OB01 — Phase 8: The Threshold
// The ceremonial exit from onboarding into GAIA proper.
// Not a confirmation screen. A rite of passage.
// FIX: Added staggered threshold-line entrance animations matching CSS definitions.

import { useEffect, useState } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { GaiaSigil } from '../components/GaiaSigil';

const THRESHOLD_LINES = [
  { text: 'The foundation is set.', muted: true },
  { text: 'Your context is yours.', muted: true },
  { text: 'GAIA is ready.', muted: false },
];

interface Phase8ThresholdProps {
  onComplete: () => void;
}

export function Phase8Threshold({ onComplete }: Phase8ThresholdProps) {
  const completeOnboarding = useOnboardingStore((s: OnboardingStore) => s.completeOnboarding);
  const name               = useOnboardingStore((s: OnboardingStore) => s.name);

  const [visibleLines, setVisibleLines] = useState<number[]>([]);
  const [showEnter, setShowEnter]       = useState(false);

  useEffect(() => {
    completeOnboarding();

    // Stagger each threshold-line into view
    THRESHOLD_LINES.forEach((_, i) => {
      setTimeout(() => {
        setVisibleLines((prev) => [...prev, i]);
      }, 600 + i * 700);
    });

    // Show Enter button after all lines have appeared
    setTimeout(() => setShowEnter(true), 600 + THRESHOLD_LINES.length * 700 + 400);
  }, [completeOnboarding]);

  return (
    <section className="phase phase--threshold" aria-label="Entering GAIA">
      <div className="phase__content phase__content--centered">
        <GaiaSigil animate brightness="bright" size={160} />

        <h1 className="threshold-greeting">
          {name ? `Welcome, ${name}.` : 'Welcome.'}
        </h1>

        <div className="threshold-lines" aria-live="polite">
          {THRESHOLD_LINES.map((line, i) => (
            <p
              key={line.text}
              className={[
                'threshold-line',
                line.muted ? 'threshold-line--muted' : '',
                visibleLines.includes(i) ? 'threshold-line--visible' : '',
              ].filter(Boolean).join(' ')}
            >
              {line.text}
            </p>
          ))}
        </div>

        {showEnter && (
          <button
            className="btn btn--primary btn--large"
            onClick={onComplete}
            autoFocus
          >
            Enter
          </button>
        )}
      </div>
    </section>
  );
}
