/**
 * src/lib/shadowApi.ts
 * Typed fetch layer for /api/shadow/* endpoints.
 *
 * All calls go through the same centralised request() helper as src/lib/api.ts
 * (relative paths, Bearer token from localStorage, 10 s timeout).
 *
 * Exported:
 *   shadowApi.getRecord(principalId)         — GET  /api/shadow/{id}
 *   shadowApi.evaluate(principalId, inputs?) — POST /api/shadow/{id}/evaluate
 *   shadowApi.reflect(principalId)           — POST /api/shadow/{id}/reflect
 *   shadowApi.history()                      — GET  /api/shadow/history
 */

import type {
  ShadowRecord,
  ShadowInputsPayload,
  ReflectionResponse,
} from '../shared/shadowTypes';

const BASE = '/api/shadow';

function getToken(): string | null {
  return localStorage.getItem('gaia_token');
}

async function request<T>(
  method: 'GET' | 'POST',
  path:   string,
  body?:  unknown,
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    'Accept':       'application/json',
  };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body:   body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(10_000),
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(
      (detail as { detail?: string }).detail ?? `HTTP ${res.status}`,
    );
  }
  return res.json() as Promise<T>;
}

export const shadowApi = {
  /**
   * Fetch the cached ShadowRecord for a principal.
   * Throws if no evaluation has been run yet (404).
   */
  getRecord: (principalId: string) =>
    request<ShadowRecord>('GET', `/${principalId}`),

  /**
   * Run a full shadow archetype evaluation.
   * Pass optional biometric/emotional signals; defaults are used if omitted.
   */
  evaluate: (principalId: string, inputs?: ShadowInputsPayload) =>
    request<ShadowRecord>('POST', `/${principalId}/evaluate`, inputs ?? null),

  /**
   * Record a reflection session (+0.05 integration_progress).
   * Must call evaluate() first or this will throw 404.
   */
  reflect: (principalId: string) =>
    request<ReflectionResponse>('POST', `/${principalId}/reflect`),

  /** Fetch all cached records across all principals (admin/debug). */
  history: () =>
    request<ShadowRecord[]>('GET', '/history'),
};
