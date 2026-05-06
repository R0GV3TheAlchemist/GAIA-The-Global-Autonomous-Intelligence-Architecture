/**
 * src/memory/memoryClient.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Typed fetch wrapper for the GAIA sidecar memory endpoints.
 */

import { API_BASE } from '../config';

const BASE       = `${API_BASE}/api/memory`;
const TIMEOUT_MS = 5_000;

// ─── Types ────────────────────────────────────────────────────────────────────

export type MemoryKind =
  | 'message' | 'fact' | 'preference' | 'goal'
  | 'emotion' | 'skill' | 'event' | 'context';

export type MemoryTier =
  | 'ephemeral' | 'short_term' | 'long_term' | 'permanent';

export interface RememberParams {
  user_id:      string;
  text:         string;
  role?:        'user' | 'gaia' | 'system';
  kind?:        MemoryKind;
  tier?:        MemoryTier;
  importance?:  number;
  session_id?:  string;
  topic_tag?:   string;
  ttl_seconds?: number;
}

export interface MemoryHit {
  id:         number;
  text:       string;
  kind:       MemoryKind;
  tier:       MemoryTier;
  role:       string;
  importance: number;
  score:      number;
  created_at: number;
  session_id: string | null;
  topic_tag:  string | null;
}

export interface RetrieveParams {
  user_id:           string;
  query:             string;
  top_k?:            number;
  kinds?:            MemoryKind[];
  tiers?:            MemoryTier[];
  topic_tag?:        string;
  since_ts?:         number;
  importance_floor?: number;
}

export interface MemoryStats {
  total:       number;
  by_kind:     Record<string, number>;
  vec_enabled: boolean;
  db_path:     string;
}

export interface MemoryHealth {
  status:       'ok' | 'not_ready' | 'error';
  ready:        boolean;
  total_items?: number;
  vec_enabled?: boolean;
  db_path?:     string;
  detail?:      string;
}

// ─── Internal fetch helpers ────────────────────────────────────────────────────

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
    signal:  AbortSignal.timeout(TIMEOUT_MS),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Memory API ${path} → ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

async function del(path: string, params: Record<string, string> = {}): Promise<unknown> {
  const qs  = new URLSearchParams(params).toString();
  const url = `${BASE}${path}${qs ? `?${qs}` : ''}`;
  const res = await fetch(url, { method: 'DELETE', signal: AbortSignal.timeout(TIMEOUT_MS) });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Memory API DELETE ${path} → ${res.status}: ${detail}`);
  }
  return res.json();
}

async function get<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  const qs  = new URLSearchParams(params).toString();
  const url = `${BASE}${path}${qs ? `?${qs}` : ''}`;
  const res = await fetch(url, { signal: AbortSignal.timeout(TIMEOUT_MS) });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`Memory API GET ${path} → ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

// ─── Public API ───────────────────────────────────────────────────────────────

export async function remember(params: RememberParams): Promise<number> {
  const body = {
    user_id:     params.user_id,
    text:        params.text,
    role:        params.role        ?? 'user',
    kind:        params.kind        ?? 'message',
    tier:        params.tier        ?? 'short_term',
    importance:  params.importance  ?? 0.5,
    session_id:  params.session_id  ?? null,
    topic_tag:   params.topic_tag   ?? null,
    ttl_seconds: params.ttl_seconds ?? null,
  };
  const resp = await post<{ id: number; status: string }>('/remember', body);
  return resp.id;
}

export async function retrieve(params: RetrieveParams): Promise<MemoryHit[]> {
  const body = {
    user_id:          params.user_id,
    query:            params.query,
    top_k:            params.top_k           ?? 10,
    kinds:            params.kinds            ?? null,
    tiers:            params.tiers            ?? null,
    topic_tag:        params.topic_tag        ?? null,
    since_ts:         params.since_ts         ?? null,
    importance_floor: params.importance_floor ?? 0.0,
  };
  const resp = await post<{ hits: MemoryHit[]; count: number }>('/retrieve', body);
  return resp.hits;
}

export async function forgetItem(item_id: number, user_id: string): Promise<void> {
  await del(`/forget/${item_id}`, { user_id });
}

export async function forgetUser(user_id: string): Promise<number> {
  const resp = await del('/forget-user', { user_id }) as { items_deleted: number };
  return resp.items_deleted;
}

/**
 * stats() — fixed: build params as Record<string, string> (no undefined values)
 * so TypeScript is happy with the `get()` helper signature.
 */
export async function stats(user_id?: string): Promise<MemoryStats> {
  const params: Record<string, string> = {};
  if (user_id) params['user_id'] = user_id;
  return get<MemoryStats>('/stats', params);
}

export async function health(): Promise<MemoryHealth> {
  return get<MemoryHealth>('/health');
}
