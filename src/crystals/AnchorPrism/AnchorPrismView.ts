/**
 * AnchorPrismView
 * Full UI panel for the AnchorPrism crystal.
 *
 * Layout:
 *   ┌──────────────────────────────────────┐
 *   │  Grounding score bar  │  score label │
 *   ├──────────────────────────────────────┤
 *   │  Category filter chips               │
 *   ├──────────────────────────────────────┤
 *   │  Anchor cards (sorted by strength)   │
 *   ├──────────────────────────────────────┤
 *   │  Add anchor form                     │
 *   └──────────────────────────────────────┘
 */

import {
  subscribe,
  addAnchor,
  reinforceAnchor,
  archiveAnchor,
  getAnchors,
} from './store';
import {
  CATEGORY_ICON,
  CATEGORY_LABEL,
  DECAY_DORMANT_THRESHOLD,
  type Anchor,
  type AnchorCategory,
  type AnchorPrismState,
} from './types';

const ALL_CATEGORIES: AnchorCategory[] = [
  'value', 'belief', 'commitment', 'boundary', 'aspiration',
];

export class AnchorPrismView {
  private _root: HTMLElement;
  private _unsub: (() => void) | null = null;

  // Filter / form state
  private _activeFilter: AnchorCategory | null = null;
  private _formText = '';
  private _formCategory: AnchorCategory = 'value';
  private _formNote = '';
  private _showArchived = false;

  constructor(container: HTMLElement) {
    this._root = document.createElement('div');
    this._root.className = 'ap-panel';
    container.appendChild(this._root);

    this._render(getAnchors());
    this._unsub = subscribe((state) => this._render(state));
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  private _render(state: AnchorPrismState): void {
    const { anchors, archived, groundingScore } = state;
    const pct = Math.round((groundingScore / 10) * 100);
    const groundingAccent = _groundingAccent(groundingScore);
    const groundingLabel = _groundingLabel(groundingScore);

    const filtered = this._activeFilter
      ? anchors.filter((a) => a.category === this._activeFilter)
      : anchors;

    this._root.innerHTML = /* html */ `
      <!-- Grounding Score -->
      <div class="ap-grounding-wrap">
        <div class="ap-grounding-bar">
          <div class="ap-grounding-fill"
            style="width:${pct}%; background:${groundingAccent}"></div>
        </div>
        <div class="ap-grounding-meta">
          <span class="ap-grounding-label" style="color:${groundingAccent}">${groundingLabel}</span>
          <span class="ap-grounding-score">${groundingScore.toFixed(1)} / 10</span>
        </div>
      </div>

      <!-- Category Filter -->
      <div class="ap-filter-row">
        <button class="ap-filter-chip ${!this._activeFilter ? 'ap-filter-chip--active' : ''}"
          data-filter="all">All</button>
        ${ALL_CATEGORIES.map(cat => /* html */ `
          <button class="ap-filter-chip ${this._activeFilter === cat ? 'ap-filter-chip--active' : ''}"
            data-filter="${cat}">
            ${CATEGORY_ICON[cat]} ${CATEGORY_LABEL[cat]}
          </button>`).join('')}
      </div>

      <!-- Anchor Cards -->
      <div class="ap-anchor-list" aria-label="Anchors">
        ${filtered.length > 0
          ? filtered.map((a) => _anchorCard(a)).join('')
          : /* html */ `<p class="ap-empty">No ${this._activeFilter ? CATEGORY_LABEL[this._activeFilter].toLowerCase() + ' ' : ''}anchors yet. Add one below.</p>`
        }
      </div>

      <!-- Add Anchor Form -->
      <form class="ap-add-form" aria-label="Add anchor">
        <div class="ap-form-category-row">
          ${ALL_CATEGORIES.map(cat => /* html */ `
            <button type="button"
              class="ap-cat-btn ${this._formCategory === cat ? 'ap-cat-btn--active' : ''}"
              data-cat="${cat}" title="${CATEGORY_LABEL[cat]}">
              ${CATEGORY_ICON[cat]}
            </button>`).join('')}
        </div>
        <div class="ap-form-input-row">
          <input id="ap-anchor-text" type="text"
            placeholder="${_placeholder(this._formCategory)}"
            value="${_esc(this._formText)}"
            class="ap-text-input" maxlength="280" autocomplete="off"/>
          <button type="submit" class="ap-add-btn">Anchor</button>
        </div>
        <input id="ap-anchor-note" type="text"
          placeholder="Optional note…"
          value="${_esc(this._formNote)}"
          class="ap-text-input ap-text-input--note" maxlength="200" autocomplete="off"/>
      </form>

      <!-- Archived toggle -->
      ${archived.length > 0 ? /* html */ `
        <button class="ap-archived-toggle" id="ap-archived-toggle">
          ${this._showArchived ? '▲ Hide' : '▼ Show'} ${archived.length} archived anchor${archived.length !== 1 ? 's' : ''}
        </button>
        ${this._showArchived ? /* html */ `
          <div class="ap-archived-list">
            ${archived.map((a) => _anchorCard(a, true)).join('')}
          </div>` : ''}
      ` : ''}
    `;

    this._bindEvents();
  }

  // -------------------------------------------------------------------------
  // Event binding
  // -------------------------------------------------------------------------

  private _bindEvents(): void {
    const root = this._root;

    // Category filter
    root.querySelectorAll<HTMLButtonElement>('.ap-filter-chip').forEach((btn) => {
      btn.addEventListener('click', () => {
        const f = btn.dataset.filter!;
        this._activeFilter = f === 'all' ? null : f as AnchorCategory;
        // Re-render via store snapshot
        this._render(getAnchors());
      });
    });

    // Form category selector
    root.querySelectorAll<HTMLButtonElement>('.ap-cat-btn').forEach((btn) => {
      btn.addEventListener('click', () => {
        this._formCategory = btn.dataset.cat as AnchorCategory;
        const input = root.querySelector<HTMLInputElement>('#ap-anchor-text');
        if (input) input.placeholder = _placeholder(this._formCategory);
        root.querySelectorAll('.ap-cat-btn').forEach((b) =>
          b.classList.toggle('ap-cat-btn--active', b === btn),
        );
      });
    });

    // Form text input
    root.querySelector<HTMLInputElement>('#ap-anchor-text')?.addEventListener('input', (e) => {
      this._formText = (e.target as HTMLInputElement).value;
    });

    root.querySelector<HTMLInputElement>('#ap-anchor-note')?.addEventListener('input', (e) => {
      this._formNote = (e.target as HTMLInputElement).value;
    });

    // Add form submit
    root.querySelector<HTMLFormElement>('.ap-add-form')?.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = this._formText.trim();
      if (!text) return;
      addAnchor(text, this._formCategory, this._formNote);
      this._formText = '';
      this._formNote = '';
    });

    // Reinforce buttons
    root.querySelectorAll<HTMLButtonElement>('[data-reinforce-id]').forEach((btn) => {
      btn.addEventListener('click', () => reinforceAnchor(btn.dataset.reinforceId!));
    });

    // Archive buttons
    root.querySelectorAll<HTMLButtonElement>('[data-archive-id]').forEach((btn) => {
      btn.addEventListener('click', () => archiveAnchor(btn.dataset.archiveId!));
    });

    // Archived toggle
    root.querySelector('#ap-archived-toggle')?.addEventListener('click', () => {
      this._showArchived = !this._showArchived;
      this._render(getAnchors());
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
// Pure helpers
// ---------------------------------------------------------------------------

function _anchorCard(anchor: Anchor, archived = false): string {
  const pct = Math.round(anchor.strength * 100);
  const isDormant = anchor.strength < DECAY_DORMANT_THRESHOLD;
  const strengthColor = anchor.strength > 0.65
    ? 'var(--color-success)'
    : anchor.strength > 0.35
    ? 'var(--color-primary)'
    : 'var(--color-warning)';

  return /* html */ `
    <div class="ap-anchor-card ${isDormant ? 'ap-anchor-card--dormant' : ''} ${archived ? 'ap-anchor-card--archived' : ''}">
      <div class="ap-anchor-top">
        <span class="ap-anchor-icon" title="${CATEGORY_LABEL[anchor.category]}">
          ${CATEGORY_ICON[anchor.category]}
        </span>
        <span class="ap-anchor-text">${_esc(anchor.text)}</span>
        <div class="ap-anchor-actions">
          ${!archived ? /* html */ `
            <button class="ap-action-btn ap-action-btn--reinforce"
              data-reinforce-id="${anchor.id}" title="Reinforce this anchor">
              ↺ Hold
            </button>
            <button class="ap-action-btn ap-action-btn--archive"
              data-archive-id="${anchor.id}" title="Archive this anchor">
              ✕
            </button>` : ''}
        </div>
      </div>
      ${anchor.note ? `<p class="ap-anchor-note">${_esc(anchor.note)}</p>` : ''}
      <div class="ap-decay-bar">
        <div class="ap-decay-fill" style="width:${pct}%; background:${strengthColor}"></div>
      </div>
      <div class="ap-anchor-meta">
        <span>${pct}% strength</span>
        <span>${anchor.reinforceCount}× reinforced</span>
      </div>
    </div>
  `;
}

function _groundingAccent(score: number): string {
  if (score >= 7.5) return 'var(--color-success)';
  if (score >= 5.0) return 'var(--color-primary)';
  if (score >= 2.5) return 'var(--color-warning)';
  return 'var(--color-error)';
}

function _groundingLabel(score: number): string {
  if (score >= 7.5) return '⬡ Deeply Rooted';
  if (score >= 5.0) return '◈ Grounded';
  if (score >= 2.5) return '◆ Drifting';
  return '◉ Unmoored';
}

function _placeholder(cat: AnchorCategory): string {
  const map: Record<AnchorCategory, string> = {
    value:      'A core value you hold…',
    belief:     'Something you believe to be true…',
    commitment: 'A commitment you\'ve made…',
    boundary:   'A line you won\'t cross…',
    aspiration: 'Something you\'re reaching toward…',
  };
  return map[cat];
}

function _esc(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
