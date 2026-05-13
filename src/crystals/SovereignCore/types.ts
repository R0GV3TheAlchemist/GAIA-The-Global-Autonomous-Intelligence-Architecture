/**
 * SovereignCore — Identity, Agency & Sovereignty Crystal
 *
 * Controls how GAIA relates to the user's sense of self:
 * - Sovereign Mode: GAIA's operating posture toward user autonomy
 * - Boundary Rules: explicit lines GAIA must never cross
 * - Autonomy Flags: fine-grained consent toggles
 * - Consent Log: immutable audit trail of every sovereignty decision
 */

export type SovereignMode =
  | 'guardian'    // GAIA actively protects, may push back gently
  | 'ally'        // GAIA supports without judgment — default
  | 'mirror'      // GAIA reflects without steering
  | 'silent'      // GAIA answers only when spoken to
  | 'sovereign';  // Full autonomy — user defines every rule

export const SOVEREIGN_MODE_ICON: Record<SovereignMode, string> = {
  guardian:  '🛡',
  ally:      '🤝',
  mirror:    '🪞',
  silent:    '🌑',
  sovereign: '👑',
};

export const SOVEREIGN_MODE_LABEL: Record<SovereignMode, string> = {
  guardian:  'Guardian',
  ally:      'Ally',
  mirror:    'Mirror',
  silent:    'Silent',
  sovereign: 'Sovereign',
};

export const SOVEREIGN_MODE_DESC: Record<SovereignMode, string> = {
  guardian:  'GAIA monitors for patterns that conflict with your stated values and may gently surface them.',
  ally:      'GAIA supports your goals without unsolicited judgment. The balanced default.',
  mirror:    'GAIA reflects your words and frames back to you without steering or advising.',
  silent:    'GAIA waits. Responds only when directly asked. No proactive suggestions.',
  sovereign: 'You set every rule. GAIA follows your boundary list with zero override latitude.',
};

// ---------------------------------------------------------------------------
// Boundary Rules
// ---------------------------------------------------------------------------

export type BoundaryCategory =
  | 'topic'       // Never discuss this subject
  | 'tone'        // Never use this tone / register
  | 'behaviour'   // Never exhibit this behaviour
  | 'data'        // Never store / surface this data type
  | 'custom';     // Free-form

export const BOUNDARY_CATEGORY_ICON: Record<BoundaryCategory, string> = {
  topic:     '🚫',
  tone:      '🎙',
  behaviour: '⚡',
  data:      '🔒',
  custom:    '✦',
};

export interface BoundaryRule {
  id: string;
  category: BoundaryCategory;
  text: string;          // e.g. "Never mention my ex-partner"
  active: boolean;
  createdAt: number;     // Unix ms
}

// ---------------------------------------------------------------------------
// Autonomy Flags
// ---------------------------------------------------------------------------

export interface AutonomyFlag {
  id: string;
  label: string;
  description: string;
  enabled: boolean;
}

/** Built-in autonomy flags — user can toggle but not delete. */
export const DEFAULT_AUTONOMY_FLAGS: Omit<AutonomyFlag, 'enabled'>[] = [
  {
    id: 'af_proactive_checkins',
    label: 'Proactive check-ins',
    description: 'GAIA may initiate a check-in if it detects unusual patterns in your usage.',
  },
  {
    id: 'af_value_drift_alerts',
    label: 'Value drift alerts',
    description: 'GAIA surfaces a gentle note if your recent actions diverge from your AnchorPrism values.',
  },
  {
    id: 'af_emotional_reflection',
    label: 'Emotional reflection',
    description: 'GAIA may name the emotional tone it senses in a conversation and ask if it resonates.',
  },
  {
    id: 'af_memory_surfacing',
    label: 'Memory surfacing',
    description: 'GAIA may reference past conversations to add context to current ones.',
  },
  {
    id: 'af_dream_pattern_links',
    label: 'Dream pattern links',
    description: 'GAIA may connect recurring SomnusVeil dream symbols to waking topics.',
  },
  {
    id: 'af_boundary_reminders',
    label: 'Boundary reminders',
    description: 'GAIA confirms before taking any action that touches an active boundary rule.',
  },
];

// ---------------------------------------------------------------------------
// Consent Log
// ---------------------------------------------------------------------------

export type ConsentEventType =
  | 'mode_change'
  | 'boundary_added'
  | 'boundary_toggled'
  | 'boundary_removed'
  | 'flag_toggled';

export interface ConsentEvent {
  id: string;
  type: ConsentEventType;
  summary: string;       // Human-readable one-liner
  timestamp: number;
}

// ---------------------------------------------------------------------------
// Composite state
// ---------------------------------------------------------------------------

export interface SovereignCoreState {
  mode: SovereignMode;
  boundaries: BoundaryRule[];
  autonomyFlags: AutonomyFlag[];
  consentLog: ConsentEvent[]; // Newest first
  activeBoundaryCount: number;
  enabledFlagCount: number;
}
