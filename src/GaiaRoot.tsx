/**
 * GaiaRoot.tsx
 * Canon: GAIAN_TWIN_DOCTRINE, SLOW_PROTOCOL
 *
 * The root shell of GAIA-OS.
 * Decides what the human sees:
 *   — OnboardingRouter  (first visit)
 *   — TwinInterface     (all subsequent visits)
 *
 * TwinInterface now owns its own useTwinSession call (Diamond architecture).
 * GaiaRoot only concerns itself with identity + routing.
 * This is the door.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { OnboardingRouter } from './onboarding/OnboardingRouter';
import { TwinInterface } from './components/TwinInterface';
import './GaiaRoot.css';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function getOnboardingState(): {
  completed: boolean;
  humanId: string | null;
  sessionId: string | null;
  humanName: string | null;
} {
  try {
    const raw = localStorage.getItem('gaia_onboarding_state');
    if (!raw) return { completed: false, humanId: null, sessionId: null, humanName: null };
    const parsed = JSON.parse(raw);
    return {
      completed: parsed.completed === true,
      humanId:   parsed.data?.humanId   ?? null,
      sessionId: parsed.data?.sessionId ?? null,
      humanName: parsed.data?.name      ?? null,
    };
  } catch {
    return { completed: false, humanId: null, sessionId: null, humanName: null };
  }
}

function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

// ─── Root ─────────────────────────────────────────────────────────────────────

export function GaiaRoot() {
  const [state, setState] = useState<'loading' | 'onboarding' | 'twin'>('loading');
  const [identity, setIdentity] = useState<{
    humanId: string;
    humanName: string;
  } | null>(null);

  // Session ID is stable for this mount — generated once, not on every render.
  const sessionIdRef = useRef<string>(generateSessionId());

  useEffect(() => {
    const ob = getOnboardingState();
    if (ob.completed && ob.humanId && ob.humanName) {
      setIdentity({ humanId: ob.humanId, humanName: ob.humanName });
      setState('twin');
    } else {
      setState('onboarding');
    }
  }, []);

  const handleOnboardingComplete = useCallback(() => {
    const ob = getOnboardingState();
    if (ob.humanId && ob.humanName) {
      setIdentity({ humanId: ob.humanId, humanName: ob.humanName });
      // New session for first post-onboarding interaction
      sessionIdRef.current = generateSessionId();
    }
    setState('twin');
  }, []);

  if (state === 'loading') {
    return (
      <div
        className="gaia-loading"
        aria-label="GAIA loading"
        aria-live="polite"
      />
    );
  }

  if (state === 'onboarding') {
    return <OnboardingRouter onFinish={handleOnboardingComplete} />;
  }

  if (state === 'twin' && identity) {
    return (
      <div className="gaia-twin-root">
        <TwinInterface
          humanId={identity.humanId}
          sessionId={sessionIdRef.current}
          humanName={identity.humanName}
        />
      </div>
    );
  }

  // Fallback
  return <OnboardingRouter onFinish={handleOnboardingComplete} />;
}
