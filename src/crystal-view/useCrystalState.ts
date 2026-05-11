/**
 * src/crystal-view/useCrystalState.ts
 * GAIA-OS — Crystal Core React hook
 * Spec: C-CC01 §2 (tick cadence) + §11.2
 *
 * Provides:
 *   - Live CrystalState, polled every 15 min
 *   - 7-day CoherenceTick history
 *   - forceTick() for post-conversation re-tick
 *   - loading / error surface
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchCrystalState, fetchCrystalHistory, forceTick } from './crystalApi';
import type { CrystalState, CoherenceTick } from './types';
import { CoherenceBand, PersonaTone } from './types';

const TICK_INTERVAL_MS = 15 * 60 * 1000; // 15 minutes

/** Safe fallback when API is not yet available */
function buildFallbackState(): CrystalState {
  return {
    timestamp:          new Date().toISOString(),
    affect_coherence:   0.5,
    stage_coherence:    0.5,
    shadow_integration: 0.5,
    schumann_alignment: 0.5,
    coherence:          0.5,
    coherence_band:     CoherenceBand.PRESENT,
    dominant_emotion:   'neutral',
    active_stage:       1,
    active_archetype:   'Unknown',
    schumann_disturbance: 'unavailable',
    inner_narrative:    'I am steady, attending to you without distraction.',
    persona_tone:       PersonaTone.PRESENT,
    orb_params: {
      glow_color:       '#1a7a5e',
      glow_intensity:   0.575,
      pulse_frequency:  0.24,
      pulse_amplitude:  0.04,
      cloud_opacity:    0.5,
      aurora_intensity: 0.5,
      rotation_speed:   0.02,
      coherence_ring:   0.5,
    },
  };
}

export interface UseCrystalStateResult {
  state:      CrystalState;
  history:    CoherenceTick[];
  loading:    boolean;
  error:      string | null;
  forceTick:  () => Promise<void>;
  lastTick:   Date | null;
}

export function useCrystalState(): UseCrystalStateResult {
  const [state,   setState]   = useState<CrystalState>(buildFallbackState);
  const [history, setHistory] = useState<CoherenceTick[]>([]);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState<string | null>(null);
  const [lastTick, setLastTick] = useState<Date | null>(null);
  const mountedRef = useRef(true);

  const load = useCallback(async (force = false): Promise<void> => {
    if (!mountedRef.current) return;
    if (force) setLoading(true);
    try {
      const [s, h] = await Promise.all([
        force ? forceTick() : fetchCrystalState(),
        fetchCrystalHistory(7),
      ]);
      if (!mountedRef.current) return;
      setState(s);
      setHistory(h);
      setError(null);
      setLastTick(new Date());
    } catch (err) {
      if (!mountedRef.current) return;
      // On error keep last good state; show error banner only on first load
      const msg = err instanceof Error ? err.message : 'Crystal Core unavailable';
      setError(msg);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    void load(false);
    const id = setInterval(() => { void load(false); }, TICK_INTERVAL_MS);
    return () => {
      mountedRef.current = false;
      clearInterval(id);
    };
  }, [load]);

  const handleForceTick = useCallback(async (): Promise<void> => {
    await load(true);
  }, [load]);

  return { state, history, loading, error, forceTick: handleForceTick, lastTick };
}
