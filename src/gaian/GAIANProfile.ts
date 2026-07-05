/**
 * GAIANProfile.ts
 * Phase 1 — Types, Storage, Re-exports
 *
 * The living record of a GAIAN across all sessions.
 * Not a user profile. A recognized presence.
 *
 * Canon: docs/canon/GAIAN_IDENTITY.md
 * Issue: #756
 *
 * NOTE: GAIANProfileManager and computeLCITrend are re-exported here
 * so GAIANRuntime.ts can import from a single path.
 */

// ---------------------------------------------------------------------------
// Core Identity
// ---------------------------------------------------------------------------

export interface GAIANProfile {
  // Identity
  architectId: string;
  displayName: string;
  birthTimestamp: string;
  birthForce: string;
  birthStage: string;

  // Constitutional layer (required by GAIANRuntime.buildProfileBlock)
  constitutional: ConstitutionalState;

  // Jungian / Crystal identity (required by buildProfileBlock)
  name: string;                  // Display alias (mirrors displayName)
  pronouns: string;
  jungianRole: string;
  preferredCrystal: string;

  // LCI
  lciBaseline: number;
  lciHistory: LCIRecord[];
  lciTrend: LCITrend;

  // Console Preferences
  activeModules: GAIANModule[];
  consoleLayout: ConsoleLayout;
  theme: string;
  orbParams: OrbParamOverride;

  // Personalization
  queryPatterns: string[];
  sessionCadence: SessionCadenceRecord;
  preferredForces: string[];
  preferredStages: string[];

  // Session Metadata
  totalSessions: number;
  lastSessionTimestamp: string;
  lastKnownPhi: number;
  lastKnownForce: string;
  lastKnownStage: string;

  // Akashic
  akashicLoaded: boolean;
  akashicVersion: string;

  // Schema
  schemaVersion: number;
}

// ---------------------------------------------------------------------------
// Constitutional State (governs service mode + safety gates)
// ---------------------------------------------------------------------------

export interface ConstitutionalState {
  serviceMode: 'STANDARD' | 'RECOVERY' | 'SUPERHUMAN' | 'SHADOW';
  ethicalGuardrailActive: boolean;
  humanModeActive: boolean;
  superhumanModeReady: boolean;
}

export function defaultConstitutionalState(): ConstitutionalState {
  return {
    serviceMode: 'STANDARD',
    ethicalGuardrailActive: true,
    humanModeActive: true,
    superhumanModeReady: false,
  };
}

// ---------------------------------------------------------------------------
// LCI
// ---------------------------------------------------------------------------

export type LCITrend = 'ascending' | 'stable' | 'descending' | 'volatile';

export interface LCIRecord {
  sessionId: string;
  phi: number;
  force: string;
  stage: string;
  timestamp: string;
}

/**
 * computeLCITrend — derives trend from history + current phi.
 * Re-exported here so GAIANRuntime can import from './GAIANProfile'.
 */
export function computeLCITrend(
  history: LCIRecord[],
  currentPhi: number
): LCITrend {
  if (history.length < 2) return 'stable';

  const recent = history.slice(-3).map((r) => r.phi);
  recent.push(currentPhi);

  const deltas = recent.slice(1).map((v, i) => v - recent[i]);
  const avgDelta = deltas.reduce((a, b) => a + b, 0) / deltas.length;

  // Volatile: direction reversal with magnitude
  const signs = deltas.map(Math.sign);
  const hasReversal = signs.some((s, i) => i > 0 && s !== 0 && s !== signs[i - 1]);
  if (hasReversal && deltas.some((d) => Math.abs(d) > 0.1)) return 'volatile';

  if (avgDelta > 0.05) return 'ascending';
  if (avgDelta < -0.05) return 'descending';
  return 'stable';
}

// ---------------------------------------------------------------------------
// Session Cadence
// ---------------------------------------------------------------------------

export interface SessionCadenceRecord {
  preferredHours: number[];
  avgSessionDuration: number;
  longestSession: number;
}

// ---------------------------------------------------------------------------
// Console Modules
// ---------------------------------------------------------------------------

export type GAIANModule =
  | 'crystal_view'
  | 'chat_view'
  | 'orb'
  | 'alignment_indicator'
  | 'greeting'
  | 'mood'
  | 'home_background'
  | 'picker';

export type ConsoleLayout = 'crystal' | 'chat' | 'orb' | 'minimal' | 'full';

// ---------------------------------------------------------------------------
// Orb
// ---------------------------------------------------------------------------

export interface OrbParamOverride {
  colorOverride?: string;
  sizeScale?: number;
  pulseRate?: number;
}

// ---------------------------------------------------------------------------
// Personalization Signal
// ---------------------------------------------------------------------------

export interface PersonalizationSignal {
  architectId: string;
  lciBaseline: number;
  lciTrend: LCITrend;
  preferredForces: string[];
  preferredStages: string[];
  queryPatterns: string[];
  sessionCadence: SessionCadenceRecord;
  consoleLayout: ConsoleLayout;
}

// ---------------------------------------------------------------------------
// Birth / Runtime shapes
// ---------------------------------------------------------------------------

export interface GaianBirthResult {
  architectId: string;
  displayName: string;
  birthTimestamp: string;
  birthForce: string;
  birthStage: string;
  initialPhi: number;
  pronouns?: string;
  jungianRole?: string;
  preferredCrystal?: string;
}

export interface RuntimeResult {
  sessionId: string;
  phi: number;
  force: string;
  stage: string;
  timestamp: string;
  durationMinutes: number;
  queryPatterns?: string[];
}

// ---------------------------------------------------------------------------
// Default profile factory
// ---------------------------------------------------------------------------

export function createDefaultProfile(birth: GaianBirthResult): GAIANProfile {
  return {
    architectId: birth.architectId,
    displayName: birth.displayName,
    name: birth.displayName,
    pronouns: birth.pronouns ?? 'they/them',
    jungianRole: birth.jungianRole ?? 'The Seeker',
    preferredCrystal: birth.preferredCrystal ?? 'Clear Quartz',
    birthTimestamp: birth.birthTimestamp,
    birthForce: birth.birthForce,
    birthStage: birth.birthStage,

    constitutional: defaultConstitutionalState(),

    lciBaseline: birth.initialPhi,
    lciHistory: [],
    lciTrend: 'stable',

    activeModules: [
      'crystal_view', 'chat_view', 'orb',
      'alignment_indicator', 'greeting', 'mood', 'home_background',
    ],
    consoleLayout: 'full',
    theme: 'viriditas_default',
    orbParams: {},

    queryPatterns: [],
    sessionCadence: { preferredHours: [], avgSessionDuration: 0, longestSession: 0 },
    preferredForces: [],
    preferredStages: [],

    totalSessions: 0,
    lastSessionTimestamp: birth.birthTimestamp,
    lastKnownPhi: birth.initialPhi,
    lastKnownForce: birth.birthForce,
    lastKnownStage: birth.birthStage,

    akashicLoaded: false,
    akashicVersion: '',
    schemaVersion: 1,
  };
}

// ---------------------------------------------------------------------------
// Re-export GAIANProfileManager so GAIANRuntime can import from one path
// ---------------------------------------------------------------------------
export { GAIANProfileManager } from './GAIANProfileManager';
