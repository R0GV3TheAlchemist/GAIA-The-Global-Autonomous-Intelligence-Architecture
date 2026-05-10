// C-OB01 — Onboarding Types
// All TypeScript interfaces and enums for the onboarding flow.

export type OnboardingPhase =
  | 0  // Bootstrap (silent)
  | 1  // Awakening
  | 2  // Introduction
  | 3  // Name Covenant
  | 4  // Three Questions
  | 5  // Consent
  | 6  // First Gift
  | 7  // Account Setup
  | 8; // Threshold

export type DepthPreference = 'surface' | 'reflective' | 'deep';

export interface SystemCapabilities {
  platform: 'windows' | 'macos' | 'linux' | 'unknown';
  hasGpu: boolean;
  diskSpaceGb: number;
  isOnline: boolean;
  locale: string;
  prefersReducedMotion: boolean;
  prefersHighContrast: boolean;
  hasScreenReader: boolean;
}

export type UserIntent =
  | 'productivity'
  | 'exploration'
  | 'self_discovery'
  | 'privacy'
  | 'building'
  | 'other';

export type SensitiveTopic =
  | 'mental_health'
  | 'relationships'
  | 'spiritual'
  | 'trauma'
  | 'political'
  | 'none'
  | 'later';

export interface ConsentPreferences {
  conversation_history: boolean;
  mood_signals: boolean;
  topic_patterns: boolean;
  usage_patterns: boolean;
  telemetry: boolean;
  cloud_backup: boolean;
}

export interface OnboardingState {
  phase: OnboardingPhase;
  completed: boolean;
  interrupted: boolean;
  onboarding_version: string;
  started_at: string | null;
  completed_at: string | null;

  // System
  system: SystemCapabilities | null;

  // Phase 3
  name: string;

  // Phase 4
  intent: UserIntent[];
  intent_other: string;
  depth_preference: DepthPreference;
  sensitive_topics: SensitiveTopic[];

  // Phase 5
  consent: ConsentPreferences;

  // Phase 7
  account_created: boolean;
  account_email: string | null;
}

export interface OnboardingActions {
  setPhase: (phase: OnboardingPhase) => void;
  nextPhase: () => void;
  setSystem: (system: SystemCapabilities) => void;
  setName: (name: string) => void;
  setIntent: (intent: UserIntent[]) => void;
  setIntentOther: (other: string) => void;
  setDepthPreference: (depth: DepthPreference) => void;
  setSensitiveTopics: (topics: SensitiveTopic[]) => void;
  toggleConsent: (key: keyof ConsentPreferences) => void;
  setAccountCreated: (email: string) => void;
  completeOnboarding: () => void;
  resetOnboarding: () => void;
  markInterrupted: () => void;
  resumeOnboarding: () => void;
}
