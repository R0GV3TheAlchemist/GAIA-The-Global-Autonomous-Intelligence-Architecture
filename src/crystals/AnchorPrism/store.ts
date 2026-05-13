/**
 * AnchorPrism Store
 * Sovereign-local anchor management.
 * hydrateFromStorage() ready for DEK ring integration.
 */

import type { Anchor, AnchorCategory, AnchorPrismState } from './types';
import {
  computeStrength,
  computeGrounding,
  DECAY_ARCHIVE_THRESHOLD,
} from './types';

// ---------------------------------------------------------------------------
// Internal state
// ---------------------------------------------------------------------------

let _anchors: Anchor[] = [];
let _listeners: Array<(state: AnchorPrismState) => void> = [];

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function _uid(): string {
  return `ap_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
}

/** Recompute all strength values and auto-archive dormant anchors. */
function _refreshStrengths(): void {
  _anchors = _anchors.map((a) => ({
    ...a,
    strength: computeStrength(a),
  }));
  // Auto-archive anchors that have fully decayed
  _anchors = _anchors.map((a) =>
    !a.archived && a.strength <= DECAY_ARCHIVE_THRESHOLD
      ? { ...a, archived: true }
      : a,
  );
}

function _buildState(): AnchorPrismState {
  _refreshStrengths();
  const active = _anchors.filter((a) => !a.archived);
  const archived = _anchors.filter((a) => a.archived);
  return {
    anchors: [...active].sort((a, b) => b.strength - a.strength),
    archived,
    groundingScore: computeGrounding(active),
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
  listener: (state: AnchorPrismState) => void,
): () => void {
  _listeners.push(listener);
  return () => {
    _listeners = _listeners.filter((l) => l !== listener);
  };
}

/** Add a new anchor at full strength. */
export function addAnchor(
  text: string,
  category: AnchorCategory,
  note = '',
): Anchor {
  const anchor: Anchor = {
    id: _uid(),
    text: text.trim(),
    category,
    strength: 1.0,
    createdAt: Date.now(),
    lastReinforcedAt: Date.now(),
    reinforceCount: 0,
    archived: false,
    note,
  };
  _anchors.push(anchor);
  _notify();
  return anchor;
}

/**
 * Reinforce an anchor — resets strength to 1.0 and increments counter.
 * Called when the user explicitly confirms an anchor still holds.
 */
export function reinforceAnchor(id: string): void {
  const anchor = _anchors.find((a) => a.id === id);
  if (!anchor) return;
  anchor.strength = 1.0;
  anchor.lastReinforcedAt = Date.now();
  anchor.reinforceCount += 1;
  _notify();
}

/** Manually archive an anchor. */
export function archiveAnchor(id: string): void {
  const anchor = _anchors.find((a) => a.id === id);
  if (!anchor) return;
  anchor.archived = true;
  _notify();
}

/** Restore an archived anchor at half strength. */
export function restoreAnchor(id: string): void {
  const anchor = _anchors.find((a) => a.id === id);
  if (!anchor) return;
  anchor.archived = false;
  anchor.strength = 0.5;
  anchor.lastReinforcedAt = Date.now();
  _notify();
}

/** Return current state snapshot. */
export function getAnchors(): AnchorPrismState {
  return _buildState();
}

/** Reset (tests / onboarding). */
export function resetPrism(): void {
  _anchors = [];
  _notify();
}

/** Hydrate from DEK ring storage. */
export function hydrateFromStorage(anchors: Anchor[]): void {
  _anchors = anchors;
  _notify();
}
