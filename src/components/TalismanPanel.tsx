/**
 * TalismanPanel.tsx
 *
 * Lists all talismans for the current GAIAN and allows activate / deactivate
 * via the /gaia-state/talisman/* REST endpoints.
 *
 * Design rules (canon #580 / Architect Protocol):
 *   - Only the sovereign owner can activate a talisman
 *   - Deactivation is always allowed (revocable consent = true)
 *   - Over-attachment warnings surface when a talisman is activated 5+ times
 *   - No talisman is created here — creation lives in the Settings panel
 *
 * Canon: #580 Talisman Object, #578 Architect Protocol, C01 Human Sovereignty
 */

import React, { useState } from 'react';
import type { TalismanChip } from '../hooks/useGaiaState';

// ── Config ───────────────────────────────────────────────────────────────────

const API_BASE = (import.meta as Record<string, unknown>)['env']
  ? ((import.meta as Record<string, unknown>)['env'] as Record<string, string>)['VITE_API_BASE'] ?? 'http://127.0.0.1:8008'
  : 'http://127.0.0.1:8008';

// ── Sub-components ────────────────────────────────────────────────────────────

function CoherenceBadge({ fn }: { fn: string }) {
  const palette: Record<string, string> = {
    GROUND:    '#7c9ef5',
    PROTECT:   '#f55c5c',
    AMPLIFY:   '#f5c842',
    RESTORE:   '#5cf592',
    FOCUS:     '#42e8d5',
    OPEN:      '#b28aff',
    INTEGRATE: '#5ec9f5',
    WITNESS:   '#a0aec0',
  };
  const color = palette[fn] ?? '#a0aec0';
  return (
    <span className="talisman-panel__fn-badge" style={{ borderColor: color, color }}>
      {fn.toLowerCase()}
    </span>
  );
}

// ── Props ─────────────────────────────────────────────────────────────────────

export interface TalismanPanelProps {
  talismans: TalismanChip[];
  onRefresh: () => void;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function TalismanPanel({ talismans, onRefresh }: TalismanPanelProps) {
  const [busy, setBusy] = useState<string | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);

  async function toggleTalisman(t: TalismanChip) {
    setBusy(t.id);
    setLocalError(null);
    const endpoint = t.is_active
      ? `${API_BASE}/gaia-state/talisman/deactivate`
      : `${API_BASE}/gaia-state/talisman/activate`;
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ talisman_id: t.id }),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({})) as Record<string, unknown>;
        throw new Error((body['detail'] as string | undefined) ?? `HTTP ${res.status}`);
      }
      onRefresh();
    } catch (e) {
      setLocalError((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  if (talismans.length === 0) {
    return (
      <div className="talisman-panel talisman-panel--empty">
        <span>No talismans registered.</span>
      </div>
    );
  }

  return (
    <div className="talisman-panel">
      <h4 className="talisman-panel__title">Talismans</h4>

      {localError && (
        <div className="talisman-panel__error">⚠ {localError}</div>
      )}

      <ul className="talisman-panel__list">
        {talismans.map((t) => (
          <li key={t.id} className={`talisman-panel__item ${t.is_active ? 'talisman-panel__item--active' : ''}`}>
            <div className="talisman-panel__item-info">
              <span className="talisman-panel__item-name">{t.name}</span>
              <CoherenceBadge fn={t.coherence_function} />
              {t.resonance?.frequency_hz != null && (
                <span className="talisman-panel__item-freq">{t.resonance.frequency_hz} Hz</span>
              )}
            </div>
            <button
              className={`talisman-panel__toggle ${
                t.is_active ? 'talisman-panel__toggle--active' : ''
              }`}
              onClick={() => toggleTalisman(t)}
              disabled={busy === t.id}
              aria-pressed={t.is_active}
              title={t.is_active ? `Deactivate ${t.name}` : `Activate ${t.name}`}
            >
              {busy === t.id ? '…' : t.is_active ? '◉' : '○'}
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default TalismanPanel;
