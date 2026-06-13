// C-OB01 — Phase 6: First Gift
// Refactor #366: receives onComplete + onBack props; no longer calls
// nextPhase() internally.

import { useEffect, useState, useCallback } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';

// ── Gift definitions ──────────────────────────────────────────────────────────
//
// Each gift card maps to a primary UserIntent. If the user's intent doesn't
// match, we fall back to the 'default' gift.

const GIFTS: Record<string, { icon: string; title: string; body: string; hint: string }> = {
  productivity: {
    icon:  '⚡',
    title: 'Focus Mode',
    body:  'A distraction-free workspace that surfaces only what matters for your current task. GAIA learns your working patterns and adjusts automatically.',
    hint:  'Activates in your first session.',
  },
  exploration: {
    icon:  '🔭',
    title: 'Deep Research',
    body:  'Multi-source synthesis with citation trails. Ask anything and GAIA will map the territory — not just answer the question.',
    hint:  'Available from day one.',
  },
  self_discovery: {
    icon:  '🪞',
    title: 'Reflection Journal',
    body:  'A private, on-device journal that GAIA can reference — but never sends anywhere. Pattern-recognition over time, entirely yours.',
    hint:  'Stored only on this device.',
  },
  privacy: {
    icon:  '🔒',
    title: 'Vault Mode',
    body:  'End-to-end encrypted conversations with zero cloud footprint. Everything local. Nothing leaves without your explicit action.',
    hint:  'Always available. Zero configuration.',
  },
  building: {
    icon:  '🛠',
    title: 'Builder\'s Toolkit',
    body:  'Code context that persists across sessions, smart scaffolding for new projects, and a GAIA that remembers your stack.',
    hint:  'Connects to your local environment.',
  },
  default: {
    icon:  '✦',
    title: 'Your Space',
    body:  'A workspace that adapts to whatever you bring to it. No predefined modes — GAIA learns from how you work.',
    hint:  'Ready when you are.',
  },
};

interface Phase6FirstGiftProps {
  onComplete: () => void;
  onBack:     () => void;
}

export function Phase6FirstGift({ onComplete, onBack }: Phase6FirstGiftProps) {
  const intent      = useOnboardingStore((s: OnboardingStore) => s.intent);
  const intentOther = useOnboardingStore((s: OnboardingStore) => s.intentOther);

  // Pick the gift based on the user's first stated intent
  const primaryIntent = Array.isArray(intent) ? (intent[0] ?? '') : '';
  const gift = GIFTS[primaryIntent] ?? GIFTS['default'];

  const [cardVisible, setCardVisible] = useState(false);
  const [showCta,     setShowCta]     = useState(false);

  useEffect(() => {
    setTimeout(() => setCardVisible(true), 400);
    setTimeout(() => setShowCta(true), 1200);
  }, []);

  const handleContinue = useCallback(() => onComplete(), [onComplete]);
  const handleSkip     = useCallback(() => onComplete(), [onComplete]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onBack();
      if ((e.key === 'Enter' || e.key === ' ') && showCta) {
        const tag = (document.activeElement as HTMLElement)?.tagName;
        if (tag !== 'BUTTON') handleContinue();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showCta, handleContinue, onBack]);

  // intentOther is used here for future gift personalisation (issue #367)
  void intentOther;

  return (
    <section className="phase phase--gift phase--enter" aria-label="Your first gift">
      <div className="phase__content phase__content--centered">

        <TypewriterText
          text="Before you begin — a gift."
          className="gift-intro"
          speed={30}
        />

        <div
          className={['gift-card', cardVisible ? 'gift-card--visible' : ''].filter(Boolean).join(' ')}
          aria-label={gift.title}
        >
          <span className="gift-card__icon" aria-hidden="true">{gift.icon}</span>
          <h2 className="gift-card__title">{gift.title}</h2>
          <p  className="gift-card__body">{gift.body}</p>
          <p  className="gift-card__hint">{gift.hint}</p>
        </div>

        {showCta && (
          <div className="phase__actions phase__content--centered">
            <button className="btn btn--primary" onClick={handleContinue} autoFocus>
              I'll take it
            </button>
            <button className="gift-skip" onClick={handleSkip}>
              Skip for now
            </button>
          </div>
        )}

      </div>
    </section>
  );
}
