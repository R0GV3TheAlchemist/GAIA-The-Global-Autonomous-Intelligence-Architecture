/**
 * ViriditasHeartView
 * Full UI panel for the ViriditasHeart crystal.
 *
 * Layout:
 *   ┌─────────────────────────────────────┐
 *   │  Mood Ring  │  Weekly Sparkline      │
 *   ├─────────────────────────────────────┤
 *   │  Log form: energy slider + mood     │
 *   │  slider + note input + [Log] button │
 *   ├─────────────────────────────────────┤
 *   │  Entry list (most recent first)     │
 *   └─────────────────────────────────────┘
 */

import {
  subscribe,
  logWellbeing,
  getVitality,
} from './store';
import {
  TIER_ACCENT,
  TIER_LABEL,
  type ViriditasHeartState,
  type WellbeingEntry,
} from './types';

export class ViriditasHeartView {
  private _root: HTMLElement;
  private _unsub: (() => void) | null = null;

  // Form state
  private _energyVal = 5;
  private _moodVal = 5;
  private _noteVal = '';

  constructor(container: HTMLElement) {
    this._root = document.createElement('div');
    this._root.className = 'vh-panel';
    container.appendChild(this._root);

    this._render(getVitality());
    this._unsub = subscribe((state) => this._render(state));
  }

  // -------------------------------------------------------------------------
  // Render
  // -------------------------------------------------------------------------

  private _render(state: ViriditasHeartState): void {
    const { log, latest } = state;
    const tier = latest?.moodTier ?? 'steady';
    const accent = TIER_ACCENT[tier];
    const tierLabel = TIER_LABEL[tier];
    const trendIcon =
      log.trend === 'up' ? '↑' : log.trend === 'down' ? '↓' : '→';

    this._root.innerHTML = /* html */ `
      <div class="vh-header">
        <div class="vh-mood-ring" style="--vh-accent:${accent}">
          <svg viewBox="0 0 80 80" width="80" height="80" aria-hidden="true">
            <circle cx="40" cy="40" r="34" fill="none"
              stroke="var(--color-surface-dynamic)" stroke-width="8"/>
            <circle cx="40" cy="40" r="34" fill="none"
              stroke="${accent}" stroke-width="8"
              stroke-dasharray="${_arcLength(latest)}"
              stroke-dashoffset="0"
              stroke-linecap="round"
              transform="rotate(-90 40 40)"
              class="vh-arc"/>
          </svg>
          <span class="vh-ring-score">${latest ? ((latest.mood + latest.energy) / 2).toFixed(1) : '—'}</span>
        </div>
        <div class="vh-meta">
          <div class="vh-tier-label" style="color:${accent}">${tierLabel}</div>
          <div class="vh-weekly">
            <span>7d energy <strong>${log.weekAvgEnergy || '—'}</strong></span>
            <span>7d mood <strong>${log.weekAvgMood || '—'}</strong></span>
            <span class="vh-trend">${trendIcon} ${log.trend}</span>
          </div>
          ${_sparkline(log.entries)}
        </div>
      </div>

      <form class="vh-log-form" aria-label="Log wellbeing">
        <div class="vh-slider-row">
          <label for="vh-energy">Energy</label>
          <input id="vh-energy" type="range" min="1" max="10" step="1"
            value="${this._energyVal}" class="vh-slider"/>
          <span class="vh-slider-val" id="vh-energy-val">${this._energyVal}</span>
        </div>
        <div class="vh-slider-row">
          <label for="vh-mood">Mood</label>
          <input id="vh-mood" type="range" min="1" max="10" step="1"
            value="${this._moodVal}" class="vh-slider"/>
          <span class="vh-slider-val" id="vh-mood-val">${this._moodVal}</span>
        </div>
        <div class="vh-note-row">
          <input id="vh-note" type="text" placeholder="How are you feeling? (optional)"
            value="${_esc(this._noteVal)}" class="vh-note-input"
            maxlength="200" autocomplete="off"/>
        </div>
        <button type="submit" class="vh-log-btn">Log Vitality</button>
      </form>

      <div class="vh-entry-list" aria-label="Wellbeing history">
        ${log.entries.slice(0, 20).map(_entryRow).join('') || '<p class="vh-empty">No entries yet. Log your first vitality check-in above.</p>'}
      </div>
    `;

    this._bindForm();
  }

  // -------------------------------------------------------------------------
  // Form binding
  // -------------------------------------------------------------------------

  private _bindForm(): void {
    const form = this._root.querySelector<HTMLFormElement>('.vh-log-form')!;
    const energyInput = form.querySelector<HTMLInputElement>('#vh-energy')!;
    const moodInput = form.querySelector<HTMLInputElement>('#vh-mood')!;
    const noteInput = form.querySelector<HTMLInputElement>('#vh-note')!;
    const energyVal = form.querySelector<HTMLSpanElement>('#vh-energy-val')!;
    const moodVal = form.querySelector<HTMLSpanElement>('#vh-mood-val')!;

    energyInput.addEventListener('input', () => {
      this._energyVal = Number(energyInput.value);
      energyVal.textContent = String(this._energyVal);
    });

    moodInput.addEventListener('input', () => {
      this._moodVal = Number(moodInput.value);
      moodVal.textContent = String(this._moodVal);
    });

    noteInput.addEventListener('input', () => {
      this._noteVal = noteInput.value;
    });

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      logWellbeing(this._energyVal, this._moodVal, this._noteVal);
      this._noteVal = '';
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
// Pure helpers (no DOM side-effects)
// ---------------------------------------------------------------------------

function _arcLength(entry: WellbeingEntry | null): string {
  const circumference = 2 * Math.PI * 34; // r=34
  if (!entry) return `0 ${circumference}`;
  const avg = (entry.mood + entry.energy) / 2;
  const filled = (avg / 10) * circumference;
  return `${filled} ${circumference}`;
}

function _sparkline(entries: WellbeingEntry[]): string {
  const last14 = entries
    .slice(0, 14)
    .reverse()
    .map((e) => (e.mood + e.energy) / 2);
  if (last14.length < 2) return '';
  const W = 120, H = 30;
  const min = Math.min(...last14);
  const max = Math.max(...last14) || 1;
  const pts = last14
    .map((v, i) => {
      const x = (i / (last14.length - 1)) * W;
      const y = H - ((v - min) / (max - min || 1)) * H;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');
  return /* html */ `
    <svg class="vh-sparkline" viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" aria-hidden="true">
      <polyline points="${pts}" fill="none" stroke="var(--color-primary)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;
}

function _entryRow(entry: WellbeingEntry): string {
  const accent = TIER_ACCENT[entry.moodTier];
  const date = new Date(entry.timestamp).toLocaleString(undefined, {
    month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
  return /* html */ `
    <div class="vh-entry" style="--vh-entry-accent:${accent}">
      <div class="vh-entry-scores">
        <span class="vh-entry-dot" style="background:${accent}"></span>
        <span>⚡ ${entry.energy}</span>
        <span>◈ ${entry.mood}</span>
      </div>
      <div class="vh-entry-body">
        ${entry.note ? `<span class="vh-entry-note">${_esc(entry.note)}</span>` : ''}
        <span class="vh-entry-time">${date}</span>
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
