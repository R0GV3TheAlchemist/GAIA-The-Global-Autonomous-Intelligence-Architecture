/**
 * ViriditasHeart — Vitality & Wellbeing Crystal
 * Types for all wellbeing data structures.
 */

export type MoodTier =
  | 'radiant'    // 9–10  — peak vitality
  | 'flourishing'// 7–8   — strong, grounded
  | 'steady'     // 5–6   — baseline, okay
  | 'low'        // 3–4   — drained, struggling
  | 'critical';  // 1–2   — crisis / very low

export interface WellbeingEntry {
  id: string;
  timestamp: number;          // Unix ms
  energy: number;             // 1–10
  mood: number;               // 1–10
  moodTier: MoodTier;
  note: string;               // Optional free-text
  tags: string[];             // e.g. ['stressed', 'creative', 'tired']
}

export interface VitalityLog {
  entries: WellbeingEntry[];
  /** Rolling 7-day average energy */
  weekAvgEnergy: number;
  /** Rolling 7-day average mood */
  weekAvgMood: number;
  /** Direction vs yesterday's average: 'up' | 'down' | 'stable' */
  trend: 'up' | 'down' | 'stable';
}

export interface ViriditasHeartState {
  log: VitalityLog;
  latest: WellbeingEntry | null;
  isLogging: boolean;
}

/** Maps MoodTier → CSS custom property accent override */
export const TIER_ACCENT: Record<MoodTier, string> = {
  radiant:    'var(--color-success)',
  flourishing:'var(--color-primary)',
  steady:     'var(--color-blue)',
  low:        'var(--color-warning)',
  critical:   'var(--color-error)',
};

export const TIER_LABEL: Record<MoodTier, string> = {
  radiant:    '✦ Radiant',
  flourishing:'◈ Flourishing',
  steady:     '◇ Steady',
  low:        '◌ Low',
  critical:   '○ Critical',
};

export function scoresToTier(mood: number, energy: number): MoodTier {
  const avg = (mood + energy) / 2;
  if (avg >= 9) return 'radiant';
  if (avg >= 7) return 'flourishing';
  if (avg >= 5) return 'steady';
  if (avg >= 3) return 'low';
  return 'critical';
}
