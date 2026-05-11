// C-OB01 — Phase 3: The Name Covenant
// GAIA asks what to call the user. Minimal, symbolic, reversible.

import React, { useState, useRef, useEffect } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';

export function Phase3NameCovenant() {
  const setName   = useOnboardingStore((s: OnboardingStore) => s.setName);
  const nextPhase = useOnboardingStore((s: OnboardingStore) => s.nextPhase);

  const [inputValue, setInputValue]     = useState('');
  const [submitted, setSubmitted]       = useState(false);
  const [responseLine, setResponseLine] = useState('');

  const advanceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    return () => {
      if (advanceTimerRef.current !== null) clearTimeout(advanceTimerRef.current);
    };
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const name = inputValue.trim() || 'Friend';
    setName(name);

    const response = inputValue.trim()
      ? `Welcome, ${name}. Let's begin.`
      : "Alright — I'll call you 'Friend' for now. You can tell me your name whenever you're ready.";

    setResponseLine(response);
    setSubmitted(true);
    advanceTimerRef.current = setTimeout(() => nextPhase(), 2200);
  };

  return (
    <section className="phase phase--name-covenant" aria-label="Name covenant">
      <div className="phase__content phase__content--centered">
        {!submitted ? (
          <>
            <h2 className="phase__question">What would you like me to call you?</h2>
            <p className="phase__subtext">
              This can be your real name, a nickname, or anything you choose.
              You can change it anytime.
            </p>
            <form className="name-form" onSubmit={handleSubmit} noValidate>
              <label htmlFor="gaia-name-input" className="sr-only">Your name</label>
              <input
                id="gaia-name-input"
                type="text"
                className="name-form__input"
                placeholder="Enter your name…"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                autoFocus
                autoComplete="off"
                maxLength={80}
                aria-describedby="name-hint"
              />
              <p id="name-hint" className="sr-only">Leave blank to be called Friend</p>
              <button type="submit" className="btn btn--primary">Continue</button>
            </form>
          </>
        ) : (
          <p className="name-response" aria-live="polite" aria-atomic="true">
            {responseLine}
          </p>
        )}
      </div>
    </section>
  );
}
