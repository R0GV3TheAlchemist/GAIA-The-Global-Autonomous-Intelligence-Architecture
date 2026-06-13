// C-OB01 — Phase 4: Three Questions
// Refactor #366: receives onComplete + onBack props; no longer calls
// nextPhase() or setPhase() internally.
//
// Internal step navigation (step 0→1→2 within this phase) remains
// self-contained because it's intra-phase — the router only needs to
// know when the whole phase is done (onComplete) or abandoned (onBack).

import { useState, useCallback, useEffect } from 'react';
import { useOnboardingStore, type OnboardingStore } from '../store/onboardingStore';
import type { UserIntent, SensitiveTopic } from '../types';

// ── Intent options ────────────────────────────────────────────────────────────

const INTENT_OPTIONS: { value: UserIntent; label: string; icon: string; desc: string }[] = [
  { value: 'productivity',    label: 'Productivity',    icon: '⚡', desc: 'Get more done, faster'       },
  { value: 'exploration',     label: 'Exploration',     icon: '🔭', desc: 'Research and discovery'      },
  { value: 'self_discovery',  label: 'Self-discovery',  icon: '🪞', desc: 'Know yourself better'        },
  { value: 'privacy',         label: 'Privacy',         icon: '🔒', desc: 'A private thinking space'    },
  { value: 'building',        label: 'Building',        icon: '🛠', desc: 'Make things'                 },
  { value: 'other',           label: 'Something else',  icon: '✦',  desc: 'I\'ll explain below'         },
];

// ── Depth options ─────────────────────────────────────────────────────────────

const DEPTH_OPTIONS: { value: 'surface' | 'reflective' | 'deep'; label: string; desc: string; detail: string; icon: string }[] = [
  {
    value:  'surface',
    label:  'Surface',
    desc:   'Fresh start each session',
    detail: 'No memory between conversations. Clean, private, ephemeral.',
    icon:   '○',
  },
  {
    value:  'reflective',
    label:  'Reflective',
    desc:   'Grows with you over time',
    detail: 'Context builds across sessions. GAIA remembers patterns, not verbatim.',
    icon:   '◐',
  },
  {
    value:  'deep',
    label:  'Deep',
    desc:   'Full memory, full trust',
    detail: 'Everything remembered. Most personalised. You control what to forget.',
    icon:   '●',
  },
];

// ── Sensitive topic options ───────────────────────────────────────────────────

const TOPIC_OPTIONS: { value: SensitiveTopic; label: string }[] = [
  { value: 'mental_health', label: 'Mental health'   },
  { value: 'relationships', label: 'Relationships'   },
  { value: 'spiritual',     label: 'Spiritual'       },
  { value: 'trauma',        label: 'Trauma'          },
  { value: 'political',     label: 'Politics'        },
];

// ── Props ─────────────────────────────────────────────────────────────────────

interface Phase4ThreeQuestionsProps {
  onComplete: () => void;
  onBack:     () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function Phase4ThreeQuestions({ onComplete, onBack }: Phase4ThreeQuestionsProps) {
  const setIntent          = useOnboardingStore((s: OnboardingStore) => s.setIntent);
  const setIntentOther     = useOnboardingStore((s: OnboardingStore) => s.setIntentOther);
  const setDepthPreference = useOnboardingStore((s: OnboardingStore) => s.setDepthPreference);
  const setSensitiveTopics = useOnboardingStore((s: OnboardingStore) => s.setSensitiveTopics);

  const savedIntent  = useOnboardingStore((s: OnboardingStore) => s.intent);
  const savedDepth   = useOnboardingStore((s: OnboardingStore) => s.depth);
  const savedTopics  = useOnboardingStore((s: OnboardingStore) => s.sensitive_topics);

  // Local state — committed to store on each step's Next
  const [step,        setStep]        = useState(0);
  const [intents,     setIntents]     = useState<UserIntent[]>(savedIntent ?? []);
  const [intentOther, setIntentOther_] = useState('');
  const [depth,       setDepth]       = useState<'surface' | 'reflective' | 'deep'>(savedDepth ?? 'reflective');
  const [topics,      setTopics]      = useState<SensitiveTopic[]>(savedTopics ?? []);
  const [stepDir,     setStepDir]     = useState<'forward' | 'back'>('forward');

  // ── Step navigation ─────────────────────────────────────────────────────────

  const goForward = useCallback(() => {
    setStepDir('forward');
    setStep((s) => s + 1);
  }, []);

  const goBack = useCallback(() => {
    if (step === 0) { onBack(); return; }
    setStepDir('back');
    setStep((s) => s - 1);
  }, [step, onBack]);

  // ── Step 0: Intent ──────────────────────────────────────────────────────────

  const handleIntentNext = useCallback(() => {
    const toSave = intents.length ? intents : (['other'] as UserIntent[]);
    setIntent(toSave);
    if (intentOther) setIntentOther(intentOther);
    goForward();
  }, [intents, intentOther, setIntent, setIntentOther, goForward]);

  const toggleIntent = useCallback((v: UserIntent) => {
    setIntents((prev) =>
      prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]
    );
  }, []);

  // ── Step 1: Depth ───────────────────────────────────────────────────────────

  const handleDepthNext = useCallback(() => {
    setDepthPreference(depth);
    goForward();
  }, [depth, setDepthPreference, goForward]);

  // ── Step 2: Sensitive topics ────────────────────────────────────────────────

  const handleTopicsNext = useCallback(() => {
    setSensitiveTopics(topics);
    onComplete();
  }, [topics, setSensitiveTopics, onComplete]);

  const toggleTopic = useCallback((v: SensitiveTopic) => {
    setTopics((prev) =>
      prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]
    );
  }, []);

  // ── Keyboard ────────────────────────────────────────────────────────────────

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') goBack();
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [goBack]);

  // ── Step direction animation class ──────────────────────────────────────────

  const enterClass = stepDir === 'forward' ? 'q4-step--enter-forward' : 'q4-step--enter-back';

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <section className="phase phase--questions phase--enter" aria-label="Three Questions">
      <div className="phase__content">

        {/* Step header */}
        <div className="q4-header">
          <span className="q4-step-label">{step + 1} / 3</span>
          <div className="q4-dots" aria-hidden="true">
            {[0, 1, 2].map((i) => (
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

        {/* Step 0 — Intent */}
        {step === 0 && (
          <div className={`q4-step ${enterClass}`} key="intent">
            <p className="q4-prompt">What brings you here?</p>
            <p className="q4-sub">Pick as many as you like.</p>
            <fieldset className="question-group" aria-label="Why are you here">
              <div className="intent-grid">
                {INTENT_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    className={['intent-card', intents.includes(opt.value) ? 'intent-card--selected' : ''].filter(Boolean).join(' ')}
                    onClick={() => toggleIntent(opt.value)}
                    aria-pressed={intents.includes(opt.value)}
                  >
                    <span className="intent-card__icon" aria-hidden="true">{opt.icon}</span>
                    <span className="intent-card__label">{opt.label}</span>
                    <span className="intent-card__desc">{opt.desc}</span>
                  </button>
                ))}
              </div>
              {intents.includes('other') && (
                <textarea
                  className="intent-other"
                  placeholder="Tell me more…"
                  value={intentOther}
                  onChange={(e) => setIntentOther_(e.target.value)}
                  rows={2}
                  maxLength={240}
                  aria-label="Describe your intent"
                />
              )}
            </fieldset>
            <div className="phase__actions q4-actions">
              <button className="btn btn--ghost" onClick={goBack}>← Back</button>
              <button className="btn btn--primary" onClick={handleIntentNext}>Next</button>
            </div>
          </div>
        )}

        {/* Step 1 — Depth */}
        {step === 1 && (
          <div className={`q4-step ${enterClass}`} key="depth">
            <p className="q4-prompt">How much should I remember?</p>
            <fieldset className="question-group" aria-label="Memory depth preference">
              <div className="depth-list">
                {DEPTH_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    className={['depth-card', depth === opt.value ? 'depth-card--selected' : ''].filter(Boolean).join(' ')}
                    onClick={() => setDepth(opt.value)}
                    aria-pressed={depth === opt.value}
                  >
                    <span className="depth-card__icon" aria-hidden="true">{opt.icon}</span>
                    <span className="depth-card__label">{opt.label}</span>
                    <span className="depth-card__desc">{opt.desc}</span>
                    <span className="depth-card__detail">{opt.detail}</span>
                  </button>
                ))}
              </div>
            </fieldset>
            <div className="phase__actions q4-actions">
              <button className="btn btn--ghost" onClick={goBack}>← Back</button>
              <button className="btn btn--primary" onClick={handleDepthNext}>Next</button>
            </div>
          </div>
        )}

        {/* Step 2 — Sensitive topics */}
        {step === 2 && (
          <div className={`q4-step ${enterClass}`} key="topics">
            <p className="q4-prompt">Any topics you'd rather I approach carefully?</p>
            <p className="q4-sub">Optional. You can change this anytime.</p>
            <fieldset className="question-group" aria-label="Sensitive topics">
              <div className="topics-chips">
                {TOPIC_OPTIONS.map((opt) => (
                  <button
                    key={opt.value}
                    className={['topic-chip', topics.includes(opt.value) ? 'topic-chip--selected' : ''].filter(Boolean).join(' ')}
                    onClick={() => toggleTopic(opt.value)}
                    aria-pressed={topics.includes(opt.value)}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </fieldset>
            <div className="phase__actions q4-actions">
              <button className="btn btn--ghost" onClick={goBack}>← Back</button>
              <button className="btn btn--primary" onClick={handleTopicsNext}>Done</button>
            </div>
          </div>
        )}

      </div>
    </section>
  );
}
