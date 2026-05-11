// C-OB01 — Phase 4: Three Questions
// GAIA asks three things: intent, depth, sensitive topics.
// These seed the Soul Mirror and permission model.

import { useState } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import type { UserIntent, DepthPreference, SensitiveTopic } from '../types';

const INTENT_OPTIONS: { value: UserIntent; label: string; description: string }[] = [
  { value: 'productivity',   label: 'Get things done',        description: 'Tasks, goals, planning' },
  { value: 'exploration',    label: 'Explore ideas',          description: 'Questions, research, curiosity' },
  { value: 'self_discovery', label: 'Understand myself',      description: 'Reflection, patterns, growth' },
  { value: 'building',       label: 'Build something',        description: 'Projects, code, creation' },
  { value: 'privacy',        label: 'Manage my digital life', description: 'Privacy, security, control' },
  { value: 'other',          label: 'Something else',         description: 'Tell GAIA in your own words' },
];

const DEPTH_OPTIONS: { value: DepthPreference; label: string; description: string }[] = [
  { value: 'surface',     label: 'Surface',    description: 'Give me answers, keep it concise' },
  { value: 'reflective',  label: 'Reflective', description: 'Think with me, offer perspectives' },
  { value: 'deep',        label: 'Deep',       description: 'Challenge me, go beneath the surface' },
];

// Only values present on the SensitiveTopic union in types.ts
const SENSITIVE_OPTIONS: { value: SensitiveTopic; label: string }[] = [
  { value: 'mental_health',  label: 'Mental health' },
  { value: 'relationships',  label: 'Relationships' },
  { value: 'trauma',         label: 'Trauma' },
  { value: 'spiritual',      label: 'Spirituality' },
  { value: 'political',      label: 'Politics' },
];

export function Phase4ThreeQuestions() {
  const nextPhase          = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const setIntent          = useOnboardingStore((s: OnboardingStore) => s.setIntent);
  const storeSetIntentOther = useOnboardingStore((s: OnboardingStore) => s.setIntentOther);
  const setDepthPreference = useOnboardingStore((s: OnboardingStore) => s.setDepthPreference);
  const setSensitiveTopics = useOnboardingStore((s: OnboardingStore) => s.setSensitiveTopics);
  const markInterrupted    = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);

  const [step, setStep]                           = useState<0 | 1 | 2>(0);
  const [selectedIntent, setSelectedIntent]       = useState<UserIntent[]>([]);
  const [intentOtherText, setIntentOtherText]     = useState('');
  const [selectedDepth, setSelectedDepth]         = useState<DepthPreference>('reflective');
  const [selectedTopics, setSelectedTopics]       = useState<SensitiveTopic[]>([]);

  const toggleIntent = (v: UserIntent) =>
    setSelectedIntent((prev) =>
      prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]
    );

  const toggleTopic = (v: SensitiveTopic) =>
    setSelectedTopics((prev) =>
      prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]
    );

  const handleNext = () => {
    if (step === 0) {
      setIntent(selectedIntent);
      if (selectedIntent.includes('other')) storeSetIntentOther(intentOtherText);
      setStep(1);
    } else if (step === 1) {
      setDepthPreference(selectedDepth);
      setStep(2);
    } else {
      setSensitiveTopics(selectedTopics);
      nextPhase();
    }
  };

  return (
    <section className="phase phase--three-questions" aria-label="Three questions">
      <div className="phase__content">

        {step === 0 && (
          <fieldset className="question-group">
            <legend className="question-label">
              What brings you here?
              <span className="question-sub">Choose all that feel true.</span>
            </legend>
            <div className="intent-grid">
              {INTENT_OPTIONS.map(({ value, label, description }) => (
                <label
                  key={value}
                  className={`intent-card ${
                    selectedIntent.includes(value) ? 'intent-card--selected' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    value={value}
                    checked={selectedIntent.includes(value)}
                    onChange={() => toggleIntent(value)}
                    className="sr-only"
                  />
                  <span className="intent-card__label">{label}</span>
                  <span className="intent-card__desc">{description}</span>
                </label>
              ))}
            </div>
            {selectedIntent.includes('other') && (
              <textarea
                className="intent-other"
                placeholder="Tell GAIA what you have in mind..."
                value={intentOtherText}
                onChange={(e) => setIntentOtherText(e.target.value)}
                rows={3}
                aria-label="Describe your intent in your own words"
              />
            )}
          </fieldset>
        )}

        {step === 1 && (
          <fieldset className="question-group">
            <legend className="question-label">
              How do you want GAIA to engage with you?
            </legend>
            <div className="depth-options">
              {DEPTH_OPTIONS.map(({ value, label, description }) => (
                <label
                  key={value}
                  className={`depth-card ${
                    selectedDepth === value ? 'depth-card--selected' : ''
                  }`}
                >
                  <input
                    type="radio"
                    name="depth"
                    value={value}
                    checked={selectedDepth === value}
                    onChange={() => setSelectedDepth(value)}
                    className="sr-only"
                  />
                  <span className="depth-card__label">{label}</span>
                  <span className="depth-card__desc">{description}</span>
                </label>
              ))}
            </div>
          </fieldset>
        )}

        {step === 2 && (
          <fieldset className="question-group">
            <legend className="question-label">
              Are there topics you'd like GAIA to approach with extra care?
              <span className="question-sub">Optional. You can change this any time.</span>
            </legend>
            <div className="topic-grid">
              {SENSITIVE_OPTIONS.map(({ value, label }) => (
                <label
                  key={value}
                  className={`topic-chip ${
                    selectedTopics.includes(value) ? 'topic-chip--selected' : ''
                  }`}
                >
                  <input
                    type="checkbox"
                    value={value}
                    checked={selectedTopics.includes(value)}
                    onChange={() => toggleTopic(value)}
                    className="sr-only"
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>
        )}

        <div className="phase__actions">
          <button
            className="btn btn--primary"
            onClick={handleNext}
            disabled={step === 0 && selectedIntent.length === 0}
            onKeyDown={(e) => { if (e.key === 'Escape') markInterrupted(); }}
          >
            {step < 2 ? 'Next' : 'Continue'}
          </button>
        </div>
      </div>
    </section>
  );
}
