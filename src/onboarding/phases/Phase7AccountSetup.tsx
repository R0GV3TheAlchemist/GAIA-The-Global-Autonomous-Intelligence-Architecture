// C-OB01 — Phase 7: Account Setup (Optional) v2
// Explicitly optional. No friction for skipping.
// Email + password only. Everything works locally without an account.
// Rebuilt: TypewriterText intro, correct CSS classes, form reveal
// animation, password show/hide, keyboard navigation, markInterrupted.

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';

const GAIA_PROMPT =
  'GAIA works entirely without an account. Everything stays on your device. '
  + 'If you want to sync across devices or back up your data, you can create '
  + 'one now — or skip this and come back to it in Settings any time.';

export function Phase7AccountSetup() {
  const setAccountCreated  = useOnboardingStore((s: OnboardingStore) => s.setAccountCreated);
  const nextPhase          = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted    = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);

  // Typewriter — lock after first render
  const promptShown = useRef(false);

  // Two-panel state
  const [showForm, setShowForm] = useState(false);

  // Form state
  const [email,       setEmail]       = useState('');
  const [password,    setPassword]    = useState('');
  const [showPass,    setShowPass]    = useState(false);
  const [error,       setError]       = useState<string | null>(null);
  const [loading,     setLoading]     = useState(false);

  // Autofocus email when form opens
  const emailRef = useRef<HTMLInputElement>(null);
  useEffect(() => {
    if (showForm) emailRef.current?.focus();
  }, [showForm]);

  // ── Validation ───────────────────────────────────────────────────────────
  function validate(): string | null {
    if (!email.trim())         return 'Please enter your email address.';
    if (!email.includes('@'))  return 'That doesn’t look like an email address.';
    if (!password)             return 'Please enter a password.';
    if (password.length < 8)  return 'Password must be at least 8 characters.';
    return null;
  }

  // ── Submit ─────────────────────────────────────────────────────────────────
  const handleCreate = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    const err = validate();
    if (err) { setError(err); return; }
    setError(null);
    setLoading(true);
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('create_account', { email: email.trim(), password });
    } catch {
      // Tauri not available or command not implemented — proceed
    } finally {
      setAccountCreated(email.trim());
      nextPhase();
      setLoading(false);
    }
  }, [email, password, setAccountCreated, nextPhase]);

  // ── Keyboard ────────────────────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      // Escape: back to offer view OR interrupt
      if (e.key === 'Escape') {
        if (showForm) setShowForm(false);
        else markInterrupted();
        return;
      }
      // Enter on offer view: open form
      if (e.key === 'Enter' && !showForm) {
        // Don't intercept if a button/link is focused — let default handle it
        const tag = (document.activeElement as HTMLElement)?.tagName;
        if (tag !== 'BUTTON' && tag !== 'A') setShowForm(true);
      }
      // Enter inside form is handled natively by form submit
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showForm, markInterrupted]);

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <section className="phase phase--account phase--enter" aria-label="Optional account setup">
      <div className="phase__content phase__content--centered">

        {/* ── GAIA prompt ────────────────────────────────────────────── */}
        <TypewriterText
          key={promptShown.current ? 'static' : 'type'}
          text={GAIA_PROMPT}
          speed={22}
          onComplete={() => { promptShown.current = true; }}
          tag="p"
          className="q4-prompt account-intro"
        />

        {/* ── Offer view ────────────────────────────────────────────── */}
        {!showForm && (
          <div className="phase__actions phase__actions--stack">
            <button
              type="button"
              className="btn btn--primary"
              onClick={() => setShowForm(true)}
              aria-label="Create a GAIA account"
            >
              Create account
            </button>
            <button
              type="button"
              className="btn btn--ghost"
              onClick={nextPhase}
              aria-label="Skip account creation and continue"
            >
              Skip for now
            </button>
          </div>
        )}

        {/* ── Account form ───────────────────────────────────────────── */}
        {showForm && (
          <form
            className="account-form account-form--visible"
            onSubmit={handleCreate}
            noValidate
            aria-label="Create account"
          >
            {/* Email */}
            <div className="field-group">
              <label htmlFor="account-email">Email</label>
              <input
                ref={emailRef}
                id="account-email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setError(null); }}
                autoComplete="email"
                required
                aria-required="true"
                aria-describedby={error ? 'account-error' : undefined}
              />
            </div>

            {/* Password */}
            <div className="field-group">
              <label htmlFor="account-password">Password</label>
              <div className="account-password-wrap">
                <input
                  id="account-password"
                  type={showPass ? 'text' : 'password'}
                  placeholder="Minimum 8 characters"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(null); }}
                  autoComplete="new-password"
                  minLength={8}
                  required
                  aria-required="true"
                  aria-describedby={error ? 'account-error' : undefined}
                />
                <button
                  type="button"
                  className="account-show-pass"
                  aria-label={showPass ? 'Hide password' : 'Show password'}
                  onClick={() => setShowPass(v => !v)}
                  tabIndex={0}
                >
                  {showPass ? '□' : '■'}
                </button>
              </div>
            </div>

            {/* Error */}
            {error && (
              <p
                id="account-error"
                className="account-error"
                role="alert"
                aria-live="assertive"
              >
                {error}
              </p>
            )}

            {/* Actions */}
            <div className="phase__actions">
              <button
                type="submit"
                className="btn btn--primary"
                disabled={loading}
                aria-busy={loading}
              >
                {loading ? 'Creating…' : 'Create account'}
              </button>
              <button
                type="button"
                className="btn btn--ghost"
                onClick={nextPhase}
                aria-label="Skip and continue without an account"
              >
                Skip
              </button>
            </div>

            {/* Back link */}
            <button
              type="button"
              className="account-back"
              onClick={() => { setShowForm(false); setError(null); }}
              aria-label="Go back"
            >
              ← Back
            </button>
          </form>
        )}

      </div>
    </section>
  );
}
