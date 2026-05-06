/**
 * src/hooks/useMemory.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * React hook for GAIA’s persistent semantic memory layer.
 *
 * Wraps the memoryClient and exposes a clean interface for React components:
 *
 *   const memory = useMemory({ userId: 'user_001', sessionId: 'sess_abc' });
 *
 *   // After receiving the user’s message:
 *   await memory.rememberTurn('user', 'I prefer dark mode');
 *
 *   // Before generating a response:
 *   const context = await memory.retrieveContext('dark mode preferences');
 *   const systemPrompt = injectMemoryContext(basePrompt, context);
 *
 *   // Read state:
 *   memory.hits        // MemoryHit[] — last retrieval results
 *   memory.busy        // boolean — request in flight
 *   memory.error       // string | null — last error message
 */

import { useSyncExternalStore, useCallback } from 'react';
import {
  remember   as apiRemember,
  retrieve   as apiRetrieve,
  forgetItem as apiForgetItem,
  forgetUser as apiForgetUser,
  stats      as apiStats,
  health     as apiHealth,
  MemoryHit,
  MemoryTier,
  MemoryStats,
  MemoryHealth,
  RememberParams,
  RetrieveParams,
} from '../memory/memoryClient';
import { injectMemoryContext } from '../memory/promptMemory';

// ─── Module-level store (shared across all hook instances) ────────────────────

interface MemoryState {
  hits:  MemoryHit[];
  busy:  boolean;
  error: string | null;
}

type Listener = () => void;

const _listeners = new Set<Listener>();
let _state: MemoryState = { hits: [], busy: false, error: null };

function _setState(patch: Partial<MemoryState>): void {
  _state = { ..._state, ...patch };
  _listeners.forEach(fn => fn());
}

const _store = {
  subscribe:   (fn: Listener) => { _listeners.add(fn); return () => _listeners.delete(fn); },
  getSnapshot: () => _state,
};

// ─── Hook options ─────────────────────────────────────────────────────────────

export interface UseMemoryOptions {
  userId:       string;
  sessionId?:   string;
  defaultTier?: MemoryTier;
}

// ─── Hook return type ─────────────────────────────────────────────────────────

export interface UseMemoryReturn {
  hits:   MemoryHit[];
  busy:   boolean;
  error:  string | null;

  remember:          (params: Omit<RememberParams, 'user_id'>) => Promise<number | null>;
  rememberTurn:      (role: 'user' | 'gaia', text: string, overrides?: Partial<Omit<RememberParams, 'user_id' | 'role' | 'text'>>) => Promise<number | null>;
  forgetItem:        (itemId: number) => Promise<void>;
  forgetUser:        () => Promise<number>;
  retrieveContext:   (query: string, options?: Partial<RetrieveParams>) => Promise<MemoryHit[]>;
  buildMemoryContext:(customHits?: MemoryHit[]) => string;
  injectIntoPrompt:  (systemPrompt: string, customHits?: MemoryHit[]) => string;
  fetchStats:        (userId?: string) => Promise<MemoryStats | null>;
  fetchHealth:       () => Promise<MemoryHealth | null>;
}

// ─── Hook ─────────────────────────────────────────────────────────────────────

export function useMemory(options: UseMemoryOptions): UseMemoryReturn {
  const { userId, sessionId, defaultTier = 'short_term' } = options;

  const state = useSyncExternalStore(
    _store.subscribe,
    _store.getSnapshot,
    _store.getSnapshot,
  );

  const remember = useCallback(async (
    params: Omit<RememberParams, 'user_id'>
  ): Promise<number | null> => {
    _setState({ busy: true, error: null });
    try {
      const id = await apiRemember({ ...params, user_id: userId, session_id: params.session_id ?? sessionId });
      _setState({ busy: false });
      return id;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn('[useMemory] remember failed:', msg);
      _setState({ busy: false, error: msg });
      return null;
    }
  }, [userId, sessionId]);

  const rememberTurn = useCallback(async (
    role: 'user' | 'gaia',
    text: string,
    overrides?: Partial<Omit<RememberParams, 'user_id' | 'role' | 'text'>>
  ): Promise<number | null> => {
    if (!text.trim()) return null;
    return remember({
      text,
      role,
      kind:        overrides?.kind        ?? 'message',
      tier:        overrides?.tier        ?? defaultTier,
      importance:  overrides?.importance  ?? (role === 'gaia' ? 0.6 : 0.5),
      session_id:  overrides?.session_id  ?? sessionId,
      topic_tag:   overrides?.topic_tag,
      ttl_seconds: overrides?.ttl_seconds,
    });
  }, [remember, sessionId, defaultTier]);

  const retrieveContext = useCallback(async (
    query: string,
    opts?: Partial<RetrieveParams>
  ): Promise<MemoryHit[]> => {
    _setState({ busy: true, error: null });
    try {
      const hits = await apiRetrieve({
        user_id:          userId,
        query,
        top_k:            opts?.top_k            ?? 12,
        kinds:            opts?.kinds,
        tiers:            opts?.tiers,
        topic_tag:        opts?.topic_tag,
        since_ts:         opts?.since_ts,
        importance_floor: opts?.importance_floor ?? 0.1,
      });
      _setState({ hits, busy: false });
      return hits;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn('[useMemory] retrieveContext failed:', msg);
      _setState({ busy: false, error: msg });
      return [];
    }
  }, [userId]);

  const forgetItem = useCallback(async (itemId: number): Promise<void> => {
    _setState({ busy: true, error: null });
    try {
      await apiForgetItem(itemId, userId);
      _setState({ busy: false, hits: _state.hits.filter(h => h.id !== itemId) });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn('[useMemory] forgetItem failed:', msg);
      _setState({ busy: false, error: msg });
    }
  }, [userId]);

  const forgetUser = useCallback(async (): Promise<number> => {
    _setState({ busy: true, error: null });
    try {
      const count = await apiForgetUser(userId);
      _setState({ busy: false, hits: [] });
      return count;
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      console.warn('[useMemory] forgetUser failed:', msg);
      _setState({ busy: false, error: msg });
      return 0;
    }
  }, [userId]);

  const buildMemoryContext = useCallback((customHits?: MemoryHit[]): string => {
    const source = customHits ?? _state.hits;
    if (!source.length) return '';
    return source
      .map((h, i) => `[${i + 1}] (${h.kind}, importance=${h.importance.toFixed(2)}) ${h.text}`)
      .join('\n');
  }, []);

  const injectIntoPrompt = useCallback((
    systemPrompt: string,
    customHits?: MemoryHit[]
  ): string => injectMemoryContext(systemPrompt, customHits ?? _state.hits), []);

  const fetchStats = useCallback(async (targetUserId?: string): Promise<MemoryStats | null> => {
    try { return await apiStats(targetUserId ?? userId); }
    catch (err) { console.warn('[useMemory] fetchStats failed:', err); return null; }
  }, [userId]);

  const fetchHealth = useCallback(async (): Promise<MemoryHealth | null> => {
    try { return await apiHealth(); }
    catch (err) { console.warn('[useMemory] fetchHealth failed:', err); return null; }
  }, []);

  return {
    hits:  state.hits,
    busy:  state.busy,
    error: state.error,
    remember,
    rememberTurn,
    forgetItem,
    forgetUser,
    retrieveContext,
    buildMemoryContext,
    injectIntoPrompt,
    fetchStats,
    fetchHealth,
  };
}
