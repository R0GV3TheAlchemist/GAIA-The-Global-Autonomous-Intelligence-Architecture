// C-OB01 — Onboarding Router v2
// Orchestrates all 9 phases (0-8). Handles interruption/resume.
// Upgraded: router-level interrupt guard, animated progress stepper,
// phase name aria-labels, escape key handler.

import { useEffect, useState, useCallback } from 'react';
import { useOnboardingStore, loadPersistedState, type OnboardingStore } from './store/onboardingStore';
import { Phase0Bootstrap }    from './phases/Phase0Bootstrap';
import { Phase1Awakening }    from './phases/Phase1Awakening';
import { Phase2Introduction } from './phases/Phase2Introduction';
import { Phase3NameCovenant } from './phases/Phase3NameCovenant';
import { Phase4ThreeQuestions } from './phases/Phase4ThreeQuestions';
import { Phase5Consent }      from './phases/Phase5Consent';
import { Phase6FirstGift }    from './phases/Phase6FirstGift';
import { Phase7AccountSetup } from './phases/Phase7AccountSetup';
import { Phase8Threshold }    from './phases/Phase8Threshold';
import './onboarding.css';

interface OnboardingRouterProps {
  onFinish: () => void;
}

const PHASE_NAMES: Record<number, string> = {
  0: 'Initialising',
  1: 'Awakening',
  2: 'Introduction',
  3: 'Your Name',
  4: 'Three Questions',
  5: 'Consent',
  6: 'First Gift',
  7: 'Account',
  8: 'Threshold',
};

// Phases shown in the progress stepper (phase 0 is silent bootstrap)
const STEPPER_PHASES = [1, 2, 3, 4, 5, 6, 7, 8];

export function OnboardingRouter({ onFinish }: OnboardingRouterProps) {
  const phase             = useOnboardingStore((s: OnboardingStore) => s.phase);
  const completed         = useOnboardingStore((s: OnboardingStore) => s.completed);
  const resumeOnboarding  = useOnboardingStore((s: OnboardingStore) => s.resumeOnboarding);
  const resetOnboarding   = useOnboardingStore((s: OnboardingStore) => s.resetOnboarding);
  const setPhase          = useOnboardingStore((s: OnboardingStore) => s.setPhase);
  const nextPhase         = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted   = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);

  const [resumePrompt, setResumePrompt] = useState(false);
  const [bootstrapped,  setBootstrapped]  = useState(false);

  useEffect(() => {
    loadPersistedState().then((saved) => {
      if (saved && saved.phase && saved.phase > 0 && !saved.completed) {
        setPhase(saved.phase as OnboardingStore['phase']);
        setResumePrompt(true);
      }
      setBootstrapped(true);
    });
  }, [setPhase]);

  // Guard: only mark interrupted when the component unmounts AND onboarding
  // is not yet completed. Without the !completed check, finishing Phase 8
  // and entering the shell immediately re-marks state as interrupted.
  useEffect(() => {
    return () => {
      if (!useOnboardingStore.getState().completed) markInterrupted();
    };
  }, [markInterrupted]);

  // Shell-level Escape key -> soft interrupt (does not navigate away)
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape' && !completed) markInterrupted();
  }, [completed, markInterrupted]);

  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  if (!bootstrapped) return null;

  if (resumePrompt) {
    return (
      <div className="onboarding-resume" role="dialog" aria-modal="true" aria-label="Resume onboarding">
        <div className="onboarding-resume__card">
          <p>We were in the middle of something.<br />Want to pick up where we left off?</p>
          <div className="phase__actions">
            <button
              className="btn btn--primary"
              onClick={() => { resumeOnboarding(); setResumePrompt(false); }}
            >
              Resume
            </button>
            <button
              className="btn btn--ghost"
              onClick={() => { resetOnboarding(); setResumePrompt(false); }}
            >
              Start over
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="onboarding-shell" aria-label="GAIA onboarding">
      <a href="#onboarding-main" className="skip-link">Skip to main content</a>

      {/* Progress stepper — only shown for phases 1-7 (not bootstrap or threshold) */}
      {phase >= 1 && phase <= 7 && (
        <nav className="ob-stepper" aria-label="Onboarding progress">
          {STEPPER_PHASES.filter(p => p <= 7).map(p => (
            <span
              key={p}
              className={[
                'ob-stepper__dot',
                p < phase  ? 'ob-stepper__dot--done'    : '',
                p === phase ? 'ob-stepper__dot--active'  : '',
              ].filter(Boolean).join(' ')}
              aria-label={`${PHASE_NAMES[p]}${
                p < phase ? ' — complete' : p === phase ? ' — current' : ''
              }`}
              role="img"
            />
          ))}
        </nav>
      )}

      <div
        id="onboarding-main"
        className="onboarding-phase-container"
        aria-label={PHASE_NAMES[phase] ?? 'Onboarding'}
      >
        {phase === 0 && <Phase0Bootstrap onComplete={nextPhase} />}
        {phase === 1 && <Phase1Awakening />}
        {phase === 2 && <Phase2Introduction />}
        {phase === 3 && <Phase3NameCovenant />}
        {phase === 4 && <Phase4ThreeQuestions />}
        {phase === 5 && <Phase5Consent />}
        {phase === 6 && <Phase6FirstGift />}
        {phase === 7 && <Phase7AccountSetup />}
        {phase === 8 && <Phase8Threshold onComplete={onFinish} />}
      </div>
    </main>
  );
}
