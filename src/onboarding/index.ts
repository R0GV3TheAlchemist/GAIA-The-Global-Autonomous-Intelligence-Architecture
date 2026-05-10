// C-OB01 — Onboarding barrel export
export { OnboardingRouter } from './OnboardingRouter';
export { useOnboardingStore, loadPersistedState } from './store/onboardingStore';
export type {
  OnboardingPhase,
  OnboardingState,
  OnboardingActions,
  SystemCapabilities,
  DepthPreference,
  UserIntent,
  SensitiveTopic,
  ConsentPreferences,
} from './types';
