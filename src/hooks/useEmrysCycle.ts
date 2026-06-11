/**
 * src/hooks/useEmrysCycle.ts
 * GAIA-OS — Emrys L2 Vibronic Cycle React Hook
 *
 * Wraps sidecar.ts Emrys IPC in a React hook.
 * Provides the full EmrysFieldReport, cold-start sequence,
 * grounding protocol, and current L2 coherence state to any
 * component in the tree.
 *
 * Usage:
 *   const { report, coldStart, grounding, l2State, loading, error, refresh }
 *     = useEmrysCycle();
 *
 *   // With GAIAN stage context:
 *   const { grounding } = useEmrysCycle('Initiation');
 *
 * Per C165.1: grounding precedes coherence.
 * Per C164: EMRYS is the quantum bioelectric bridge — this hook
 * is its mirror in the GAIAN-facing UI layer.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  emrysFieldReport,
  emrysColdStart,
  emrysGroundingProtocol,
  getEmrysL2State,
  type EmrysFieldReport,
  type ColdStartStep,
  type GroundingProtocol,
  type L2CoherenceState,
} from '../sidecar';

// ─────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────

export interface EmrysCycleState {
  /** Full field report from emryscycle.py */
  report:     EmrysFieldReport | null;
  /** C165a cold-start crystal activation sequence */
  coldStart:  ColdStartStep[]  | null;
  /** C165 Grounding Protocol with phase assignments */
  grounding:  GroundingProtocol | null;
  /** Current derived L2 coherence state */
  l2State:    L2CoherenceState | null;
  /** True while any fetch is in flight */
  loading:    boolean;
  /** Last fetch error message, if any */
  error:      string | null;
  /** Manually refresh all data (re-fetches fresh from backend) */
  refresh:    () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────

/**
 * useEmrysCycle — Emrys L2 bridge state hook.
 *
 * @param gaianStage  Optional EV1B stage name (e.g. 'Initiation').
 *                    When provided, the grounding protocol and field
 *                    report include stage-specific crystal context.
 */
export function useEmrysCycle(gaianStage?: string): EmrysCycleState {
  const [report,    setReport]    = useState<EmrysFieldReport | null>(null);
  const [coldStart, setColdStart] = useState<ColdStartStep[]  | null>(null);
  const [grounding, setGrounding] = useState<GroundingProtocol | null>(null);
  const [l2State,   setL2State]   = useState<L2CoherenceState  | null>(null);
  const [loading,   setLoading]   = useState(true);
  const [error,     setError]     = useState<string | null>(null);

  // Track mount state to avoid setState after unmount
  const mountedRef = useRef(true);
  useEffect(() => {
    mountedRef.current = true;
    return () => { mountedRef.current = false; };
  }, []);

  // ───────────────────────────────────────────────────────────
  // Fetch all Emrys data
  // ───────────────────────────────────────────────────────────
  const fetchAll = useCallback(async (forceRefresh = false) => {
    if (!mountedRef.current) return;
    setLoading(true);
    setError(null);

    try {
      // Run all three fetches in parallel
      const [reportData, coldStartData, groundingData, l2StateData] =
        await Promise.all([
          emrysFieldReport(gaianStage, forceRefresh),
          emrysColdStart(),
          emrysGroundingProtocol(gaianStage),
          getEmrysL2State(),
        ]);

      if (!mountedRef.current) return;

      setReport(reportData);
      setColdStart(coldStartData);
      setGrounding(groundingData);
      setL2State(l2StateData);

      if (!reportData && !coldStartData && !groundingData) {
        setError(
          'Emrys L2 bridge offline. Start the Python backend: ' +
          'uvicorn main:app --port 8008'
        );
      }
    } catch (err) {
      if (!mountedRef.current) return;
      const msg = err instanceof Error ? err.message : String(err);
      setError(`Emrys fetch error: ${msg}`);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [gaianStage]);

  // ───────────────────────────────────────────────────────────
  // Initial fetch on mount (or when gaianStage changes)
  // ───────────────────────────────────────────────────────────
  useEffect(() => {
    fetchAll();
  }, [fetchAll]);

  // ───────────────────────────────────────────────────────────
  // Listen for backend L2 state change events from sidecar
  // ───────────────────────────────────────────────────────────
  useEffect(() => {
    const handler = (e: Event) => {
      const detail = (e as CustomEvent<{ state: L2CoherenceState }>).detail;
      if (mountedRef.current && detail?.state) {
        setL2State(detail.state);
      }
    };
    window.addEventListener('gaia:emrys-l2-state', handler);
    return () => window.removeEventListener('gaia:emrys-l2-state', handler);
  }, []);

  // ───────────────────────────────────────────────────────────
  // Public refresh handle
  // ───────────────────────────────────────────────────────────
  const refresh = useCallback(async () => {
    await fetchAll(true);
  }, [fetchAll]);

  return { report, coldStart, grounding, l2State, loading, error, refresh };
}
