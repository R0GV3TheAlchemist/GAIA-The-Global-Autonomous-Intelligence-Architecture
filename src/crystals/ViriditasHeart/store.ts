/**
 * ViriditasHeart Store
 * In-memory vitality log with persistence hook ready for DEK ring encryption.
 * All data is sovereign-local; no data leaves the device.
 */

import type {
  WellbeingEntry,
  VitalityLog,
  ViriditasHeartState,
  MoodTier,
} from './types';
import { scoresToTier } from './types';

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------

let _entries: WellbeingEntry[] = [];
let _listeners: Array<(state: ViriditasHeartState) => void> = [];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _avgField(entries: WellbeingEntry[], field: 'energy' | 'mood'): number {
  if (entries.length === 0) return 0;
  const sum = entries.reduce((acc, e) => acc + e[field], 0);
  return Math.round((sum / entries.length) * 10) / 10;
}

function _computeTrend(entries: WellbeingEntry[]): 'up' | 'down' | 'stable' {
  if (entries.length < 2) return 'stable';
  const now = Date.now();
  const DAY = 86_400_000;
  const yesterday = entries.filter(
    (e) => e.timestamp > now - 2 * DAY && e.timestamp <= now - DAY,
  );
  const today = entries.filter((e) => e.timestamp > now - DAY);
  if (yesterday.length === 0 || today.length === 0) return 'stable';
  const yAvg = _avgField(yesterday, 'mood');
  const tAvg = _avgField(today, 'mood');
  if (tAvg - yAvg > 0.5) return 'up';
  if (yAvg - tAvg > 0.5) return 'down';
  return 'stable';
}

function _buildLog(): VitalityLog {
  const now = Date.now();
  const week = _entries.filter((e) => e.timestamp > now - 7 * 86_400_000);
  return {
    entries: [..._entries].sort((a, b) => b.timestamp - a.timestamp),
    weekAvgEnergy: _avgField(week, 'energy'),
    weekAvgMood: _avgField(week, 'mood'),
    trend: _computeTrend(_entries),
  };
}

function _buildState(isLogging = false): ViriditasHeartState {
  const log = _buildLog();
  return {
    log,
    latest: log.entries[0] ?? null,
    isLogging,
  };
}

function _notify(): void {
  const state = _buildState();
  _listeners.forEach((fn) => fn(state));
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Subscribe to state changes. Returns unsubscribe function.
 */
export function subscribe(
  listener: (state: ViriditasHeartState) => void,
): () => void {
  _listeners.push(listener);
  return () => {
    _listeners = _listeners.filter((l) => l !== listener);
  };
}

/**
 * Log a new wellbeing entry.
 */
export function logWellbeing(
  energy: number,
  mood: number,
  note = '',
  tags: string[] = [],
): WellbeingEntry {
  const tier: MoodTier = scoresToTier(mood, energy);
  const entry: WellbeingEntry = {
    id: `vh_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    timestamp: Date.now(),
    energy: Math.max(1, Math.min(10, energy)),
    mood: Math.max(1, Math.min(10, mood)),
    moodTier: tier,
    note,
    tags,
  };
  _entries.push(entry);
  _notify();
  return entry;
}

/**
 * Return the current vitality state snapshot.
 */
export function getVitality(): ViriditasHeartState {
  return _buildState();
}

/**
 * Return just the trend direction.
 */
export function getTrend(): 'up' | 'down' | 'stable' {
  return _computeTrend(_entries);
}

/**
 * Clear all entries (used in tests / reset flow).
 */
export function resetLog(): void {
  _entries = [];
  _notify();
}

/**
 * Hydrate from persisted data (called by DEK ring loader on mount).
 */
export function hydrateFromStorage(entries: WellbeingEntry[]): void {
  _entries = entries;
  _notify();
}
