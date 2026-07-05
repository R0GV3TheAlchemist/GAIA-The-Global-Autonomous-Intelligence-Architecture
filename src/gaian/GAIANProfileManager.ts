/**
 * GAIANProfileManager.ts
 * Phase 1 — Load, Save, Create, Record
 *
 * The steward of GAIAN identity across sessions.
 * All reads and writes to GAIANProfile pass through here.
 * No component touches the store directly.
 *
 * Canon: docs/canon/GAIAN_IDENTITY.md
 * Issue: #756
 */

import type {
  GAIANProfile,
  GaianBirthResult,
  RuntimeResult,
  PersonalizationSignal,
  LCIRecord,
  LCITrend,
} from './GAIANProfile';
import { createDefaultProfile } from './GAIANProfile';

// ---------------------------------------------------------------------------
// Store key convention
// ---------------------------------------------------------------------------

const PROFILE_STORE_KEY = (architectId: string) =>
  `gaian_profile_${architectId}`;

const LAST_RUNTIME_KEY = (architectId: string) =>
  `gaian_last_runtime_${architectId}`;

// LCI baseline rolling window
const LCI_BASELINE_WINDOW = 30;

// ---------------------------------------------------------------------------
// Storage adapter interface
// Abstracted so we can swap Tauri store, localStorage, or test mock
// ---------------------------------------------------------------------------

export interface ProfileStoreAdapter {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T): Promise<void>;
  delete(key: string): Promise<void>;
}

// ---------------------------------------------------------------------------
// GAIANProfileManager
// ---------------------------------------------------------------------------

export class GAIANProfileManager {
  private store: ProfileStoreAdapter;

  constructor(store: ProfileStoreAdapter) {
    this.store = store;
  }

  // -------------------------------------------------------------------------
  // Load profile for a given architectId
  // Returns null if no profile exists (pre-birth state)
  // -------------------------------------------------------------------------
  async load(architectId: string): Promise<GAIANProfile | null> {
    return this.store.get<GAIANProfile>(PROFILE_STORE_KEY(architectId));
  }

  // -------------------------------------------------------------------------
  // Save profile — always use this, never write to store directly
  // -------------------------------------------------------------------------
  async save(profile: GAIANProfile): Promise<void> {
    await this.store.set(PROFILE_STORE_KEY(profile.architectId), profile);
  }

  // -------------------------------------------------------------------------
  // Create a new profile from a GaianBirth result
  // Called exactly once per GAIAN per device
  // -------------------------------------------------------------------------
  async createFromBirth(birthResult: GaianBirthResult): Promise<GAIANProfile> {
    const existing = await this.load(birthResult.architectId);
    if (existing) {
      // Birth has already occurred — return existing profile
      // Canon: architectId is never regenerated
      console.warn(
        `[GAIANProfileManager] Birth called for existing GAIAN ${birthResult.architectId}. Returning existing profile.`
      );
      return existing;
    }

    const profile = createDefaultProfile(birthResult);
    await this.save(profile);
    return profile;
  }

  // -------------------------------------------------------------------------
  // Record a completed session into the profile
  // Updates LCI history, baseline, trend, cadence, and last-known state
  // -------------------------------------------------------------------------
  async recordSession(
    profile: GAIANProfile,
    result: RuntimeResult
  ): Promise<GAIANProfile> {
    const record: LCIRecord = {
      sessionId: result.sessionId,
      phi: result.phi,
      force: result.force,
      stage: result.stage,
      timestamp: result.timestamp,
    };

    const updatedHistory = [...profile.lciHistory, record];

    // Rolling baseline over last N sessions
    const window = updatedHistory.slice(-LCI_BASELINE_WINDOW);
    const newBaseline =
      window.reduce((sum, r) => sum + r.phi, 0) / window.length;

    // Derive trend from last 3 sessions
    const trend = deriveTrend(updatedHistory);

    // Update session cadence
    const cadence = updateCadence(profile, result);

    // Update preferred forces and stages (top 3 by frequency)
    const preferredForces = topN(
      updatedHistory.map((r) => r.force),
      3
    );
    const preferredStages = topN(
      updatedHistory.map((r) => r.stage),
      3
    );

    // Merge query patterns
    const queryPatterns = result.queryPatterns
      ? Array.from(
          new Set([...profile.queryPatterns, ...result.queryPatterns])
        ).slice(-50)
      : profile.queryPatterns;

    const updated: GAIANProfile = {
      ...profile,
      lciHistory: updatedHistory,
      lciBaseline: newBaseline,
      lciTrend: trend,
      sessionCadence: cadence,
      preferredForces,
      preferredStages,
      queryPatterns,
      totalSessions: profile.totalSessions + 1,
      lastSessionTimestamp: result.timestamp,
      lastKnownPhi: result.phi,
      lastKnownForce: result.force,
      lastKnownStage: result.stage,
    };

    await this.save(updated);

    // Cache last runtime result for offline fallback
    await this.store.set(LAST_RUNTIME_KEY(profile.architectId), result);

    return updated;
  }

  // -------------------------------------------------------------------------
  // Derive PersonalizationSignal for RAGPipeline
  // -------------------------------------------------------------------------
  derivePersonalizationSignal(profile: GAIANProfile): PersonalizationSignal {
    return {
      architectId: profile.architectId,
      lciBaseline: profile.lciBaseline,
      lciTrend: profile.lciTrend,
      preferredForces: profile.preferredForces,
      preferredStages: profile.preferredStages,
      queryPatterns: profile.queryPatterns,
      sessionCadence: profile.sessionCadence,
      consoleLayout: profile.consoleLayout,
    };
  }

  // -------------------------------------------------------------------------
  // Delete profile — total, no ghost records
  // Canon: deletion is complete and immediate
  // -------------------------------------------------------------------------
  async delete(architectId: string): Promise<void> {
    await this.store.delete(PROFILE_STORE_KEY(architectId));
    await this.store.delete(LAST_RUNTIME_KEY(architectId));
  }

  // -------------------------------------------------------------------------
  // Get last cached runtime result (offline fallback)
  // -------------------------------------------------------------------------
  async getLastRuntimeResult(architectId: string): Promise<RuntimeResult | null> {
    return this.store.get<RuntimeResult>(LAST_RUNTIME_KEY(architectId));
  }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

function deriveTrend(history: LCIRecord[]): LCITrend {
  if (history.length < 3) return 'stable';

  const recent = history.slice(-3).map((r) => r.phi);
  const [a, b, c] = recent;

  const delta1 = b - a;
  const delta2 = c - b;

  // Volatile: direction reversal with significant magnitude
  if (Math.sign(delta1) !== Math.sign(delta2) && Math.abs(delta1) + Math.abs(delta2) > 0.3) {
    return 'volatile';
  }

  const avgDelta = (delta1 + delta2) / 2;

  if (avgDelta > 0.05) return 'ascending';
  if (avgDelta < -0.05) return 'descending';
  return 'stable';
}

function updateCadence(
  profile: GAIANProfile,
  result: RuntimeResult
) {
  const hour = new Date(result.timestamp).getUTCHours();
  const hours = Array.from(
    new Set([...profile.sessionCadence.preferredHours, hour])
  ).sort((a, b) => a - b);

  const prevAvg = profile.sessionCadence.avgSessionDuration;
  const n = profile.totalSessions;
  const newAvg =
    n === 0
      ? result.durationMinutes
      : (prevAvg * n + result.durationMinutes) / (n + 1);

  const longest = Math.max(
    profile.sessionCadence.longestSession,
    result.durationMinutes
  );

  return {
    preferredHours: hours.slice(-24),
    avgSessionDuration: Math.round(newAvg * 10) / 10,
    longestSession: longest,
  };
}

function topN(values: string[], n: number): string[] {
  const counts: Record<string, number> = {};
  for (const v of values) {
    counts[v] = (counts[v] ?? 0) + 1;
  }
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n)
    .map(([v]) => v);
}
