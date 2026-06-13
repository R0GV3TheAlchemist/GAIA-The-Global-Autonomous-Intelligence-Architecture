// C-OB01 — Phase 3: Name Covenant
// Refactor #366: receives onComplete + onBack props; no longer calls
// nextPhase() or setPhase() internally.

import { useState, useCallback, useRef, useEffect } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';

interface Phase3NameCovenantProps {
  onComplete: () => void;
  onBack:     () => void;
}

export function Phase3NameCovenant({ onComplete, onBack }: Phase3NameCovenantProps) {
  const setName = useOnboardingStore((s: OnboardingStore) => s.setName);
  const name    = useOnboardingStore((s: OnboardingStore) => s.name);

  const [input,     setInput]     = useState(name ?? '');
  const [confirmed, setConfirmed] = useState(false);
  const [shake,     setShake]     = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { inputRef.current?.focus(); }, []);

  const handleSubmit = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed) {
      setShake(true);
      setTimeout(() => setShake(false), 500);
      return;
    }
    setName(trimmed);
    setConfirmed(true);
    setTimeout(() => onComplete(), 1200);
  }, [input, setName, onComplete]);

  const handleKey = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleSubmit();
  }, [handleSubmit]);

  if (confirmed) {
    return (
      <section className="phase phase--name phase--enter" aria-label="Name confirmed">
        <div className="phase__content phase__content--centered">
          <div className="name-confirmed">
            <p className="name-confirmed__echo">{input.trim()}</p>
            <p className="name-confirmed__sub">I'll remember that.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="phase phase--name phase--enter" aria-label="Your name">
      <div className="phase__content">
        <p className="gaia-question">What should I call you?</p>

        <div
          className={['name-input-wrap', shake ? 'name-input-wrap--shake' : ''].filter(Boolean).join(' ')}
        >
          <input
            ref={inputRef}
            type="text"
            className="name-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKey}
            placeholder="Your name"
            maxLength={48}
            autoComplete="off"
            spellCheck={false}
            aria-label="Enter your name"
          />
          <button
            className="btn btn--primary"
            onClick={handleSubmit}
            disabled={!input.trim()}
          >
            That's me
          </button>
        </div>

        <button className="q4-none-btn" onClick={onBack}>
          ← Back
        </button>
      </div>
    </section>
  );
}
