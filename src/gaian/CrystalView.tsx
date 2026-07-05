/**
 * CrystalView.tsx
 * Long-press sheet — opens when the user presses and holds the GaianOrb
 * for 600ms.
 *
 * Tab bar:
 *   ◆ Coherence   — existing Ψ score / component bars / narrative (unchanged)
 *   ◆ ClarusLens  — mounts ClarusLensView into a portal div
 *   ◆ AnchorPrism — mounts AnchorPrismView into a portal div
 *   ◆ SomnusVeil  — mounts SomnusVeilView into a portal div
 *   ◆ SovereignCore — mounts SovereignCoreView into a portal div
 *
 * Each crystal tab is LAZY: the View class is instantiated only when that
 * tab is first activated, then kept alive for the session (not re-created
 * on subsequent opens). Tabs call dispose() only when CrystalView itself
 * unmounts.
 *
 * Dismiss gestures:
 *   - Swipe sheet down ≥ 80px  (touch)
 *   - Click backdrop
 *   - Press ✕ button
 *   - Press Escape
 *
 * M2 addition (Issue #756):
 *   Accepts an optional `profile: GAIANProfile` prop.  When provided,
 *   the tab bar filters against profile.activeModules — tabs for modules
 *   not yet active are shown in a locked state (dimmed, not clickable,
 *   aria-disabled) rather than hidden entirely, so the architect always
 *   knows what exists and what is still unlocking.
 *
 *   The coherence tab (Ψ) is always unlocked regardless of activeModules.
 *
 *   When profile is not provided (null/undefined), all tabs are shown
 *   unlocked — identical to the pre-M2 behavior.
 */

import { useEffect, useRef, useState, useCallback, useMemo } from 'react';
import type { CrystalState } from '../hooks/useCrystalCore';
import type { GAIANProfile } from './GAIANProfile';
import { ClarusLensView } from '../crystals/ClarusLens/ClarusLensView';
import { AnchorPrismView } from '../crystals/AnchorPrism/AnchorPrismView';
import { SomnusVeilView } from '../crystals/SomnusVeil/SomnusVeilView';
import { SovereignCoreView } from '../crystals/SovereignCore/SovereignCoreView';
import './crystal-view.css';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type CrystalTab =
  | 'coherence'
  | 'clarus'
  | 'anchor'
  | 'somnus'
  | 'sovereign';

/**
 * Static tab definitions.
 * `moduleKey` maps to the key used in GAIANProfile.activeModules.
 * 'coherence' has no moduleKey — it is always unlocked.
 */
const TABS: { id: CrystalTab; label: string; icon: string; moduleKey?: string }[] = [
  { id: 'coherence', label: 'Coherence',     icon: '\u03a8' },           // always unlocked
  { id: 'clarus',    label: 'ClarusLens',    icon: '\ud83d\udd2d', moduleKey: 'ClarusLens'    },
  { id: 'anchor',    label: 'AnchorPrism',   icon: '\u25c7',      moduleKey: 'AnchorPrism'   },
  { id: 'somnus',    label: 'SomnusVeil',    icon: '\ud83c\udf19', moduleKey: 'SomnusVeil'    },
  { id: 'sovereign', label: 'SovereignCore', icon: '\ud83d\udc51', moduleKey: 'SovereignCore' },
];

interface CrystalViewProps {
  state:       CrystalState | null;
  onClose:     () => void;
  /** Optional: open directly to a specific tab */
  initialTab?: CrystalTab;
  /**
   * M2 — architect profile.  When provided, tab availability is gated
   * by profile.activeModules.  When absent, all tabs are unlocked.
   */
  profile?:    GAIANProfile | null;
}

// Persist active tab across open/close within the session
let _persistedTab: CrystalTab = 'coherence';

// Component weight labels matching the spec
const COMPONENT_META: Record<string, { label: string; weight: number; desc: string }> = {
  affect:   { label: 'Affect',   weight: 0.35, desc: 'Emotional tone and energy' },
  stage:    { label: 'Stage',    weight: 0.30, desc: 'Developmental coherence' },
  shadow:   { label: 'Shadow',   weight: 0.20, desc: 'Unintegrated material' },
  schumann: { label: 'Schumann', weight: 0.15, desc: 'Earth field resonance' },
};

const BAND_EMOJI: Record<string, string> = {
  Fractured:   '\ud83d\udd34',
  Fragmented:  '\ud83d\udfe0',
  Coherent:    '\ud83d\udfe1',
  Resonant:    '\ud83d\udfe2',
  Crystalline: '\u2728',
};

const TONE_COLORS: Record<string, string> = {
  RADIANT:  'crystal-badge--radiant',
  WARM:     'crystal-badge--warm',
  GROUNDED: 'crystal-badge--grounded',
  MEASURED: 'crystal-badge--measured',
  SPARSE:   'crystal-badge--sparse',
};

const SWIPE_THRESHOLD = 80;

// ---------------------------------------------------------------------------
// CrystalView component
// ---------------------------------------------------------------------------

export function CrystalView({ state, onClose, initialTab, profile }: CrystalViewProps) {
  const sheetRef = useRef<HTMLDivElement>(null);
  const [activeTab, setActiveTab] = useState<CrystalTab>(initialTab ?? _persistedTab);

  // Refs to live crystal host divs
  const clarusHostRef    = useRef<HTMLDivElement | null>(null);
  const anchorHostRef    = useRef<HTMLDivElement | null>(null);
  const somnusHostRef    = useRef<HTMLDivElement | null>(null);
  const sovereignHostRef = useRef<HTMLDivElement | null>(null);

  // Refs to lazily-created View instances
  const clarusViewRef    = useRef<ClarusLensView    | null>(null);
  const anchorViewRef    = useRef<AnchorPrismView   | null>(null);
  const somnusViewRef    = useRef<SomnusVeilView    | null>(null);
  const sovereignViewRef = useRef<SovereignCoreView | null>(null);

  // ── M2: derive unlocked tab set from profile.activeModules ─────────────────────
  //
  // unlockedModules is a Set of moduleKey strings that are active.
  // 'coherence' has no moduleKey and is always unlocked.
  // When profile is absent, all modules are treated as unlocked.
  const unlockedModules = useMemo<Set<string>>(() => {
    if (!profile || !profile.activeModules) {
      // No profile — unlock everything (pre-M2 behavior)
      return new Set(TABS.map(t => t.moduleKey ?? ''));
    }
    return new Set(
      Object.entries(profile.activeModules)
        .filter(([, active]) => active)
        .map(([key]) => key)
    );
  }, [profile]);

  /**
   * Returns true when a tab is available for interaction.
   * Coherence is always available.  Others require their moduleKey
   * to be present in unlockedModules.
   */
  const isUnlocked = useCallback((tab: typeof TABS[number]): boolean => {
    if (!tab.moduleKey) return true;  // coherence — always unlocked
    return unlockedModules.has(tab.moduleKey);
  }, [unlockedModules]);

  // If the currently-active tab becomes locked (e.g. profile changes at
  // runtime), fall back to coherence so the UI is never stranded.
  useEffect(() => {
    const currentTabDef = TABS.find(t => t.id === activeTab);
    if (currentTabDef && !isUnlocked(currentTabDef)) {
      setActiveTab('coherence');
      _persistedTab = 'coherence';
    }
  }, [activeTab, isUnlocked]);

  // ── Swipe-to-dismiss ────────────────────────────────────────────────────────
  const [dragY, setDragY]           = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const touchStartY = useRef<number | null>(null);

  const reducedMotion =
    typeof window !== 'undefined'
      ? window.matchMedia('(prefers-reduced-motion: reduce)').matches
      : false;

  const handleTouchStart = (e: React.TouchEvent<HTMLDivElement>) => {
    touchStartY.current = e.touches[0].clientY;
    setIsDragging(false);
    setDragY(0);
  };

  const handleTouchMove = (e: React.TouchEvent<HTMLDivElement>) => {
    if (touchStartY.current === null) return;
    const delta = e.touches[0].clientY - touchStartY.current;
    if (delta <= 0) return;
    setIsDragging(true);
    if (!reducedMotion) setDragY(delta);
  };

  const handleTouchEnd = () => {
    const delta = dragY;
    touchStartY.current = null;
    setIsDragging(false);
    setDragY(0);
    if (delta >= SWIPE_THRESHOLD) onClose();
  };

  // ── Tab switch: persist + lazy-mount crystal views ─────────────────────────
  const handleTabChange = useCallback((tab: CrystalTab, unlocked: boolean) => {
    if (!unlocked) return;   // locked tab — ignore click
    _persistedTab = tab;
    setActiveTab(tab);
  }, []);

  useEffect(() => {
    if (activeTab === 'clarus' && clarusHostRef.current && !clarusViewRef.current) {
      clarusViewRef.current = new ClarusLensView(clarusHostRef.current);
    }
    if (activeTab === 'anchor' && anchorHostRef.current && !anchorViewRef.current) {
      anchorViewRef.current = new AnchorPrismView(anchorHostRef.current);
    }
    if (activeTab === 'somnus' && somnusHostRef.current && !somnusViewRef.current) {
      somnusViewRef.current = new SomnusVeilView(somnusHostRef.current);
    }
    if (activeTab === 'sovereign' && sovereignHostRef.current && !sovereignViewRef.current) {
      sovereignViewRef.current = new SovereignCoreView(sovereignHostRef.current);
    }
  }, [activeTab]);

  // Dispose all crystal views on unmount
  useEffect(() => {
    return () => {
      clarusViewRef.current?.dispose();
      anchorViewRef.current?.dispose();
      somnusViewRef.current?.dispose();
      sovereignViewRef.current?.dispose();
    };
  }, []);

  // ── Focus trap + Escape ──────────────────────────────────────────────────
  useEffect(() => {
    const el = sheetRef.current;
    if (!el) return;
    const focusable = el.querySelectorAll<HTMLElement>(
      'button:not([aria-disabled="true"]), [href], input, textarea, [tabindex]:not([tabindex="-1"])'
    );
    (focusable[0] as HTMLElement | undefined)?.focus();

    const handleKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { onClose(); return; }
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
  }, [onClose, activeTab]);

  // ── Derived coherence values ────────────────────────────────────────────────
  const psi   = state?.psi  ?? 0.5;
  const band  = state?.band ?? 'Coherent';
  const tone  = state?.persona_tone ?? 'GROUNDED';
  const pct   = Math.round(psi * 100);
  const emoji = BAND_EMOJI[band] ?? '\ud83d\udfe1';

  const sheetStyle: React.CSSProperties =
    isDragging && dragY > 0
      ? { transform: `translateY(${dragY}px)`, transition: 'none' }
      : {};

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <>
      {/* Backdrop */}
      <div className="crystal-view__backdrop" onClick={onClose} aria-hidden="true" />

      {/* Sheet */}
      <div
        ref={sheetRef}
        className={`crystal-view${isDragging ? ' crystal-view--dragging' : ''}`}
        style={sheetStyle}
        role="dialog"
        aria-modal="true"
        aria-label="GAIA crystal suite"
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
      >
        {/* Drag handle */}
        <div className="crystal-view__drag-handle" aria-hidden="true" />

        {/* Header */}
        <div className="crystal-view__header">
          <h2 className="crystal-view__title">Crystal Suite</h2>
          <button
            className="crystal-view__close"
            onClick={onClose}
            aria-label="Close crystal suite"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" aria-hidden="true">
              <path d="M18 6 6 18M6 6l12 12"/>
            </svg>
          </button>
        </div>

        {/* Tab bar — M2: locked tabs are dimmed + aria-disabled */}
        <div className="crystal-tabs" role="tablist" aria-label="Crystal panels">
          {TABS.map((tab) => {
            const unlocked = isUnlocked(tab);
            return (
              <button
                key={tab.id}
                className={[
                  'crystal-tab',
                  activeTab === tab.id  ? 'crystal-tab--active' : '',
                  !unlocked            ? 'crystal-tab--locked' : '',
                ].filter(Boolean).join(' ')}
                role="tab"
                aria-selected={activeTab === tab.id}
                aria-controls={`crystal-panel-${tab.id}`}
                aria-disabled={!unlocked || undefined}
                title={!unlocked ? `${tab.label} — not yet active` : undefined}
                onClick={() => handleTabChange(tab.id, unlocked)}
              >
                <span className="crystal-tab__icon" aria-hidden="true">
                  {unlocked ? tab.icon : '\ud83d\udd12'}
                </span>
                <span className="crystal-tab__label">{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* ── Coherence panel (always in DOM, hidden when inactive) ── */}
        <div
          id="crystal-panel-coherence"
          className={`crystal-panel${activeTab === 'coherence' ? ' crystal-panel--active' : ''}`}
          role="tabpanel"
          aria-labelledby="crystal-tab-coherence"
          hidden={activeTab !== 'coherence'}
        >
          {/* Ψ score */}
          <div className="crystal-view__score-row">
            <div className="crystal-view__score"
              aria-label={`Coherence score: ${pct} percent, ${band}`}>
              <span className="crystal-view__psi" aria-hidden="true">Ψ</span>
              <span className="crystal-view__pct">{pct}</span>
              <span className="crystal-view__pct-unit">%</span>
              <span className="crystal-view__band">{emoji} {band}</span>
            </div>
            <span
              className={`crystal-badge ${TONE_COLORS[tone] ?? 'crystal-badge--grounded'}`}
              aria-label={`Persona tone: ${tone}`}
            >
              {tone}
            </span>
          </div>

          {/* Ψ bar */}
          <div className="crystal-view__psi-bar"
            role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
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
                    <span className="crystal-component__weight"
                      aria-label={`weight ${Math.round(meta.weight * 100)} percent`}>
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

          {state?.timestamp && (
            <p className="crystal-view__timestamp">
              Updated{' '}
              <time dateTime={state.timestamp}>
                {new Date(state.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </time>
            </p>
          )}
        </div>

        {/* ── ClarusLens panel ── */}
        <div
          id="crystal-panel-clarus"
          className={`crystal-panel crystal-panel--host${activeTab === 'clarus' ? ' crystal-panel--active' : ''}`}
          role="tabpanel"
          aria-labelledby="crystal-tab-clarus"
          hidden={activeTab !== 'clarus'}
          ref={clarusHostRef}
        />

        {/* ── AnchorPrism panel ── */}
        <div
          id="crystal-panel-anchor"
          className={`crystal-panel crystal-panel--host${activeTab === 'anchor' ? ' crystal-panel--active' : ''}`}
          role="tabpanel"
          aria-labelledby="crystal-tab-anchor"
          hidden={activeTab !== 'anchor'}
          ref={anchorHostRef}
        />

        {/* ── SomnusVeil panel ── */}
        <div
          id="crystal-panel-somnus"
          className={`crystal-panel crystal-panel--host${activeTab === 'somnus' ? ' crystal-panel--active' : ''}`}
          role="tabpanel"
          aria-labelledby="crystal-tab-somnus"
          hidden={activeTab !== 'somnus'}
          ref={somnusHostRef}
        />

        {/* ── SovereignCore panel ── */}
        <div
          id="crystal-panel-sovereign"
          className={`crystal-panel crystal-panel--host${activeTab === 'sovereign' ? ' crystal-panel--active' : ''}`}
          role="tabpanel"
          aria-labelledby="crystal-tab-sovereign"
          hidden={activeTab !== 'sovereign'}
          ref={sovereignHostRef}
        />

      </div>
    </>
  );
}
