/**
 * src/api/index.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Barrel export for all Tauri invoke() API clients.
 *
 * Usage:
 *   import { memoryRecall, TauriMemoryClient, stageEvaluate } from '../api';
 *   import { MeshStatusWidget, useMeshStatus } from '../api';
 */

export * from './memory'
export * from '../mesh'
