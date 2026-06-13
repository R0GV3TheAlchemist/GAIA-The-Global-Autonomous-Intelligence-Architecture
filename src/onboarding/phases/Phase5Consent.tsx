// C-OB01 — Phase 5: Consent
// Refactor #366: receives onComplete + onBack props; no longer calls
// nextPhase() internally.

import { useEffect, useState, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import type { ConsentPreferences } from '../types';

const CONSENT_ITEMS: {
  key:   keyof ConsentPreferences;
  icon:  string;
  label: string;
  desc:  string;
  group: 'core' | 'optional';
  defaultOn: boolean;
}[] = [
  { key: 'conversation_history', icon: '💬', label: 'Conversation history',  desc: 'GAIA can reference earlier parts of a conversation.',         group: 'core',     defaultOn: true  },
  { key: 'mood_signals',         icon: '🌡', label: 'Mood signals',          desc: 'Subtle cues about tone — not stored, just used in-session.',  group: 'core',     defaultOn: true  },
  { key: 'topic_patterns',       icon: '🧵', label: 'Topic patterns',        desc: 'What you tend to explore across sessions.',                   group: 'core',     defaultOn: true  },
  { key: 'usage_patterns',       icon: '📊', label: 'Usage patterns',        desc: 'When and how you use GAIA — helps optimise performance.',      group: 'optional', defaultOn: true  },
  { key: 'telemetry',            icon: '📡', label: 'Anonymous telemetry',   desc: 'Crash reports and performance data. Never personal content.',  group: 'optional', defaultOn: false },
  { key: 'cloud_backup',         icon: '☁️', label: 'Cloud backup',          desc: 'Encrypted backup of your context. Off by default.',           group: 'optional', defaultOn: false },
];

interface Phase5ConsentProps {
  onComplete: () => void;
  onBack:     () => void;
}

export function Phase5Consent({ onComplete, onBack }: Phase5ConsentProps) {
  const consent       = useOnboardingStore((s: OnboardingStore) => s.consent);
  const toggleConsent = useOnboardingStore((s: OnboardingStore) => s.toggleConsent);

  const [visibleCount, setVisibleCount] = useState(0);

  // Stagger items in
  useEffect(() => {
    CONSENT_ITEMS.forEach((_, i) => {
      setTimeout(() => setVisibleCount((n) => n + 1), 120 + i * 90);
    });
  }, []);

  const handleContinue = useCallback(() => onComplete(), [onComplete]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onBack();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onBack]);

  const coreItems     = CONSENT_ITEMS.filter((i) => i.group === 'core');
  const optionalItems = CONSENT_ITEMS.filter((i) => i.group === 'optional');

  const renderItem = (item: typeof CONSENT_ITEMS[number], globalIndex: number) => (
    <div
      key={item.key}
      className={[
        'consent-item',
        consent[item.key] ? 'consent-item--on' : '',
        globalIndex < visibleCount ? 'consent-item--visible' : '',
      ].filter(Boolean).join(' ')}
    >
      <span className="consent-item__icon" aria-hidden="true">{item.icon}</span>
      <div className="consent-item__body">
        <span className="consent-item__label">{item.label}</span>
        <span className="consent-item__desc">{item.desc}</span>
      </div>
      <button
        className={['consent-toggle', consent[item.key] ? 'consent-toggle--on' : ''].filter(Boolean).join(' ')}
        onClick={() => toggleConsent(item.key)}
        role="switch"
        aria-checked={consent[item.key]}
        aria-label={`Toggle ${item.label}`}
      >
        <span className="consent-toggle__thumb" />
      </button>
    </div>
  );

  return (
    <section className="phase phase--consent phase--enter" aria-label="Privacy preferences">
      <div className="phase__content">
        <p className="gaia-question">What are you comfortable with?</p>
        <p className="gaia-aside">You can change any of this later in Settings.</p>

        <div className="consent-list" role="group" aria-label="Consent preferences">
          <span className="consent-group-label">Core experience</span>
          {coreItems.map((item) => renderItem(item, CONSENT_ITEMS.indexOf(item)))}

          <hr className="consent-divider" />
          <span className="consent-group-label consent-group-label--dim">Optional</span>
          {optionalItems.map((item) => renderItem(item, CONSENT_ITEMS.indexOf(item)))}
        </div>

        <p className="consent-footer">
          Core items are on by default. Optional items are off.
          <br />
          <em className="consent-footer__path">Settings → Privacy</em> to adjust anytime.
        </p>

        <div className="phase__actions">
          <button className="btn btn--ghost" onClick={onBack}>← Back</button>
          <button className="btn btn--primary" onClick={handleContinue} autoFocus>Continue</button>
        </div>
      </div>
    </section>
  );
}
