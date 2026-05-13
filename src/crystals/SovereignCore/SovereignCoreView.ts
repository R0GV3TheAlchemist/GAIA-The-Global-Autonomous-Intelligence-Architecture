/**
 * SovereignCoreView
 * Full UI panel for the SovereignCore crystal.
 *
 * Layout:
 *   ┌──────────────────────────────────────┐
 *   │  Sovereign Mode selector (5 modes)   │
 *   │  Mode description                    │
 *   ├──────────────────────────────────────┤
 *   │  Tabs: [Boundaries] [Flags] [Log]    │
 *   ├──────────────────────────────────────┤
 *   │  Active tab content                  │
 *   └──────────────────────────────────────┘
 */

import {
  subscribe,
  setMode,
  addBoundary,
  toggleBoundary,
  removeBoundary,
  toggleFlag,
  getSovereign,
} from './store';
import {
  SOVEREIGN_MODE_ICON,
  SOVEREIGN_MODE_LABEL,
  SOVEREIGN_MODE_DESC,
  BOUNDARY_CATEGORY_ICON,
  type SovereignCoreState,
  type SovereignMode,
  type BoundaryCategory,
  type BoundaryRule,
  type AutonomyFlag,
  type ConsentEvent,
} from './types';

const MODES: SovereignMode[] = ['guardian', 'ally', 'mirror', 'silent', 'sovereign'];
const CATEGORIES: BoundaryCategory[] = ['topic', 'tone', 'behaviour', 'data', 'custom'];

export class SovereignCoreView {
  private _root: HTMLElement;
  private _unsub: (() => void) | null = null;

  private _activeTab: 'boundaries' | 'flags' | 'log' = 'boundaries';

  // Boundary form state
  private _boundaryText = '';
  private _boundaryCategory: BoundaryCategory = 'topic';

  constructor(container: HTMLElement) {
    this._root = document.createElement('div');
    this._root.className = 'sc-panel';
    container.appendChild(this._root);

    this._render(getSovereign());
    this._unsub = subscribe((state) => this._render(state));
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  private _render(state: SovereignCoreState): void {
    const { mode, activeBoundaryCount, enabledFlagCount } = state;

    this._root.innerHTML = /* html */ `
      <!-- Mode Selector -->
      <div class="sc-mode-row" role="group" aria-label="Sovereign mode">
        ${MODES.map((m) => /* html */ `
          <button class="sc-mode-btn ${mode === m ? 'sc-mode-btn--active' : ''}"
            data-mode="${m}" title="${SOVEREIGN_MODE_LABEL[m]}" aria-pressed="${mode === m}">
            <span class="sc-mode-icon">${SOVEREIGN_MODE_ICON[m]}</span>
            <span class="sc-mode-label">${SOVEREIGN_MODE_LABEL[m]}</span>
          </button>`).join('')}
      </div>
      <p class="sc-mode-desc">${_esc(SOVEREIGN_MODE_DESC[mode])}</p>

      <!-- Stats strip -->
      <div class="sc-stats-row">
        <div class="sc-stat">
          <span class="sc-stat-value">${activeBoundaryCount}</span>
          <span class="sc-stat-label">active boundaries</span>
        </div>
        <div class="sc-stat">
          <span class="sc-stat-value">${enabledFlagCount}</span>
          <span class="sc-stat-label">autonomy flags on</span>
        </div>
        <div class="sc-stat">
          <span class="sc-stat-value">${state.consentLog.length}</span>
          <span class="sc-stat-label">consent events</span>
        </div>
      </div>

      <!-- Tabs -->
      <div class="sc-tabs" role="tablist">
        <button class="sc-tab ${this._activeTab === 'boundaries' ? 'sc-tab--active' : ''}"
          data-tab="boundaries" role="tab">🚫 Boundaries
          ${activeBoundaryCount > 0 ? `<span class="sc-badge">${activeBoundaryCount}</span>` : ''}
        </button>
        <button class="sc-tab ${this._activeTab === 'flags' ? 'sc-tab--active' : ''}"
          data-tab="flags" role="tab">⚑ Autonomy Flags</button>
        <button class="sc-tab ${this._activeTab === 'log' ? 'sc-tab--active' : ''}"
          data-tab="log" role="tab">📋 Consent Log</button>
      </div>

      <!-- Tab Content -->
      <div class="sc-tab-content">
        ${
          this._activeTab === 'boundaries'
            ? this._renderBoundariesTab(state)
            : this._activeTab === 'flags'
            ? this._renderFlagsTab(state)
            : this._renderLogTab(state)
        }
      </div>
    `;

    this._bindEvents();
  }

  // -------------------------------------------------------------------------
  // Boundaries tab
  // -------------------------------------------------------------------------

  private _renderBoundariesTab(state: SovereignCoreState): string {
    return /* html */ `
      <form class="sc-form" id="sc-boundary-form" aria-label="Add boundary rule">
        <div class="sc-cat-row">
          ${CATEGORIES.map((c) => /* html */ `
            <button type="button"
              class="sc-cat-btn ${this._boundaryCategory === c ? 'sc-cat-btn--active' : ''}"
              data-cat="${c}" title="${c}">${BOUNDARY_CATEGORY_ICON[c]} ${c}</button>`).join('')}
        </div>
        <div class="sc-form-row">
          <input id="sc-boundary-text" type="text"
            placeholder="Describe this boundary precisely…"
            value="${_esc(this._boundaryText)}"
            class="sc-input sc-input--grow" maxlength="300"/>
          <button type="submit" class="sc-add-btn">Add</button>
        </div>
      </form>

      <div class="sc-boundary-list">
        ${state.boundaries.length === 0
          ? '<p class="sc-empty">No boundaries set. GAIA operates within its default ethical limits.</p>'
          : state.boundaries.map(_boundaryCard).join('')}
      </div>
    `;
  }

  // -------------------------------------------------------------------------
  // Flags tab
  // -------------------------------------------------------------------------

  private _renderFlagsTab(state: SovereignCoreState): string {
    return /* html */ `
      <div class="sc-flag-list">
        ${state.autonomyFlags.map(_flagRow).join('')}
      </div>
    `;
  }

  // -------------------------------------------------------------------------
  // Log tab
  // -------------------------------------------------------------------------

  private _renderLogTab(state: SovereignCoreState): string {
    if (state.consentLog.length === 0) {
      return '<p class="sc-empty">No consent events recorded yet.</p>';
    }
    return /* html */ `
      <div class="sc-log-list">
        ${state.consentLog.slice(0, 50).map(_logRow).join('')}
      </div>
    `;
  }

  // -------------------------------------------------------------------------
  // Event binding
  // -------------------------------------------------------------------------

  private _bindEvents(): void {
    const root = this._root;

    // Mode buttons
    root.querySelectorAll<HTMLButtonElement>('.sc-mode-btn').forEach((btn) => {
      btn.addEventListener('click', () => setMode(btn.dataset.mode as SovereignMode));
    });

    // Tabs
    root.querySelectorAll<HTMLButtonElement>('.sc-tab').forEach((btn) => {
      btn.addEventListener('click', () => {
        this._activeTab = btn.dataset.tab as typeof this._activeTab;
        this._render(getSovereign());
      });
    });

    if (this._activeTab === 'boundaries') this._bindBoundaryForm();
    if (this._activeTab === 'flags') this._bindFlagRows();
  }

  private _bindBoundaryForm(): void {
    const root = this._root;

    // Category selector
    root.querySelectorAll<HTMLButtonElement>('.sc-cat-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        this._boundaryCategory = btn.dataset.cat as BoundaryCategory;
        root.querySelectorAll('.sc-cat-btn').forEach((b) =>
          b.classList.toggle('sc-cat-btn--active', b === btn),
        );
      });
    });

    root.querySelector<HTMLInputElement>('#sc-boundary-text')?.addEventListener('input', (e) => {
      this._boundaryText = (e.target as HTMLInputElement).value;
    });

    root.querySelector<HTMLFormElement>('#sc-boundary-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = this._boundaryText.trim();
      if (!text) return;
      addBoundary(text, this._boundaryCategory);
      this._boundaryText = '';
    });

    // Toggle / remove buttons on existing cards
    root.querySelectorAll<HTMLButtonElement>('.sc-boundary-toggle').forEach((btn) => {
      btn.addEventListener('click', () => toggleBoundary(btn.dataset.id!));
    });
    root.querySelectorAll<HTMLButtonElement>('.sc-boundary-remove').forEach((btn) => {
      btn.addEventListener('click', () => removeBoundary(btn.dataset.id!));
    });
  }

  private _bindFlagRows(): void {
    this._root.querySelectorAll<HTMLInputElement>('.sc-flag-toggle').forEach((input) => {
      input.addEventListener('change', () => toggleFlag(input.dataset.id!));
    });
  }

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  dispose(): void {
    this._unsub?.();
    this._root.remove();
  }
}

// ---------------------------------------------------------------------------
// Pure render helpers
// ---------------------------------------------------------------------------

function _boundaryCard(rule: BoundaryRule): string {
  return /* html */ `
    <div class="sc-boundary-card ${rule.active ? '' : 'sc-boundary-card--paused'}">
      <span class="sc-boundary-cat-icon" title="${rule.category}">
        ${BOUNDARY_CATEGORY_ICON[rule.category]}
      </span>
      <span class="sc-boundary-text">${_esc(rule.text)}</span>
      <div class="sc-boundary-actions">
        <button class="sc-boundary-toggle sc-icon-btn"
          data-id="${rule.id}"
          title="${rule.active ? 'Pause boundary' : 'Activate boundary'}"
          aria-label="${rule.active ? 'Pause' : 'Activate'}">
          ${rule.active ? '⏸' : '▶'}
        </button>
        <button class="sc-boundary-remove sc-icon-btn sc-icon-btn--danger"
          data-id="${rule.id}" title="Remove boundary" aria-label="Remove">✕</button>
      </div>
    </div>
  `;
}

function _flagRow(flag: AutonomyFlag): string {
  return /* html */ `
    <label class="sc-flag-row">
      <div class="sc-flag-info">
        <span class="sc-flag-label">${_esc(flag.label)}</span>
        <span class="sc-flag-desc">${_esc(flag.description)}</span>
      </div>
      <div class="sc-toggle-wrap">
        <input type="checkbox" class="sc-flag-toggle sr-only"
          data-id="${flag.id}" ${flag.enabled ? 'checked' : ''}
          aria-label="${_esc(flag.label)}"/>
        <span class="sc-toggle ${flag.enabled ? 'sc-toggle--on' : ''}" aria-hidden="true"></span>
      </div>
    </label>
  `;
}

function _logRow(event: ConsentEvent): string {
  const d = new Date(event.timestamp);
  const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const date = d.toLocaleDateString([], { month: 'short', day: 'numeric' });
  return /* html */ `
    <div class="sc-log-row">
      <span class="sc-log-type sc-log-type--${event.type.replace('_', '-')}">${_logTypeLabel(event.type)}</span>
      <span class="sc-log-summary">${_esc(event.summary)}</span>
      <span class="sc-log-time">${date} ${time}</span>
    </div>
  `;
}

function _logTypeLabel(type: string): string {
  const map: Record<string, string> = {
    mode_change:       'MODE',
    boundary_added:    'ADDED',
    boundary_toggled:  'TOGGLED',
    boundary_removed:  'REMOVED',
    flag_toggled:      'FLAG',
  };
  return map[type] ?? type.toUpperCase();
}

function _esc(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
