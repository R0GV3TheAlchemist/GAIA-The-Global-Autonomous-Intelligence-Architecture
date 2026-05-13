/**
 * SovereignCore Store
 * Sovereign-local identity & agency state.
 */

import type {
  SovereignMode,
  BoundaryRule,
  BoundaryCategory,
  AutonomyFlag,
  ConsentEvent,
  ConsentEventType,
  SovereignCoreState,
} from './types';
import { DEFAULT_AUTONOMY_FLAGS } from './types';

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------

let _mode: SovereignMode = 'ally';
let _boundaries: BoundaryRule[] = [];
let _autonomyFlags: AutonomyFlag[] = DEFAULT_AUTONOMY_FLAGS.map((f) => ({
  ...f,
  enabled: true,
}));
let _consentLog: ConsentEvent[] = [];
let _listeners: Array<(state: SovereignCoreState) => void> = [];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _uid(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
}

function _log(type: ConsentEventType, summary: string): void {
  _consentLog.unshift({
    id: _uid('ce'),
    type,
    summary,
    timestamp: Date.now(),
  });
  // Cap log at 100 entries
  if (_consentLog.length > 100) _consentLog = _consentLog.slice(0, 100);
}

function _buildState(): SovereignCoreState {
  return {
    mode: _mode,
    boundaries: [..._boundaries].sort((a, b) => b.createdAt - a.createdAt),
    autonomyFlags: [..._autonomyFlags],
    consentLog: [..._consentLog],
    activeBoundaryCount: _boundaries.filter((b) => b.active).length,
    enabledFlagCount: _autonomyFlags.filter((f) => f.enabled).length,
  };
}

function _notify(): void {
  const state = _buildState();
  _listeners.forEach((fn) => fn(state));
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function subscribe(
  listener: (state: SovereignCoreState) => void,
): () => void {
  _listeners.push(listener);
  return () => {
    _listeners = _listeners.filter((l) => l !== listener);
  };
}

/** Set GAIA's sovereign operating mode. */
export function setMode(mode: SovereignMode): void {
  const prev = _mode;
  _mode = mode;
  _log('mode_change', `Mode changed: ${prev} → ${mode}`);
  _notify();
}

/** Add a new boundary rule. */
export function addBoundary(
  text: string,
  category: BoundaryCategory,
): BoundaryRule {
  const rule: BoundaryRule = {
    id: _uid('br'),
    category,
    text: text.trim(),
    active: true,
    createdAt: Date.now(),
  };
  _boundaries.push(rule);
  _log('boundary_added', `Boundary added [${category}]: "${rule.text.slice(0, 60)}"`);
  _notify();
  return rule;
}

/** Toggle a boundary rule active/inactive. */
export function toggleBoundary(id: string): void {
  const rule = _boundaries.find((b) => b.id === id);
  if (!rule) return;
  rule.active = !rule.active;
  _log(
    'boundary_toggled',
    `Boundary ${rule.active ? 'activated' : 'paused'}: "${rule.text.slice(0, 60)}"`,
  );
  _notify();
}

/** Permanently remove a boundary rule. */
export function removeBoundary(id: string): void {
  const rule = _boundaries.find((b) => b.id === id);
  if (!rule) return;
  _boundaries = _boundaries.filter((b) => b.id !== id);
  _log('boundary_removed', `Boundary removed: "${rule.text.slice(0, 60)}"`);
  _notify();
}

/** Toggle an autonomy flag on/off. */
export function toggleFlag(id: string): void {
  const flag = _autonomyFlags.find((f) => f.id === id);
  if (!flag) return;
  flag.enabled = !flag.enabled;
  _log(
    'flag_toggled',
    `Flag "${flag.label}" ${flag.enabled ? 'enabled' : 'disabled'}`,
  );
  _notify();
}

/** Return current state snapshot. */
export function getSovereign(): SovereignCoreState {
  return _buildState();
}

/** Reset to defaults (onboarding / tests). */
export function resetSovereign(): void {
  _mode = 'ally';
  _boundaries = [];
  _autonomyFlags = DEFAULT_AUTONOMY_FLAGS.map((f) => ({ ...f, enabled: true }));
  _consentLog = [];
  _notify();
}

/** Hydrate from DEK ring storage. */
export function hydrateFromStorage(
  mode: SovereignMode,
  boundaries: BoundaryRule[],
  autonomyFlags: AutonomyFlag[],
  consentLog: ConsentEvent[],
): void {
  _mode = mode;
  _boundaries = boundaries;
  _autonomyFlags = autonomyFlags;
  _consentLog = consentLog;
  _notify();
}
