/**
 * CrystalView.tsx
 * Long-press sheet — opens when the user presses and holds the GaianOrb
 * for 600ms. Shows the live CrystalState: coherence score, band,
 * component bars, GAIA's inner narrative, and persona tone badge.
 *
 * The host (GaianHome or equivalent) is responsible for:
 *   1. Detecting the long-press gesture on the orb container
 *   2. Passing the current CrystalState from useCrystalCore
 *   3. Mounting/unmounting this component
 *
 * Usage:
 *   <CrystalView state={crystalState} onClose={() => setOpen(false)} />
 */

import { useEffect, useRef } from 'react';
import type { CrystalState } from '../hooks/useCrystalCore';
import './crystal-view.css';

interface CrystalViewProps {
  state:   CrystalState | null;
  onClose: () => void;
}

// Component weight labels matching the spec
const COMPONENT_META: Record<string, { label: string; weight: number; desc: string }> = {
  affect:   { label: 'Affect',   weight: 0.35, desc: 'Emotional tone and energy' },
  stage:    { label: 'Stage',    weight: 0.30, desc: 'Developmental coherence' },
  shadow:   { label: 'Shadow',   weight: 0.20, desc: 'Unintegrated material' },
  schumann: { label: 'Schumann', weight: 0.15, desc: 'Earth field resonance' },
};

const BAND_EMOJI: Record<string, string> = {
  Fractured:   '🔴',
  Fragmented:  '🟠',
  Coherent:    '🟡',
  Resonant:    '🟢',
  Crystalline: '✨',
};

const TONE_COLORS: Record<string, string> = {
  RADIANT:  'crystal-badge--radiant',
  WARM:     'crystal-badge--warm',
  GROUNDED: 'crystal-badge--grounded',
  MEASURED: 'crystal-badge--measured',
  SPARSE:   'crystal-badge--sparse',
};

export function CrystalView({ state, onClose }: CrystalViewProps) {
  const sheetRef = useRef<HTMLDivElement>(null);

  // Trap focus inside sheet while open
  useEffect(() => {
    const el = sheetRef.current;
    if (!el) return;
    const focusable = el.querySelectorAll<HTMLElement>(
      'button, [href], input, [tabindex]:not([tabindex="-1"])'
    );
    focusable[0]?.focus();

    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'Tab') {
        const first = focusable[0];
        const last  = focusable[focusable.length - 1];
        if (e.shiftKey && document.activeElement === first) {
          e.preventDefault(); last?.focus();
        } else if (!e.shiftKey && document.activeElement === last) {
          e.preventDefault(); first?.focus();
        }
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [onClose]);

  const psi    = state?.psi  ?? 0.5;
  const band   = state?.band ?? 'Coherent';
  const tone   = state?.persona_tone ?? 'GROUNDED';
  const pct    = Math.round(psi * 100);
  const emoji  = BAND_EMOJI[band] ?? '🟡';

  return (
    <>
      {/* Backdrop */}
      <div
        className="crystal-view__backdrop"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Sheet */}
      <div
        ref={sheetRef}
        className="crystal-view"
        role="dialog"
        aria-modal="true"
        aria-label="GAIA coherence state"
      >
        {/* Header */}
        <div className="crystal-view__header">
          <div className="crystal-view__title-row">
            <span className="crystal-view__emoji" aria-hidden="true">{emoji}</span>
            <h2 className="crystal-view__title">Coherence</h2>
            <span
              className={`crystal-badge ${TONE_COLORS[tone] ?? 'crystal-badge--grounded'}`}
              aria-label={`Persona tone: ${tone}`}
            >
              {tone}
            </span>
          </div>
          <button
            className="crystal-view__close"
            onClick={onClose}
            aria-label="Close coherence view"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M18 6 6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        {/* Ψ score */}
        <div className="crystal-view__score" aria-label={`Coherence score: ${pct} percent, ${band}`}>
          <span className="crystal-view__psi" aria-hidden="true">Ψ</span>
          <span className="crystal-view__pct">{pct}</span>
          <span className="crystal-view__pct-unit">%</span>
          <span className="crystal-view__band">{band}</span>
        </div>

        {/* Ψ bar */}
        <div className="crystal-view__psi-bar" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
          <div className="crystal-view__psi-fill" style={{ width: `${pct}%` }} />
        </div>

        {/* Component bars */}
        <div className="crystal-view__components" aria-label="Coherence components">
          {Object.entries(COMPONENT_META).map(([key, meta]) => {
            const raw  = state?.components?.[key as keyof typeof state.components] ?? 0.5;
            const cpct = Math.round(raw * 100);
            return (
              <div key={key} className="crystal-component">
                <div className="crystal-component__header">
                  <span className="crystal-component__label">{meta.label}</span>
                  <span className="crystal-component__weight" aria-label={`weight ${Math.round(meta.weight * 100)} percent`}>
                    {Math.round(meta.weight * 100)}%
                  </span>
                  <span className="crystal-component__value">{cpct}</span>
                </div>
                <div
                  className="crystal-component__bar"
                  role="progressbar"
                  aria-valuenow={cpct}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${meta.label}: ${cpct}%`}
                >
                  <div
                    className={`crystal-component__fill crystal-component__fill--${key}`}
                    style={{ width: `${cpct}%` }}
                  />
                </div>
                <p className="crystal-component__desc">{meta.desc}</p>
              </div>
            );
          })}
        </div>

        {/* GAIA narrative */}
        {state?.narrative && (
          <div className="crystal-view__narrative">
            <p className="crystal-view__narrative-text">{state.narrative}</p>
          </div>
        )}

        {/* Footer — last updated */}
        {state?.timestamp && (
          <p className="crystal-view__timestamp">
            Updated <time dateTime={state.timestamp}>
              {new Date(state.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </time>
          </p>
        )}
      </div>
    </>
  );
}
