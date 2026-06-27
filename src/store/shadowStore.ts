/**
 * src/store/shadowStore.ts
 * GAIA-OS Shadow Store — useSyncExternalStore-compatible.
 * Canon: Shadow Engine — 7-Archetype Integration Layer
 *
 * Holds the last ShadowRecord fetched from /api/shadow/*.
 * Components subscribe via useShadow() (src/hooks/useShadow.ts).
 *
 * Architecture mirrors sessionStore / crystalStore exactly:
 *   - Plain TypeScript, no React imports
 *   - Stable getSnapshot() reference (only updates on state change)
 *   - subscribe() / unsubscribe() via Set<listener>
 */

import type { ShadowRecord, ShadowInputsPayload } from '../shared/shadowTypes';
import { shadowApi } from '../lib/shadowApi';

// ── State shape ────────────────────────────────────────────────────────────

export interface ShadowState {
  record:     ShadowRecord | null;
  loading:    boolean;
  error:      string | null;
  lastFetch:  number | null;   // Date.now() timestamp
}

export interface ShadowActions {
  evaluate:          (principalId: string, inputs?: ShadowInputsPayload) => Promise<void>;
  reflect:           (principalId: string) => Promise<void>;
  fetchRecord:       (principalId: string) => Promise<void>;
  clearError:        () => void;
  subscribe:         (listener: () => void) => () => void;
  getSnapshot:       () => ShadowState;
}

export type ShadowStore = ShadowState & ShadowActions;

// ── Store factory ──────────────────────────────────────────────────────────

function createShadowStore(): ShadowStore {
  let state: ShadowState = {
    record:    null,
    loading:   false,
    error:     null,
    lastFetch: null,
  };

  let cachedSnapshot: ShadowState = { ...state };
  const listeners = new Set<() => void>();

  function notify(): void {
    listeners.forEach(l => l());
  }

  function setState(patch: Partial<ShadowState>): void {
    state = { ...state, ...patch };
    cachedSnapshot = { ...state };
    notify();
  }

  async function evaluate(
    principalId: string,
    inputs?: ShadowInputsPayload,
  ): Promise<void> {
    setState({ loading: true, error: null });
    try {
      const record = await shadowApi.evaluate(principalId, inputs);
      setState({ record, loading: false, lastFetch: Date.now() });
    } catch (err) {
      setState({
        loading: false,
        error: err instanceof Error ? err.message : String(err),
      });
    }
  }

  async function reflect(principalId: string): Promise<void> {
    setState({ loading: true, error: null });
    try {
      const res = await shadowApi.reflect(principalId);
      // Merge updated integration_progress into existing record
      if (state.record) {
        setState({
          loading: false,
          record: {
            ...state.record,
            integration_progress: res.integration_progress,
          },
        });
      } else {
        setState({ loading: false });
      }
    } catch (err) {
      setState({
        loading: false,
        error: err instanceof Error ? err.message : String(err),
      });
    }
  }

  async function fetchRecord(principalId: string): Promise<void> {
    setState({ loading: true, error: null });
    try {
      const record = await shadowApi.getRecord(principalId);
      setState({ record, loading: false, lastFetch: Date.now() });
    } catch (err) {
      // 404 means no evaluation yet — treat as empty, not an error
      const msg = err instanceof Error ? err.message : String(err);
      const is404 = msg.includes('404') || msg.toLowerCase().includes('no shadow record');
      setState({
        loading: false,
        error:   is404 ? null : msg,
        record:  is404 ? null : state.record,
      });
    }
  }

  function clearError(): void {
    setState({ error: null });
  }

  return {
    get record()    { return state.record; },
    get loading()   { return state.loading; },
    get error()     { return state.error; },
    get lastFetch() { return state.lastFetch; },

    evaluate,
    reflect,
    fetchRecord,
    clearError,

    subscribe(listener: () => void): () => void {
      listeners.add(listener);
      return () => listeners.delete(listener);
    },
    getSnapshot(): ShadowState {
      return cachedSnapshot;
    },
  };
}

export const shadowStore = createShadowStore();
