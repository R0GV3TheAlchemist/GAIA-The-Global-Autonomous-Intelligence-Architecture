/**
 * ClarusLensView
 * Full UI panel for the ClarusLens crystal.
 *
 * Layout:
 *   ┌──────────────────────────────────────┐
 *   │  Clarity meter bar  │  Score + label │
 *   ├──────────────────────────────────────┤
 *   │  Active intention card (or prompt)  │
 *   ├──────────────────────────────────────┤
 *   │  Set intention form                 │
 *   ├──────────────────────────────────────┤
 *   │  Focus areas chip grid              │
 *   ├──────────────────────────────────────┤
 *   │  Intention history list             │
 *   └──────────────────────────────────────┘
 */

import { subscribe, setIntention, completeIntention, addFocusArea, setFocusAreaStatus, getCurrentFocus } from './store';
import { clarityLabel, clarityAccent, type ClarusLensState, type FocusArea, type Intention } from './types';

export class ClarusLensView {
  private _root: HTMLElement;
  private _unsub: (() => void) | null = null;

  // Form state
  private _intentionText = '';
  private _selectedAreaId: string | null = null;
  private _newAreaText = '';

  constructor(container: HTMLElement) {
    this._root = document.createElement('div');
    this._root.className = 'cl-panel';
    container.appendChild(this._root);

    this._render(getCurrentFocus());
    this._unsub = subscribe((state) => this._render(state));
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  private _render(state: ClarusLensState): void {
    const { clarity, currentIntention, focusAreas, intentions } = state;
    const accent = clarityAccent(clarity.total);
    const label = clarityLabel(clarity.total);
    const pct = Math.round((clarity.total / 10) * 100);

    this._root.innerHTML = /* html */ `
      <!-- Clarity Meter -->
      <div class="cl-clarity-bar-wrap">
        <div class="cl-clarity-bar">
          <div class="cl-clarity-fill" style="width:${pct}%; background:${accent}"></div>
        </div>
        <div class="cl-clarity-meta">
          <span class="cl-clarity-label" style="color:${accent}">${label}</span>
          <span class="cl-clarity-score">${clarity.total.toFixed(1)} / 10</span>
        </div>
        <div class="cl-clarity-breakdown">
          <span title="Recency of last intention">⏱ ${clarity.recency.toFixed(1)}</span>
          <span title="Focus balance (1–3 active areas ideal)">⊕ ${clarity.focusBalance.toFixed(1)}</span>
          <span title="Follow-through rate">✓ ${clarity.followThrough.toFixed(1)}</span>
        </div>
      </div>

      <!-- Current Intention -->
      <div class="cl-intention-card">
        ${currentIntention
          ? /* html */ `
            <div class="cl-intention-active">
              <span class="cl-intention-icon" style="color:${accent}">◈</span>
              <span class="cl-intention-text">${_esc(currentIntention.text)}</span>
              <button class="cl-complete-btn" data-id="${currentIntention.id}"
                aria-label="Mark intention complete">✓ Done</button>
            </div>`
          : /* html */ `
            <p class="cl-intention-empty">No active intention. Set one below to focus your energy.</p>`
        }
      </div>

      <!-- Set Intention Form -->
      <form class="cl-set-form" aria-label="Set intention">
        <div class="cl-set-row">
          <input id="cl-intention-input" type="text"
            placeholder="What is your intention right now?"
            value="${_esc(this._intentionText)}"
            class="cl-text-input" maxlength="280" autocomplete="off"/>
          <button type="submit" class="cl-set-btn">Set</button>
        </div>
        <div class="cl-area-select">
          <span class="cl-area-select-label">Focus area:</span>
          ${focusAreas.filter(a => a.status === 'active').map(a => /* html */ `
            <button type="button" class="cl-area-chip ${this._selectedAreaId === a.id ? 'cl-area-chip--selected' : ''}"
              data-area-id="${a.id}">${_esc(a.label)}</button>
          `).join('')}
          <button type="button" class="cl-area-chip cl-area-chip--add" id="cl-add-area-toggle">+ Area</button>
        </div>
        <div class="cl-add-area-row" id="cl-add-area-row" style="display:none">
          <input id="cl-new-area" type="text" placeholder="New focus area…"
            value="${_esc(this._newAreaText)}" class="cl-text-input cl-text-input--sm"
            maxlength="60" autocomplete="off"/>
          <button type="button" class="cl-set-btn cl-set-btn--sm" id="cl-add-area-btn">Add</button>
        </div>
      </form>

      <!-- Focus Areas Grid -->
      ${focusAreas.length > 0 ? /* html */ `
        <div class="cl-areas-section">
          <div class="cl-section-label">Focus Areas</div>
          <div class="cl-areas-grid">
            ${focusAreas.map(a => _areaChip(a)).join('')}
          </div>
        </div>` : ''}

      <!-- Intention History -->
      <div class="cl-history">
        <div class="cl-section-label">Recent Intentions</div>
        <div class="cl-history-list">
          ${[...intentions].reverse().slice(0, 15).map(i => _intentionRow(i, focusAreas)).join('') ||
            '<p class="cl-empty">No intentions logged yet.</p>'}
        </div>
      </div>
    `;

    this._bindEvents();
  }

  // -------------------------------------------------------------------------
  // Event binding
  // -------------------------------------------------------------------------

  private _bindEvents(): void {
    const root = this._root;

    // Set intention form
    const form = root.querySelector<HTMLFormElement>('.cl-set-form')!;
    const intentionInput = root.querySelector<HTMLInputElement>('#cl-intention-input')!;

    intentionInput.addEventListener('input', () => {
      this._intentionText = intentionInput.value;
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const text = this._intentionText.trim();
      if (!text) return;
      setIntention(text, this._selectedAreaId);
      this._intentionText = '';
      this._selectedAreaId = null;
    });

    // Area chip selection
    root.querySelectorAll<HTMLButtonElement>('.cl-area-chip[data-area-id]').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.areaId!;
        this._selectedAreaId = this._selectedAreaId === id ? null : id;
        // Re-render to reflect selection without full store update
        btn.classList.toggle('cl-area-chip--selected', this._selectedAreaId === id);
        root.querySelectorAll<HTMLButtonElement>('.cl-area-chip[data-area-id]').forEach(b => {
          if (b !== btn) b.classList.remove('cl-area-chip--selected');
        });
      });
    });

    // Add area toggle
    root.querySelector('#cl-add-area-toggle')?.addEventListener('click', () => {
      const row = root.querySelector<HTMLElement>('#cl-add-area-row')!;
      row.style.display = row.style.display === 'none' ? 'flex' : 'none';
      root.querySelector<HTMLInputElement>('#cl-new-area')?.focus();
    });

    // Add area confirm
    root.querySelector('#cl-add-area-btn')?.addEventListener('click', () => {
      const input = root.querySelector<HTMLInputElement>('#cl-new-area')!;
      const label = input.value.trim();
      if (!label) return;
      const area = addFocusArea(label);
      this._selectedAreaId = area.id;
      this._newAreaText = '';
    });

    root.querySelector<HTMLInputElement>('#cl-new-area')?.addEventListener('input', (e) => {
      this._newAreaText = (e.target as HTMLInputElement).value;
    });

    // Complete intention
    root.querySelector<HTMLButtonElement>('.cl-complete-btn')?.addEventListener('click', (e) => {
      const id = (e.currentTarget as HTMLButtonElement).dataset.id!;
      completeIntention(id, 1);
    });

    // Area status toggle (click area chip in the grid)
    root.querySelectorAll<HTMLButtonElement>('.cl-area-grid-chip').forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.areaId!;
        const current = btn.dataset.status as 'active' | 'paused' | 'completed';
        const next = current === 'active' ? 'paused' : 'active';
        setFocusAreaStatus(id, next);
      });
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

function _areaChip(area: FocusArea): string {
  const statusIcon = area.status === 'active' ? '●' : area.status === 'paused' ? '◐' : '○';
  return /* html */ `
    <button class="cl-area-grid-chip cl-area-grid-chip--${area.status}"
      data-area-id="${area.id}" data-status="${area.status}"
      title="${area.status === 'active' ? 'Click to pause' : 'Click to reactivate'}">
      <span>${statusIcon}</span>
      <span>${_esc(area.label)}</span>
    </button>
  `;
}

function _intentionRow(intention: Intention, areas: FocusArea[]): string {
  const area = areas.find(a => a.id === intention.focusAreaId);
  const done = intention.completedAt !== null;
  const date = new Date(intention.createdAt).toLocaleString(undefined, {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
  return /* html */ `
    <div class="cl-history-row ${done ? 'cl-history-row--done' : ''}">
      <span class="cl-history-dot">${done ? '✓' : '◈'}</span>
      <div class="cl-history-body">
        <span class="cl-history-text">${_esc(intention.text)}</span>
        <div class="cl-history-meta">
          ${area ? `<span class="cl-history-area">${_esc(area.label)}</span>` : ''}
          <span class="cl-history-time">${date}</span>
        </div>
      </div>
    </div>
  `;
}

function _esc(str: string): string {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
