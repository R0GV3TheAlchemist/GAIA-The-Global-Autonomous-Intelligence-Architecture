/**
 * src/api/index.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Barrel export for all Tauri invoke() API clients.
 *
 * Usage:
 *   import { memoryRecall, TauriMemoryClient, stageEvaluate } from '../api';
 *   import { stateGet, stateOverride, GAIAStateClient, StateHUD } from '../api';
 *   import { talismanActivate, TalismanDoc } from '../api';
 */

export * from './memory';
export * from './state';
export * from '../mesh';
