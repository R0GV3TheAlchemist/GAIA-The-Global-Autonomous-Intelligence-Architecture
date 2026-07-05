/**
 * GAIANProfile.ts
 * Phase 1 — Types & Storage
 *
 * The living record of a GAIAN across all sessions.
 * Not a user profile. A recognized presence.
 *
 * Canon: docs/canon/GAIAN_IDENTITY.md
 * Issue: #756
 */

// ---------------------------------------------------------------------------
// Core Identity
// ---------------------------------------------------------------------------

export interface GAIANProfile {
  // Identity
  architectId: string;           // Stable GAIAN identity anchor (from GaianBirth)
  displayName: string;           // Preferred name
  birthTimestamp: string;        // ISO 8601 — when this GAIAN was born
  birthForce: string;            // Spectral force at time of birth
  birthStage: string;            // MagnumOpus stage at time of birth

  // LCI History
  lciBaseline: number;           // Rolling 30-session average phi
  lciHistory: LCIRecord[];       // Per-session phi snapshots
  lciTrend: LCITrend;            // Current trajectory

  // Console Preferences
  activeModules: GAIANModule[];  // Which console modules are active
  consoleLayout: ConsoleLayout;  // Layout preference
  theme: string;                 // ViriditasTheme key
  orbParams: OrbParamOverride;   // Per-profile orb customization

  // Personalization Signals
  queryPatterns: string[];           // Top recurring query categories
  sessionCadence: SessionCadenceRecord; // When does this GAIAN typically engage?
  preferredForces: string[];         // Spectral forces this GAIAN resonates with most
  preferredStages: string[];         // MagnumOpus stages most frequently occupied

  // Session Metadata
  totalSessions: number;
  lastSessionTimestamp: string;
  lastKnownPhi: number;
  lastKnownForce: string;
  lastKnownStage: string;

  // Akashic Link
  akashicLoaded: boolean;
  akashicVersion: string;        // Last Akashic record version hash

  // Schema versioning for future migrations
  schemaVersion: number;
}

// ---------------------------------------------------------------------------
// LCI (Living Coherence Index)
// ---------------------------------------------------------------------------

export type LCITrend = 'ascending' | 'stable' | 'descending' | 'volatile';

export interface LCIRecord {
  sessionId: string;
  phi: number;
  force: string;
  stage: string;
  timestamp: string;             // ISO 8601
}

// ---------------------------------------------------------------------------
// Session Cadence
// ---------------------------------------------------------------------------

export interface SessionCadenceRecord {
  preferredHours: number[];      // 0–23 UTC hours most active
  avgSessionDuration: number;    // minutes
  longestSession: number;        // minutes
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
// Orb Customization
// ---------------------------------------------------------------------------

export interface OrbParamOverride {
  colorOverride?: string;        // Hex color, if user has personalized
  sizeScale?: number;            // 0.5–2.0 multiplier
  pulseRate?: number;            // Beats per minute
}

// ---------------------------------------------------------------------------
// Personalization Signal (fed into RAGPipeline)
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
// GaianBirth result shape (consumed by createFromBirth)
// ---------------------------------------------------------------------------

export interface GaianBirthResult {
  architectId: string;
  displayName: string;
  birthTimestamp: string;
  birthForce: string;
  birthStage: string;
  initialPhi: number;
}

// ---------------------------------------------------------------------------
// RuntimeResult shape (consumed by recordSession)
// ---------------------------------------------------------------------------

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
    birthTimestamp: birth.birthTimestamp,
    birthForce: birth.birthForce,
    birthStage: birth.birthStage,

    lciBaseline: birth.initialPhi,
    lciHistory: [],
    lciTrend: 'stable',

    activeModules: [
      'crystal_view',
      'chat_view',
      'orb',
      'alignment_indicator',
      'greeting',
      'mood',
      'home_background',
    ],
    consoleLayout: 'full',
    theme: 'viriditas_default',
    orbParams: {},

    queryPatterns: [],
    sessionCadence: {
      preferredHours: [],
      avgSessionDuration: 0,
      longestSession: 0,
    },
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
