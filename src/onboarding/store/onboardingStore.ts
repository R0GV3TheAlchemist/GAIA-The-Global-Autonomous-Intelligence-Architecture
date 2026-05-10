// C-OB01 — Onboarding Zustand Store
// Manages all onboarding state with persistence to onboarding_state.json
// via Tauri's fs API when available.

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import type {
  OnboardingState,
  OnboardingActions,
  OnboardingPhase,
  SystemCapabilities,
  UserIntent,
  DepthPreference,
  SensitiveTopic,
  ConsentPreferences,
} from '../types';

const DEFAULT_CONSENT: ConsentPreferences = {
  conversation_history: true,
  mood_signals: true,
  topic_patterns: true,
  usage_patterns: true,
  telemetry: false,
  cloud_backup: false,
};

const INITIAL_STATE: OnboardingState = {
  phase: 0,
  completed: false,
  interrupted: false,
  onboarding_version: '1.0',
  started_at: null,
  completed_at: null,
  system: null,
  name: '',
  intent: [],
  intent_other: '',
  depth_preference: 'reflective',
  sensitive_topics: [],
  consent: DEFAULT_CONSENT,
  account_created: false,
  account_email: null,
};

// Persist to Tauri fs if available, otherwise silently skip
async function persistState(state: OnboardingState): Promise<void> {
  try {
    const { writeTextFile, BaseDirectory } = await import('@tauri-apps/plugin-fs');
    await writeTextFile(
      'onboarding_state.json',
      JSON.stringify(state, null, 2),
      { baseDir: BaseDirectory.AppData }
    );
  } catch {
    // Browser/non-Tauri environment — silently continue
  }
}

export async function loadPersistedState(): Promise<Partial<OnboardingState> | null> {
  try {
    const { readTextFile, exists, BaseDirectory } = await import('@tauri-apps/plugin-fs');
    const fileExists = await exists('onboarding_state.json', { baseDir: BaseDirectory.AppData });
    if (!fileExists) return null;
    const raw = await readTextFile('onboarding_state.json', { baseDir: BaseDirectory.AppData });
    return JSON.parse(raw) as Partial<OnboardingState>;
  } catch {
    return null;
  }
}

type OnboardingStore = OnboardingState & OnboardingActions;

export const useOnboardingStore = create<OnboardingStore>()(
  subscribeWithSelector((set, get) => ({
    ...INITIAL_STATE,

    setPhase: (phase: OnboardingPhase) => {
      set({ phase });
      persistState(get());
    },

    nextPhase: () => {
      const current = get().phase;
      const next = Math.min(current + 1, 8) as OnboardingPhase;
      set({ phase: next });
      persistState(get());
    },

    setSystem: (system: SystemCapabilities) => {
      set({ system, started_at: new Date().toISOString() });
    },

    setName: (name: string) => {
      set({ name });
      persistState(get());
    },

    setIntent: (intent: UserIntent[]) => {
      set({ intent });
    },

    setIntentOther: (intent_other: string) => {
      set({ intent_other });
    },

    setDepthPreference: (depth_preference: DepthPreference) => {
      set({ depth_preference });
    },

    setSensitiveTopics: (sensitive_topics: SensitiveTopic[]) => {
      set({ sensitive_topics });
    },

    toggleConsent: (key: keyof ConsentPreferences) => {
      const current = get().consent;
      set({ consent: { ...current, [key]: !current[key] } });
    },

    setAccountCreated: (email: string) => {
      set({ account_created: true, account_email: email });
      persistState(get());
    },

    completeOnboarding: () => {
      const completed_at = new Date().toISOString();
      set({ completed: true, interrupted: false, completed_at, phase: 8 });
      persistState(get());

      // Seed Soul Mirror baseline via Tauri command if available
      const state = get();
      seedSoulMirror(state).catch(() => {});
    },

    resetOnboarding: () => {
      set({ ...INITIAL_STATE });
      persistState(get());
    },

    markInterrupted: () => {
      set({ interrupted: true });
      persistState(get());
    },

    resumeOnboarding: () => {
      set({ interrupted: false });
    },
  }))
);

async function seedSoulMirror(state: OnboardingState): Promise<void> {
  try {
    const { invoke } = await import('@tauri-apps/api/core');
    await invoke('seed_soul_mirror', {
      responses: {
        name: state.name,
        intent: state.intent,
        intent_other: state.intent_other,
        depth_preference: state.depth_preference,
        sensitive_topics: state.sensitive_topics,
        consent: state.consent,
        completed_at: state.completed_at,
      },
    });
  } catch {
    // Tauri command not yet implemented or browser env
  }
}
