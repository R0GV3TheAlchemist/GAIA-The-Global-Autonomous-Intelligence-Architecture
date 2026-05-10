/**
 * src/api/memory.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Typed Tauri invoke() wrappers for all Soul Mirror Rust commands.
 *
 * Architecture
 * ┌────────────────┐   invoke()   ┌──────────────────┐   reqwest   ┌──────────────┐
 * │  React / TS    │ ──────────▶ │  Rust (memory.rs)│ ──────────▶ │  Python      │
 * │  (renderer)    │ ◀────────── │  managed state   │ ◀────────── │  sidecar     │
 * └────────────────┘             └──────────────────┘             └──────────────┘
 *
 * Every function has a built-in fallback to the direct fetch client
 * (memoryClient.ts) so dev mode still works even if the sidecar isn't
 * bound to the Rust port yet.
 */

import { invoke } from '@tauri-apps/api/core';
import * as direct from '../memory/memoryClient';

// ─── Re-export shared types so callers only need one import ───────────────────
export type {
  MemoryKind,
  MemoryTier,
  RememberParams,
  MemoryHit,
  RetrieveParams,
  MemoryStats,
  MemoryHealth,
} from '../memory/memoryClient';

// ─── Affect types ─────────────────────────────────────────────────────────────

export interface AffectAnalyzeParams {
  user_id:    string;
  text:       string;
  session_id?: string;
  context?:   string[];
}

export interface AffectVector {
  valence:   number;   // -1.0 → +1.0
  arousal:   number;   //  0.0 → +1.0
  dominance: number;   //  0.0 → +1.0
  primary:   string;   // e.g. "joy", "sadness"
  secondary: string[];
  confidence: number;
}

export interface AffectSnapshot {
  ts:      number;
  vector:  AffectVector;
  text_snippet: string;
}

export interface AffectTrend {
  user_id:        string;
  window_days:    number;
  valence_trend:  number;   // ArcTrend slope
  arousal_trend:  number;
  dominant_state: string;
  snapshots:      AffectSnapshot[];
}

// ─── Stage types ──────────────────────────────────────────────────────────────

export interface StageEvaluateParams {
  user_id:      string;
  session_turn: number;
  affect?:      AffectVector;
  signals?:     Record<string, unknown>;
}

export type MagnumOpusStage =
  | 'Nigredo'
  | 'Albedo'
  | 'Citrinitas'
  | 'Rubedo'
  | 'Philosopher';

export interface StageResult {
  user_id:        string;
  current_stage:  MagnumOpusStage;
  previous_stage: MagnumOpusStage | null;
  advanced:       boolean;
  progress:       number;           // 0.0 – 1.0 within current stage
  reason:         string;
}

// ─── Key / DEK types ──────────────────────────────────────────────────────────

export interface KeyStatus {
  active_key_id:   string;
  key_count:       number;
  last_rotation:   number;   // unix ts
  rotation_due_in: number;   // seconds
}

export interface KeyRotateResult {
  new_key_id:    string;
  records_rekey: number;
  duration_ms:   number;
}

// ─── Internal: invoke with direct-fetch fallback ──────────────────────────────

type InvokeResult<T> = Promise<T>;

async function safeInvoke<T>(cmd: string, args: Record<string, unknown>): InvokeResult<T> {
  try {
    return await invoke<T>(cmd, args);
  } catch (err) {
    console.warn(`[GAIA:api/memory] invoke('${cmd}') failed, using direct fetch fallback:`, err);
    throw err;   // let caller handle; fallback wrappers catch it individually
  }
}

// ─── Memory commands ─────────────────────────────────────────────────────────

/**
 * Store a chat turn / fact / preference into sovereign memory.
 * Falls back to direct fetch if Tauri bridge is unavailable.
 */
export async function memoryRemember(
  params: direct.RememberParams,
): Promise<number> {
  try {
    const resp = await safeInvoke<{ id: number; status: string }>(
      'memory_remember',
      { params },
    );
    return resp.id;
  } catch {
    return direct.remember(params);
  }
}

/**
 * Retrieve semantically relevant memories for context injection.
 * Falls back to direct fetch if Tauri bridge is unavailable.
 */
export async function memoryRecall(
  params: direct.RetrieveParams,
): Promise<direct.MemoryHit[]> {
  try {
    const resp = await safeInvoke<{ hits: direct.MemoryHit[]; count: number }>(
      'memory_recall',
      { params },
    );
    return resp.hits;
  } catch {
    return direct.retrieve(params);
  }
}

/**
 * Distil a semantic pattern from recent memories.
 */
export async function memorySemantic(
  userId: string,
  query: string,
  topK = 5,
): Promise<direct.MemoryHit[]> {
  try {
    const resp = await safeInvoke<{ hits: direct.MemoryHit[]; count: number }>(
      'memory_semantic',
      { user_id: userId, query, top_k: topK },
    );
    return resp.hits;
  } catch {
    return direct.retrieve({ user_id: userId, query, top_k: topK });
  }
}

// ─── DEK / Key-ring commands ──────────────────────────────────────────────────

/** Return the health of the DEK ring — key count, last rotation, next due. */
export async function memoryKeyStatus(): Promise<KeyStatus> {
  return safeInvoke<KeyStatus>('memory_key_status', {});
}

/** Trigger a forward DEK rotation — re-keys all stored memory records. */
export async function memoryKeyRotate(): Promise<KeyRotateResult> {
  return safeInvoke<KeyRotateResult>('memory_key_rotate', {});
}

// ─── Affect commands ──────────────────────────────────────────────────────────

/**
 * Run NLP affect inference on a single text fragment.
 * Returns a VAD (Valence-Arousal-Dominance) vector + primary emotion label.
 */
export async function affectAnalyze(
  params: AffectAnalyzeParams,
): Promise<AffectVector> {
  return safeInvoke<AffectVector>('affect_analyze', { params });
}

/**
 * Fetch the last N days of affect snapshots for a user.
 */
export async function affectHistory(
  userId: string,
  days = 7,
): Promise<AffectSnapshot[]> {
  return safeInvoke<AffectSnapshot[]>('affect_history', {
    user_id: userId,
    days,
  });
}

/**
 * Get the ArcTrend (valence momentum) for a user over the last N days.
 */
export async function affectTrend(
  userId: string,
  windowDays = 7,
): Promise<AffectTrend> {
  return safeInvoke<AffectTrend>('affect_trend', {
    user_id:     userId,
    window_days: windowDays,
  });
}

// ─── Magnum Opus Stage command ────────────────────────────────────────────────

/**
 * Run a full Magnum Opus stage evaluation tick.
 * Called after each meaningful conversation turn.
 * Returns the user's current stage + whether they advanced.
 */
export async function stageEvaluate(
  params: StageEvaluateParams,
): Promise<StageResult> {
  return safeInvoke<StageResult>('stage_evaluate', { params });
}

// ─── TauriMemoryClient class (for DI / testing scenarios) ─────────────────────

/**
 * Object-oriented wrapper around the module-level functions.
 * Useful when you want to inject a memory client via React context
 * or stub it in tests.
 *
 * @example
 * const client = new TauriMemoryClient('user-uuid-123');
 * const hits   = await client.recall('What does the user love?');
 */
export class TauriMemoryClient {
  constructor(private readonly userId: string) {}

  /** Store a turn in sovereign memory. */
  async remember(
    text: string,
    opts: Omit<direct.RememberParams, 'user_id' | 'text'> = {},
  ): Promise<number> {
    return memoryRemember({ user_id: this.userId, text, ...opts });
  }

  /** Retrieve context-relevant memories. */
  async recall(
    query: string,
    opts: Omit<direct.RetrieveParams, 'user_id' | 'query'> = {},
  ): Promise<direct.MemoryHit[]> {
    return memoryRecall({ user_id: this.userId, query, ...opts });
  }

  /** Distil a semantic pattern. */
  async semantic(query: string, topK = 5): Promise<direct.MemoryHit[]> {
    return memorySemantic(this.userId, query, topK);
  }

  /** Analyse affect for a text fragment. */
  async analyzeAffect(
    text: string,
    sessionId?: string,
  ): Promise<AffectVector> {
    return affectAnalyze({ user_id: this.userId, text, session_id: sessionId });
  }

  /** Get affect history over the last N days. */
  async affectHistory(days = 7): Promise<AffectSnapshot[]> {
    return affectHistory(this.userId, days);
  }

  /** Get ArcTrend valence momentum. */
  async affectTrend(windowDays = 7): Promise<AffectTrend> {
    return affectTrend(this.userId, windowDays);
  }

  /** Run a Magnum Opus stage tick. */
  async evaluateStage(
    sessionTurn: number,
    affect?: AffectVector,
    signals?: Record<string, unknown>,
  ): Promise<StageResult> {
    return stageEvaluate({
      user_id:      this.userId,
      session_turn: sessionTurn,
      affect,
      signals,
    });
  }

  /** DEK ring health. */
  keyStatus(): Promise<KeyStatus> {
    return memoryKeyStatus();
  }

  /** Rotate DEK. */
  keyRotate(): Promise<KeyRotateResult> {
    return memoryKeyRotate();
  }
}
