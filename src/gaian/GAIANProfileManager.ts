/**
 * GAIANProfileManager.ts
 * Phase 1 — Load, Save, Create, Record, SessionOpen
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
} from './GAIANProfile';
import { createDefaultProfile, computeLCITrend } from './GAIANProfile';

// ---------------------------------------------------------------------------
// Store key helpers
// ---------------------------------------------------------------------------

const PROFILE_KEY = (id: string) => `gaian_profile_${id}`;
const RUNTIME_KEY = (id: string) => `gaian_last_runtime_${id}`;

const LCI_BASELINE_WINDOW = 30;

// ---------------------------------------------------------------------------
// Storage adapter — swap Tauri store, localStorage, or test mock
// ---------------------------------------------------------------------------

export interface ProfileStoreAdapter {
  get<T>(key: string): Promise<T | null>;
  set<T>(key: string, value: T): Promise<void>;
  delete(key: string): Promise<void>;
}

// ---------------------------------------------------------------------------
// TauriStoreAdapter — production adapter using @tauri-apps/plugin-store
// ---------------------------------------------------------------------------

export class TauriStoreAdapter implements ProfileStoreAdapter {
  private storeName: string;

  constructor(storeName = 'gaian_profiles.dat') {
    this.storeName = storeName;
  }

  private async getStore() {
    // Dynamic import so non-Tauri environments don't break at module load
    const { load } = await import('@tauri-apps/plugin-store');
    return load(this.storeName);
  }

  async get<T>(key: string): Promise<T | null> {
    const store = await this.getStore();
    const value = await store.get<T>(key);
    return value ?? null;
  }

  async set<T>(key: string, value: T): Promise<void> {
    const store = await this.getStore();
    await store.set(key, value);
    await store.save();
  }

  async delete(key: string): Promise<void> {
    const store = await this.getStore();
    await store.delete(key);
    await store.save();
  }
}

// ---------------------------------------------------------------------------
// GAIANProfileManager
// ---------------------------------------------------------------------------

export class GAIANProfileManager {
  private store: ProfileStoreAdapter;

  constructor(store?: ProfileStoreAdapter) {
    // Default to Tauri store in production; pass mock in tests
    this.store = store ?? new TauriStoreAdapter();
  }

  // Load — returns null if pre-birth
  async load(architectId: string): Promise<GAIANProfile | null> {
    return this.store.get<GAIANProfile>(PROFILE_KEY(architectId));
  }

  // Save — always use this, never touch store directly
  async save(profile: GAIANProfile): Promise<void> {
    await this.store.set(PROFILE_KEY(profile.architectId), profile);
  }

  // Create from birth — called exactly once per GAIAN per device
  async createFromBirth(birthResult: GaianBirthResult): Promise<GAIANProfile> {
    const existing = await this.load(birthResult.architectId);
    if (existing) {
      console.warn(`[GAIANProfileManager] Birth called for existing GAIAN ${birthResult.architectId}. Returning existing profile.`);
      return existing;
    }
    const profile = createDefaultProfile(birthResult);
    await this.save(profile);
    return profile;
  }

  /**
   * recordSessionOpen — called by GAIANRuntime.sessionInit()
   * Updates LCI history, trend, totalSessions, and last-known state
   * at the START of a session (before the user's first query).
   */
  async recordSessionOpen(
    architectId: string,
    sessionId: string,
    phi: number,
    timestamp: string,
  ): Promise<GAIANProfile | null> {
    const profile = await this.load(architectId);
    if (!profile) return null;

    const record: LCIRecord = {
      sessionId,
      phi,
      force: profile.lastKnownForce,
      stage: profile.lastKnownStage,
      timestamp,
    };

    const updatedHistory = [...profile.lciHistory, record];
    const window = updatedHistory.slice(-LCI_BASELINE_WINDOW);
    const newBaseline = window.reduce((s, r) => s + r.phi, 0) / window.length;
    const trend = computeLCITrend(updatedHistory, phi);

    const updated: GAIANProfile = {
      ...profile,
      lciHistory: updatedHistory,
      lciBaseline: newBaseline,
      lciTrend: trend,
      totalSessions: profile.totalSessions + 1,
      lastSessionTimestamp: timestamp,
      lastKnownPhi: phi,
    };

    await this.save(updated);
    return updated;
  }

  // recordSession — called at END of session with full RuntimeResult
  async recordSession(
    profile: GAIANProfile,
    result: RuntimeResult
  ): Promise<GAIANProfile> {
    const cadence = updateCadence(profile, result);
    const preferredForces = topN(profile.lciHistory.map((r) => r.force), 3);
    const preferredStages = topN(profile.lciHistory.map((r) => r.stage), 3);
    const queryPatterns = result.queryPatterns
      ? Array.from(new Set([...profile.queryPatterns, ...result.queryPatterns])).slice(-50)
      : profile.queryPatterns;

    const updated: GAIANProfile = {
      ...profile,
      sessionCadence: cadence,
      preferredForces,
      preferredStages,
      queryPatterns,
      lastKnownForce: result.force,
      lastKnownStage: result.stage,
    };

    await this.save(updated);
    await this.store.set(RUNTIME_KEY(profile.architectId), result);
    return updated;
  }

  // Derive PersonalizationSignal for RAGPipeline
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

  // Delete — total, no ghost records (Canon: deletion is complete)
  async delete(architectId: string): Promise<void> {
    await this.store.delete(PROFILE_KEY(architectId));
    await this.store.delete(RUNTIME_KEY(architectId));
  }

  // Offline fallback
  async getLastRuntimeResult(architectId: string): Promise<RuntimeResult | null> {
    return this.store.get<RuntimeResult>(RUNTIME_KEY(architectId));
  }
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function updateCadence(profile: GAIANProfile, result: RuntimeResult) {
  const hour = new Date(result.timestamp).getUTCHours();
  const hours = Array.from(new Set([...profile.sessionCadence.preferredHours, hour])).sort((a, b) => a - b);
  const n = profile.totalSessions;
  const prevAvg = profile.sessionCadence.avgSessionDuration;
  const newAvg = n === 0 ? result.durationMinutes : (prevAvg * n + result.durationMinutes) / (n + 1);
  return {
    preferredHours: hours.slice(-24),
    avgSessionDuration: Math.round(newAvg * 10) / 10,
    longestSession: Math.max(profile.sessionCadence.longestSession, result.durationMinutes),
  };
}

function topN(values: string[], n: number): string[] {
  const counts: Record<string, number> = {};
  for (const v of values) counts[v] = (counts[v] ?? 0) + 1;
  return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, n).map(([v]) => v);
}
