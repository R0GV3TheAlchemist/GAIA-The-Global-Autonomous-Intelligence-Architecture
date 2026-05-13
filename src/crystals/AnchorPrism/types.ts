/**
 * AnchorPrism — Grounding & Context Memory Crystal
 *
 * Anchors are recurring beliefs, values, and commitments the user has expressed.
 * They decay over time if not reinforced — GAIA references them when giving
 * advice to stay contextually grounded.
 */

export type AnchorCategory =
  | 'value'       // Core values: e.g. "Sovereignty matters above convenience"
  | 'belief'      // Worldview: e.g. "Consciousness is non-local"
  | 'commitment'  // Active pledges: e.g. "Ship GAIA-OS before June"
  | 'boundary'    // Hard limits: e.g. "I don't sacrifice sleep for deadlines"
  | 'aspiration'; // Long-range goals: e.g. "Build something that outlives me"

export const CATEGORY_ICON: Record<AnchorCategory, string> = {
  value:       '⬡',
  belief:      '◈',
  commitment:  '◆',
  boundary:    '◉',
  aspiration:  '✦',
};

export const CATEGORY_LABEL: Record<AnchorCategory, string> = {
  value:       'Value',
  belief:      'Belief',
  commitment:  'Commitment',
  boundary:    'Boundary',
  aspiration:  'Aspiration',
};

/**
 * Anchor strength: 0–1.
 * Starts at 1.0 on creation / reinforcement.
 * Decays by DECAY_RATE_PER_DAY per day since last reinforcement.
 * Below DECAY_DORMANT_THRESHOLD → anchor is considered dormant.
 * Reaches 0 and is auto-archived at DECAY_ARCHIVE_THRESHOLD.
 */
export const DECAY_RATE_PER_DAY = 0.07;       // ~14 days to full decay from 1.0
export const DECAY_DORMANT_THRESHOLD = 0.35;  // Visual fade starts here
export const DECAY_ARCHIVE_THRESHOLD = 0.05;  // Auto-archive below this

export interface Anchor {
  id: string;
  text: string;
  category: AnchorCategory;
  /** 0–1, recomputed on read via computeStrength() */
  strength: number;
  createdAt: number;       // Unix ms
  lastReinforcedAt: number;
  reinforceCount: number;  // How many times the user has consciously reinforced this
  archived: boolean;
  note: string;            // Optional elaboration
}

/**
 * Compute current anchor strength based on time since last reinforcement.
 * Pure function — call on read, not on write.
 */
export function computeStrength(anchor: Anchor): number {
  const daysSince =
    (Date.now() - anchor.lastReinforcedAt) / 86_400_000;
  const decayed = anchor.strength - daysSince * DECAY_RATE_PER_DAY;
  return Math.max(0, Math.round(decayed * 1000) / 1000);
}

export interface AnchorPrismState {
  anchors: Anchor[];          // All non-archived, strength recomputed
  archived: Anchor[];         // Archived (auto or manual)
  /** Overall grounding score 0–10: avg strength of top-5 active anchors × 10 */
  groundingScore: number;
}

export function computeGrounding(anchors: Anchor[]): number {
  const active = anchors
    .filter((a) => !a.archived)
    .sort((a, b) => b.strength - a.strength)
    .slice(0, 5);
  if (active.length === 0) return 0;
  const avg = active.reduce((s, a) => s + a.strength, 0) / active.length;
  return Math.round(avg * 10 * 10) / 10;
}
