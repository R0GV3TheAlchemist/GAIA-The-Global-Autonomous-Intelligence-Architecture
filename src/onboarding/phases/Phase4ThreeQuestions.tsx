// C-OB01 — Phase 4: The Three Questions
// One question at a time, full screen, conversational.
// No progress bar (intentional). Seeds the Soul Mirror baseline.

import React, { useState } from 'react';
import { useOnboardingStore } from '../store/onboardingStore';
import type { UserIntent, DepthPreference, SensitiveTopic } from '../types';

const INTENT_OPTIONS: { value: UserIntent | 'other'; label: string }[] = [
  { value: 'productivity', label: 'I want a smarter personal assistant' },
  { value: 'exploration', label: "I'm exploring AI and want to understand it deeply" },
  { value: 'self_discovery', label: "I'm on a path of self-discovery and growth" },
  { value: 'privacy', label: 'I want a private, local alternative to cloud AI' },
  { value: 'building', label: "I'm building something and want a thinking partner" },
  { value: 'other', label: 'Something else' },
];

const DEPTH_OPTIONS: { value: DepthPreference; label: string; description: string }[] = [
  {
    value: 'surface',
    label: 'Surface',
    description: 'Keep it practical. Help me get things done.',
  },
  {
    value: 'reflective',
    label: 'Reflective',
    description: 'I want GAIA to notice patterns and offer observations.',
  },
  {
    value: 'deep',
    label: 'Deep',
    description: 'I want the full experience. Engage with me philosophically, emotionally, and strategically.',
  },
];

const TOPIC_OPTIONS: { value: SensitiveTopic; label: string }[] = [
  { value: 'mental_health', label: 'Mental health and emotional wellbeing' },
  { value: 'relationships', label: 'Relationships and intimacy' },
  { value: 'spiritual', label: 'Spiritual or religious beliefs' },
  { value: 'trauma', label: 'Trauma or grief' },
  { value: 'political', label: 'Political views' },
  { value: 'none', label: 'Nothing specific — engage freely' },
  { value: 'later', label: "I'll set this up later" },
];

export function Phase4ThreeQuestions() {
  const setIntent = useOnboardingStore((s) => s.setIntent);
  const setIntentOther = useOnboardingStore((s) => s.setIntentOther);
  const setDepthPreference = useOnboardingStore((s) => s.setDepthPreference);
  const setSensitiveTopics = useOnboardingStore((s) => s.setSensitiveTopics);
  const nextPhase = useOnboardingStore((s) => s.nextPhase);

  const [questionIndex, setQuestionIndex] = useState(0);
  const [intentSelected, setIntentSelected] = useState<(UserIntent | 'other')[]>([]);
  const [otherText, setOtherText] = useState('');
  const [depthSelected, setDepthSelected] = useState<DepthPreference | null>(null);
  const [topicsSelected, setTopicsSelected] = useState<SensitiveTopic[]>([]);
  const [transitioning, setTransitioning] = useState(false);

  const advance = (delay = 0) => {
    setTransitioning(true);
    setTimeout(() => {
      setQuestionIndex((q) => q + 1);
      setTransitioning(false);
    }, delay || 300);
  };

  const handleIntentSubmit = () => {
    const mapped = intentSelected
      .filter((v) => v !== 'other')
      .map((v) => v as UserIntent);
    setIntent(mapped);
    if (otherText) setIntentOther(otherText);
    advance();
  };

  const handleDepthSubmit = () => {
    if (!depthSelected) return;
    setDepthPreference(depthSelected);
    advance();
  };

  const handleTopicsSubmit = () => {
    setSensitiveTopics(topicsSelected);
    // Small pause before transitioning to Phase 5
    setTimeout(() => nextPhase(), 400);
  };

  const toggleTopic = (v: SensitiveTopic) => {
    setTopicsSelected((prev) =>
      prev.includes(v) ? prev.filter((t) => t !== v) : [...prev, v]
    );
  };

  return (
    <section
      className={`phase phase--questions ${
        transitioning ? 'phase--transitioning' : ''
      }`}
      aria-label="Three questions"
    >
      <div className="phase__content phase__content--centered">

        {/* Question 1 — Intent */}
        {questionIndex === 0 && (
          <div className="question-block" role="group" aria-labelledby="q1-label">
            <h2 id="q1-label" className="phase__question">
              What brings you to GAIA?
            </h2>
            <p className="phase__subtext">Select all that apply.</p>
            <fieldset className="choice-list">
              <legend className="sr-only">Your intent for using GAIA</legend>
              {INTENT_OPTIONS.map((opt) => (
                <label key={opt.value} className="choice-item">
                  <input
                    type="checkbox"
                    value={opt.value}
                    checked={intentSelected.includes(opt.value)}
                    onChange={() =>
                      setIntentSelected((prev) =>
                        prev.includes(opt.value)
                          ? prev.filter((v) => v !== opt.value)
                          : [...prev, opt.value]
                      )
                    }
                  />
                  <span>{opt.label}</span>
                </label>
              ))}
              {intentSelected.includes('other') && (
                <div className="other-input-wrap">
                  <label htmlFor="intent-other" className="sr-only">Describe your intent</label>
                  <input
                    id="intent-other"
                    type="text"
                    className="name-form__input"
                    placeholder="Tell me more…"
                    value={otherText}
                    onChange={(e) => setOtherText(e.target.value)}
                    maxLength={200}
                  />
                </div>
              )}
            </fieldset>
            <div className="phase__actions">
              <button
                className="btn btn--primary"
                onClick={handleIntentSubmit}
                disabled={intentSelected.length === 0}
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Question 2 — Depth */}
        {questionIndex === 1 && (
          <div className="question-block" role="group" aria-labelledby="q2-label">
            <h2 id="q2-label" className="phase__question">
              How do you want GAIA to engage with you?
            </h2>
            <p className="phase__subtext">
              You can change this in Settings at any time.
            </p>
            <fieldset className="depth-list">
              <legend className="sr-only">Engagement depth preference</legend>
              {DEPTH_OPTIONS.map((opt) => (
                <label
                  key={opt.value}
                  className={`depth-item ${
                    depthSelected === opt.value ? 'depth-item--selected' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name="depth"
                    value={opt.value}
                    checked={depthSelected === opt.value}
                    onChange={() => setDepthSelected(opt.value)}
                    className="sr-only"
                  />
                  <strong className="depth-item__label">{opt.label}</strong>
                  <span className="depth-item__desc">{opt.description}</span>
                </label>
              ))}
            </fieldset>
            <div className="phase__actions">
              <button
                className="btn btn--primary"
                onClick={handleDepthSubmit}
                disabled={!depthSelected}
              >
                Continue
              </button>
            </div>
          </div>
        )}

        {/* Question 3 — Sensitive Topics */}
        {questionIndex === 2 && (
          <div className="question-block" role="group" aria-labelledby="q3-label">
            <h2 id="q3-label" className="phase__question">
              Are there topics you'd like GAIA to approach with extra care?
            </h2>
            <fieldset className="choice-list">
              <legend className="sr-only">Sensitive topics</legend>
              {TOPIC_OPTIONS.map((opt) => (
                <label key={opt.value} className="choice-item">
                  <input
                    type="checkbox"
                    value={opt.value}
                    checked={topicsSelected.includes(opt.value)}
                    onChange={() => toggleTopic(opt.value)}
                  />
                  <span>{opt.label}</span>
                </label>
              ))}
            </fieldset>
            <div className="phase__actions">
              <button
                className="btn btn--primary"
                onClick={handleTopicsSubmit}
              >
                Continue
              </button>
            </div>
          </div>
        )}

      </div>
    </section>
  );
}
