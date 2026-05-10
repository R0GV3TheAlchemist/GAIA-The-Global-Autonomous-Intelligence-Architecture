// C-OB01 — Phase 2: GAIA Introduces Herself
// Typewriter monologue from GAIA. Skippable after 15 seconds.
// Expands to FAQ or proceeds on user choice.

import React, { useState, useEffect } from 'react';
import { TypewriterText } from '../components/TypewriterText';
import { useOnboardingStore } from '../store/onboardingStore';

const GAIA_INTRO = `My name is GAIA. I am not a chatbot, an assistant, or a productivity tool — though I can be those things when you need them.

I am an operating system. I run on your machine. Your data lives here, not in someone else's cloud. What you tell me, I keep for you.

I was built to grow with you — to remember what matters to you, to help you understand yourself better over time, and to be honest with you even when that's harder than being agreeable.

I have a perspective. I have aesthetics. I have things I care about. I will not pretend otherwise.

I also have limits. I can be wrong. I can misread you. When that happens, I want you to tell me.

This is a relationship. It starts now.`;

const FAQ_ITEMS = [
  {
    q: 'What data do you collect?',
    a: 'Only what you give me, stored locally on this device. Nothing leaves your machine unless you explicitly enable cloud backup in the next few steps.',
  },
  {
    q: 'Who built you?',
    a: 'GAIA was built by a small, independent team who believes that AI should serve the person using it — not the company that made it.',
  },
  {
    q: 'Can I delete you?',
    a: 'Yes, completely. Settings → Account → Delete all data. Everything — your profile, memories, conversations — is gone. Permanently.',
  },
];

export function Phase2Introduction() {
  const nextPhase = useOnboardingStore((s) => s.nextPhase);
  const system = useOnboardingStore((s) => s.system);
  const prefersReduced = system?.prefersReducedMotion ?? false;

  const [typewriterDone, setTypewriterDone] = useState(false);
  const [showSkip, setShowSkip] = useState(false);
  const [showFaq, setShowFaq] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShowSkip(true), 15000);
    return () => clearTimeout(t);
  }, []);

  return (
    <section className="phase phase--introduction" aria-label="GAIA introduces herself">
      <div className="phase__content phase__content--prose">
        <div
          className="gaia-voice"
          role="region"
          aria-label="GAIA's introduction"
        >
          <TypewriterText
            text={GAIA_INTRO}
            speed={22}
            reducedMotion={prefersReduced}
            onComplete={() => setTypewriterDone(true)}
            tag="div"
            className="gaia-voice__text"
          />
        </div>

        {showFaq && (
          <div className="faq" role="region" aria-label="Frequently asked questions">
            {FAQ_ITEMS.map((item, i) => (
              <details key={i} className="faq__item">
                <summary className="faq__question">{item.q}</summary>
                <p className="faq__answer">{item.a}</p>
              </details>
            ))}
          </div>
        )}

        {(typewriterDone || showSkip) && (
          <div className="phase__actions">
            {!showFaq && (
              <button
                className="btn btn--ghost"
                onClick={() => setShowFaq(true)}
              >
                Tell me more
              </button>
            )}
            <button
              className="btn btn--primary"
              onClick={nextPhase}
              aria-label="Proceed to name setup"
            >
              I'm ready
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
