// C-OB01 — Phase 3: The Name Covenant v2
// GAIA asks the user's name. First data exchange.
// Upgraded: auto-focus, Enter to submit, live validation with shake,
// confirmation echo before advancing.

import { useState, useRef, useEffect, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';

export function Phase3NameCovenant() {
  const setName   = useOnboardingStore((s: OnboardingStore) => s.setName);
  const nextPhase = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const storedName = useOnboardingStore((s: OnboardingStore) => s.name);

  const [inputVal,    setInputVal]    = useState(storedName || '');
  const [shake,       setShake]       = useState(false);
  const [confirmed,   setConfirmed]   = useState(false);
  const [showPrompt,  setShowPrompt]  = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-focus input after the typewriter prompt finishes
  const handlePromptComplete = useCallback(() => {
    setShowPrompt(true);
    setTimeout(() => inputRef.current?.focus(), 80);
  }, []);

  // If user already has a stored name (resuming), show input immediately
  useEffect(() => {
    if (storedName) {
      setShowPrompt(true);
      setTimeout(() => inputRef.current?.focus(), 80);
    }
  }, [storedName]);

  const handleSubmit = useCallback(() => {
    const trimmed = inputVal.trim();
    if (!trimmed) {
      setShake(true);
      setTimeout(() => setShake(false), 500);
      inputRef.current?.focus();
      return;
    }
    setName(trimmed);
    setConfirmed(true);
    // Brief pause to show the confirmation echo, then advance
    setTimeout(nextPhase, 1400);
  }, [inputVal, setName, nextPhase]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') { e.preventDefault(); handleSubmit(); }
  }, [handleSubmit]);

  return (
    <section className="phase phase--name-covenant phase--enter" aria-label="What is your name?">
      <div className="phase__content phase__content--centered">

        {!confirmed ? (
          <>
            <TypewriterText
              key="name-prompt"
              text="What would you like me to call you?"
              speed={36}
              onComplete={handlePromptComplete}
              tag="p"
              className="gaia-question"
            />

            {showPrompt && (
              <div className={`name-input-wrap${shake ? ' name-input-wrap--shake' : ''}`}>
                <input
                  ref={inputRef}
                  type="text"
                  className="name-input"
                  value={inputVal}
                  onChange={e => setInputVal(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Your name"
                  maxLength={48}
                  autoComplete="off"
                  aria-label="Enter your name"
                />
                <button
                  className="btn btn--primary"
                  onClick={handleSubmit}
                  disabled={!inputVal.trim()}
                  aria-label="Confirm name"
                >
                  That's me
                </button>
              </div>
            )}
          </>
        ) : (
          <div className="name-confirmed" aria-live="polite">
            <p className="name-confirmed__echo">
              {inputVal.trim()}.
            </p>
            <p className="name-confirmed__sub">I'll remember that.</p>
          </div>
        )}

      </div>
    </section>
  );
}
