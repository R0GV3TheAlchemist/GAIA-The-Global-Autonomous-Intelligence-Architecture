/**
 * Crystal suite barrel export.
 * Import View classes and store getters from one place.
 */

// ClarusLens
export { ClarusLensView } from './ClarusLens/ClarusLensView';
export {
  getCurrentFocus,
  getClarity,
  setIntention,
  completeIntention,
  addFocusArea,
  setFocusAreaStatus,
  resetLens,
  hydrateFromStorage as hydrateClarusLens,
  subscribe as subscribeClarusLens,
} from './ClarusLens/store';
export type {
  ClarusLensState,
  FocusArea,
  FocusStatus,
  Intention,
  ClarityBreakdown,
} from './ClarusLens/types';

// AnchorPrism
export { AnchorPrismView } from './AnchorPrism/AnchorPrismView';
export {
  getAnchors,
  addAnchor,
  reinforceAnchor,
  archiveAnchor,
  resetPrism,
  hydrateFromStorage as hydrateAnchorPrism,
  subscribe as subscribeAnchorPrism,
} from './AnchorPrism/store';
export type { AnchorPrismState, Anchor, AnchorCategory } from './AnchorPrism/types';

// SomnusVeil
export { SomnusVeilView } from './SomnusVeil/SomnusVeilView';
export { getSomnus, setRestState, logSleep, logDream, subscribe as subscribeSomnusVeil } from './SomnusVeil/store';
export type { SomnusVeilState, RestState, SleepEntry, DreamEntry } from './SomnusVeil/types';

// SovereignCore
export { SovereignCoreView } from './SovereignCore/SovereignCoreView';
export { getSovereign, setMode, addBoundary, toggleBoundary, removeBoundary, toggleFlag, subscribe as subscribeSovereignCore } from './SovereignCore/store';
export type { SovereignCoreState, SovereignMode, BoundaryRule, AutonomyFlag } from './SovereignCore/types';
