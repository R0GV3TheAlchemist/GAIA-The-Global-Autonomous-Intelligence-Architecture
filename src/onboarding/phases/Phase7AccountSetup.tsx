// C-OB01 — Phase 7: Account Setup
// Refactor #366: receives onComplete + onBack props; no longer calls
// nextPhase() internally.

import { useState, useCallback, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';

// ── Views ─────────────────────────────────────────────────────────────────────
//
// 'offer'  — GAIA explains the account is optional, presents two paths
// 'form'   — email + password form
// 'local'  — confirming local-only path

type View = 'offer' | 'form' | 'local';

interface Phase7AccountSetupProps {
  onComplete: () => void;
  onBack:     () => void;
}

export function Phase7AccountSetup({ onComplete, onBack }: Phase7AccountSetupProps) {
  const name             = useOnboardingStore((s: OnboardingStore) => s.name);
  const setAccountCreated = useOnboardingStore((s: OnboardingStore) => s.setAccountCreated);

  const [view,        setView]        = useState<View>('offer');
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [showPass,    setShowPass]    = useState(false);
  const [submitting,  setSubmitting]  = useState(false);
  const [error,       setError]       = useState('');
  const [showForm,    setShowForm]    = useState(false);

  // Slide form in after mount
  useEffect(() => {
    if (view === 'form') {
      const t = setTimeout(() => setShowForm(true), 80);
      return () => clearTimeout(t);
    }
    setShowForm(false);
  }, [view]);

  // ── Keyboard ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (view === 'form') { setView('offer'); return; }
        onBack();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [view, onBack]);

  // ── Account creation ──────────────────────────────────────────────────────────
  const handleCreateAccount = useCallback(async () => {
    setError('');
    const trimmedEmail = email.trim();
    if (!trimmedEmail || !password) {
      setError('Please enter an email and password.');
      return;
    }
    const emailOk = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail);
    if (!emailOk) {
      setError('That doesn't look like a valid email address.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setSubmitting(true);
    try {
      await invoke('create_account', { email: trimmedEmail, password });
      setAccountCreated(trimmedEmail);
      onComplete();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setSubmitting(false);
    }
  }, [email, password, setAccountCreated, onComplete]);

  const handleSkip = useCallback(() => onComplete(), [onComplete]);

  // ── Offer view ────────────────────────────────────────────────────────────────
  if (view === 'offer') {
    return (
      <section className="phase phase--account phase--enter" aria-label="Account setup">
        <div className="phase__content phase__content--centered">
          <TypewriterText
            text={`No account required, ${name || 'friend'}. Everything works locally. An account unlocks encrypted cloud backup and sync across devices — nothing more.`}
            className="account-intro"
            speed={18}
          />
          <div className="phase__actions phase__actions--stack">
            <button
              className="btn btn--primary"
              onClick={() => setView('form')}
            >
              Create account
            </button>
            <button
              className="btn btn--secondary"
              onClick={handleSkip}
            >
              Stay local
            </button>
          </div>
        </div>
      </section>
    );
  }

  // ── Form view ─────────────────────────────────────────────────────────────────
  return (
    <section className="phase phase--account phase--enter" aria-label="Create account">
      <div className="phase__content phase__content--centered">
        <TypewriterText
          text="Create your account."
          className="account-intro"
          speed={24}
        />

        <form
          className={['account-form', showForm ? 'account-form--visible' : ''].filter(Boolean).join(' ')}
          onSubmit={(e) => { e.preventDefault(); handleCreateAccount(); }}
          noValidate
        >
          <div className="field-group">
            <label htmlFor="ob-email">Email</label>
            <input
              id="ob-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              autoFocus
            />
          </div>

          <div className="field-group">
            <label htmlFor="ob-password">Password</label>
            <div className="account-password-wrap">
              <input
                id="ob-password"
                type={showPass ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min. 8 characters"
                autoComplete="new-password"
              />
              <button
                type="button"
                className="account-show-pass"
                onClick={() => setShowPass((v) => !v)}
                aria-label={showPass ? 'Hide password' : 'Show password'}
              >
                {showPass ? '🙈' : '👁'}
              </button>
            </div>
          </div>

          {error && <p className="account-error" role="alert">{error}</p>}

          <button
            type="submit"
            className="btn btn--primary"
            disabled={submitting}
          >
            {submitting ? 'Creating…' : 'Create account'}
          </button>
        </form>

        <button
          className="account-back"
          onClick={() => setView('offer')}
        >
          ← Back
        </button>
      </div>
    </section>
  );
}
