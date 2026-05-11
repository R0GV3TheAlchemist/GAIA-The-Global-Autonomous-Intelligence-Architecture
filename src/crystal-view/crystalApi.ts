/**
 * src/crystal-view/crystalApi.ts
 * GAIA-OS — Crystal Core API calls
 * Spec: C-CC01 §9
 */

import type { CrystalState, CoherenceTick } from './types';

const BASE = '/crystal';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) throw new Error(`Crystal API ${path} — ${res.status}`);
  return res.json() as Promise<T>;
}

/** GET /crystal/state — current CrystalState snapshot */
export async function fetchCrystalState(): Promise<CrystalState> {
  return get<CrystalState>('/state');
}

/** GET /crystal/history?days=N — array of CoherenceTick for trend arc */
export async function fetchCrystalHistory(days = 7): Promise<CoherenceTick[]> {
  return get<CoherenceTick[]>(`/history?days=${days}`);
}

/** POST /crystal/tick — force immediate re-tick */
export async function forceTick(): Promise<CrystalState> {
  const res = await fetch(`${BASE}/tick`, {
    method:  'POST',
    headers: { Accept: 'application/json' },
  });
  if (!res.ok) throw new Error(`Crystal tick — ${res.status}`);
  return res.json() as Promise<CrystalState>;
}
