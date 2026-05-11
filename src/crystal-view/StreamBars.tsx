/**
 * src/crystal-view/StreamBars.tsx
 * GAIA-OS — Four input stream gauges
 * Spec: C-CC01 §11.2
 *
 * Soft horizontal gauges for affect / stage / shadow / schumann.
 * Deliberately no percentage labels — felt coherence, not audited performance.
 */

import React from 'react';
import type { CrystalState } from './types';

interface StreamBarsProps {
  state: CrystalState;
}

interface StreamDef {
  key:   keyof CrystalState;
  label: string;
  note:  string;
}

const STREAMS: StreamDef[] = [
  { key: 'affect_coherence',   label: 'Affect',  note: 'emotional arc' },
  { key: 'stage_coherence',    label: 'Stage',   note: 'growth markers' },
  { key: 'shadow_integration', label: 'Shadow',  note: 'integration' },
  { key: 'schumann_alignment', label: 'Field',   note: 'Schumann alignment' },
];

const StreamBar: React.FC<{ label: string; note: string; value: number }> = ({ label, note, value }) => (
  <div className="stream-bar" role="presentation">
    <div className="stream-bar__header">
      <span className="stream-bar__label">{label}</span>
      <span className="stream-bar__note">{note}</span>
    </div>
    <div className="stream-bar__track" aria-label={`${label} — ${Math.round(value * 100)}%`}>
      <div
        className="stream-bar__fill"
        style={{ width: `${value * 100}%` }}
      />
    </div>
  </div>
);

export const StreamBars: React.FC<StreamBarsProps> = ({ state }) => (
  <div className="stream-bars">
    {STREAMS.map(({ key, label, note }) => (
      <StreamBar
        key={key}
        label={label}
        note={note}
        value={state[key] as number}
      />
    ))}
  </div>
);

export default StreamBars;
