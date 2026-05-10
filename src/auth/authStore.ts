/**
 * src/auth/authStore.ts
 * GAIA-OS Auth State — Sprint G-9
 *
 * Zustand store managing:
 *   - JWT access token (in-memory only — no localStorage, Tauri sandbox safe)
 *   - Decoded user claims (TokenPayload)
 *   - Auth lifecycle: login, logout, refreshUser
 *   - Hydration state (isHydrating) for app boot
 *
 * Design principle: the token never touches persistent storage in the
 * browser layer. The sidecar/Tauri layer may handle secure storage
 * separately via the OS keychain (future: G-10).
 *
 * Canon Ref: C01 (Sovereignty), C15 (Consent)
 */

import { create } from 'zustand';
import { issueToken, fetchMe, type TokenPayload, type TokenRequest, type AuthError } from './authApi';

// ------------------------------------------------------------------ //
//  State shape                                                         //
// ------------------------------------------------------------------ //

export interface AuthState {
  /** Raw JWT string — null when unauthenticated */
  token: string | null;
  /** Decoded user claims — null when unauthenticated */
  user: TokenPayload | null;
  /** True while the store is verifying a token on boot */
  isHydrating: boolean;
  /** True when a login/register request is in flight */
  isLoading: boolean;
  /** Last auth error message — cleared on next login attempt */
  error: string | null;

  // Actions
  login: (req: TokenRequest) => Promise<{ success: boolean; error?: AuthError }>;
  logout: () => void;
  /**
   * refreshUser — call on app boot with a previously-issued token.
   * Validates via GET /auth/me and populates the store if valid.
   */
  refreshUser: (token: string) => Promise<boolean>;
  clearError: () => void;
}

// ------------------------------------------------------------------ //
//  Store                                                               //
// ------------------------------------------------------------------ //

export const useAuthStore = create<AuthState>((set, get) => ({
  token:       null,
  user:        null,
  isHydrating: false,
  isLoading:   false,
  error:       null,

  // ---------------------------------------------------------------- //
  //  login                                                            //
  // ---------------------------------------------------------------- //
  login: async (req: TokenRequest) => {
    set({ isLoading: true, error: null });

    const result = await issueToken(req);

    if (result.error) {
      set({ isLoading: false, error: result.error.message });
      return { success: false, error: result.error };
    }

    const { access_token, user_id, role, gaian_slug } = result.data;

    // Construct the payload from the token response fields
    // (avoids a second round-trip to /auth/me on login)
    const user: TokenPayload = {
      user_id,
      role: role as 'user' | 'admin',
      gaian_slug: gaian_slug ?? undefined,
    };

    set({ token: access_token, user, isLoading: false, error: null });
    return { success: true };
  },

  // ---------------------------------------------------------------- //
  //  logout                                                           //
  // ---------------------------------------------------------------- //
  logout: () => {
    set({ token: null, user: null, error: null });
  },

  // ---------------------------------------------------------------- //
  //  refreshUser — boot-time token validation                         //
  // ---------------------------------------------------------------- //
  refreshUser: async (token: string) => {
    set({ isHydrating: true });

    const result = await fetchMe(token);

    if (result.error) {
      // Token invalid or expired — clear state silently
      set({ token: null, user: null, isHydrating: false });
      return false;
    }

    set({ token, user: result.data, isHydrating: false });
    return true;
  },

  // ---------------------------------------------------------------- //
  //  clearError                                                       //
  // ---------------------------------------------------------------- //
  clearError: () => set({ error: null }),
}));

// ------------------------------------------------------------------ //
//  Selector helpers (use in components)                               //
// ------------------------------------------------------------------ //

/** True when the user is authenticated and hydration is complete */
export const selectIsAuthed = (s: AuthState): boolean =>
  !s.isHydrating && s.token !== null && s.user !== null;

/** True when auth state is still being resolved on boot */
export const selectIsHydrating = (s: AuthState): boolean => s.isHydrating;
