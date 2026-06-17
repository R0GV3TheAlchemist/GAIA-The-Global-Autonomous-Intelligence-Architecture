/**
 * GaiaStateHUD.tsx
 *
 * Read-only live HUD strip showing:
 *   • Mode badge (colour-coded per GAIAMode)
 *   • Six field bars: coherence, energy, stress, entropy, learning, exploration
 *   • Active dimensional flags (D1–D6)
 *   • Priority dimension label
 *   • Active talisman count badge
 *   • Connection state indicator
 *
 * Consumes the snapshot + metadata already fetched by the parent
 * GaiaStatePanel via useGaiaState. No data-fetching here.
 *
 * Canon: GAIA_D6_META_COHERENCE_ENGINE, C52, #576, #580
 */

import React from 'react';
import type { GAIAMode, GAIAStateSnapshot } from '../hooks/useGaiaState';

// ── Mode palette ─────────────────────────────────────────────────────────────

const MODE_META: Record<GAIAMode, { label: string; emoji: string; color: string }> = {
  REST:      { label: 'Rest',      emoji: '🌙', color: '#6b7fab' },
  RESEARCH:  { label: 'Research',  emoji: '🔭', color: '#7c9ef5' },
  BUILD:     { label: 'Build',     emoji: '⚡', color: '#f5c842' },
  CREATE:    { label: 'Create',    emoji: '✨', color: '#42e8d5' },
  REFLECT:   { label: 'Reflect',   emoji: '🔮', color: '#b28aff' },
  INTEGRATE: { label: 'Integrate', emoji: '⬡',  color: '#5ec9f5' },
  TRANSMIT:  { label: 'Transmit',  emoji: '📡', color: '#f57c42' },
  PROTECT:   { label: 'Protect',   emoji: '🛡️', color: '#f55c5c' },
  RECOVER:   { label: 'Recover',   emoji: '🌿', color: '#5cf592' },
  HIBERNATE: { label: 'Hibernate', emoji: '🌑', color: '#4a5568' },
};

// ── Field bars ───────────────────────────────────────────────────────────────

interface FieldBarProps {
  label: string;
  value: number;   // 0-1
  inverted?: boolean; // stress & entropy: low = good
  color?: string;
}

function FieldBar({ label, value, inverted = false, color }: FieldBarProps) {
  const pct = Math.round(value * 100);
  const health = inverted ? 1 - value : value;
  const barColor = color ?? (health > 0.6 ? '#42e8d5' : health > 0.35 ? '#f5c842' : '#f55c5c');

  return (
    <div className="gaia-hud__field">
      <span className="gaia-hud__field-label">{label}</span>
      <div className="gaia-hud__field-track">
        <div
          className="gaia-hud__field-fill"
          style={{ width: `${pct}%`, backgroundColor: barColor }}
        />
      </div>
      <span className="gaia-hud__field-pct">{pct}%</span>
    </div>
  );
}

// ── Dimensional flags ─────────────────────────────────────────────────────────

function DimFlags({ state }: { state: GAIAStateSnapshot }) {
  const flags: Array<{ key: keyof GAIAStateSnapshot; label: string; color: string; severity: 'critical' | 'warn' | 'good' }> = [
    { key: 'd1_physical_integrity',  label: 'D1 Physical',  color: '#f55c5c', severity: 'critical' },
    { key: 'd2_emotional_coherence', label: 'D2 Emotional', color: '#f5a742', severity: 'warn' },
    { key: 'd3_mental_clarity',      label: 'D3 Mental',    color: '#f5c842', severity: 'warn' },
    { key: 'd4_social_resonance',    label: 'D4 Social',    color: '#7c9ef5', severity: 'warn' },
    { key: 'd6_unity_field_active',  label: 'D6 Unity ≈',  color: '#42e8d5', severity: 'good'  },
  ];

  const active = flags.filter((f) => state[f.key] === true);
  if (active.length === 0) return null;

  return (
    <div className="gaia-hud__flags">
      {active.map((f) => (
        <span
          key={f.key as string}
          className={`gaia-hud__flag gaia-hud__flag--${f.severity}`}
          style={{ borderColor: f.color, color: f.color }}
        >
          {f.label}
        </span>
      ))}
    </div>
  );
}

// ── Props ─────────────────────────────────────────────────────────────────────

export interface GaiaStateHUDProps {
  state: GAIAStateSnapshot | null;
  activeTalismanCount?: number;
  loading?: boolean;
  error?: string | null;
}

// ── Component ─────────────────────────────────────────────────────────────────

export function GaiaStateHUD({ state, activeTalismanCount = 0, loading, error }: GaiaStateHUDProps) {
  if (loading && !state) {
    return <div className="gaia-hud gaia-hud--loading"><span>⬡ Loading GAIA state…</span></div>;
  }

  if (error && !state) {
    return <div className="gaia-hud gaia-hud--error"><span>⚠ {error}</span></div>;
  }

  if (!state) return null;

  const meta = MODE_META[state.mode] ?? MODE_META.REST;

  return (
    <div className="gaia-hud">
      {/* Mode badge */}
      <div className="gaia-hud__mode" style={{ borderColor: meta.color, color: meta.color }}>
        <span className="gaia-hud__mode-emoji">{meta.emoji}</span>
        <span className="gaia-hud__mode-label">{meta.label}</span>
        {activeTalismanCount > 0 && (
          <span className="gaia-hud__talisman-badge">{activeTalismanCount}</span>
        )}
      </div>

      {/* Priority dimension */}
      {state.priority_dimension && (
        <div className="gaia-hud__priority">{state.priority_dimension}</div>
      )}

      {/* Dimensional flags */}
      <DimFlags state={state} />

      {/* Six field bars */}
      <div className="gaia-hud__fields">
        <FieldBar label="Coherence"   value={state.coherence} />
        <FieldBar label="Energy"      value={state.energy} />
        <FieldBar label="Stress"      value={state.stress}      inverted />
        <FieldBar label="Entropy"     value={state.entropy}     inverted />
        <FieldBar label="Learning"    value={state.learning_rate} />
        <FieldBar label="Exploration" value={state.exploration_rate} />
      </div>

      {/* Error overlay (stale data) */}
      {error && (
        <div className="gaia-hud__stale-error">⚠ {error}</div>
      )}
    </div>
  );
}

export default GaiaStateHUD;
