/**
 * src/auth/AuthGate.tsx
 * GAIA-OS Auth Gate — Sprint G-9
 *
 * Top-level authentication boundary.
 *
 * Behaviour:
 *   - While isHydrating → shows a minimal breathing loader (not a full spinner)
 *   - When unauthenticated → renders <LoginScreen />
 *   - When authenticated → renders children
 *
 * Usage:
 *   // In main.tsx or App.tsx:
 *   <AuthGate>
 *     <GaiaShell />
 *   </AuthGate>
 *
 * Canon Ref: C01 (Sovereignty)
 */

import React, { useEffect } from 'react';
import { useAuthStore, selectIsAuthed, selectIsHydrating } from './authStore';
import { LoginScreen } from './LoginScreen';
import './LoginScreen.css';

interface AuthGateProps {
  children: React.ReactNode;
}

export function AuthGate({ children }: AuthGateProps) {
  const isAuthed    = useAuthStore(selectIsAuthed);
  const isHydrating = useAuthStore(selectIsHydrating);

  // On mount: if a token were stored in a future secure store (G-10),
  // we'd call refreshUser here. For now, we start unauthenticated.
  // This hook is the right place for that integration.
  useEffect(() => {
    // Future G-10: const savedToken = await secureStore.get('gaia_token');
    // if (savedToken) await useAuthStore.getState().refreshUser(savedToken);
  }, []);

  if (isHydrating) {
    return (
      <div className="auth-gate-loading" aria-live="polite" aria-label="GAIA is waking">
        <div className="auth-gate-orb" />
        <p className="auth-gate-loading-text">GAIA is waking…</p>
      </div>
    );
  }

  if (!isAuthed) {
    return <LoginScreen />;
  }

  return <>{children}</>;
}
