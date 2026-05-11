/**
 * src/auth/authApi.ts
 * GAIA-OS Auth API Client — Sprint G-9
 *
 * Typed wrappers around:
 *   POST /auth/token  — issue JWT (login / register)
 *   GET  /auth/me     — verify token + return user claims
 *
 * Canon Ref: C01 (Sovereignty), C15 (Consent)
 */

// ------------------------------------------------------------------ //
//  Types (mirror core/auth.py)                                        //
// ------------------------------------------------------------------ //

export interface TokenRequest {
  user_id: string;
  admin_key?: string;
  gaian_slug?: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;   // seconds
  role: 'user' | 'admin';
  user_id: string;
  gaian_slug?: string;  // returned when a Gaian is bound to this identity
}

export interface TokenPayload {
  user_id: string;
  role: 'user' | 'admin';
  gaian_slug?: string;
  exp?: number;
}

export interface AuthError {
  code: 'INVALID_CREDENTIALS' | 'NETWORK_ERROR' | 'TOKEN_EXPIRED' | 'UNKNOWN';
  message: string;
}

// ------------------------------------------------------------------ //
//  Base URL — reads from Vite env or falls back to sidecar default    //
// ------------------------------------------------------------------ //

function getBaseUrl(): string {
  return (import.meta.env?.VITE_GAIA_API_URL as string | undefined) ?? 'http://127.0.0.1:8787';
}

async function gaiiaFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<{ data: T; error: null } | { data: null; error: AuthError }> {
  try {
    const res = await fetch(`${getBaseUrl()}${path}`, {
      headers: { 'Content-Type': 'application/json', ...(init?.headers ?? {}) },
      ...init,
    });

    if (res.status === 401) {
      return { data: null, error: { code: 'INVALID_CREDENTIALS', message: 'Identity not recognised. Check your credentials.' } };
    }
    if (res.status === 403) {
      return { data: null, error: { code: 'INVALID_CREDENTIALS', message: 'Access denied.' } };
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({})) as Record<string, unknown>;
      return {
        data: null,
        error: {
          code: 'UNKNOWN',
          message: (body['detail'] as string | undefined) ?? `Request failed (${res.status})`,
        },
      };
    }

    const data = (await res.json()) as T;
    return { data, error: null };
  } catch {
    return {
      data: null,
      error: {
        code: 'NETWORK_ERROR',
        message: 'Cannot reach GAIA. Is the sidecar running?',
      },
    };
  }
}

// ------------------------------------------------------------------ //
//  Auth API calls                                                      //
// ------------------------------------------------------------------ //

/**
 * POST /auth/token
 * Issues a JWT for the given user_id.
 */
export async function issueToken(
  req: TokenRequest,
): Promise<{ data: TokenResponse; error: null } | { data: null; error: AuthError }> {
  return gaiiaFetch<TokenResponse>('/auth/token', {
    method: 'POST',
    body: JSON.stringify(req),
  });
}

/**
 * GET /auth/me
 * Validates an existing token and returns its decoded claims.
 */
export async function fetchMe(
  token: string,
): Promise<{ data: TokenPayload; error: null } | { data: null; error: AuthError }> {
  return gaiiaFetch<TokenPayload>('/auth/me', {
    method: 'GET',
    headers: { Authorization: `Bearer ${token}` },
  });
}
