/**
 * src/hooks/useAlignment.ts
 * GAIA-OS — Alignment State Hook  (web-app branch)
 *
 * React hook — polls GET /api/alignment every POLL_INTERVAL_MS
 * milliseconds and returns the live AlignmentStateResponse.
 *
 * Web migration: replaced Tauri invoke() with fetch().
 * rawRmssd is forwarded as a query param when available.
 *
 * Usage:
 *   const { state, loading, error, refresh } = useAlignment();
 *
 * Backend contract:
 *   GET /api/alignment?rmssd=<number|omit>
 *   → JSON AlignmentState  (same shape as the Rust response)
 */

import { useEffect, useRef, useState, useCallback } from 'react';

// ---------------------------------------------------------------------------
// Types  (mirror AlignmentStateResponse from the Python backend)
// ---------------------------------------------------------------------------

export type AlignmentTier =
  | 'minimal'
  | 'core'
  | 'standard'
  | 'full'
  | 'vibrant';

export interface AlignmentState {
  score:            number;   // 0–100
  hrv_score:        number;   // 0–100
  schumann_score:   number;   // 0–100
  solar_kp:         number;
  ui_tier:          AlignmentTier;
  last_updated:     string;   // ISO-8601 UTC
  fallback_mode:    string;   // empty string when all feeds healthy
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const POLL_INTERVAL_MS = 30_000;  // 30 s
const ERROR_BACKOFF_MS = 10_000;  // 10 s retry on error
const API_ENDPOINT     = '/api/alignment';

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

interface UseAlignmentResult {
  state:   AlignmentState | null;
  loading: boolean;
  error:   string | null;
  refresh: () => void;
}

export function useAlignment(rawRmssd: number | null = null): UseAlignmentResult {
  const [state,   setState]   = useState<AlignmentState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState<string | null>(null);

  const timerRef   = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mountedRef = useRef(true);

  const fetchAlignment = useCallback(async () => {
    if (!mountedRef.current) return;
    setLoading(true);

    try {
      // Build URL — attach rmssd as query param when available
      const url = new URL(API_ENDPOINT, window.location.origin);
      if (rawRmssd !== null) url.searchParams.set('rmssd', String(rawRmssd));

      const res = await fetch(url.toString(), {
        headers: { 'Accept': 'application/json' },
        signal:  AbortSignal.timeout(8_000),   // 8 s hard timeout
      });

      if (!res.ok) throw new Error(`Alignment API ${res.status}: ${res.statusText}`);

      const result = await res.json() as AlignmentState;

      if (!mountedRef.current) return;
      setState(result);
      setError(null);
      timerRef.current = setTimeout(fetchAlignment, POLL_INTERVAL_MS);

    } catch (err) {
      if (!mountedRef.current) return;
      const msg = err instanceof Error ? err.message : String(err);
      setError(msg);
      timerRef.current = setTimeout(fetchAlignment, ERROR_BACKOFF_MS);
    } finally {
      if (mountedRef.current) setLoading(false);
    }
  }, [rawRmssd]);

  const refresh = useCallback(() => {
    if (timerRef.current) clearTimeout(timerRef.current);
    fetchAlignment();
  }, [fetchAlignment]);

  useEffect(() => {
    mountedRef.current = true;
    fetchAlignment();
    return () => {
      mountedRef.current = false;
      if (timerRef.current) clearTimeout(timerRef.current);
    };
  }, [fetchAlignment]);

  return { state, loading, error, refresh };
}
