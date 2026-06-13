// C-OB01 — Phase 6: The First Gift v2
// GAIA gives something based on user intent before asking anything more.
// Intentional inversion of standard onboarding psychology.
// Upgraded: animated gift card entrance, improved aria-labels,
// gift card uses full intent array (multi-intent aware),
// 'Tell GAIA' variant seeds an initial conversation starter.

import { useMemo, useEffect, useState } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';

interface Gift {
  icon:    string;
  title:   string;
  body:    string;
  action:  string;
  hint?:   string;
}

/**
 * Priority order: self_discovery > privacy > building > exploration > productivity > default
 * Multi-intent users see the gift most relevant to their first matched priority.
 */
function selectGift(intent: string[]): Gift {
  if (intent.includes('self_discovery')) return {
    icon:   '✦',
    title:  'A question to begin with',
    body:   "What's one thing you want more of in your life right now? Ask me. I'll remember what you say.",
    action: 'Ask GAIA',
    hint:   'This opens a conversation — not a form.',
  };
  if (intent.includes('privacy')) return {
    icon:   '🗂',
    title:  'Where your data lives',
    body:   'A complete map of every file GAIA creates on your device — every folder, every path. Nothing hidden.',
    action: 'Show me the map',
    hint:   'All data stays on this device.',
  };
  if (intent.includes('building')) return {
    icon:   '◻',
    title:  'An empty canvas',
    body:   "A blank project space with me ready to think alongside you. Bring an idea — or just start talking.",
    action: 'Open canvas',
  };
  if (intent.includes('exploration')) return {
    icon:   '◎',
    title:  "How GAIA's memory works",
    body:   "A short walkthrough of how I remember things, what I notice, and how you can guide what I learn about you.",
    action: 'Show me',
    hint:   'Takes about 2 minutes.',
  };
  if (intent.includes('productivity')) return {
    icon:   '▸',
    title:  'Your Daily Briefing ritual',
    body:   "A pre-built template to start each day with GAIA — your tasks, your intentions, your context.",
    action: 'Open Daily Briefing',
    hint:   'You can edit this any time.',
  };
  return {
    icon:   '◌',
    title:  'A place to begin',
    body:   'GAIA is ready. Explore at whatever pace feels right. There is no wrong way to start.',
    action: 'Continue',
  };
}

export function Phase6FirstGift() {
  const intent    = useOnboardingStore((s: OnboardingStore) => s.intent);
  const name      = useOnboardingStore((s: OnboardingStore) => s.name);
  const nextPhase = useOnboardingStore((s: OnboardingStore) => s.nextPhase);

  const gift   = useMemo(() => selectGift(intent), [intent]);
  const [visible, setVisible] = useState(false);

  // Slight delay so the card entrance animation plays after phase fade-in
  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 320);
    return () => clearTimeout(t);
  }, []);

  return (
    <section className="phase phase--first-gift phase--enter" aria-label="Your first gift from GAIA">
      <div className="phase__content phase__content--centered">

        <p className="gaia-aside">
          {name ? `${name}, here's something to start with.` : 'Here's something to start with.'}
        </p>

        <div
          className={`gift-card${visible ? ' gift-card--visible' : ''}`}
          role="region"
          aria-label={gift.title}
        >
          <span className="gift-card__icon" aria-hidden>{gift.icon}</span>
          <h2 className="gift-card__title">{gift.title}</h2>
          <p  className="gift-card__body">{gift.body}</p>
          {gift.hint && <p className="gift-card__hint">{gift.hint}</p>}
          <button
            className="btn btn--secondary"
            onClick={nextPhase}
            aria-label={`${gift.action} — ${gift.title}`}
          >
            {gift.action}
          </button>
        </div>

        <button
          className="btn btn--ghost btn--small"
          onClick={nextPhase}
          aria-label="Skip this gift and continue to account setup"
        >
          Skip for now
        </button>

      </div>
    </section>
  );
}
