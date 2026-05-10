// src/memory/index.ts
// Re-export everything from the memory module.

export { mountMemory } from './Memory';
export * from './memoryClient';
export * from './promptMemory';

// ─── Tauri invoke() bridge ────────────────────────────────────────────────────────
// Prefer these over the direct-fetch functions above when running in
// a Tauri context — they route through the Rust bridge (memory.rs)
// for full sovereign-memory security guarantees.
export {
  // Memory
  memoryRemember,
  memoryRecall,
  memorySemantic,
  // DEK ring
  memoryKeyStatus,
  memoryKeyRotate,
  // Affect
  affectAnalyze,
  affectHistory,
  affectTrend,
  // Magnum Opus stage
  stageEvaluate,
  // Class-based client
  TauriMemoryClient,
} from '../api/memory';

export type {
  AffectAnalyzeParams,
  AffectVector,
  AffectSnapshot,
  AffectTrend,
  StageEvaluateParams,
  MagnumOpusStage,
  StageResult,
  KeyStatus,
  KeyRotateResult,
} from '../api/memory';
