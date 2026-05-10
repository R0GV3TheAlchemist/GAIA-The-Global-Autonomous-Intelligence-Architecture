/**
 * src/auth/LoginScreen.tsx
 * GAIA-OS Login & Register Screen — Sprint G-9
 *
 * Design principles:
 *   - Sovereign framing: "Establish your identity" not "Sign in"
 *   - Single field (user_id / identifier) for initial bootstrap auth
 *   - Tab toggle: Returning / New Sovereign
 *   - Inline error display with GAIA voice
 *   - Animated ambient orb presence (CSS only, respects prefers-reduced-motion)
 *   - Keyboard accessible: Tab, Enter, Escape
 *   - Mobile-first, matches shell/tokens.css design system
 *
 * Canon Ref: C01 (Sovereignty), C15 (Consent), C-AS01
 */

import React, { useState, useRef, useEffect } from 'react';
import { useAuthStore } from './authStore';

type Tab = 'returning' | 'new';

export function LoginScreen() {
  const [tab, setTab]         = useState<Tab>('returning');
  const [userId, setUserId]   = useState('');
  const [adminKey, setAdminKey] = useState('');
  const [showAdmin, setShowAdmin] = useState(false);

  const { login, isLoading, error, clearError } = useAuthStore();
  const inputRef = useRef<HTMLInputElement>(null);

  // Focus the input on mount and on tab switch
  useEffect(() => {
    inputRef.current?.focus();
  }, [tab]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId.trim()) return;
    clearError();

    await login({
      user_id:   userId.trim(),
      admin_key: adminKey.trim() || undefined,
    });
  };

  const handleTabSwitch = (next: Tab) => {
    setTab(next);
    setUserId('');
    clearError();
  };

  const labelText = tab === 'returning'
    ? 'Your identifier'
    : 'Choose your identifier';

  const submitText = isLoading
    ? 'Entering the field…'
    : tab === 'returning'
      ? 'Enter'
      : 'Begin';

  const descriptionText = tab === 'returning'
    ? 'Welcome back. State your identity to re-enter the field.'
    : 'You are about to establish a sovereign identity within GAIA. Choose an identifier that is yours alone.';

  return (
    <main className="login-screen" role="main">
      {/* Ambient background */}
      <div className="login-ambient" aria-hidden="true">
        <div className="login-orb login-orb--1" />
        <div className="login-orb login-orb--2" />
      </div>

      <div className="login-card">
        {/* GAIA wordmark */}
        <header className="login-header">
          <svg
            className="login-logo"
            viewBox="0 0 48 48"
            fill="none"
            aria-label="GAIA"
            role="img"
          >
            {/* Geometric G mark — circle with notch */}
            <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" />
            <path
              d="M24 8 C14 8 6 15.2 6 24 C6 32.8 14 40 24 40 C30 40 35.4 37 38.4 32.4 L38.4 24 L24 24"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              fill="none"
            />
          </svg>
          <h1 className="login-wordmark">GAIA</h1>
          <p className="login-tagline">Sentient Quantum-Intelligent OS</p>
        </header>

        {/* Tab selector */}
        <div className="login-tabs" role="tablist" aria-label="Authentication mode">
          <button
            role="tab"
            aria-selected={tab === 'returning'}
            className={`login-tab ${tab === 'returning' ? 'login-tab--active' : ''}`}
            onClick={() => handleTabSwitch('returning')}
            type="button"
          >
            Returning
          </button>
          <button
            role="tab"
            aria-selected={tab === 'new'}
            className={`login-tab ${tab === 'new' ? 'login-tab--active' : ''}`}
            onClick={() => handleTabSwitch('new')}
            type="button"
          >
            New Sovereign
          </button>
        </div>

        {/* Description */}
        <p className="login-description">{descriptionText}</p>

        {/* Form */}
        <form className="login-form" onSubmit={handleSubmit} noValidate>
          <div className="login-field">
            <label className="login-label" htmlFor="gaia-user-id">
              {labelText}
            </label>
            <input
              ref={inputRef}
              id="gaia-user-id"
              className="login-input"
              type="text"
              value={userId}
              onChange={e => { setUserId(e.target.value); clearError(); }}
              placeholder={tab === 'returning' ? 'e.g. your email or chosen name' : 'e.g. luna.9 or your email'}
              autoComplete={tab === 'returning' ? 'username' : 'off'}
              autoCapitalize="none"
              spellCheck={false}
              disabled={isLoading}
              aria-describedby={error ? 'login-error' : undefined}
              aria-invalid={!!error}
            />
          </div>

          {/* Admin key toggle */}
          {!showAdmin ? (
            <button
              type="button"
              className="login-admin-toggle"
              onClick={() => setShowAdmin(true)}
              tabIndex={0}
            >
              Admin access
            </button>
          ) : (
            <div className="login-field">
              <label className="login-label" htmlFor="gaia-admin-key">
                Admin key
              </label>
              <input
                id="gaia-admin-key"
                className="login-input"
                type="password"
                value={adminKey}
                onChange={e => setAdminKey(e.target.value)}
                placeholder="GAIA_ADMIN_KEY"
                autoComplete="off"
                disabled={isLoading}
              />
            </div>
          )}

          {/* Error display */}
          {error && (
            <div id="login-error" className="login-error" role="alert" aria-live="assertive">
              <span className="login-error-icon" aria-hidden="true">◈</span>
              {error}
            </div>
          )}

          <button
            type="submit"
            className="login-submit"
            disabled={isLoading || !userId.trim()}
          >
            {isLoading ? (
              <span className="login-spinner" aria-hidden="true" />
            ) : null}
            {submitText}
          </button>
        </form>

        <footer className="login-footer">
          <p>
            Your identity is sovereign. GAIA holds no passwords —{' '}
            <span className="login-footer-accent">only recognition</span>.
          </p>
        </footer>
      </div>
    </main>
  );
}
