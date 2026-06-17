/**
 * useGaiaState.ts
 *
 * React hook that keeps the frontend in sync with GAIAState on the Python
 * sidecar backend.
 *
 * Strategy:
 *   1. On mount, fetch the full health report via GET /gaia-state/health
 *      (includes state snapshot + active talismans + D6 evaluation).
 *   2. Open a WebSocket to /gaia-state/ws and apply STATE_UPDATE patches
 *      as they arrive — no polling while the socket is live.
 *   3. Fall back to polling every `pollIntervalMs` (default 30 s) when the
 *      socket is disconnected. Auto-reconnect with 3 s back-off.
 *   4. Expose { state, talismans, activeTalismans, loading, error, refresh }
 *      so components can read and trigger manual refreshes.
 *
 * Canon: GAIA_D6_META_COHERENCE_ENGINE, C52
 */

import { useCallback, useEffect, useRef, useState } from 'react';

// ── Types (mirror gaia/core/state.py + gaia/core/talisman.py) ───────────────

export type GAIAMode =
  | 'REST'
  | 'RESEARCH'
  | 'BUILD'
  | 'CREATE'
  | 'REFLECT'
  | 'INTEGRATE'
  | 'TRANSMIT'
  | 'PROTECT'
  | 'RECOVER'
  | 'HIBERNATE';

export interface GAIAStateSnapshot {
  coherence: number;         // 0-1
  energy: number;            // 0-1
  stress: number;            // 0-1
  entropy: number;           // 0-1
  learning_rate: number;     // 0-1
  exploration_rate: number;  // 0-1
  conservation_rate: number; // 0-1
  mode: GAIAMode;
  priority_dimension: string | null;
  d1_physical_integrity: boolean;
  d2_emotional_coherence: boolean;
  d3_mental_clarity: boolean;
  d4_social_resonance: boolean;
  d6_unity_field_active: boolean;
  session_id: string;
  updated_at: string; // ISO timestamp
}

export interface TalismanChip {
  id: string;
  name: string;
  is_active: boolean;
  coherence_function: string;
  layer: string;
  resonance?: { frequency_hz?: number | null };
}

export interface HealthReport {
  state: GAIAStateSnapshot;
  recommended_mode: GAIAMode;
  priority_dimension: string | null;
  dimensional_flags: string[];
  active_talismans: TalismanChip[];
  session_duration_hours: number;
  last_evaluated: string;
}

// ── Config ───────────────────────────────────────────────────────────────────

const API_BASE = (import.meta as Record<string, unknown>)['env']
  ? ((import.meta as Record<string, unknown>)['env'] as Record<string, string>)['VITE_API_BASE'] ?? 'http://127.0.0.1:8008'
  : 'http://127.0.0.1:8008';

const WS_BASE = API_BASE.replace(/^http/, 'ws');

// ── Hook ─────────────────────────────────────────────────────────────────────

export interface UseGaiaStateResult {
  state: GAIAStateSnapshot | null;
  talismans: TalismanChip[];
  activeTalismans: TalismanChip[];
  loading: boolean;
  error: string | null;
  refresh: () => void;
}

export function useGaiaState(pollIntervalMs = 30_000): UseGaiaStateResult {
  const [state, setState] = useState<GAIAStateSnapshot | null>(null);
  const [talismans, setTalismans] = useState<TalismanChip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);
  const mounted = useRef(true);

  // ── Fetch health report ───────────────────────────────────────────────────
  const fetchHealth = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/gaia-state/health`, {
        headers: { 'Content-Type': 'application/json' },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: HealthReport = await res.json();
      if (!mounted.current) return;
      setState(data.state);
      setTalismans(data.active_talismans ?? []);
      setError(null);
    } catch (e) {
      if (mounted.current) setError((e as Error).message);
    } finally {
      if (mounted.current) setLoading(false);
    }
  }, []);

  // ── WebSocket ─────────────────────────────────────────────────────────────
  const openWs = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState < 2) return; // already open/connecting

    const ws = new WebSocket(`${WS_BASE}/gaia-state/ws`);
    wsRef.current = ws;

    ws.onopen = () => {
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      // Stop fallback polling while socket is live
      if (pollTimer.current) clearInterval(pollTimer.current);
    };

    ws.onmessage = (evt) => {
      if (!mounted.current) return;
      try {
        const msg = JSON.parse(evt.data as string);
        if (msg.type === 'STATE_UPDATE') {
          setState((prev) => (prev ? { ...prev, ...msg.data } : msg.data as GAIAStateSnapshot));
        }
        if (msg.type === 'PONG') { /* keep-alive, ignore */ }
      } catch { /* ignore malformed */ }
    };

    ws.onclose = () => {
      if (!mounted.current) return;
      // Restart fallback polling and schedule reconnect
      pollTimer.current = setInterval(fetchHealth, pollIntervalMs);
      reconnectTimer.current = setTimeout(openWs, 3_000);
    };

    ws.onerror = () => ws.close();
  }, [fetchHealth, pollIntervalMs]);

  // ── Mount / unmount ───────────────────────────────────────────────────────
  useEffect(() => {
    mounted.current = true;
    fetchHealth().then(openWs);

    return () => {
      mounted.current = false;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      if (pollTimer.current) clearInterval(pollTimer.current);
      wsRef.current?.close();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const activeTalismans = talismans.filter((t) => t.is_active);

  return {
    state,
    talismans,
    activeTalismans,
    loading,
    error,
    refresh: fetchHealth,
  };
}
