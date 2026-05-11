/**
 * src/auth/authStore.ts
 * GAIA-OS Auth State — Sprint G-9
 *
 * Zustand v4 store (curried form) managing:
 *   - JWT access token (in-memory only)
 *   - Decoded user claims (TokenPayload)
 *   - Auth lifecycle: login, logout, refreshUser
 *   - Hydration state for app boot
 *
 * Canon Ref: C01 (Sovereignty), C15 (Consent)
 */

import { create } from 'zustand';
import { issueToken, fetchMe, type TokenPayload, type TokenRequest, type AuthError } from './authApi';

export interface AuthState {
  token: string | null;
  user: TokenPayload | null;
  isHydrating: boolean;
  isLoading: boolean;
  error: string | null;

  login: (req: TokenRequest) => Promise<{ success: boolean; error?: AuthError }>;
  logout: () => void;
  refreshUser: (token: string) => Promise<boolean>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()((set) => ({
  token:       null,
  user:        null,
  isHydrating: false,
  isLoading:   false,
  error:       null,

  login: async (req: TokenRequest) => {
    set({ isLoading: true, error: null });

    const result = await issueToken(req);

    if (result.error) {
      set({ isLoading: false, error: result.error.message });
      return { success: false, error: result.error };
    }

    const { access_token, user_id, role, gaian_slug } = result.data;

    const user: TokenPayload = {
      user_id,
      role: role as 'user' | 'admin',
      gaian_slug: gaian_slug ?? undefined,
    };

    set({ token: access_token, user, isLoading: false, error: null });
    return { success: true };
  },

  logout: () => {
    set({ token: null, user: null, error: null });
  },

  refreshUser: async (token: string) => {
    set({ isHydrating: true });

    const result = await fetchMe(token);

    if (result.error) {
      set({ token: null, user: null, isHydrating: false });
      return false;
    }

    set({ token, user: result.data, isHydrating: false });
    return true;
  },

  clearError: () => set({ error: null }),
}));

export const selectIsAuthed = (s: AuthState): boolean =>
  !s.isHydrating && s.token !== null && s.user !== null;

export const selectIsHydrating = (s: AuthState): boolean => s.isHydrating;
