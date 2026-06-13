// C-OB01 — Phase 4: Three Questions v2
// GAIA asks three things: intent, depth, sensitive topics.
// These seed the Soul Mirror and permission model.
// Rebuilt: conversational step flow, animated transitions, GAIA voice prompts,
// back navigation, full keyboard support, no required fields on step 2.

import { useState, useCallback, useEffect, useRef } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import { TypewriterText } from '../components/TypewriterText';
import type { UserIntent, DepthPreference, SensitiveTopic } from '../types';

// ── Data ───────────────────────────────────────────────────────────────────────────

const INTENT_OPTIONS: {
  value:       UserIntent;
  icon:        string;
  label:       string;
  description: string;
}[] = [
  { value: 'productivity',   icon: '▸',  label: 'Get things done',        description: 'Tasks, goals, planning' },
  { value: 'exploration',    icon: '◎',  label: 'Explore ideas',          description: 'Questions, research, curiosity' },
  { value: 'self_discovery', icon: '✦',  label: 'Understand myself',      description: 'Reflection, patterns, growth' },
  { value: 'building',       icon: '◻',  label: 'Build something',        description: 'Projects, code, creation' },
  { value: 'privacy',        icon: '🗂',  label: 'Manage my digital life', description: 'Privacy, security, control' },
  { value: 'other',          icon: '…',  label: 'Something else',         description: 'I\'ll tell GAIA in my own words' },
];

const DEPTH_OPTIONS: {
  value:       DepthPreference;
  icon:        string;
  label:       string;
  description: string;
  detail:      string;
}[] = [
  {
    value:       'surface',
    icon:        '―',
    label:       'Surface',
    description: 'Give me answers',
    detail:      'Concise, direct, no extra context unless I ask.',
  },
  {
    value:       'reflective',
    icon:        '∿',
    label:       'Reflective',
    description: 'Think with me',
    detail:      'Offer perspectives, ask questions back, explore ideas together.',
  },
  {
    value:       'deep',
    icon:        '∞',
    label:       'Deep',
    description: 'Go beneath the surface',
    detail:      'Challenge assumptions, make connections, don\'t hold back.',
  },
];

const SENSITIVE_OPTIONS: { value: SensitiveTopic; label: string; emoji: string }[] = [
  { value: 'mental_health',  label: 'Mental health',  emoji: '🧐' },
  { value: 'relationships',  label: 'Relationships',  emoji: '🤝' },
  { value: 'trauma',         label: 'Trauma',         emoji: '🛑' },
  { value: 'spiritual',      label: 'Spirituality',   emoji: '✶' },
  { value: 'political',      label: 'Politics',       emoji: '🌎' },
];

// ── GAIA question prompts (typed once per step) ─────────────────────────────────────

const STEP_PROMPTS = [
  'What brings you here? Choose everything that feels true.',
  'How do you want me to think with you?',
  'Are there areas you\'d like me to be more careful in?',
];

// ── Transition direction ───────────────────────────────────────────────────────────

type TransitionState = 'idle' | 'exiting-forward' | 'exiting-back' | 'entering-forward' | 'entering-back';

// ── Component ───────────────────────────────────────────────────────────────────────

export function Phase4ThreeQuestions() {
  const nextPhase           = useOnboardingStore((s: OnboardingStore) => s.nextPhase);
  const setIntent           = useOnboardingStore((s: OnboardingStore) => s.setIntent);
  const setIntentOther      = useOnboardingStore((s: OnboardingStore) => s.setIntentOther);
  const setDepthPreference  = useOnboardingStore((s: OnboardingStore) => s.setDepthPreference);
  const setSensitiveTopics  = useOnboardingStore((s: OnboardingStore) => s.setSensitiveTopics);
  const markInterrupted     = useOnboardingStore((s: OnboardingStore) => s.markInterrupted);
  const storedName          = useOnboardingStore((s: OnboardingStore) => s.name);

  const [step,           setStep]           = useState<0 | 1 | 2>(0);
  const [transition,     setTransition]     = useState<TransitionState>('idle');

  // Step 0 — intent
  const [selectedIntent,   setSelectedIntent]   = useState<UserIntent[]>([]);
  const [intentOtherText,  setIntentOtherText]  = useState('');
  const [showOther,        setShowOther]        = useState(false);

  // Step 1 — depth
  const [selectedDepth,    setSelectedDepth]    = useState<DepthPreference>('reflective');

  // Step 2 — topics
  const [selectedTopics,   setSelectedTopics]   = useState<SensitiveTopic[]>([]);

  // Track whether the TypewriterText prompt for the current step has been shown
  // Use a ref so the typewriter key never changes after the first render of a step
  const promptShownRef = useRef<Set<number>>(new Set());

  // ── Transition engine ─────────────────────────────────────────────────────────────
  // Plays a 240ms exit animation then swaps the step, then enters.
  // direction: 'forward' | 'back'
  const changeStep = useCallback((target: 0 | 1 | 2, direction: 'forward' | 'back') => {
    setTransition(direction === 'forward' ? 'exiting-forward' : 'exiting-back');
    setTimeout(() => {
      setStep(target);
      setTransition(direction === 'forward' ? 'entering-forward' : 'entering-back');
      setTimeout(() => setTransition('idle'), 260);
    }, 240);
  }, []);

  // ── Intent toggle ─────────────────────────────────────────────────────────────────

  const toggleIntent = useCallback((v: UserIntent) => {
    setSelectedIntent(prev => {
      const next = prev.includes(v) ? prev.filter(x => x !== v) : [...prev, v];
      setShowOther(next.includes('other'));
      return next;
    });
  }, []);

  // ── Topics toggle ────────────────────────────────────────────────────────────────

  const toggleTopic = useCallback((v: SensitiveTopic) => {
    setSelectedTopics(prev =>
      prev.includes(v) ? prev.filter(x => x !== v) : [...prev, v]
    );
  }, []);

  // ── Advance ──────────────────────────────────────────────────────────────────────

  const handleNext = useCallback(() => {
    if (step === 0) {
      setIntent(selectedIntent);
      if (selectedIntent.includes('other')) setIntentOther(intentOtherText);
      changeStep(1, 'forward');
    } else if (step === 1) {
      setDepthPreference(selectedDepth);
      changeStep(2, 'forward');
    } else {
      // Final step — commit everything and advance the phase
      setSensitiveTopics(selectedTopics);
      nextPhase();
    }
  }, [step, selectedIntent, intentOtherText, selectedDepth, selectedTopics,
      setIntent, setIntentOther, setDepthPreference, setSensitiveTopics, nextPhase, changeStep]);

  const handleBack = useCallback(() => {
    if (step === 1) changeStep(0, 'back');
    else if (step === 2) changeStep(1, 'back');
  }, [step, changeStep]);

  // ── Keyboard handler ─────────────────────────────────────────────────────────────

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { markInterrupted(); return; }
      // Enter advances only if the focused element is not a textarea
      if (e.key === 'Enter' && document.activeElement?.tagName !== 'TEXTAREA') {
        if (canAdvance) handleNext();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [handleNext, markInterrupted, step, selectedIntent]);

  const canAdvance = step === 0 ? selectedIntent.length > 0 : true;

  // ── Transition CSS class ───────────────────────────────────────────────────────────

  const transitionClass =
    transition === 'exiting-forward'  ? 'q4-step--exit-forward'  :
    transition === 'exiting-back'     ? 'q4-step--exit-back'     :
    transition === 'entering-forward' ? 'q4-step--enter-forward' :
    transition === 'entering-back'    ? 'q4-step--enter-back'    : '';

  // ── Personalised greeting for step 0 ─────────────────────────────────────────────

  const prompt0 = storedName
    ? `${storedName}, what brings you here? Choose everything that feels true.`
    : STEP_PROMPTS[0];

  // ── Render ─────────────────────────────────────────────────────────────────────────

  return (
    <section className="phase phase--three-questions phase--enter" aria-label="Three questions">
      <div className="phase__content">

        {/* ── Step counter ─────────────────────────────────────────────────────── */}
        <div className="q4-header" aria-label={`Question ${step + 1} of 3`}>
          <span className="q4-step-label">{step + 1} / 3</span>
          <div className="q4-dots" role="presentation">
            {[0, 1, 2].map(i => (
              <span
                key={i}
                className={[
                  'q4-dot',
                  i < step  ? 'q4-dot--done'   : '',
                  i === step ? 'q4-dot--active' : '',
                ].filter(Boolean).join(' ')}
              />
            ))}
          </div>
        </div>

        {/* ── Animated step container ──────────────────────────────────────────────── */}
        <div className={`q4-step ${transitionClass}`}>

          {/* ─ Step 0: Intent ─ */}
          {step === 0 && (
            <fieldset className="question-group" aria-label="What brings you here">
              <legend className="sr-only">What brings you here?</legend>

              <TypewriterText
                key={`prompt-0-${promptShownRef.current.has(0) ? 'static' : 'type'}`}
                text={prompt0}
                speed={28}
                onComplete={() => promptShownRef.current.add(0)}
                tag="p"
                className="q4-prompt"
              />

              <div className="intent-grid">
                {INTENT_OPTIONS.map(({ value, icon, label, description }) => (
                  <button
                    key={value}
                    type="button"
                    className={`intent-card${selectedIntent.includes(value) ? ' intent-card--selected' : ''}`}
                    onClick={() => toggleIntent(value)}
                    aria-pressed={selectedIntent.includes(value)}
                  >
                    <span className="intent-card__icon" aria-hidden>{icon}</span>
                    <span className="intent-card__label">{label}</span>
                    <span className="intent-card__desc">{description}</span>
                  </button>
                ))}
              </div>

              {showOther && (
                <textarea
                  className="intent-other"
                  placeholder="Tell GAIA what you have in mind…"
                  value={intentOtherText}
                  onChange={e => setIntentOtherText(e.target.value)}
                  rows={3}
                  maxLength={500}
                  autoFocus
                  aria-label="Describe your intent"
                />
              )}
            </fieldset>
          )}

          {/* ─ Step 1: Depth ─ */}
          {step === 1 && (
            <fieldset className="question-group" aria-label="Depth preference">
              <legend className="sr-only">How deep should GAIA go?</legend>

              <TypewriterText
                key={`prompt-1-${promptShownRef.current.has(1) ? 'static' : 'type'}`}
                text={STEP_PROMPTS[1]}
                speed={28}
                onComplete={() => promptShownRef.current.add(1)}
                tag="p"
                className="q4-prompt"
              />

              <div className="depth-list" role="radiogroup" aria-label="Depth options">
                {DEPTH_OPTIONS.map(({ value, icon, label, description, detail }) => (
                  <button
                    key={value}
                    type="button"
                    role="radio"
                    aria-checked={selectedDepth === value}
                    className={`depth-card${selectedDepth === value ? ' depth-card--selected' : ''}`}
                    onClick={() => setSelectedDepth(value)}
                  >
                    <span className="depth-card__icon" aria-hidden>{icon}</span>
                    <span className="depth-card__label">{label}</span>
                    <span className="depth-card__desc">{description}</span>
                    <span className="depth-card__detail">{detail}</span>
                  </button>
                ))}
              </div>
            </fieldset>
          )}

          {/* ─ Step 2: Topics ─ */}
          {step === 2 && (
            <fieldset className="question-group" aria-label="Sensitive topics">
              <legend className="sr-only">Sensitive topics</legend>

              <TypewriterText
                key={`prompt-2-${promptShownRef.current.has(2) ? 'static' : 'type'}`}
                text={STEP_PROMPTS[2]}
                speed={28}
                onComplete={() => promptShownRef.current.add(2)}
                tag="p"
                className="q4-prompt"
              />

              <p className="q4-sub">You can change this any time in Settings.</p>

              <div className="topics-chips" role="group" aria-label="Topic chips">
                {SENSITIVE_OPTIONS.map(({ value, label, emoji }) => (
                  <button
                    key={value}
                    type="button"
                    className={`topic-chip${selectedTopics.includes(value) ? ' topic-chip--selected' : ''}`}
                    onClick={() => toggleTopic(value)}
                    aria-pressed={selectedTopics.includes(value)}
                  >
                    <span aria-hidden>{emoji}</span> {label}
                  </button>
                ))}
              </div>

              <button
                type="button"
                className="q4-none-btn"
                onClick={() => setSelectedTopics([])}
                aria-label="Clear all topic selections"
              >
                None of these
              </button>
            </fieldset>
          )}

        </div>{/* end .q4-step */}

        {/* ── Actions ────────────────────────────────────────────────────────────── */}
        <div className="phase__actions q4-actions">
          {step > 0 && (
            <button
              type="button"
              className="btn btn--ghost btn--small"
              onClick={handleBack}
              aria-label="Go back to previous question"
            >
              ← Back
            </button>
          )}
          <button
            type="button"
            className="btn btn--primary"
            onClick={handleNext}
            disabled={!canAdvance}
            aria-label={step < 2 ? 'Continue to next question' : 'Finish three questions'}
          >
            {step < 2 ? 'Continue →' : 'These feel right'}
          </button>
        </div>

      </div>
    </section>
  );
}
