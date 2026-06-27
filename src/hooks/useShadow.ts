/**
 * src/hooks/useShadow.ts
 * React hook for the Shadow Engine.
 *
 * Usage:
 *   const shadow = useShadow(principalId);
 *
 *   // Read state
 *   shadow.record            — ShadowRecord | null
 *   shadow.loading           — boolean
 *   shadow.error             — string | null
 *   shadow.isActivated       — boolean  (intensity ≥ 0.35)
 *   shadow.intensityLevel    — 'dormant' | 'stirring' | 'active' | 'dominant' | 'consuming'
 *   shadow.integrationStage  — 'unmet' | 'awareness' | 'engagement' | 'embodiment' | 'integrated'
 *   shadow.dominantArchetype — string | null
 *   shadow.scores            — Record<ShadowArchetypeName, number> | null
 *
 *   // Actions
 *   shadow.evaluate(inputs?)  — run full archetype scoring
 *   shadow.reflect()          — record a reflection session (+0.05 integration)
 *   shadow.refresh()          — fetch latest cached record from backend
 *   shadow.clearError()       — dismiss error state
 *
 * Optional auto-polling:
 *   useShadow(principalId, { pollMs: 30_000 })
 */

import { useSyncExternalStore, useCallback, useEffect } from 'react';
import { shadowStore } from '../store/shadowStore';
import {
  type ShadowInputsPayload,
  type ShadowArchetypeName,
  intensityLevel,
  integrationStage,
} from '../shared/shadowTypes';

export interface UseShadowOptions {
  /** If set, polls fetchRecord() at this interval (ms). Default: no polling. */
  pollMs?: number;
  /** If true, auto-fetches on mount. Default: true. */
  fetchOnMount?: boolean;
}

export interface UseShadowReturn {
  // ── Raw state ──────────────────────────────────────────────────────────
  record:            import('../shared/shadowTypes').ShadowRecord | null;
  loading:           boolean;
  error:             string | null;
  lastFetch:         number | null;

  // ── Derived ────────────────────────────────────────────────────────────
  isActivated:       boolean;
  intensityLevel:    import('../shared/shadowTypes').ShadowIntensityLevel;
  integrationStage:  import('../shared/shadowTypes').IntegrationStage;
  dominantArchetype: ShadowArchetypeName | null;
  scores:            Record<ShadowArchetypeName, number> | null;
  intensityPct:      number;   // 0 – 100, for progress bars
  integrationPct:    number;   // 0 – 100, for progress bars

  // ── Actions ────────────────────────────────────────────────────────────
  evaluate:    (inputs?: ShadowInputsPayload) => Promise<void>;
  reflect:     () => Promise<void>;
  refresh:     () => Promise<void>;
  clearError:  () => void;
}

export function useShadow(
  principalId: string,
  options: UseShadowOptions = {},
): UseShadowReturn {
  const { pollMs, fetchOnMount = true } = options;

  const state = useSyncExternalStore(
    shadowStore.subscribe.bind(shadowStore),
    shadowStore.getSnapshot.bind(shadowStore),
  );

  // ── Actions ────────────────────────────────────────────────────────────

  const evaluate = useCallback(
    (inputs?: ShadowInputsPayload) => shadowStore.evaluate(principalId, inputs),
    [principalId],
  );

  const reflect = useCallback(
    () => shadowStore.reflect(principalId),
    [principalId],
  );

  const refresh = useCallback(
    () => shadowStore.fetchRecord(principalId),
    [principalId],
  );

  const clearError = useCallback(
    () => shadowStore.clearError(),
    [],
  );

  // ── Fetch on mount ─────────────────────────────────────────────────────

  useEffect(() => {
    if (fetchOnMount) void refresh();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [principalId]);

  // ── Optional polling ───────────────────────────────────────────────────

  useEffect(() => {
    if (!pollMs || pollMs < 1000) return;
    const id = setInterval(() => void refresh(), pollMs);
    return () => clearInterval(id);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [principalId, pollMs]);

  // ── Derived values ─────────────────────────────────────────────────────

  const record    = state.record;
  const intensity = record?.shadow_intensity ?? 0;
  const progress  = record?.integration_progress ?? 0;

  return {
    // raw
    record,
    loading:   state.loading,
    error:     state.error,
    lastFetch: state.lastFetch,

    // derived
    isActivated:       record?.is_activated ?? false,
    intensityLevel:    intensityLevel(intensity),
    integrationStage:  integrationStage(progress),
    dominantArchetype: record?.active_archetype ?? null,
    scores:            record
      ? (record.archetype_scores as Record<ShadowArchetypeName, number>)
      : null,
    intensityPct:   Math.round(intensity  * 100),
    integrationPct: Math.round(progress   * 100),

    // actions
    evaluate,
    reflect,
    refresh,
    clearError,
  };
}
