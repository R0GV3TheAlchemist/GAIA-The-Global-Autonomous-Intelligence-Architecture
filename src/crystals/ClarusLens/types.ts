/**
 * ClarusLens — Clarity & Focus Crystal
 * Types for intentions, focus areas, and the clarity score model.
 */

export type FocusStatus = 'active' | 'paused' | 'completed';

export interface FocusArea {
  id: string;
  label: string;          // e.g. "GAIA-OS", "Health", "Music"
  status: FocusStatus;
  createdAt: number;      // Unix ms
  lastTouchedAt: number;  // Updated each time an intention references this area
}

export interface Intention {
  id: string;
  text: string;           // The stated intention, e.g. "Ship ClarusLens today"
  focusAreaId: string | null;
  createdAt: number;
  completedAt: number | null;
  /** 0–1 confidence the user followed through, set by GAIA on next check-in */
  followThrough: number | null;
}

/**
 * Clarity score 0–10.
 * Derived from:
 *   - recency of last intention set             (0–3)
 *   - number of active focus areas (sweet spot: 1–3) (0–3)
 *   - follow-through rate on recent intentions  (0–4)
 */
export interface ClarityBreakdown {
  recency: number;        // 0–3
  focusBalance: number;   // 0–3
  followThrough: number;  // 0–4
  total: number;          // 0–10
}

export interface ClarusLensState {
  focusAreas: FocusArea[];
  intentions: Intention[];
  currentIntention: Intention | null;
  clarity: ClarityBreakdown;
}

// ---------------------------------------------------------------------------
// Clarity computation (pure)
// ---------------------------------------------------------------------------

export function computeClarity(
  intentions: Intention[],
  focusAreas: FocusArea[],
): ClarityBreakdown {
  // Recency: full score if intention set within 4h, decays to 0 at 48h
  const latest = intentions[intentions.length - 1];
  let recency = 0;
  if (latest) {
    const ageHours = (Date.now() - latest.createdAt) / 3_600_000;
    recency = Math.max(0, 3 - (ageHours / 48) * 3);
    recency = Math.round(recency * 10) / 10;
  }

  // Focus balance: 1 area = 2, 2–3 areas = 3, 0 or 4+ = 1, >6 = 0
  const active = focusAreas.filter((f) => f.status === 'active').length;
  let focusBalance = 0;
  if (active === 1) focusBalance = 2;
  else if (active >= 2 && active <= 3) focusBalance = 3;
  else if (active === 4) focusBalance = 2;
  else if (active === 5) focusBalance = 1;
  else if (active > 5) focusBalance = 0;

  // Follow-through: avg of last 5 completed intentions
  const completed = intentions
    .filter((i) => i.followThrough !== null)
    .slice(-5);
  let followThrough = 0;
  if (completed.length > 0) {
    const avg =
      completed.reduce((s, i) => s + (i.followThrough ?? 0), 0) /
      completed.length;
    followThrough = Math.round(avg * 4 * 10) / 10;
  }

  const total =
    Math.round((recency + focusBalance + followThrough) * 10) / 10;

  return { recency, focusBalance, followThrough, total };
}

export function clarityLabel(score: number): string {
  if (score >= 8.5) return '◈ Crystal Clear';
  if (score >= 6.5) return '◇ Focused';
  if (score >= 4.5) return '◆ Forming';
  if (score >= 2.5) return '◉ Scattered';
  return '○ Adrift';
}

export function clarityAccent(score: number): string {
  if (score >= 8.5) return 'var(--color-success)';
  if (score >= 6.5) return 'var(--color-primary)';
  if (score >= 4.5) return 'var(--color-blue)';
  if (score >= 2.5) return 'var(--color-warning)';
  return 'var(--color-error)';
}
