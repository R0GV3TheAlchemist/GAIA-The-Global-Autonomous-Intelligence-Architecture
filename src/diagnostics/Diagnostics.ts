// GAIA Diagnostics Panel
// Displays startup timing, sidecar health, version info, mesh storage health,
// and a live log tail.
// Canon Ref: C43 — Sovereign Distribution

import './Diagnostics.css';
import { invoke }        from '@tauri-apps/api/core';
import { getVersion }    from '@tauri-apps/api/app';
import { listen }        from '@tauri-apps/api/event';
import { API_BASE }      from '../config';
import { getLogBuffer, LogEntry } from './logger';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface StoreStatus  { reachable: boolean; latency_ms: number | null }
interface MeshResponse {
  ok:             boolean
  checked_at:     string
  backend_driver: string
  node_id:        string
  stores: Record<string, StoreStatus>
}

const STORE_KEYS: Array<keyof MeshResponse['stores']> = [
  'audit', 'sovereign_memory', 'telemetry', 'crisis_engine',
]

const STORE_LABELS: Record<string, string> = {
  audit:            '\u{1F4CB} Audit',
  sovereign_memory: '\u{1F9E0} Sovereign Memory',
  telemetry:        '\u{1F4E1} Telemetry',
  crisis_engine:    '\u{1F6E1}\uFE0F Crisis Engine',
}

// ---------------------------------------------------------------------------
// Mount
// ---------------------------------------------------------------------------

export function mountDiagnostics(root: HTMLElement): void {
  root.innerHTML = `
    <div class="diag-panel">
      <div class="diag-header">
        <span class="diag-title">&#9881; Diagnostics</span>
        <div class="diag-actions">
          <button id="diag-refresh" class="diag-btn">&#8635; Refresh</button>
          <button id="diag-open-logs" class="diag-btn">&#128193; Open Log Folder</button>
          <button id="diag-copy" class="diag-btn">&#128203; Copy Report</button>
        </div>
      </div>

      <!-- KPI grid -->
      <div class="diag-grid">
        <div class="diag-card">
          <div class="diag-card-label">App Version</div>
          <div id="diag-version" class="diag-card-value">&#8230;</div>
        </div>
        <div class="diag-card">
          <div class="diag-card-label">Sidecar</div>
          <div id="diag-sidecar" class="diag-card-value">&#8230;</div>
        </div>
        <div class="diag-card">
          <div class="diag-card-label">Cold Start</div>
          <div id="diag-coldstart" class="diag-card-value">&#8230;</div>
        </div>
        <div class="diag-card">
          <div class="diag-card-label">Log Buffer</div>
          <div id="diag-bufsize" class="diag-card-value">&#8230;</div>
        </div>
      </div>

      <!-- Mesh Status section -->
      <div class="diag-mesh-section">
        <div class="diag-mesh-header">
          <span class="diag-mesh-title">&#127760; Mesh Storage</span>
          <span id="diag-mesh-badge" class="diag-mesh-badge">&#8230;</span>
          <span id="diag-mesh-meta" class="diag-mesh-meta"></span>
        </div>
        <div class="diag-mesh-rows">
          ${STORE_KEYS.map(key => `
          <div class="diag-mesh-row" id="diag-mesh-row-${key}">
            <span class="diag-mesh-dot" id="diag-mesh-dot-${key}"></span>
            <span class="diag-mesh-name">${STORE_LABELS[key] ?? key}</span>
            <div class="diag-mesh-bar-wrap">
              <div class="diag-mesh-bar-fill" id="diag-mesh-bar-${key}"></div>
            </div>
            <span class="diag-mesh-val" id="diag-mesh-val-${key}">&#8230;</span>
          </div>`).join('')}
        </div>
        <div class="diag-mesh-footer">
          <span id="diag-mesh-checked">not yet polled</span>
        </div>
      </div>

      <!-- Log tail -->
      <div class="diag-log-section">
        <div class="diag-log-toolbar">
          <span class="diag-log-title">Log Tail</span>
          <select id="diag-log-filter" class="diag-select">
            <option value="ALL">ALL</option>
            <option value="INFO">INFO</option>
            <option value="WARN">WARN</option>
            <option value="ERROR">ERROR</option>
          </select>
          <button id="diag-log-clear" class="diag-btn">Clear</button>
        </div>
        <div id="diag-log-list" class="diag-log-list"></div>
      </div>
    </div>
  `;

  const t0 = performance.now();
  let coldStartMs: number | null = null;

  listen('sidecar:ready', () => {
    coldStartMs = performance.now() - t0;
    refreshStats(coldStartMs);
  });

  // -------------------------------------------------------------------------
  // Mesh status
  // -------------------------------------------------------------------------

  let _lastMeshResponse: MeshResponse | null = null

  async function renderMeshStatus(): Promise<void> {
    let data: MeshResponse | null = null
    try {
      const res = await fetch(`${API_BASE}/mesh/status`, {
        signal: AbortSignal.timeout(2000),
        cache:  'no-store',
      })
      if (res.ok) data = await res.json() as MeshResponse
    } catch { /* sidecar offline */ }

    _lastMeshResponse = data

    // Badge
    const badge = document.getElementById('diag-mesh-badge')
    if (badge) {
      if (!data) {
        badge.textContent  = 'OFFLINE'
        badge.className    = 'diag-mesh-badge degraded'
      } else {
        badge.textContent  = data.ok ? 'ALL OK' : 'DEGRADED'
        badge.className    = `diag-mesh-badge ${data.ok ? 'ok' : 'degraded'}`
      }
    }

    // Meta chips
    const meta = document.getElementById('diag-mesh-meta')
    if (meta && data) {
      meta.textContent = `${data.backend_driver} · node: ${data.node_id}`
    }

    // Store rows
    for (const key of STORE_KEYS) {
      const store: StoreStatus | undefined = data?.stores[key]

      const dot  = document.getElementById(`diag-mesh-dot-${key}`)
      const bar  = document.getElementById(`diag-mesh-bar-${key}`)
      const val  = document.getElementById(`diag-mesh-val-${key}`)

      const reachable  = store?.reachable ?? false
      const latency_ms = store?.latency_ms ?? null

      // Dot
      if (dot) dot.className = `diag-mesh-dot ${reachable ? 'up' : 'down'}`

      // Bar
      if (bar) {
        const BAR_MAX = 50
        const pct     = latency_ms !== null
          ? Math.min((latency_ms / BAR_MAX) * 100, 100).toFixed(1)
          : '0'
        bar.style.width = `${pct}%`
        bar.className   = `diag-mesh-bar-fill ${
          !reachable   ? 'bar-unknown' :
          latency_ms === null ? 'bar-unknown' :
          latency_ms < 5  ? 'bar-fast' :
          latency_ms < 20 ? 'bar-ok'
                          : 'bar-slow'
        }`
      }

      // Value
      if (val) {
        if (!reachable) {
          val.textContent  = 'unreachable'
          val.style.color  = '#a13544'
        } else {
          val.textContent  = latency_ms !== null ? `${latency_ms.toFixed(1)} ms` : '—'
          val.style.color  = ''
        }
      }
    }

    // Footer timestamp
    const checked = document.getElementById('diag-mesh-checked')
    if (checked) {
      checked.textContent = data
        ? `checked ${new Date(data.checked_at).toLocaleTimeString()}`
        : 'fetch failed'
    }
  }

  // -------------------------------------------------------------------------
  // Stats refresh
  // -------------------------------------------------------------------------

  async function refreshStats(csMs?: number): Promise<void> {
    try {
      const v  = await getVersion();
      const el = document.getElementById('diag-version');
      if (el) el.textContent = `v${v}`;
    } catch { /* ignore */ }

    try {
      const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(2000) });
      const el  = document.getElementById('diag-sidecar');
      if (el) {
        el.textContent = res.ok ? '\u25cf online' : '\u25cf degraded';
        el.style.color = res.ok ? '#4f98a3' : '#fdab43';
      }
    } catch {
      const el = document.getElementById('diag-sidecar');
      if (el) { el.textContent = '\u25cf offline'; el.style.color = '#dd6974'; }
    }

    const csEl = document.getElementById('diag-coldstart');
    if (csEl) {
      const ms = csMs ?? coldStartMs;
      csEl.textContent = ms !== null ? `${(ms / 1000).toFixed(2)} s` : 'measuring\u2026';
    }

    const buf   = getLogBuffer();
    const bufEl = document.getElementById('diag-bufsize');
    if (bufEl) bufEl.textContent = `${buf.length} entries`;

    // Mesh status (piggybacks on the same 10 s cycle)
    await renderMeshStatus();

    renderLogTail();
  }

  // -------------------------------------------------------------------------
  // Log tail
  // -------------------------------------------------------------------------

  function renderLogTail(): void {
    const filter  = (document.getElementById('diag-log-filter') as HTMLSelectElement)?.value ?? 'ALL';
    const listEl  = document.getElementById('diag-log-list');
    if (!listEl) return;

    const levels: Record<string, number> = { DEBUG: 0, INFO: 1, WARN: 2, ERROR: 3 };
    const minLevel = levels[filter] ?? 0;

    const entries = getLogBuffer()
      .filter(e => (levels[e.level] ?? 0) >= minLevel)
      .slice(-100);

    listEl.innerHTML = entries.length === 0
      ? '<div class="diag-log-empty">No log entries.</div>'
      : entries.map(renderEntry).join('');

    listEl.scrollTop = listEl.scrollHeight;
  }

  function renderEntry(e: LogEntry): string {
    const levelClass = `diag-log-level-${e.level.toLowerCase()}`;
    const time = e.ts.slice(11, 23);
    const data = e.data !== undefined ? ` ${JSON.stringify(e.data)}` : '';
    return `
      <div class="diag-log-row">
        <span class="diag-log-time">${time}</span>
        <span class="diag-log-level ${levelClass}">${e.level}</span>
        <span class="diag-log-module">${escHtml(e.module)}</span>
        <span class="diag-log-msg">${escHtml(e.msg)}${escHtml(data)}</span>
      </div>`;
  }

  // -------------------------------------------------------------------------
  // Event bindings
  // -------------------------------------------------------------------------

  document.getElementById('diag-refresh')?.addEventListener('click', () => refreshStats());

  document.getElementById('diag-open-logs')?.addEventListener('click', async () => {
    try { await invoke('open_log_dir'); }
    catch (e) { console.warn('[GAIA:diag] open_log_dir failed:', e); }
  });

  document.getElementById('diag-copy')?.addEventListener('click', () => {
    const report = buildReport();
    navigator.clipboard.writeText(report).then(() => {
      const btn = document.getElementById('diag-copy');
      if (btn) {
        btn.textContent = '\u2713 Copied';
        setTimeout(() => { btn.textContent = '\u{1F4CB} Copy Report'; }, 2000);
      }
    });
  });

  document.getElementById('diag-log-filter')?.addEventListener('change', renderLogTail);
  document.getElementById('diag-log-clear')?.addEventListener('click', () => {
    const listEl = document.getElementById('diag-log-list');
    if (listEl) listEl.innerHTML = '<div class="diag-log-empty">Log cleared (in-view only).</div>';
  });

  // -------------------------------------------------------------------------
  // Bootstrap
  // -------------------------------------------------------------------------

  refreshStats();
  setInterval(() => refreshStats(), 10_000);
}

// ---------------------------------------------------------------------------
// Clipboard report
// ---------------------------------------------------------------------------

function buildReport(): string {
  const lines: string[] = [
    `GAIA Diagnostics Report \u2014 ${new Date().toISOString()}`,
    '='.repeat(60),
    ...getLogBuffer().slice(-50).map(e =>
      `${e.ts} [${e.level}] ${e.module}: ${e.msg}${
        e.data !== undefined ? ' ' + JSON.stringify(e.data) : ''
      }`),
  ];
  return lines.join('\n');
}

function escHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}
