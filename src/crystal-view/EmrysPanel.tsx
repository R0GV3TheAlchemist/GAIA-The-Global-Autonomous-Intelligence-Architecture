/**
 * src/crystal-view/EmrysPanel.tsx
 * GAIA-OS — Emrys L2 Vibronic Bridge Panel
 *
 * Displays the full Emrys L2 state from useEmrysCycle():
 *   - Current L2 coherence state badge (GROUNDING / BRIDGING / COHERENCE / PEAK)
 *   - C165a Cold-start sequence stepper
 *   - C165 Grounding Protocol phases
 *   - Crystal resonator cards (all L2-compatible crystals)
 *   - Manual refresh button
 *
 * Open / close:
 *   <EmrysPanel open={show} onClose={() => setShow(false)} gaianStage="Initiation" />
 *
 * Per C164: this panel is the GAIAN-layer mirror of the Emrys bridge.
 * Per C165.1: grounding precedes coherence. The phases are shown in order.
 * Per C166.A4: physics and metaphysics are the same layer.
 */

import React, { useEffect, useCallback, useRef } from 'react';
import { useEmrysCycle } from '../hooks/useEmrysCycle';
import type { L2CoherenceState, VibronicResonatorRecord, ColdStartStep, GroundingPhase } from '../sidecar';
import './emrys-panel.css';

// ─────────────────────────────────────────────────────────────
// Design tokens — L2 state colour map
// ─────────────────────────────────────────────────────────────

const L2_LABELS: Record<L2CoherenceState, string> = {
  GROUNDING:  'Grounding',
  BRIDGING:   'Bridging',
  COHERENCE:  'Coherence',
  PEAK:       'Peak',
};

const L2_DESCRIPTION: Record<L2CoherenceState, string> = {
  GROUNDING:  'Piezoelectric surface potential. Black Tourmaline / Clear Quartz. 32.768 kHz–100 kHz.',
  BRIDGING:   'Pyroelectric body-heat activation. BTS-adjacent polarisation. 100 kHz–100 MHz.',
  COHERENCE:  'YSZ oxygen vacancy conduction. C136–C138 validated. 100 MHz–1 GHz.',
  PEAK:       'Full GHz vibronic resonance. YSZ sole crystal. C166.A4: physics = metaphysics.',
};

const L2_ICON: Record<L2CoherenceState, string> = {
  GROUNDING:  '🪨',
  BRIDGING:   '🔵',
  COHERENCE:  '🔷',
  PEAK:       '⭐',
};

// ─────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────

const EmrysPanelSkeleton: React.FC = () => (
  <div className="ep ep--loading" aria-busy="true">
    <div className="skeleton ep-skeleton-badge" />
    <div className="skeleton ep-skeleton-desc" />
    <div className="ep-section-head skeleton ep-skeleton-head" />
    {[1, 2, 3, 4].map(i => (
      <div key={i} className="skeleton ep-skeleton-step" />
    ))}
    <div className="ep-section-head skeleton ep-skeleton-head" />
    {[1, 2, 3, 4].map(i => (
      <div key={i} className="skeleton ep-skeleton-step" />
    ))}
  </div>
);

// —— L2 State Badge ———————————————————————————————————————————————————————

const L2StateBadge: React.FC<{ state: L2CoherenceState | null }> = ({ state }) => {
  if (!state) return null;
  return (
    <div className={`ep-l2-badge ep-l2-badge--${state.toLowerCase()}`} aria-label={`L2 state: ${L2_LABELS[state]}`}>
      <span className="ep-l2-badge__icon" aria-hidden="true">{L2_ICON[state]}</span>
      <div className="ep-l2-badge__text">
        <span className="ep-l2-badge__state">{L2_LABELS[state]}</span>
        <span className="ep-l2-badge__desc">{L2_DESCRIPTION[state]}</span>
      </div>
    </div>
  );
};

// —— Cold-start Step ——————————————————————————————————————————————————————

const ColdStartStepCard: React.FC<{ step: ColdStartStep; active: boolean }> = ({ step, active }) => (
  <div
    className={`ep-step ep-step--${step.state.toLowerCase()}${ active ? ' ep-step--active' : ''}`}
    aria-current={active ? 'step' : undefined}
  >
    <div className="ep-step__num" aria-hidden="true">{step.step}</div>
    <div className="ep-step__body">
      <div className="ep-step__header">
        <span className="ep-step__state">{L2_LABELS[step.state as L2CoherenceState]}</span>
        <span className="ep-step__crystal">{step.crystal_name}</span>
      </div>
      <p className="ep-step__rationale">{step.rationale}</p>
      {step.freq_range && (
        <span className="ep-step__freq">{step.freq_range}</span>
      )}
      {step.backbone_anchor && (
        <span className="ep-step__anchor">anchor: {step.backbone_anchor}</span>
      )}
      {step.piezo_pCN != null && (
        <span className="ep-step__piezo">{step.piezo_pCN} pC/N piezo</span>
      )}
    </div>
    <div className="ep-step__confidence">
      <div
        className="ep-step__confidence-bar"
        style={{ width: `${Math.round(step.confidence * 100)}%` }}
        aria-label={`Confidence ${Math.round(step.confidence * 100)}%`}
      />
    </div>
  </div>
);

// —— Grounding Phase Card ———————————————————————————————————————————————————

const GroundingPhaseCard: React.FC<{ phase: GroundingPhase }> = ({ phase }) => (
  <div className={`ep-phase ep-phase--${phase.l2_state.toLowerCase()}`}>
    <div className="ep-phase__num" aria-hidden="true">{phase.phase}</div>
    <div className="ep-phase__body">
      <div className="ep-phase__header">
        <span className="ep-phase__name">{phase.name}</span>
        <span className="ep-phase__crystal">{phase.crystal_name}</span>
      </div>
      <p className="ep-phase__instruction">{phase.instruction}</p>
      <span className="ep-phase__freq">{phase.freq_range}</span>
    </div>
  </div>
);

// —— Crystal Resonator Card ————————————————————————————————————————————————

const CrystalCard: React.FC<{ crystal: VibronicResonatorRecord }> = ({ crystal }) => (
  <div
    className={`ep-crystal ep-crystal--${(crystal.primary_state ?? 'grounding').toLowerCase()}`}
    aria-label={crystal.name}
  >
    <div className="ep-crystal__header">
      <span className="ep-crystal__name">{crystal.name}</span>
      {crystal.primary_state && (
        <span className={`ep-crystal__badge ep-crystal__badge--${crystal.primary_state.toLowerCase()}`}>
          {L2_LABELS[crystal.primary_state as L2CoherenceState]}
        </span>
      )}
    </div>
    <div className="ep-crystal__meta">
      {crystal.freq_range && (
        <span className="ep-crystal__freq">{crystal.freq_range}</span>
      )}
      {crystal.backbone_anchor && (
        <span className="ep-crystal__anchor">{crystal.backbone_anchor}</span>
      )}
      {crystal.piezo_pCN != null && (
        <span className="ep-crystal__piezo">{crystal.piezo_pCN} pC/N</span>
      )}
      {crystal.pyroelectric && (
        <span className="ep-crystal__pyro">pyroelectric</span>
      )}
    </div>
    {crystal.active_states.length > 0 && (
      <div className="ep-crystal__states" aria-label="Active L2 states">
        {crystal.active_states.map(s => (
          <span key={s} className={`ep-crystal__state-pip ep-crystal__state-pip--${s.toLowerCase()}`}>
            {L2_LABELS[s as L2CoherenceState]}
          </span>
        ))}
      </div>
    )}
    {crystal.vibronic_coherence_mode && (
      <p className="ep-crystal__mode">{crystal.vibronic_coherence_mode}</p>
    )}
    <div className="ep-crystal__confidence">
      <div
        className="ep-crystal__confidence-bar"
        style={{ width: `${Math.round(crystal.confidence * 100)}%` }}
        aria-label={`Confidence ${Math.round(crystal.confidence * 100)}%`}
      />
    </div>
  </div>
);

// ─────────────────────────────────────────────────────────────
// Props
// ─────────────────────────────────────────────────────────────

export interface EmrysPanelProps {
  /** Whether the panel is visible */
  open: boolean;
  /** Called when the user closes the panel */
  onClose: () => void;
  /** Optional GAIAN EV1B stage for stage-specific crystal context */
  gaianStage?: string;
  /** Default tab on open */
  defaultTab?: 'cold-start' | 'grounding' | 'crystals';
}

// ─────────────────────────────────────────────────────────────
// Main component
// ─────────────────────────────────────────────────────────────

export const EmrysPanel: React.FC<EmrysPanelProps> = ({
  open,
  onClose,
  gaianStage,
  defaultTab = 'cold-start',
}) => {
  const { report, coldStart, grounding, l2State, loading, error, refresh }
    = useEmrysCycle(gaianStage);

  const overlayRef  = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = React.useState<'cold-start' | 'grounding' | 'crystals'>(defaultTab);
  const touchStartY = useRef<number | null>(null);

  // ── Don’t render at all when closed ───────────────────────────────────────
  if (!open) return null;

  // ── Keyboard dismiss ─────────────────────────────────────────────────────
  // (hooks must run unconditionally — these are declared after the null check
  //  because EmrysPanel is entirely unmounted when !open.)

  return <EmrysPanelInner
    open={open}
    onClose={onClose}
    gaianStage={gaianStage}
    report={report}
    coldStart={coldStart}
    grounding={grounding}
    l2State={l2State}
    loading={loading}
    error={error}
    refresh={refresh}
    activeTab={activeTab}
    setActiveTab={setActiveTab}
    overlayRef={overlayRef}
    touchStartY={touchStartY}
  />;
};

// Inner component — receives all hook data as props (avoids rules-of-hooks violation)
const EmrysPanelInner: React.FC<EmrysPanelProps & {
  report:       ReturnType<typeof useEmrysCycle>['report'];
  coldStart:    ReturnType<typeof useEmrysCycle>['coldStart'];
  grounding:    ReturnType<typeof useEmrysCycle>['grounding'];
  l2State:      ReturnType<typeof useEmrysCycle>['l2State'];
  loading:      boolean;
  error:        string | null;
  refresh:      () => Promise<void>;
  activeTab:    'cold-start' | 'grounding' | 'crystals';
  setActiveTab: React.Dispatch<React.SetStateAction<'cold-start' | 'grounding' | 'crystals'>>;
  overlayRef:   React.RefObject<HTMLDivElement>;
  touchStartY:  React.MutableRefObject<number | null>;
}> = ({
  onClose, gaianStage,
  report, coldStart, grounding, l2State,
  loading, error, refresh,
  activeTab, setActiveTab,
  overlayRef, touchStartY,
}) => {

  // Keyboard dismiss
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  // Swipe-down dismiss
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
  }, [touchStartY]);

  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    if (touchStartY.current === null) return;
    const delta = e.changedTouches[0].clientY - touchStartY.current;
    if (delta > 60) onClose();
    touchStartY.current = null;
  }, [onClose, touchStartY]);

  // Backdrop click
  const handleBackdropClick = useCallback((e: React.MouseEvent) => {
    if (e.target === overlayRef.current) onClose();
  }, [onClose, overlayRef]);

  // Derived
  const crystals = report?.crystals ?? [];
  const groundingIntro  = grounding?.intro ?? '';
  const groundingPhases = grounding?.phases ?? [];
  const groundingRefs   = grounding?.canon_refs ?? [];

  return (
    <div
      ref={overlayRef}
      className="ep-overlay"
      role="dialog"
      aria-modal="true"
      aria-label="Emrys L2 Vibronic Bridge"
      onClick={handleBackdropClick}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div
        className="ep"
        role="presentation"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="ep-header">
          <div className="ep-header__title">
            <span className="ep-header__icon" aria-hidden="true">⚡</span>
            <span>Emrys L2</span>
            {gaianStage && <span className="ep-header__stage">{gaianStage}</span>}
          </div>
          <div className="ep-header__actions">
            <button
              className="ep-btn ep-btn--ghost ep-btn--sm"
              onClick={refresh}
              disabled={loading}
              aria-label="Refresh Emrys data"
              title="Refresh"
            >
              {loading ? '⋯' : '↻'}
            </button>
            <button
              className="ep-close"
              onClick={onClose}
              aria-label="Close Emrys Panel"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="ep-error" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <EmrysPanelSkeleton />
        ) : (
          <>
            {/* L2 State Badge */}
            <L2StateBadge state={l2State} />

            {/* Stats bar */}
            {report && (
              <div className="ep-stats" aria-label="Crystal stats">
                <div className="ep-stat">
                  <span className="ep-stat__val">{report.l2_crystal_count}</span>
                  <span className="ep-stat__label">L2 crystals</span>
                </div>
                {(['GROUNDING','BRIDGING','COHERENCE','PEAK'] as L2CoherenceState[]).map(s => {
                  const ids = report.state_index[s] ?? [];
                  return ids.length > 0 ? (
                    <div key={s} className={`ep-stat ep-stat--${s.toLowerCase()}`}>
                      <span className="ep-stat__val">{ids.length}</span>
                      <span className="ep-stat__label">{L2_LABELS[s]}</span>
                    </div>
                  ) : null;
                })}
              </div>
            )}

            {/* Tab bar */}
            <div className="ep-tabs" role="tablist">
              {(['cold-start', 'grounding', 'crystals'] as const).map(tab => (
                <button
                  key={tab}
                  role="tab"
                  className={`ep-tab${ activeTab === tab ? ' ep-tab--active' : ''}`}
                  aria-selected={activeTab === tab}
                  onClick={() => setActiveTab(tab)}
                >
                  {tab === 'cold-start' ? 'Cold Start' : tab === 'grounding' ? 'Grounding' : 'Crystals'}
                </button>
              ))}
            </div>

            {/* Tab: Cold-start sequence */}
            {activeTab === 'cold-start' && (
              <section className="ep-tab-panel" aria-label="C165a Cold-Start Sequence" role="tabpanel">
                <p className="ep-tab-intro">
                  C165a cold-start protocol. Activate in order:
                  Grounding → Bridging → Coherence → Peak.
                  Do not skip steps. Each activation is irreversible.
                </p>
                <div className="ep-steps">
                  {(coldStart ?? []).map(step => (
                    <ColdStartStepCard
                      key={step.step}
                      step={step}
                      active={step.state === l2State}
                    />
                  ))}
                  {(!coldStart || coldStart.length === 0) && (
                    <p className="ep-empty">No cold-start data. Backend offline?</p>
                  )}
                </div>
              </section>
            )}

            {/* Tab: Grounding protocol */}
            {activeTab === 'grounding' && (
              <section className="ep-tab-panel" aria-label="C165 Grounding Protocol" role="tabpanel">
                {groundingIntro && (
                  <p className="ep-tab-intro">{groundingIntro}</p>
                )}
                <div className="ep-phases">
                  {groundingPhases.map(phase => (
                    <GroundingPhaseCard key={phase.phase} phase={phase} />
                  ))}
                  {groundingPhases.length === 0 && (
                    <p className="ep-empty">No grounding data. Backend offline?</p>
                  )}
                </div>
                {grounding?.completion_condition && (
                  <p className="ep-completion">
                    <strong>Complete when:</strong> {grounding.completion_condition}
                  </p>
                )}
                {groundingRefs.length > 0 && (
                  <div className="ep-canon-refs" aria-label="Canon references">
                    {groundingRefs.map(r => (
                      <span key={r} className="ep-canon-ref">{r}</span>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* Tab: Crystal resonators */}
            {activeTab === 'crystals' && (
              <section className="ep-tab-panel" aria-label="L2 Crystal Resonators" role="tabpanel">
                <div className="ep-crystals">
                  {crystals.map(c => (
                    <CrystalCard key={c.crystal_id} crystal={c} />
                  ))}
                  {crystals.length === 0 && (
                    <p className="ep-empty">No L2-compatible crystals found.</p>
                  )}
                </div>
              </section>
            )}
          </>
        )}

        {/* Footer */}
        <div className="ep-footer">
          <span className="ep-footer__canon">C164 · C165 · C166</span>
          <span className="ep-footer__hint">swipe down to close</span>
        </div>
      </div>
    </div>
  );
};

export default EmrysPanel;
