/**
 * ClarusLens Store
 * In-memory focus & intention state.
 * hydrateFromStorage() ready for DEK ring integration.
 */

import type { FocusArea, Intention, ClarusLensState, FocusStatus } from './types';
import { computeClarity } from './types';

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------

let _focusAreas: FocusArea[] = [];
let _intentions: Intention[] = [];
let _listeners: Array<(state: ClarusLensState) => void> = [];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _buildState(): ClarusLensState {
  const sorted = [..._intentions].sort((a, b) => a.createdAt - b.createdAt);
  const current = [...sorted].reverse().find((i) => i.completedAt === null) ?? null;
  return {
    focusAreas: [..._focusAreas],
    intentions: sorted,
    currentIntention: current,
    clarity: computeClarity(sorted, _focusAreas),
  };
}

function _notify(): void {
  const state = _buildState();
  _listeners.forEach((fn) => fn(state));
}

function _uid(prefix: string): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export function subscribe(
  listener: (state: ClarusLensState) => void,
): () => void {
  _listeners.push(listener);
  return () => {
    _listeners = _listeners.filter((l) => l !== listener);
  };
}

/** Set a new active intention, optionally linked to a focus area. */
export function setIntention(
  text: string,
  focusAreaId: string | null = null,
): Intention {
  const intention: Intention = {
    id: _uid('cl_int'),
    text: text.trim(),
    focusAreaId,
    createdAt: Date.now(),
    completedAt: null,
    followThrough: null,
  };
  _intentions.push(intention);
  // Touch the linked focus area
  if (focusAreaId) {
    const area = _focusAreas.find((a) => a.id === focusAreaId);
    if (area) area.lastTouchedAt = Date.now();
  }
  _notify();
  return intention;
}

/** Mark the current intention complete with an optional follow-through score (0–1). */
export function completeIntention(
  id: string,
  followThrough: number | null = null,
): void {
  const intention = _intentions.find((i) => i.id === id);
  if (!intention) return;
  intention.completedAt = Date.now();
  intention.followThrough = followThrough;
  _notify();
}

/** Add or update a focus area. */
export function addFocusArea(label: string): FocusArea {
  const existing = _focusAreas.find(
    (a) => a.label.toLowerCase() === label.toLowerCase(),
  );
  if (existing) {
    existing.status = 'active';
    existing.lastTouchedAt = Date.now();
    _notify();
    return existing;
  }
  const area: FocusArea = {
    id: _uid('cl_area'),
    label: label.trim(),
    status: 'active',
    createdAt: Date.now(),
    lastTouchedAt: Date.now(),
  };
  _focusAreas.push(area);
  _notify();
  return area;
}

/** Update status of a focus area. */
export function setFocusAreaStatus(id: string, status: FocusStatus): void {
  const area = _focusAreas.find((a) => a.id === id);
  if (!area) return;
  area.status = status;
  _notify();
}

/** Return current state snapshot. */
export function getCurrentFocus(): ClarusLensState {
  return _buildState();
}

/** Return current clarity score only. */
export function getClarity(): number {
  return _buildState().clarity.total;
}

/** Reset all state (tests / onboarding reset). */
export function resetLens(): void {
  _focusAreas = [];
  _intentions = [];
  _notify();
}

/** Hydrate from persisted storage (DEK ring). */
export function hydrateFromStorage(
  focusAreas: FocusArea[],
  intentions: Intention[],
): void {
  _focusAreas = focusAreas;
  _intentions = intentions;
  _notify();
}
