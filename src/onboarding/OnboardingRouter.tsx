// C-OB01 — Onboarding Router
// Orchestrates all 8 phases. Handles interruption/resume.
// Entry point: mount this at the /onboarding route.

import { useEffect, useState } from 'react';
import { useOnboardingStore, loadPersistedState, type OnboardingStore } from './store/onboardingStore';
import { Phase0Bootstrap } from './phases/Phase0Bootstrap';
import { Phase1Awakening } from './phases/Phase1Awakening';
import { Phase2Introduction } from './phases/Phase2Introduction';
import { Phase3NameCovenant } from './phases/Phase3NameCovenant';
import { Phase4ThreeQuestions } from './phases/Phase4ThreeQuestions';
import { Phase5Consent } from './phases/Phase5Consent';
import { Phase6FirstGift } from './phases/Phase6FirstGift';
import { Phase7AccountSetup } from './phases/Phase7AccountSetup';
import { Phase8Threshold } from './phases/Phase8Threshold';
import './onboarding.css';

interface OnboardingRouterProps {
  onFinish: () => void;
}

export function OnboardingRouter({ onFinish }: OnboardingRouterProps) {
  const phase          = useOnboardingStore((s: OnboardingStore) => s.phase);
  const resumeOnboarding = useOnboardingStore((s: OnboardingStore) => s.resumeOnboarding);
  const resetOnboarding  = useOnboardingStore((s: OnboardingStore) => s.resetOnboarding);
  const setPhase       = useOnboardingStore((s: OnboardingStore) => s.setPhase);
  const nextPhase      = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);

  const [resumePrompt, setResumePrompt] = useState(false);
  const [bootstrapped, setBootstrapped] = useState(false);

  useEffect(() => {
    loadPersistedState().then((saved) => {
      if (saved && saved.phase && saved.phase > 0 && !saved.completed) {
        setPhase(saved.phase as any);
        setResumePrompt(true);
      }
      setBootstrapped(true);
    });
  }, [setPhase]);

  useEffect(() => {
    return () => {
      if (!useOnboardingStore.getState().completed) markInterrupted();
    };
  }, [markInterrupted]);

  if (!bootstrapped) return null;

  if (resumePrompt) {
    return (
      <div className="onboarding-resume" role="dialog" aria-modal="true" aria-label="Resume onboarding">
        <div className="onboarding-resume__card">
          <p>We were in the middle of something. Want to pick up where we left off?</p>
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
      <div id="onboarding-main" className="onboarding-phase-container">
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
