/**
 * src/api/state.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Typed Tauri invoke() wrappers for all GAIAState + D6 + Talisman commands.
 *
 * Architecture (mirrors memory.ts pattern):
 * ┌────────────────┐  invoke()  ┌─────────────────────┐  sidecar  ┌──────────────────┐
 * │  React / TS    │ ─────────▶│  Rust (state.rs)    │ ─────────▶│  Python          │
 * │  (renderer)    │ ◀──────── │  managed state      │ ◀──────── │  core/state.py   │
 * └────────────────┘           └─────────────────────┘           └──────────────────┘
 *
 * Every function falls back to direct fetch against the Python sidecar
 * so dev mode works even before the Rust bridge is wired.
 *
 * Canon anchor: Issue #576, Issue #568, Issue #580
 * Created: June 17, 2026
 */

import { invoke } from '@tauri-apps/api/core';

// ─── Re-export StateHUD so callers only need one import ───────────────────────
export { StateHUD } from '../components/StateHUD';
export type { GAIAStateSnapshot, GAIAMode } from '../components/StateHUD';

// ─── Sidecar base URL ────────────────────────────────────────────────────────
// Port 8008 matches main.py (GAIA_PORT env var, default 8008)
const SIDECAR_BASE = 'http://localhost:8008';

// ─── Types ───────────────────────────────────────────────────────────────────

export type GAIAMode =
  | 'BUILD'
  | 'RESEARCH'
  | 'REFLECT'
  | 'RECOVER'
  | 'PROTECT'
  | 'TRANSCEND';

export type ArchitectSignal =
  | 'FORCE_BUILD'
  | 'FORCE_RESEARCH'
  | 'FORCE_REFLECT'
  | 'FORCE_RECOVER'
  | 'FORCE_PROTECT'
  | 'RESUME_AUTO';

export type TalismanStatus = 'INACTIVE' | 'ACTIVE' | 'SUSPENDED' | 'EXPIRED';

/**
 * Full GAIAState snapshot — mirrors GAIAState.to_dict() in state.py.
 */
export interface GAIAStateSnapshot {
  coherence:          number;
  energy:             number;
  stress:             number;
  entropy:            number;
  learning_rate:      number;
  exploration_rate:   number;
  conservation_rate:  number;
  mode:               GAIAMode;
  architect_signal:   ArchitectSignal | null;
  active_talismans:   string[];
  last_updated:       number;
  session_id:         string | null;
  coherence_band:     string;
  is_safe_to_build:   boolean;
  is_in_crisis:       boolean;
  d6_reason?:         string;
}

/**
 * D6 intervention — mirrors D6Intervention in state.py.
 */
export interface D6Intervention {
  recommended_mode: GAIAMode;
  reason:           string;
  urgency:          'critical' | 'advisory' | 'informational';
  previous_mode:    GAIAMode;
  timestamp:        number;
}

/**
 * Talisman field effect — mirrors TalismanFieldEffect in talisman.py.
 */
export interface TalismanFieldEffect {
  coherence?:          number;
  energy?:             number;
  stress?:             number;
  entropy?:            number;
  learning_rate?:      number;
  exploration_rate?:   number;
  conservation_rate?:  number;
}

/**
 * Full Talisman document — mirrors Talisman.to_dict() in talisman.py.
 */
export interface TalismanDoc {
  id:               string;
  name:             string;
  intent:           string;
  field_effect:     TalismanFieldEffect;
  status:           TalismanStatus;
  owner_id:         string | null;
  crystal_ids:      string[];
  activation_count: number;
  created_at:       number;
  activated_at:     number | null;
  expires_at:       number | null;
  tags:             string[];
  notes:            string;
  is_active:        boolean;
  is_expired:       boolean;
}

/**
 * Payload for creating or updating a Talisman.
 */
export interface TalismanWriteParams {
  name:         string;
  intent:       string;
  field_effect: TalismanFieldEffect;
  owner_id?:    string;
  crystal_ids?: string[];
  expires_at?:  number | null;
  tags?:        string[];
  notes?:       string;
}

/**
 * Response from activate / deactivate.
 */
export interface TalismanActivationResult {
  talisman: TalismanDoc;
  state:    GAIAStateSnapshot;
}

// ─── Internal helpers ─────────────────────────────────────────────────────────
async function safeInvoke<T>(cmd: string, args: Record<string, unknown>): Promise<T> {
  try {
    return await invoke<T>(cmd, args);
  } catch (err) {
    console.warn(`[GAIA:api/state] invoke('${cmd}') failed, using direct fetch fallback:`, err);
    throw err;
  }
}

async function directFetch<T>(path: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${SIDECAR_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...opts,
  });
  if (!res.ok) throw new Error(`[GAIA:api/state] ${path} → ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

// ─── GAIAState commands ───────────────────────────────────────────────────────

/** Fetch the current GAIAState snapshot. Polled by StateHUD. */
export async function stateGet(): Promise<GAIAStateSnapshot> {
  try {
    return await safeInvoke<GAIAStateSnapshot>('state_get', {});
  } catch {
    return directFetch<GAIAStateSnapshot>('/api/state');
  }
}

/** Update one or more GAIAState fields. D6 re-evaluates after every write. */
export async function stateUpdate(
  updates: Partial<Omit<GAIAStateSnapshot,
    'mode' | 'architect_signal' | 'active_talismans' | 'last_updated'
    | 'session_id' | 'coherence_band' | 'is_safe_to_build' | 'is_in_crisis'
  >>,
): Promise<GAIAStateSnapshot> {
  try {
    return await safeInvoke<GAIAStateSnapshot>('state_update', { updates });
  } catch {
    return directFetch<GAIAStateSnapshot>('/api/state', {
      method: 'PATCH',
      body: JSON.stringify(updates),
    });
  }
}

/** Send an Architect override signal (Issue #578). */
export async function stateOverride(
  signal: ArchitectSignal,
): Promise<GAIAStateSnapshot> {
  try {
    return await safeInvoke<GAIAStateSnapshot>('state_override', { signal });
  } catch {
    return directFetch<GAIAStateSnapshot>('/api/state/override', {
      method: 'POST',
      body: JSON.stringify({ signal }),
    });
  }
}

/** D6 dry-run: what would the engine recommend right now? */
export async function stateEvaluate(): Promise<D6Intervention> {
  try {
    return await safeInvoke<D6Intervention>('state_evaluate', {});
  } catch {
    return directFetch<D6Intervention>('/api/state/evaluate');
  }
}

/** Fetch the last N state history snapshots. */
export async function stateHistory(lastN = 50): Promise<GAIAStateSnapshot[]> {
  try {
    return await safeInvoke<GAIAStateSnapshot[]>('state_history', { last_n: lastN });
  } catch {
    return directFetch<GAIAStateSnapshot[]>(`/api/state/history?n=${lastN}`);
  }
}

// ─── Talisman commands ────────────────────────────────────────────────────────

export async function talismanList(ownerId?: string): Promise<TalismanDoc[]> {
  try {
    return await safeInvoke<TalismanDoc[]>('talisman_list', { owner_id: ownerId ?? null });
  } catch {
    const q = ownerId ? `?owner_id=${ownerId}` : '';
    return directFetch<TalismanDoc[]>(`/api/talismans${q}`);
  }
}

export async function talismanGet(id: string): Promise<TalismanDoc> {
  try {
    return await safeInvoke<TalismanDoc>('talisman_get', { id });
  } catch {
    return directFetch<TalismanDoc>(`/api/talismans/${id}`);
  }
}

export async function talismanCreate(params: TalismanWriteParams): Promise<TalismanDoc> {
  try {
    return await safeInvoke<TalismanDoc>('talisman_create', { params });
  } catch {
    return directFetch<TalismanDoc>('/api/talismans', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }
}

export async function talismanUpdate(
  id: string,
  params: Partial<TalismanWriteParams>,
): Promise<TalismanDoc> {
  try {
    return await safeInvoke<TalismanDoc>('talisman_update', { id, params });
  } catch {
    return directFetch<TalismanDoc>(`/api/talismans/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(params),
    });
  }
}

/** Activate a talisman — applies field_effect to GAIAState. */
export async function talismanActivate(id: string): Promise<TalismanActivationResult> {
  try {
    return await safeInvoke<TalismanActivationResult>('talisman_activate', { id });
  } catch {
    return directFetch<TalismanActivationResult>(`/api/talismans/${id}/activate`, {
      method: 'POST',
    });
  }
}

/** Deactivate a talisman — reverses field_effect from GAIAState. */
export async function talismanDeactivate(id: string): Promise<TalismanActivationResult> {
  try {
    return await safeInvoke<TalismanActivationResult>('talisman_deactivate', { id });
  } catch {
    return directFetch<TalismanActivationResult>(`/api/talismans/${id}/deactivate`, {
      method: 'POST',
    });
  }
}

export async function talismanDelete(id: string): Promise<{ deleted: boolean }> {
  try {
    return await safeInvoke<{ deleted: boolean }>('talisman_delete', { id });
  } catch {
    return directFetch<{ deleted: boolean }>(`/api/talismans/${id}`, {
      method: 'DELETE',
    });
  }
}

// ─── GAIAStateClient class (for DI / testing) ─────────────────────────────────

export class GAIAStateClient {
  // ── State ──
  get(): Promise<GAIAStateSnapshot>                     { return stateGet(); }
  update(u: Parameters<typeof stateUpdate>[0]):          Promise<GAIAStateSnapshot>        { return stateUpdate(u); }
  override(s: ArchitectSignal):                         Promise<GAIAStateSnapshot>        { return stateOverride(s); }
  evaluate():                                            Promise<D6Intervention>           { return stateEvaluate(); }
  history(n?: number):                                  Promise<GAIAStateSnapshot[]>      { return stateHistory(n); }

  // ── Talismans ──
  listTalismans(ownerId?: string):                      Promise<TalismanDoc[]>            { return talismanList(ownerId); }
  getTalisman(id: string):                              Promise<TalismanDoc>              { return talismanGet(id); }
  createTalisman(p: TalismanWriteParams):               Promise<TalismanDoc>              { return talismanCreate(p); }
  updateTalisman(id: string, p: Partial<TalismanWriteParams>): Promise<TalismanDoc>       { return talismanUpdate(id, p); }
  activateTalisman(id: string):                         Promise<TalismanActivationResult> { return talismanActivate(id); }
  deactivateTalisman(id: string):                       Promise<TalismanActivationResult> { return talismanDeactivate(id); }
  deleteTalisman(id: string):                           Promise<{ deleted: boolean }>     { return talismanDelete(id); }
}
