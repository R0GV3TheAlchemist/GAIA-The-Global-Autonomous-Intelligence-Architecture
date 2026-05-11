/**
 * useCrystalCore.ts
 * Polling hook — fetches /crystal/state from the Python sidecar every 10s.
 * On each successful tick:
 *   1. Stores CrystalState in React state (for CrystalView to render)
 *   2. Calls orb.setParams(state.orb_params) to drive the visual layer
 *
 * Graceful degradation:
 *   - If sidecar is unreachable, CrystalState is null and the orb
 *     continues on its last known params (no flicker, no error toast).
 *   - Falls back to orbParamsFromPsi(0.5) on first mount if sidecar
 *     hasn't responded yet, so the orb is never in an uninitialised state.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { orbParamsFromPsi } from '../gaian/OrbParams';
import type { OrbParams } from '../gaian/OrbParams';
import type { GaianOrb } from '../gaian/GaianOrb';

// ── Types mirroring the Python sidecar response (crystal/types.py) ─────────

export interface ComponentScores {
  affect:   number;  // A — 0–1
  stage:    number;  // S — 0–1
  shadow:   number;  // E — 0–1
  schumann: number;  // H — 0–1
}

export interface CrystalState {
  psi:          number;           // Ψ coherence score 0–1
  band:         string;           // e.g. 'Coherent'
  components:   ComponentScores;
  orb_params:   OrbParams;
  narrative:    string;           // one-sentence inner monologue
  persona_tone: string;           // e.g. 'WARM', 'RADIANT', 'SPARSE'
  timestamp:    string;           // ISO-8601
}

const SIDECAR_URL = 'http://localhost:8008/crystal/state';
const POLL_MS     = 10_000; // 10 seconds

// ── Hook ─────────────────────────────────────────────────────────────────────

export function useCrystalCore(orb: GaianOrb | null): {
  state:   CrystalState | null;
  loading: boolean;
  error:   string | null;
} {
  const [state,   setState]   = useState<CrystalState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState<string | null>(null);

  const orbRef   = useRef<GaianOrb | null>(orb);
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Keep orbRef current without re-triggering the effect
  useEffect(() => { orbRef.current = orb; }, [orb]);

  const tick = useCallback(async () => {
    try {
      const res = await fetch(SIDECAR_URL, {
        signal: AbortSignal.timeout(4000),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = (await res.json()) as CrystalState;

      setState(data);
      setError(null);

      // Drive the orb
      if (orbRef.current) {
        orbRef.current.setParams(data.orb_params);
      }
    } catch (err) {
      // Sidecar unreachable — set fallback params once, then stay quiet
      setError(err instanceof Error ? err.message : 'Sidecar unavailable');
      if (!state && orbRef.current) {
        orbRef.current.setParams(orbParamsFromPsi(0.5));
      }
    } finally {
      setLoading(false);
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Immediate first tick
    void tick();

    // Poll every 10s
    timerRef.current = setInterval(() => { void tick(); }, POLL_MS);

    return () => {
      if (timerRef.current !== null) clearInterval(timerRef.current);
    };
  }, [tick]);

  return { state, loading, error };
}
