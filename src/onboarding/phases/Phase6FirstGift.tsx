// C-OB01 — Phase 6: The First Gift v3
// GAIA gives something based on user intent before asking anything more.
// Intentional inversion of standard onboarding psychology.
// Rebuilt: TypewriterText intro, card gated on prompt completion,
// 'other' intent personalisation, primary CTA hierarchy, keyboard support.

import { useMemo, useEffect, useRef, useState, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';

// ── Gift shape ────────────────────────────────────────────────────────────────────

interface Gift {
  icon:   string;
  title:  string;
  body:   string;
  action: string;
  hint?:  string;
}

// ── Gift selection ───────────────────────────────────────────────────────────────
//
// Priority: self_discovery > privacy > building > exploration >
//           productivity > other (personalised) > default
// Multi-intent users see the gift for their highest-priority intent.
//
function selectGift(intent: string[], intentOther: string): Gift {
  if (intent.includes('self_discovery')) return {
    icon:   '✦',
    title:  'A question to begin with',
    body:   "What’s one thing you want more of in your life right now? Ask me. I’ll remember what you say.",
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
    title:  "How GAIA’s memory works",
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
  // 'other' with text — personalised using their own words
  if (intent.includes('other') && intentOther.trim().length > 0) return {
    icon:   '…',
    title:  'Let’s start there',
    body:   `You said you’re here for something else. I’d like to hear more. Start with: “${intentOther.trim().slice(0, 120)}”`,
    action: 'Tell GAIA more',
    hint:   'This opens our first real conversation.',
  };
  // Default fallback
  return {
    icon:   '◌',
    title:  'A place to begin',
    body:   'I’m ready. Explore at whatever pace feels right. There is no wrong way to start.',
    action: 'Let’s begin',
  };
}

// ── Component ─────────────────────────────────────────────────────────────────────

export function Phase6FirstGift() {
  const intent        = useOnboardingStore((s: OnboardingStore) => s.intent);
  const intentOther   = useOnboardingStore((s: OnboardingStore) => s.intent_other);
  const name          = useOnboardingStore((s: OnboardingStore) => s.name);
  const nextPhase     = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const markInterrupted = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);

  const gift = useMemo(() => selectGift(intent, intentOther ?? ''), [intent, intentOther]);

  // Typewriter prompt — lock key after first render so it never re-types
  const promptShown = useRef(false);

  // Gift card is hidden until the typewriter finishes
  const [cardVisible, setCardVisible] = useState(false);

  const handlePromptComplete = useCallback(() => {
    promptShown.current = true;
    // Small beat after prompt ends before card slides in
    setTimeout(() => setCardVisible(true), 160);
  }, []);

  // Keyboard: Enter → advance, Escape → interrupt
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { markInterrupted(); return; }
      if (e.key === 'Enter')  nextPhase();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [nextPhase, markInterrupted]);

  const introPrompt = name
    ? `${name}, here is something to start with.`
    : 'Here is something to start with.';

  const titleId = 'gift-title';

  return (
    <section className="phase phase--first-gift phase--enter" aria-label="Your first gift from GAIA">
      <div className="phase__content phase__content--centered">

        {/* ── GAIA intro line ─────────────────────────────────────────────── */}
        <TypewriterText
          key={promptShown.current ? 'static' : 'type'}
          text={introPrompt}
          speed={28}
          onComplete={handlePromptComplete}
          tag="p"
          className="q4-prompt gift-intro"
        />

        {/* ── Gift card ──────────────────────────────────────────────────── */}
        <article
          className={`gift-card${cardVisible ? ' gift-card--visible' : ''}`}
          aria-labelledby={titleId}
          aria-live="polite"
        >
          <span className="gift-card__icon" aria-hidden>{gift.icon}</span>
          <h2   className="gift-card__title" id={titleId}>{gift.title}</h2>
          <p    className="gift-card__body">{gift.body}</p>
          {gift.hint && (
            <p className="gift-card__hint" aria-label={`Hint: ${gift.hint}`}>
              {gift.hint}
            </p>
          )}

          <button
            type="button"
            className="btn btn--primary"
            onClick={nextPhase}
            aria-label={`${gift.action} — ${gift.title}`}
          >
            {gift.action}
          </button>
        </article>

        {/* ── Skip ───────────────────────────────────────────────────────────── */}
        {cardVisible && (
          <button
            type="button"
            className="gift-skip"
            onClick={nextPhase}
            aria-label="Skip this gift and continue"
          >
            Skip for now
          </button>
        )}

      </div>
    </section>
  );
}
