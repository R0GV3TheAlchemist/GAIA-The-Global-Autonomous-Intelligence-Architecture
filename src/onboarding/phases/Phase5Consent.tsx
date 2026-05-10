// C-OB01 — Phase 5: Consent & Data Architecture
// Explicit, informed consent. Not a ToS wall — a conversation.
// Each toggle is individually reversible.

import React from 'react';
import { useOnboardingStore } from '../store/onboardingStore';
import type { ConsentPreferences } from '../types';

interface ConsentCardDef {
  key: keyof ConsentPreferences;
  what: string;
  why: string;
  defaultOn: boolean;
}

const CONSENT_CARDS: ConsentCardDef[] = [
  {
    key: 'conversation_history',
    what: 'Conversation history',
    why: 'So I can remember context across sessions',
    defaultOn: true,
  },
  {
    key: 'mood_signals',
    what: 'Mood & tone signals',
    why: 'So I can adapt how I speak to you',
    defaultOn: true,
  },
  {
    key: 'topic_patterns',
    what: 'Topics you return to',
    why: 'So I can notice patterns over time',
    defaultOn: true,
  },
  {
    key: 'usage_patterns',
    what: 'Usage patterns (time, frequency)',
    why: 'To improve my timing and pacing',
    defaultOn: true,
  },
  {
    key: 'telemetry',
    what: 'Device telemetry (crashes, errors)',
    why: 'To help developers fix bugs — anonymized',
    defaultOn: false,
  },
  {
    key: 'cloud_backup',
    what: 'Optional cloud backup',
    why: 'Encrypted sync to your personal cloud',
    defaultOn: false,
  },
];

export function Phase5Consent() {
  const consent = useOnboardingStore((s) => s.consent);
  const toggleConsent = useOnboardingStore((s) => s.toggleConsent);
  const nextPhase = useOnboardingStore((s) => s.nextPhase);

  return (
    <section className="phase phase--consent" aria-label="Privacy and consent">
      <div className="phase__content phase__content--wide">
        <div className="gaia-voice gaia-voice--short">
          <p>
            Before we go further, I want to be clear about what I remember and what I don't
            — and to ask your permission.
          </p>
          <p>
            Everything you share with me is stored locally on this device by default.
            I do not send your conversations, your name, or your preferences to any server
            unless you explicitly ask me to.
          </p>
          <p>Here's what I'd like to track, with your permission:</p>
        </div>

        <div
          className="consent-cards"
          role="group"
          aria-label="Data collection preferences"
        >
          {CONSENT_CARDS.map((card) => {
            const isOn = consent[card.key];
            return (
              <div key={card.key} className="consent-card">
                <div className="consent-card__info">
                  <strong className="consent-card__what">{card.what}</strong>
                  <span className="consent-card__why">{card.why}</span>
                </div>
                <button
                  className={`consent-toggle ${
                    isOn ? 'consent-toggle--on' : 'consent-toggle--off'
                  }`}
                  role="switch"
                  aria-checked={isOn}
                  aria-label={`${card.what}: ${isOn ? 'enabled' : 'disabled'}`}
                  onClick={() => toggleConsent(card.key)}
                >
                  <span className="consent-toggle__thumb" />
                  <span className="sr-only">{isOn ? 'On' : 'Off'}</span>
                </button>
              </div>
            );
          })}
        </div>

        <p className="consent-footnote">
          You can review and change all of these in Settings → Privacy at any time.
        </p>

        <div className="phase__actions">
          <button
            className="btn btn--primary"
            onClick={nextPhase}
            aria-label="Save consent preferences and continue"
          >
            Save my preferences and continue
          </button>
        </div>
      </div>
    </section>
  );
}
