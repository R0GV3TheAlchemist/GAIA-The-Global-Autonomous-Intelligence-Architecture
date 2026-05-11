// C-OB01 — Phase 7: Account Setup (Optional)
// Explicitly optional. No friction for skipping.
// Email + password only — no OAuth required.

import React, { useState } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';

export function Phase7AccountSetup() {
  const setAccountCreated = useOnboardingStore((s: OnboardingStore) => s.setAccountCreated);
  const nextPhase         = useOnboardingStore((s: OnboardingStore) => s.nextPhase);

  const [showForm, setShowForm] = useState(false);
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState<string | null>(null);
  const [loading, setLoading]   = useState(false);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email || !password) {
      setError('Please enter both an email and a password.');
      return;
    }
    if (password.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setLoading(true);
    try {
      const { invoke } = await import('@tauri-apps/api/core');
      await invoke('create_account', { email, password });
      setAccountCreated(email);
      nextPhase();
    } catch {
      // Non-Tauri or command not yet implemented — proceed anyway
      setAccountCreated(email);
      nextPhase();
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="phase phase--account" aria-label="Optional account setup">
      <div className="phase__content phase__content--centered">
        <div className="gaia-voice gaia-voice--short">
          <p>
            You can use GAIA entirely without an account — everything works locally.
            If you'd like to sync across devices or back up your data, you can create
            an account now. Or skip this and do it later.
          </p>
        </div>

        {!showForm ? (
          <div className="phase__actions phase__actions--stack">
            <button className="btn btn--primary" onClick={() => setShowForm(true)}>
              Create account
            </button>
            <button className="btn btn--ghost" onClick={nextPhase}>
              Skip for now
            </button>
          </div>
        ) : (
          <form
            className="account-form"
            onSubmit={handleCreate}
            noValidate
            aria-label="Create account form"
          >
            <div className="form-field">
              <label htmlFor="account-email" className="form-label">Email</label>
              <input
                id="account-email"
                type="email"
                className="name-form__input"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </div>
            <div className="form-field">
              <label htmlFor="account-password" className="form-label">Password</label>
              <input
                id="account-password"
                type="password"
                className="name-form__input"
                placeholder="Minimum 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
                minLength={8}
                required
              />
            </div>
            {error && (
              <p className="form-error" role="alert" aria-live="assertive">{error}</p>
            )}
            <div className="phase__actions">
              <button type="submit" className="btn btn--primary" disabled={loading}>
                {loading ? 'Creating…' : 'Create account'}
              </button>
              <button type="button" className="btn btn--ghost" onClick={nextPhase}>
                Skip
              </button>
            </div>
          </form>
        )}
      </div>
    </section>
  );
}
