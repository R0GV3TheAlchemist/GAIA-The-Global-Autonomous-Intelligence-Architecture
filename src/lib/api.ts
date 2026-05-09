/**
 * src/lib/api.ts
 * GAIA-OS — Web API Client  (web-app branch)
 *
 * Centralised fetch wrapper for all GAIA backend calls.
 * All endpoints are relative (/api/...) so the Vite proxy handles
 * routing to the Python backend in dev, and a reverse proxy handles
 * it in production.
 *
 * Exported helpers:
 *   api.get<T>(path)            — GET  /api/{path}
 *   api.post<T>(path, body)     — POST /api/{path}
 *   api.alignment(rmssd?)       — GET  /api/alignment
 *   api.health()                — GET  /api/health
 *
 * Auth token is read from localStorage on every call so it
 * reflects the latest login state without needing a React context.
 */

const BASE = '/api';

function getToken(): string | null {
  return localStorage.getItem('gaia_token');
}

async function request<T>(
  method: 'GET' | 'POST' | 'PUT' | 'DELETE',
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

export const api = {
  get:  <T>(path: string)              => request<T>('GET',  path),
  post: <T>(path: string, body: unknown) => request<T>('POST', path, body),

  /** GET /api/alignment?rmssd=<n> */
  alignment: (rmssd?: number | null) => {
    const qs = rmssd != null ? `?rmssd=${rmssd}` : '';
    return request<import('../hooks/useAlignment').AlignmentState>(
      'GET', `/alignment${qs}`,
    );
  },

  /** GET /api/health — backend liveness check */
  health: () => request<{ status: string }>('GET', '/health'),
};
