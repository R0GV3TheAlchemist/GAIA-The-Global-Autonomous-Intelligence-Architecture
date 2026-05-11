// C-OB01 — Phase 5: Consent
// Explicit, granular, reversible consent.
// Not a wall of text. A real conversation about trust.

import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import type { ConsentPreferences } from '../types';

const CONSENT_ITEMS: {
  key: keyof ConsentPreferences;
  label: string;
  description: string;
  default: boolean;
}[] = [
  {
    key: 'conversation_history',
    label: 'Conversation memory',
    description: 'GAIA remembers what we discuss so she can build on it over time.',
    default: true,
  },
  {
    key: 'mood_signals',
    label: 'Mood signals',
    description: 'GAIA notices emotional tone in how you write and adjusts her approach.',
    default: true,
  },
  {
    key: 'topic_patterns',
    label: 'Topic patterns',
    description: 'GAIA tracks which subjects you return to, to surface connections.',
    default: true,
  },
  {
    key: 'usage_patterns',
    label: 'Usage patterns',
    description: 'How you use GAIA — times, features, frequency — helps her adapt.',
    default: true,
  },
  {
    key: 'telemetry',
    label: 'Anonymous telemetry',
    description: 'Crash reports and performance data. Never linked to your identity.',
    default: false,
  },
  {
    key: 'cloud_backup',
    label: 'Cloud backup',
    description: 'Encrypted backup of your GAIA data. Off by default — your choice.',
    default: false,
  },
];

export function Phase5Consent() {
  const consent        = useOnboardingStore((s: OnboardingStore) => s.consent);
  const toggleConsent  = useOnboardingStore((s: OnboardingStore) => s.toggleConsent);
  const nextPhase      = useOnboardingStore((s: OnboardingStore) => s.nextPhase);

  return (
    <section className="phase phase--consent" aria-label="Privacy and consent">
      <div className="phase__content">
        <p className="gaia-aside">
          Here is what I'd like to remember and notice. You control all of it.
        </p>
        <div className="consent-list" role="group" aria-label="Consent preferences">
          {CONSENT_ITEMS.map(({ key, label, description }) => (
            <label key={key} className="consent-item">
              <div className="consent-item__text">
                <span className="consent-item__label">{label}</span>
                <span className="consent-item__desc">{description}</span>
              </div>
              <button
                role="switch"
                aria-checked={consent[key]}
                aria-label={`Toggle ${label}`}
                className={`consent-toggle ${
                  consent[key] ? 'consent-toggle--on' : 'consent-toggle--off'
                }`}
                onClick={() => toggleConsent(key)}
              >
                <span className="consent-toggle__thumb" />
              </button>
            </label>
          ))}
        </div>
        <div className="phase__actions">
          <button className="btn btn--primary" onClick={nextPhase}>
            These feel right
          </button>
        </div>
      </div>
    </section>
  );
}
