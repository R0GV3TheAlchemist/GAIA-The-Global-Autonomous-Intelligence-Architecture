/**
 * StateHUD.tsx
 * GAIA-OS Frontend — GAIAState HUD Component
 *
 * Displays the current GAIAState in a compact heads-up display:
 *   - Current mode badge (colour-coded by GAIAMode)
 *   - Coherence, energy, stress bars
 *   - Active talismans list
 *   - D6 last intervention reason
 *
 * Reads from the /api/state WebSocket or REST endpoint.
 * Architect can override mode directly from the HUD.
 *
 * Canon anchor: Issue #576, Issue #580
 * Created: June 17, 2026
 */

import React, { useEffect, useState, useCallback } from 'react';

// ---------------------------------------------------------------------------
// Types — mirror of src/core/state.py GAIAState.to_dict()
// ---------------------------------------------------------------------------

export type GAIAMode =
  | 'BUILD'
  | 'RESEARCH'
  | 'REFLECT'
  | 'RECOVER'
  | 'PROTECT'
  | 'TRANSCEND';

export interface GAIAStateSnapshot {
  coherence: number;
  energy: number;
  stress: number;
  entropy: number;
  learning_rate: number;
  exploration_rate: number;
  conservation_rate: number;
  mode: GAIAMode;
  architect_signal: string | null;
  active_talismans: string[];
  last_updated: number;
  session_id: string | null;
  coherence_band: string;
  is_safe_to_build: boolean;
  is_in_crisis: boolean;
  d6_reason?: string;
}

// ---------------------------------------------------------------------------
// Mode colour map
// ---------------------------------------------------------------------------

const MODE_COLOURS: Record<GAIAMode, { bg: string; text: string; glow: string }> = {
  BUILD:     { bg: '#1a3a5c', text: '#4fc3f7', glow: '0 0 12px #4fc3f780' },
  RESEARCH:  { bg: '#1a3a2a', text: '#81c784', glow: '0 0 12px #81c78480' },
  REFLECT:   { bg: '#2a2a4a', text: '#ce93d8', glow: '0 0 12px #ce93d880' },
  RECOVER:   { bg: '#3a2a1a', text: '#ffb74d', glow: '0 0 12px #ffb74d80' },
  PROTECT:   { bg: '#3a1a1a', text: '#ef9a9a', glow: '0 0 16px #ef9a9aaa' },
  TRANSCEND: { bg: '#2a1a3a', text: '#ffe082', glow: '0 0 20px #ffe082cc' },
};

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

interface BarProps {
  label: string;
  value: number;
  colour: string;
  inverse?: boolean; // inverse = high value is bad (stress, entropy)
}

const MetricBar: React.FC<BarProps> = ({ label, value, colour, inverse = false }) => {
  const pct = Math.round(value * 100);
  const displayColour = inverse && value > 0.6 ? '#ef9a9a' : colour;
  return (
    <div style={{ marginBottom: 6 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, marginBottom: 2, opacity: 0.85 }}>
        <span>{label}</span>
        <span style={{ color: displayColour }}>{pct}%</span>
      </div>
      <div style={{ height: 4, background: '#1a1a2e', borderRadius: 2, overflow: 'hidden' }}>
        <div
          style={{
            height: '100%',
            width: `${pct}%`,
            background: displayColour,
            borderRadius: 2,
            transition: 'width 0.4s ease',
            boxShadow: `0 0 6px ${displayColour}80`,
          }}
        />
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main HUD component
// ---------------------------------------------------------------------------

interface StateHUDProps {
  /** REST endpoint to poll for state. Defaults to /api/state */
  endpoint?: string;
  /** Polling interval in ms. Defaults to 3000. */
  pollInterval?: number;
  /** Called when Architect sends a mode override. */
  onArchitectOverride?: (signal: string) => void;
  /** If true, renders in compact single-line mode */
  compact?: boolean;
}

export const StateHUD: React.FC<StateHUDProps> = ({
  endpoint = '/api/state',
  pollInterval = 3000,
  onArchitectOverride,
  compact = false,
}) => {
  const [state, setState] = useState<GAIAStateSnapshot | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(!compact);

  const fetchState = useCallback(async () => {
    try {
      const res = await fetch(endpoint);
      if (!res.ok) throw new Error(`State fetch failed: ${res.status}`);
      const data: GAIAStateSnapshot = await res.json();
      setState(data);
      setError(null);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    }
  }, [endpoint]);

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, pollInterval);
    return () => clearInterval(interval);
  }, [fetchState, pollInterval]);

  if (!state) {
    return (
      <div style={hudContainer('#0d0d1a', '1px solid #333')}>
        <span style={{ color: '#555', fontSize: 11 }}>
          {error ? `⚠ ${error}` : 'Loading GAIAState...'}
        </span>
      </div>
    );
  }

  const colours = MODE_COLOURS[state.mode];

  return (
    <div
      style={{
        ...hudContainer(colours.bg, `1px solid ${colours.text}30`),
        boxShadow: state.is_in_crisis ? colours.glow : 'none',
        transition: 'box-shadow 0.4s ease',
      }}
    >
      {/* Header row */}
      <div
        style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', cursor: 'pointer' }}
        onClick={() => setExpanded(e => !e)}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: 2,
              color: colours.text,
              textShadow: colours.glow,
              padding: '2px 7px',
              border: `1px solid ${colours.text}60`,
              borderRadius: 3,
            }}
          >
            {state.mode}
          </span>
          <span style={{ fontSize: 10, color: '#aaa' }}>
            {state.coherence_band}
          </span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          {state.active_talismans.length > 0 && (
            <span style={{ fontSize: 9, color: '#ffe082', letterSpacing: 1 }}>
              ◆ {state.active_talismans.length}
            </span>
          )}
          <span style={{ color: '#555', fontSize: 10 }}>{expanded ? '▲' : '▼'}</span>
        </div>
      </div>

      {/* Expanded body */}
      {expanded && (
        <div style={{ marginTop: 10 }}>
          <MetricBar label="Coherence" value={state.coherence} colour={colours.text} />
          <MetricBar label="Energy"    value={state.energy}    colour={colours.text} />
          <MetricBar label="Stress"    value={state.stress}    colour="#ef9a9a" inverse />
          <MetricBar label="Entropy"   value={state.entropy}   colour="#ffb74d" inverse />

          {/* D6 reason */}
          {state.d6_reason && (
            <div style={{ marginTop: 8, fontSize: 10, color: '#888', fontStyle: 'italic', lineHeight: 1.4 }}>
              {state.d6_reason}
            </div>
          )}

          {/* Active talismans */}
          {state.active_talismans.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 9, color: '#666', letterSpacing: 1, marginBottom: 4 }}>ACTIVE TALISMANS</div>
              {state.active_talismans.map(id => (
                <div key={id} style={{ fontSize: 10, color: '#ffe082', marginBottom: 2 }}>◆ {id.slice(0, 8)}…</div>
              ))}
            </div>
          )}

          {/* Architect override controls */}
          {onArchitectOverride && (
            <div style={{ marginTop: 10, borderTop: '1px solid #333', paddingTop: 8 }}>
              <div style={{ fontSize: 9, color: '#666', letterSpacing: 1, marginBottom: 6 }}>ARCHITECT OVERRIDE</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                {(['BUILD', 'RESEARCH', 'REFLECT', 'RECOVER', 'PROTECT'] as GAIAMode[]).map(m => (
                  <button
                    key={m}
                    onClick={() => onArchitectOverride(`FORCE_${m}`)}
                    style={{
                      fontSize: 9,
                      padding: '2px 6px',
                      background: state.mode === m ? `${MODE_COLOURS[m].text}22` : '#111',
                      color: MODE_COLOURS[m].text,
                      border: `1px solid ${MODE_COLOURS[m].text}40`,
                      borderRadius: 3,
                      cursor: 'pointer',
                      letterSpacing: 1,
                    }}
                  >
                    {m}
                  </button>
                ))}
                <button
                  onClick={() => onArchitectOverride('RESUME_AUTO')}
                  style={{
                    fontSize: 9,
                    padding: '2px 6px',
                    background: '#111',
                    color: '#888',
                    border: '1px solid #333',
                    borderRadius: 3,
                    cursor: 'pointer',
                    letterSpacing: 1,
                  }}
                >
                  AUTO
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Style helpers
// ---------------------------------------------------------------------------

function hudContainer(bg: string, border: string): React.CSSProperties {
  return {
    background: bg,
    border,
    borderRadius: 6,
    padding: '10px 12px',
    minWidth: 200,
    maxWidth: 280,
    fontFamily: '"JetBrains Mono", "Fira Code", monospace',
    color: '#ccc',
    userSelect: 'none',
    transition: 'background 0.4s ease, border 0.4s ease',
  };
}

export default StateHUD;
