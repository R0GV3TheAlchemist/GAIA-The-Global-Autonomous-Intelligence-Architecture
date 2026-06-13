// C-OB01 — Phase 5: Consent v2
// Explicit, granular, reversible consent.
// Not a wall of text. A real conversation about trust.
// Rebuilt: GAIA typewriter framing, staggered item reveal, grouped sections,
// accessible toggle switches, keyboard support.

import { useEffect, useRef, useState } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';
import type { ConsentPreferences } from '../types';

// ── Consent item definitions ────────────────────────────────────────────────

const CONSENT_ITEMS: {
  key:         keyof ConsentPreferences;
  icon:        string;
  label:       string;
  description: string;
  group:       'core' | 'optional';
}[] = [
  {
    key:         'conversation_history',
    icon:        '◎',
    label:       'Conversation memory',
    description: 'I remember what we discuss so I can build on it over time.',
    group:       'core',
  },
  {
    key:         'mood_signals',
    icon:        '∿',
    label:       'Mood signals',
    description: 'I notice the emotional tone in how you write and adjust my approach.',
    group:       'core',
  },
  {
    key:         'topic_patterns',
    icon:        '⬡',
    label:       'Topic patterns',
    description: 'I track which subjects you return to, to surface connections.',
    group:       'core',
  },
  {
    key:         'usage_patterns',
    icon:        '◈',
    label:       'Usage patterns',
    description: 'How you use me — times, features, frequency — helps me adapt.',
    group:       'core',
  },
  {
    key:         'telemetry',
    icon:        '↗',
    label:       'Anonymous telemetry',
    description: 'Crash reports and performance data. Never linked to your identity.',
    group:       'optional',
  },
  {
    key:         'cloud_backup',
    icon:        '⬡',
    label:       'Cloud backup',
    description: 'Encrypted backup of your GAIA data. Stored nowhere I can read it.',
    group:       'optional',
  },
];

const GAIA_PROMPT =
  'Here is what I can remember and notice. You control all of it — now and always.';

// ── Component ────────────────────────────────────────────────────────────────

export function Phase5Consent() {
  const consent        = useOnboardingStore((s: OnboardingStore) => s.consent);
  const toggleConsent  = useOnboardingStore((s: OnboardingStore) => s.toggleConsent);
  const nextPhase      = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);

  // Lock typewriter after first render so it doesn't re-type on re-render
  const promptShown = useRef(false);

  // Stagger: reveal items one by one after prompt finishes
  const [revealCount, setRevealCount] = useState(0);

  const handlePromptComplete = () => {
    promptShown.current = true;
    // Start cascading reveal — one item every 90ms
    CONSENT_ITEMS.forEach((_, i) => {
      setTimeout(() => setRevealCount(i + 1), i * 90);
    });
  };

  // Keyboard: Enter → advance, Escape → interrupt
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { markInterrupted(); return; }
      if (e.key === 'Enter') nextPhase();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [nextPhase, markInterrupted]);

  // ── Render ────────────────────────────────────────────────────────────────

  const coreItems     = CONSENT_ITEMS.filter(i => i.group === 'core');
  const optionalItems = CONSENT_ITEMS.filter(i => i.group === 'optional');
  const coreStart     = 0;
  const optStart      = coreItems.length;

  return (
    <section className="phase phase--consent phase--enter" aria-label="Privacy and consent">
      <div className="phase__content">

        {/* ── GAIA prompt ─────────────────────────────────────────────── */}
        <TypewriterText
          key={promptShown.current ? 'static' : 'type'}
          text={GAIA_PROMPT}
          speed={26}
          onComplete={handlePromptComplete}
          tag="p"
          className="q4-prompt"
        />

        {/* ── Consent items ────────────────────────────────────────────── */}
        <div className="consent-list" role="group" aria-label="Consent preferences">

          {/* Core group */}
          <p className="consent-group-label">On by default · stored only on your device</p>
          {coreItems.map(({ key, icon, label, description }, i) => (
            <ConsentRow
              key={key}
              icon={icon}
              label={label}
              description={description}
              checked={consent[key]}
              visible={revealCount > coreStart + i}
              onToggle={() => toggleConsent(key)}
            />
          ))}

          {/* Divider */}
          <div className="consent-divider" role="separator" />

          {/* Optional group */}
          <p className="consent-group-label consent-group-label--dim">Optional extras · off by default</p>
          {optionalItems.map(({ key, icon, label, description }, i) => (
            <ConsentRow
              key={key}
              icon={icon}
              label={label}
              description={description}
              checked={consent[key]}
              visible={revealCount > optStart + i}
              onToggle={() => toggleConsent(key)}
            />
          ))}
        </div>

        {/* ── Footer note ─────────────────────────────────────────────── */}
        <p className="consent-footer">
          You can change any of this at any time in{' '}
          <span className="consent-footer__path">Settings → Privacy</span>.
        </p>

        {/* ── Actions ─────────────────────────────────────────────────── */}
        <div className="phase__actions">
          <button
            type="button"
            className="btn btn--primary"
            onClick={nextPhase}
            aria-label="Accept consent preferences and continue"
          >
            I'm ready
          </button>
        </div>

      </div>
    </section>
  );
}

// ── ConsentRow sub-component ─────────────────────────────────────────────────
//
// Rendered as a div + role=switch button rather than label/input
// so keyboard Space on the toggle fires toggle without also firing
// the label click — avoids double-toggle on keyboard.
//
interface ConsentRowProps {
  icon:        string;
  label:       string;
  description: string;
  checked:     boolean;
  visible:     boolean;
  onToggle:    () => void;
}

function ConsentRow({ icon, label, description, checked, visible, onToggle }: ConsentRowProps) {
  return (
    <div
      className={`consent-item${
        checked  ? ' consent-item--on'      : ''
      }${
        visible  ? ' consent-item--visible' : ''
      }`}
    >
      <span className="consent-item__icon" aria-hidden>{icon}</span>

      <div className="consent-item__body">
        <span className="consent-item__label">{label}</span>
        <span className="consent-item__desc">{description}</span>
      </div>

      <button
        type="button"
        role="switch"
        aria-checked={checked}
        aria-label={`${checked ? 'Disable' : 'Enable'} ${label}`}
        className={`consent-toggle${checked ? ' consent-toggle--on' : ''}`}
        onClick={onToggle}
        onKeyDown={(e) => { if (e.key === ' ') { e.preventDefault(); onToggle(); } }}
      >
        <span className="consent-toggle__thumb" aria-hidden />
      </button>
    </div>
  );
}
