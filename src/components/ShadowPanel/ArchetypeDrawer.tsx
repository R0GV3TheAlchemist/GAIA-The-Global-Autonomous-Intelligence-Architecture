/**
 * src/components/ShadowPanel/ArchetypeDrawer.tsx
 * GAIA-OS — Archetype Detail Drawer
 *
 * Slide-in panel that renders the full detail view for a single shadow
 * archetype. Triggered by ShadowPanel.onArchetypeClick.
 *
 * Architecture:
 *   • Renders as a <dialog> (native modal semantics + focus trap).
 *   • Does NOT own shadow data — receives the ShadowRecord as a prop so
 *     it stays in sync with whatever ShadowPanel is already polling.
 *   • Escape key and backdrop click both close the drawer.
 *   • Uses the same CSS custom-property system as shadow-panel.css
 *     (--sp-hue, --sp-dominant, --sp-pct) to stay visually consistent.
 *
 * Props:
 *   archetype  — the archetype currently selected (null = closed)
 *   record     — live ShadowRecord from useShadow (may be null)
 *   onClose    — called when the drawer should close
 *
 * Canon: Shadow Engine — 7-Archetype Integration Layer
 */

import React, {
  useEffect,
  useRef,
  useCallback,
} from 'react';
import type { ShadowRecord } from '../../hooks/useShadow';
import {
  type ShadowArchetypeName,
  ALL_SHADOW_ARCHETYPES,
  ACTIVATION_THRESHOLD,
} from '../../shared/shadowTypes';
import './archetype-drawer.css';

// ── Archetype rich metadata ───────────────────────────────────────────────

const ARCHETYPE_HUES: Record<ShadowArchetypeName, string> = {
  Orphan:    '#7c9ef5',
  Warrior:   '#f55c5c',
  Wanderer:  '#f5c842',
  Caregiver: '#5cf592',
  Seeker:    '#42e8d5',
  Destroyer: '#e07b39',
  Creator:   '#b28aff',
};

const ARCHETYPE_GLYPHS: Record<ShadowArchetypeName, string> = {
  Orphan:    '◯',
  Warrior:   '⚔',
  Wanderer:  '↯',
  Caregiver: '❧',
  Seeker:    '◎',
  Destroyer: '⬙',
  Creator:   '✶',
};

interface ArchetypeMeta {
  shadow:       string;  // the unintegrated wound / core fear
  gift:         string;  // what it offers when integrated
  question:     string;  // the reflective question this archetype asks
  integration:  string;  // one-sentence integration practice
  activation:   string;  // what activated state looks / feels like
  bodyResonance: string; // where this archetype lives in the body
}

const ARCHETYPE_META: Record<ShadowArchetypeName, ArchetypeMeta> = {
  Orphan: {
    shadow:       'Abandonment, the fear that you will always be left behind or that belonging is permanently out of reach.',
    gift:         'Radical resilience and the capacity to find belonging anywhere — the Orphan integrated becomes the ultimate survivor who needs no external validation.',
    question:     'Where in your life are you still waiting to be chosen?',
    integration:  'Practise self-rescue: identify one situation this week where you relied on external rescue and instead act from your own sufficiency.',
    activation:   'Withdrawal, victimhood narratives, excessive self-sufficiency that refuses help, or clinging dependency — both poles arise from the same wound.',
    bodyResonance: 'Solar plexus and throat — a collapsing in the chest, voice that disappears under pressure.',
  },
  Warrior: {
    shadow:       'Domination, the drive to defeat at the cost of relationship — courage weaponised into aggression.',
    gift:         'Disciplined courage, boundary-setting, and the ability to act decisively in service of a value larger than the self.',
    question:     'Who or what are you really fighting for?',
    integration:  'Channel one aggressive impulse this week into a protective act — defend someone else\'s boundary rather than enforcing your own.',
    activation:   'Chronic combativeness, picking fights where none exist, or the opposite: total collapse of will, an inability to assert anything.',
    bodyResonance: 'Jaw, shoulders, and hands — the body armours at the points of action and speech.',
  },
  Wanderer: {
    shadow:       'Chronic flight, the compulsion to leave before arrival — freedom used as an avoidance strategy.',
    gift:         'Visionary independence, the ability to see beyond convention and bring genuinely new perspectives into any system.',
    question:     'What are you refusing to arrive at?',
    integration:  'Stay with one discomfort long enough to find what it contains — set a timer for twenty minutes and do not leave the feeling.',
    activation:   'Restlessness that prevents depth, romanticising departure, or the frozen paralysis of a wanderer who no longer knows where to wander.',
    bodyResonance: 'Feet and lower back — a lightness that becomes groundlessness, a back that aches from carrying paths not yet taken.',
  },
  Caregiver: {
    shadow:       'Martyrdom, care as control — giving in order to never be abandoned, or to avoid one\'s own needs.',
    gift:         'Genuine compassion grounded in sovereignty — the ability to nourish others without depleting the self.',
    question:     'Who takes care of you?',
    integration:  'Receive something today without deflecting it — let a compliment land, accept an offer of help fully.',
    activation:   'Exhaustion-driven resentment, passive-aggressive sacrifice, or the opposite: emotional withdrawal dressed as independence.',
    bodyResonance: 'Heart and arms — a heaviness across the chest, the arms that extend and cannot pull back.',
  },
  Seeker: {
    shadow:       'Infinite dissatisfaction, truth weaponised into perpetual incompleteness — always one insight away from arrival.',
    gift:         'The philosophical clarity that cuts through consensus reality and finds the pattern beneath the pattern.',
    question:     'What if you already have what you\'re looking for?',
    integration:  'Practice knowing: make one decision today without researching it further. Trust the intelligence already accumulated.',
    activation:   'Analysis paralysis, spiritual bypassing, the endless accumulation of frameworks that substitute for lived experience.',
    bodyResonance: 'Third eye and crown — a buzzing above the neck, thoughts that outrun the body.',
  },
  Destroyer: {
    shadow:       'Nihilism, destruction without transformation — the impulse to raze without any vision of what grows from the ashes.',
    gift:         'The power to end what must end — the Destroyer integrated becomes the sacred fire of necessary endings and honest grief.',
    question:     'What are you clinging to that must be released?',
    integration:  'Name one thing that has ended and allow the grief of it — do not replace or reframe it. Let it be gone.',
    activation:   'Self-sabotage, relational detonation, addictive cycles, or frozen inability to change anything at all.',
    bodyResonance: 'Sacrum and gut — a churning below the navel, the body\'s knowledge that something is dying.',
  },
  Creator: {
    shadow:       'Grandiosity and creative narcissism — vision used as escape from the ordinary labour of manifestation.',
    gift:         'Generative presence, the capacity to bring genuinely original form into the world and inspire it in others.',
    question:     'What are you creating that is not for an audience?',
    integration:  'Make something small and imperfect today and do not share it — reclaim creation as private act.',
    activation:   'Perfectionist paralysis, the half-finished project graveyard, or compulsive output without quality or discernment.',
    bodyResonance: 'Throat and hands — voice that aches to speak, hands restless when empty.',
  },
};

const INTENSITY_LABELS: Record<string, string> = {
  dormant:   'Dormant',
  stirring:  'Stirring',
  active:    'Active',
  dominant:  'Dominant',
  consuming: 'Consuming',
};

// ── Props ─────────────────────────────────────────────────────────────────

export interface ArchetypeDrawerProps {
  archetype: ShadowArchetypeName | null;
  record:    ShadowRecord | null;
  onClose:   () => void;
}

// ── Helpers ───────────────────────────────────────────────────────────────

function score(record: ShadowRecord | null, name: ShadowArchetypeName): number {
  return record?.archetype_scores?.[name] ?? 0;
}

function intensityLevel(s: number): string {
  if (s >= 0.85) return 'consuming';
  if (s >= 0.70) return 'dominant';
  if (s >= ACTIVATION_THRESHOLD) return 'active';
  if (s >= 0.15) return 'stirring';
  return 'dormant';
}

// ── Section helper ────────────────────────────────────────────────────────

const Section: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <section className="ad__section">
    <h4 className="ad__section-title">{title}</h4>
    <div className="ad__section-body">{children}</div>
  </section>
);

// ── Comparison bar list ───────────────────────────────────────────────────

function ComparisonBars({
  record,
  selected,
}: {
  record: ShadowRecord | null;
  selected: ShadowArchetypeName;
}) {
  return (
    <ul className="ad__comparison" aria-label="All archetype scores">
      {ALL_SHADOW_ARCHETYPES.map((name) => {
        const pct = Math.round(score(record, name) * 100);
        const hue = ARCHETYPE_HUES[name];
        const isSelected = name === selected;
        return (
          <li
            key={name}
            className={`ad__comparison-row${isSelected ? ' ad__comparison-row--selected' : ''}`}
            style={{ '--sp-hue': hue } as React.CSSProperties}
          >
            <span className="ad__comparison-glyph" aria-hidden>
              {ARCHETYPE_GLYPHS[name]}
            </span>
            <span className="ad__comparison-name">{name}</span>
            <div
              className="ad__comparison-track"
              role="progressbar"
              aria-valuenow={pct}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${name}: ${pct}%`}
            >
              <div
                className="ad__comparison-fill"
                style={{ '--sp-pct': `${pct}%` } as React.CSSProperties}
              />
            </div>
            <span className="ad__comparison-score">{pct}%</span>
          </li>
        );
      })}
    </ul>
  );
}

// ── Component ─────────────────────────────────────────────────────────────

export function ArchetypeDrawer({ archetype, record, onClose }: ArchetypeDrawerProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const isOpen    = archetype !== null;

  // Open / close the native <dialog>
  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    if (isOpen && !el.open) {
      el.showModal();
    } else if (!isOpen && el.open) {
      el.close();
    }
  }, [isOpen]);

  // Escape key is handled natively by <dialog>; sync React state via 'cancel' event
  useEffect(() => {
    const el = dialogRef.current;
    if (!el) return;
    const handler = (e: Event) => { e.preventDefault(); onClose(); };
    el.addEventListener('cancel', handler);
    return () => el.removeEventListener('cancel', handler);
  }, [onClose]);

  // Backdrop click → close
  const handleBackdropClick = useCallback(
    (e: React.MouseEvent<HTMLDialogElement>) => {
      if (e.target === dialogRef.current) onClose();
    },
    [onClose],
  );

  if (!archetype) {
    // Render closed shell — dialog stays in DOM so CSS transitions work
    return (
      <dialog
        ref={dialogRef}
        className="ad ad--closed"
        aria-label="Archetype detail drawer"
        onClick={handleBackdropClick}
      />
    );
  }

  const meta  = ARCHETYPE_META[archetype];
  const hue   = ARCHETYPE_HUES[archetype];
  const glyph = ARCHETYPE_GLYPHS[archetype];
  const s     = score(record, archetype);
  const pct   = Math.round(s * 100);
  const level = intensityLevel(s);
  const activated = s >= ACTIVATION_THRESHOLD;

  return (
    <dialog
      ref={dialogRef}
      className="ad"
      aria-label={`${archetype} archetype detail`}
      style={{ '--sp-hue': hue, '--sp-dominant': hue } as React.CSSProperties}
      onClick={handleBackdropClick}
    >
      <div className="ad__panel" role="document">

        {/* ── Close button ── */}
        <button
          className="ad__close"
          onClick={onClose}
          aria-label="Close archetype drawer"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden>
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>

        {/* ── Identity header ── */}
        <header className="ad__header">
          <span className="ad__glyph" aria-hidden style={{ color: hue }}>{glyph}</span>
          <div className="ad__title-group">
            <h2 className="ad__title">{archetype}</h2>
            <div className="ad__badges">
              <span className={`ad__intensity-badge ad__intensity-badge--${level}`}>
                {INTENSITY_LABELS[level]}
              </span>
              {activated && (
                <span className="ad__activated-badge">▲ Active</span>
              )}
            </div>
          </div>
        </header>

        {/* ── Score bar ── */}
        <div className="ad__score-row">
          <span className="ad__score-label">Score</span>
          <div
            className="ad__score-track"
            role="progressbar"
            aria-valuenow={pct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`${archetype} intensity: ${pct}%`}
          >
            <div
              className="ad__score-fill"
              style={{ '--sp-pct': `${pct}%` } as React.CSSProperties}
            />
            <span
              className="ad__score-threshold"
              style={{ left: `${ACTIVATION_THRESHOLD * 100}%` }}
              title="Activation threshold"
              aria-hidden
            />
          </div>
          <span className="ad__score-value">{pct}%</span>
        </div>

        {/* ── Rich detail sections ── */}
        <div className="ad__content">

          <Section title="The Shadow">
            <p>{meta.shadow}</p>
          </Section>

          <Section title="The Gift">
            <p>{meta.gift}</p>
          </Section>

          <Section title="The Question">
            <blockquote className="ad__blockquote">
              &ldquo;{meta.question}&rdquo;
            </blockquote>
          </Section>

          <Section title="Body Resonance">
            <p>{meta.bodyResonance}</p>
          </Section>

          <Section title="Integration Practice">
            <p className="ad__practice">{meta.integration}</p>
          </Section>

          <Section title="Activated State">
            <p className="ad__activation-note">{meta.activation}</p>
          </Section>

          <Section title="All Archetypes">
            <ComparisonBars record={record} selected={archetype} />
          </Section>

        </div>
      </div>
    </dialog>
  );
}

export default ArchetypeDrawer;
