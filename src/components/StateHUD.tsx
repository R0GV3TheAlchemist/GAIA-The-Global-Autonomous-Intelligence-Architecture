/**
 * StateHUD.tsx
 * ============
 * GAIA State HUD — Real-time operational state display
 * Canon reference: C52 Part II (Simultaneous Lens Protocol), #576
 * Issues: #576, #571
 *
 * Shows:
 *   - Current GAIAMode with color coding
 *   - Coherence, Energy, Stress, Entropy as progress bars
 *   - Dimensional health flags (D1–D4, D6)
 *   - Active talismans
 *   - D6 Engine recommendation badge
 *   - Real-time WebSocket connection
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type GAIAMode =
  | 'BUILD'
  | 'RESEARCH'
  | 'REFLECT'
  | 'CREATE'
  | 'REST'
  | 'RECOVER'
  | 'PROTECT'
  | 'INTEGRATE';

interface DimensionalHealth {
  D1_critical: boolean;
  D2_distress: boolean;
  D3_saturated: boolean;
  D4_isolated: boolean;
  D6_approaching: boolean;
}

interface GAIAStateSnapshot {
  energy: number;
  coherence: number;
  stress: number;
  learning_rate: number;
  exploration_rate: number;
  conservation_rate: number;
  entropy: number;
  mode: GAIAMode;
  session_id: string | null;
  gaian_id: string | null;
  updated_at: number;
  dimensional_health: DimensionalHealth;
  priority_dimension: string;
}

interface WSMessage {
  type: 'STATE_INIT' | 'STATE_UPDATE' | 'PONG' | 'ERROR' | 'UNKNOWN';
  state?: GAIAStateSnapshot;
  t?: number;
  detail?: string;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const MODE_COLORS: Record<GAIAMode, { bg: string; text: string; border: string }> = {
  BUILD:     { bg: '#1a1a2e', text: '#FFD700', border: '#FFD700' },
  RESEARCH:  { bg: '#1a1a2e', text: '#FF8C00', border: '#FF8C00' },
  REFLECT:   { bg: '#1a1a2e', text: '#9B59B6', border: '#9B59B6' },
  CREATE:    { bg: '#1a1a2e', text: '#00CED1', border: '#00CED1' },
  REST:      { bg: '#1a1a2e', text: '#27AE60', border: '#27AE60' },
  RECOVER:   { bg: '#1a1a2e', text: '#3498DB', border: '#3498DB' },
  PROTECT:   { bg: '#1a1a2e', text: '#E74C3C', border: '#E74C3C' },
  INTEGRATE: { bg: '#0a0a1a', text: '#E8D5B7', border: '#E8D5B7' },
};

const MODE_EMOJI: Record<GAIAMode, string> = {
  BUILD:     '🔨',
  RESEARCH:  '🔭',
  REFLECT:   '🌊',
  CREATE:    '✨',
  REST:      '🌙',
  RECOVER:   '🌱',
  PROTECT:   '🛡️',
  INTEGRATE: '🔮',
};

const FIELD_CONFIG = [
  { key: 'coherence',        label: 'Coherence',    color: '#9B59B6', invert: false },
  { key: 'energy',           label: 'Energy',       color: '#FFD700', invert: false },
  { key: 'stress',           label: 'Stress',       color: '#E74C3C', invert: true  },
  { key: 'entropy',          label: 'Entropy',      color: '#E67E22', invert: true  },
  { key: 'learning_rate',    label: 'Learning',     color: '#3498DB', invert: false },
  { key: 'exploration_rate', label: 'Exploration',  color: '#00CED1', invert: false },
] as const;

const DIM_HEALTH_CONFIG: Array<{
  key: keyof DimensionalHealth;
  label: string;
  isGood: boolean;
  severity: 'critical' | 'warn' | 'good';
}> = [
  { key: 'D1_critical',   label: 'D1 Physical',   isGood: false, severity: 'critical' },
  { key: 'D2_distress',   label: 'D2 Emotional',  isGood: false, severity: 'warn'     },
  { key: 'D3_saturated',  label: 'D3 Mental',     isGood: false, severity: 'warn'     },
  { key: 'D4_isolated',   label: 'D4 Social',     isGood: false, severity: 'warn'     },
  { key: 'D6_approaching',label: 'D6 Unity ≈',   isGood: true,  severity: 'good'     },
];

const WS_URL = 'ws://localhost:8000/state/ws';
const RECONNECT_DELAY_MS = 3000;

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const FieldBar: React.FC<{
  label: string;
  value: number;
  color: string;
  invert: boolean;
}> = ({ label, value, color, invert }) => {
  const displayValue = Math.round(value * 100);
  // For inverted fields (stress, entropy), a low value is "good"
  const healthPct = invert ? 1 - value : value;
  const opacity = 0.3 + healthPct * 0.7;

  return (
    <div style={{ marginBottom: '6px' }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '11px',
        color: '#aaa',
        marginBottom: '3px',
      }}>
        <span>{label}</span>
        <span style={{ color, fontWeight: 600 }}>{displayValue}%</span>
      </div>
      <div style={{
        height: '6px',
        borderRadius: '3px',
        background: 'rgba(255,255,255,0.08)',
        overflow: 'hidden',
      }}>
        <div
          style={{
            height: '100%',
            width: `${displayValue}%`,
            background: color,
            opacity,
            borderRadius: '3px',
            transition: 'width 0.4s ease, opacity 0.4s ease',
          }}
        />
      </div>
    </div>
  );
};

const DimHealthFlag: React.FC<{
  label: string;
  active: boolean;
  isGood: boolean;
  severity: 'critical' | 'warn' | 'good';
}> = ({ label, active, isGood, severity }) => {
  if (!active) return null;

  const colors = {
    critical: { bg: 'rgba(231,76,60,0.15)', border: '#E74C3C', text: '#FF6B6B' },
    warn:     { bg: 'rgba(230,126,34,0.15)', border: '#E67E22', text: '#F39C12' },
    good:     { bg: 'rgba(0,206,209,0.12)', border: '#00CED1', text: '#00CED1' },
  };
  const c = colors[severity];

  return (
    <div style={{
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: '12px',
      border: `1px solid ${c.border}`,
      background: c.bg,
      color: c.text,
      fontSize: '10px',
      fontWeight: 600,
      marginRight: '4px',
      marginBottom: '4px',
      letterSpacing: '0.5px',
    }}>
      {label}
    </div>
  );
};

// ---------------------------------------------------------------------------
// Main HUD component
// ---------------------------------------------------------------------------

export interface StateHUDProps {
  /** Optional override WebSocket URL (defaults to localhost:8000) */
  wsUrl?: string;
  /** Whether to show the full field breakdown or compact mode-only view */
  compact?: boolean;
  /** Called whenever state updates — useful for parent components */
  onStateChange?: (state: GAIAStateSnapshot) => void;
}

export const StateHUD: React.FC<StateHUDProps> = ({
  wsUrl = WS_URL,
  compact = false,
  onStateChange,
}) => {
  const [state, setState] = useState<GAIAStateSnapshot | null>(null);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      if (reconnectTimer.current) {
        clearTimeout(reconnectTimer.current);
        reconnectTimer.current = null;
      }
    };

    ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data);
        if ((msg.type === 'STATE_INIT' || msg.type === 'STATE_UPDATE') && msg.state) {
          setState(msg.state);
          setLastUpdate(msg.t ?? Date.now() / 1000);
          onStateChange?.(msg.state);
        }
      } catch {
        // malformed message — ignore
      }
    };

    ws.onclose = () => {
      setConnected(false);
      reconnectTimer.current = setTimeout(connect, RECONNECT_DELAY_MS);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, [wsUrl, onStateChange]);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, [connect]);

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  if (!state) {
    return (
      <div style={hudContainerStyle}>
        <div style={{ color: '#555', fontSize: '11px', textAlign: 'center', padding: '12px' }}>
          {connected ? 'Loading state…' : 'Connecting to GAIA…'}
        </div>
      </div>
    );
  }

  const modeColors = MODE_COLORS[state.mode] ?? MODE_COLORS.BUILD;
  const activeFlags = DIM_HEALTH_CONFIG.filter(
    (c) => state.dimensional_health[c.key]
  );

  return (
    <div style={{
      ...hudContainerStyle,
      borderColor: modeColors.border,
      boxShadow: `0 0 12px ${modeColors.border}22`,
    }}>
      {/* Header — Mode + connection indicator */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '10px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '16px' }}>{MODE_EMOJI[state.mode]}</span>
          <span style={{
            fontSize: '13px',
            fontWeight: 700,
            color: modeColors.text,
            letterSpacing: '1.5px',
          }}>
            {state.mode}
          </span>
        </div>
        <div style={{
          width: '7px',
          height: '7px',
          borderRadius: '50%',
          background: connected ? '#27AE60' : '#E74C3C',
          boxShadow: connected ? '0 0 6px #27AE60' : '0 0 6px #E74C3C',
        }} />
      </div>

      {/* Dimensional health flags */}
      {activeFlags.length > 0 && (
        <div style={{ marginBottom: '10px' }}>
          {activeFlags.map((cfg) => (
            <DimHealthFlag
              key={cfg.key}
              label={cfg.label}
              active={state.dimensional_health[cfg.key]}
              isGood={cfg.isGood}
              severity={cfg.severity}
            />
          ))}
        </div>
      )}

      {/* Field bars */}
      {!compact && (
        <div style={{ marginBottom: '6px' }}>
          {FIELD_CONFIG.map(({ key, label, color, invert }) => (
            <FieldBar
              key={key}
              label={label}
              value={state[key as keyof GAIAStateSnapshot] as number}
              color={color}
              invert={invert}
            />
          ))}
        </div>
      )}

      {/* Priority dimension */}
      {!compact && (
        <div style={{
          marginTop: '8px',
          padding: '5px 8px',
          borderRadius: '6px',
          background: 'rgba(255,255,255,0.04)',
          fontSize: '10px',
          color: '#777',
          letterSpacing: '0.5px',
        }}>
          Priority: <span style={{ color: '#aaa', fontWeight: 600 }}>
            {state.priority_dimension}
          </span>
        </div>
      )}

      {/* Footer — GAIAN ID + last update */}
      <div style={{
        marginTop: '8px',
        display: 'flex',
        justifyContent: 'space-between',
        fontSize: '9px',
        color: '#444',
      }}>
        <span>{state.gaian_id ?? 'GAIAN'}</span>
        {lastUpdate && (
          <span>{new Date(lastUpdate * 1000).toLocaleTimeString()}</span>
        )}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const hudContainerStyle: React.CSSProperties = {
  position: 'fixed',
  bottom: '20px',
  right: '20px',
  width: '220px',
  background: '#0d0d1a',
  border: '1px solid #333',
  borderRadius: '12px',
  padding: '14px',
  fontFamily: '\'JetBrains Mono\', \'Fira Code\', monospace',
  zIndex: 9999,
  userSelect: 'none',
  backdropFilter: 'blur(8px)',
};

export default StateHUD;
