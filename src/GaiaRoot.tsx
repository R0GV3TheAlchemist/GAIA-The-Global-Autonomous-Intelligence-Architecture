// GaiaRoot.tsx
// #368 — Top-level onboarding gate.
//
// Sits between main.tsx and GaiaShell. On every boot it reads the persisted
// onboarding state from disk. If completed, it opens GaiaShell directly.
// If not completed, it shows OnboardingRouter. When onboarding finishes,
// it transitions to GaiaShell without a page reload.
//
// Boot flow:
//   1. Mount → show <GaiaBootSplash /> while loadPersistedState() is in flight
//   2a. completed: true  → render <GaiaShell />
//   2b. completed: false → render <OnboardingRouter onFinish={...} />
//   3. onFinish called    → swap to <GaiaShell /> with a fade transition
//
// Notes:
//   - initSidecar and notificationBridge are still kicked off in main.tsx;
//     this component is purely concerned with the visual routing decision.
//   - The transition uses CSS classes rather than a router library so we
//     don't add a dependency for a single boolean branch.

import { useEffect, useState } from 'react';
import { loadPersistedState } from './onboarding/store/onboardingStore';
import { OnboardingRouter }   from './onboarding/OnboardingRouter';
import { GaiaShell }          from './shell/GaiaShell';
import { GaiaBootSplash }     from './shell/GaiaBootSplash';

// ── App states ────────────────────────────────────────────────────────────
//
// 'booting'    — loadPersistedState() is in flight; show boot splash
// 'onboarding' — onboarding_state.json absent or completed: false
// 'shell'      — completed: true, or onboarding just finished

type AppState = 'booting' | 'onboarding' | 'shell';

// ── Transition duration ─────────────────────────────────────────────────────
//
// When onboarding completes, we fade the onboarding shell out and the GAIA
// shell in. TRANSITION_MS must match the CSS animation duration in
// GaiaRoot.css (.gaia-root--transitioning).

const TRANSITION_MS = 600;

export function GaiaRoot() {
  const [appState,     setAppState]     = useState<AppState>('booting');
  const [transitioning, setTransitioning] = useState(false);

  // ── Boot: read persisted onboarding state ─────────────────────────────────
  useEffect(() => {
    loadPersistedState().then((saved) => {
      if (saved?.completed === true) {
        setAppState('shell');
      } else {
        setAppState('onboarding');
      }
    });
  }, []);

  // ── onFinish: onboarding → shell transition ────────────────────────────────
  //
  // Called by OnboardingRouter when Phase 8's Enter button is pressed.
  // We start a CSS fade-out, then swap to 'shell' after TRANSITION_MS.

  const handleOnboardingFinish = () => {
    setTransitioning(true);
    setTimeout(() => {
      setTransitioning(false);
      setAppState('shell');
    }, TRANSITION_MS);
  };

  // ── Render ─────────────────────────────────────────────────────────────────

  if (appState === 'booting') {
    return <GaiaBootSplash />;
  }

  if (appState === 'onboarding') {
    return (
      <div
        className={[
          'gaia-root',
          transitioning ? 'gaia-root--transitioning' : '',
        ].filter(Boolean).join(' ')}
      >
        <OnboardingRouter onFinish={handleOnboardingFinish} />
      </div>
    );
  }

  // appState === 'shell'
  return (
    <div className="gaia-root gaia-root--shell-enter">
      <GaiaShell />
    </div>
  );
}
