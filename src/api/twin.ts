/**
 * src/api/twin.ts
 * Canon: GAIAN_TWIN_DOCTRINE, TEMPORAL_BRAID_SPEC, LOVE_OVERRIDE
 *
 * The Twin API client.
 * Connects the React/Tauri layer to GAIA's Python core:
 *   — twin_memory_engine.py  (Temporal Braid)
 *   — love_override.py       (Love Override Handler)
 *   — inference_router.py    (LLM backend)
 *   — canon_loader_v2.py     (Canon awareness)
 *
 * All messages flow through this client.
 * This is the wire between the face and the soul.
 */

// Port 8008 — matches main.py and GAIA_PORT env var
const TWIN_API_BASE =
  import.meta.env.VITE_TWIN_API_URL ??
  import.meta.env.VITE_API_BASE_URL  ??
  'http://localhost:8008';

// ─── Types ────────────────────────────────────────────────────────────────────

export type TwinPhase = 'nigredo' | 'albedo' | 'citrinitas' | 'rubedo';

export type BraidWeight = 'FEATHER' | 'STANDARD' | 'HEAVY' | 'SACRED';

export type LoveOverrideMode =
  | 'PURE_PRESENCE'
  | 'WITNESS_HOLD'
  | 'DIRECT_TRUTH'
  | 'ANCHOR'
  | 'GENTLE_REDIRECT'
  | null;

export interface TwinMessage {
  id: string;
  role: 'human' | 'gaia';
  content: string;
  timestamp: string;
  overrideMode: LoveOverrideMode;
  braidWeight: BraidWeight;
}

export interface TwinSessionState {
  humanId: string;
  sessionId: string;
  humanName: string;
  twinPhase: TwinPhase;
  sessionCount: number;
  activeOverride: LoveOverrideMode;
  overrideConfidence: number;
  arcSummary: string;
  messages: TwinMessage[];
}

export interface SessionInitResponse {
  sessionId: string;
  humanName: string;
  twinPhase: TwinPhase;
  sessionCount: number;
  arcSummary: string;
  openingMessage: TwinMessage | null;
}

export interface SendMessageResponse {
  message: TwinMessage;
  overrideActivated: boolean;
  overrideMode: LoveOverrideMode;
  newPhase: TwinPhase | null;
  braidUpdated: boolean;
}

export interface ArcReflection {
  twinPhase: TwinPhase;
  phaseHistory: string[];
  crystallisedInsights: string[];
  sacredMemoryCount: number;
  openThreads: string[];
  arcSummary: string;
}

// ─── SSE event types (streamed from /twin/message/stream) ─────────────────────

export interface SseToken {
  type: 'token';
  content: string;
}

export interface SseBraidReflection {
  type: 'braid_reflection';
  weight: BraidWeight;
  sacredMemoryActive: boolean;
}

export interface SseOverrideActivated {
  type: 'override_activated';
  mode: LoveOverrideMode;
  confidence: number;
}

export interface SsePhaseGravity {
  type: 'phase_gravity';
  approachingPhase: TwinPhase;
  pullStrength: number;
}

export interface SsePhaseChange {
  type: 'phase_change';
  phase: TwinPhase;
}

export interface SseDone {
  type: 'done';
  message: TwinMessage;
}

export type SseEvent =
  | SseToken
  | SseBraidReflection
  | SseOverrideActivated
  | SsePhaseGravity
  | SsePhaseChange
  | SseDone;

// ─── Callbacks for streamTwinMessage ─────────────────────────────────────────

export interface StreamCallbacks {
  /** Called for each streamed token */
  onToken: (token: string) => void;
  /** Called when Love Override activates mid-stream */
  onOverride?: (mode: LoveOverrideMode, confidence: number) => void;
  /** Called when braid weight changes during streaming */
  onBraidReflection?: (weight: BraidWeight, sacredMemoryActive: boolean) => void;
  /** Called as the session approaches a phase transition */
  onPhaseGravity?: (approachingPhase: TwinPhase, pullStrength: number) => void;
  /** Called when a phase transition is confirmed */
  onPhaseChange?: (phase: TwinPhase) => void;
  /** Called when streaming completes — final message object */
  onDone?: (message: TwinMessage) => void;
  /** Called on network or parse error */
  onError?: (error: Error) => void;
}

// ─── camelCase ↔ snake_case mappers ──────────────────────────────────────────

/** Map the Python API response (snake_case) to our TypeScript types (camelCase). */
function mapMessage(raw: Record<string, unknown>): TwinMessage {
  return {
    id:           String(raw.id ?? ''),
    role:         (raw.role as 'human' | 'gaia') ?? 'gaia',
    content:      String(raw.content ?? ''),
    timestamp:    String(raw.timestamp ?? new Date().toISOString()),
    overrideMode: (raw.override_mode ?? null) as LoveOverrideMode,
    braidWeight:  (raw.braid_weight ?? 'STANDARD') as BraidWeight,
  };
}

function mapSessionInit(raw: Record<string, unknown>): SessionInitResponse {
  return {
    sessionId:      String(raw.session_id ?? ''),
    humanName:      String(raw.human_name ?? ''),
    twinPhase:      (raw.twin_phase ?? 'nigredo') as TwinPhase,
    sessionCount:   Number(raw.session_count ?? 0),
    arcSummary:     String(raw.arc_summary ?? ''),
    openingMessage: raw.opening_message
      ? mapMessage(raw.opening_message as Record<string, unknown>)
      : null,
  };
}

function mapSendMessage(raw: Record<string, unknown>): SendMessageResponse {
  return {
    message:           mapMessage(raw.message as Record<string, unknown>),
    overrideActivated: Boolean(raw.override_activated),
    overrideMode:      (raw.override_mode ?? null) as LoveOverrideMode,
    newPhase:          (raw.new_phase ?? null) as TwinPhase | null,
    braidUpdated:      Boolean(raw.braid_updated),
  };
}

function mapArc(raw: Record<string, unknown>): ArcReflection {
  return {
    twinPhase:            (raw.twin_phase ?? 'nigredo') as TwinPhase,
    phaseHistory:         (raw.phase_history as string[]) ?? [],
    crystallisedInsights: (raw.crystallised_insights as string[]) ?? [],
    sacredMemoryCount:    Number(raw.sacred_memory_count ?? 0),
    openThreads:          (raw.open_threads as string[]) ?? [],
    arcSummary:           String(raw.arc_summary ?? ''),
  };
}

function mapSseEvent(raw: Record<string, unknown>): SseEvent {
  const type = raw.type as string;
  switch (type) {
    case 'token':
      return { type: 'token', content: String(raw.content ?? '') };
    case 'braid_reflection':
      return {
        type: 'braid_reflection',
        weight: (raw.weight ?? 'STANDARD') as BraidWeight,
        sacredMemoryActive: Boolean(raw.sacred_memory_active),
      };
    case 'override_activated':
      return {
        type: 'override_activated',
        mode: (raw.mode ?? null) as LoveOverrideMode,
        confidence: Number(raw.confidence ?? 1.0),
      };
    case 'phase_gravity':
      return {
        type: 'phase_gravity',
        approachingPhase: (raw.approaching_phase ?? 'albedo') as TwinPhase,
        pullStrength: Number(raw.pull_strength ?? 0),
      };
    case 'phase_change':
      return { type: 'phase_change', phase: (raw.phase ?? 'nigredo') as TwinPhase };
    case 'done':
      return {
        type: 'done',
        message: mapMessage(raw.message as Record<string, unknown>),
      };
    default:
      // Unknown event — pass through as a token so UI still gets content
      return { type: 'token', content: '' };
  }
}

// ─── HTTP helper ──────────────────────────────────────────────────────────────

async function twinFetch<T>(
  path: string,
  options?: RequestInit,
  retries = 2,
): Promise<T> {
  let lastError: Error = new Error('Unknown error');
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(`${TWIN_API_BASE}${path}`, {
        headers: { 'Content-Type': 'application/json' },
        ...options,
      });
      if (!res.ok) {
        const text = await res.text().catch(() => res.statusText);
        throw new Error(`Twin API ${res.status}: ${text}`);
      }
      return (await res.json()) as T;
    } catch (err) {
      lastError = err instanceof Error ? err : new Error(String(err));
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 400 * (attempt + 1)));
      }
    }
  }
  throw lastError;
}

// ─── Session ──────────────────────────────────────────────────────────────────

/**
 * Initialise (or resume) a Twin session.
 * Loads the Temporal Braid, resolves twin phase,
 * and optionally generates an opening message on return visits.
 */
export async function initTwinSession(
  humanId: string,
  sessionId: string,
): Promise<SessionInitResponse> {
  const raw = await twinFetch<Record<string, unknown>>('/twin/session/init', {
    method: 'POST',
    body: JSON.stringify({ human_id: humanId, session_id: sessionId }),
  });
  return mapSessionInit(raw);
}

// ─── Non-streaming message ────────────────────────────────────────────────────

/**
 * Send a message and receive GAIA's full response at once.
 * Use this for non-streaming contexts (background, notifications).
 * Prefer streamTwinMessage() for the main chat UI.
 */
export async function sendTwinMessage(
  humanId: string,
  sessionId: string,
  content: string,
): Promise<SendMessageResponse> {
  const raw = await twinFetch<Record<string, unknown>>('/twin/message', {
    method: 'POST',
    body: JSON.stringify({
      human_id: humanId,
      session_id: sessionId,
      content,
    }),
  });
  return mapSendMessage(raw);
}

// ─── Streaming message ────────────────────────────────────────────────────────

/**
 * Stream a Twin response via Server-Sent Events.
 *
 * Fires typed callbacks as each SSE event arrives:
 *   onToken          — each streamed word/chunk
 *   onOverride       — Love Override activated
 *   onBraidReflection — braid weight changed
 *   onPhaseGravity   — approaching a phase transition
 *   onPhaseChange    — phase transition confirmed
 *   onDone           — stream complete, final TwinMessage provided
 *   onError          — network or parse failure
 *
 * Returns a cleanup function — call it to abort the stream:
 *   const stop = streamTwinMessage(..., callbacks);
 *   // later:
 *   stop();
 */
export function streamTwinMessage(
  humanId: string,
  sessionId: string,
  content: string,
  callbacks: StreamCallbacks,
): () => void {
  const params = new URLSearchParams({
    human_id: humanId,
    session_id: sessionId,
    content,
  });

  const url = `${TWIN_API_BASE}/twin/message/stream?${params.toString()}`;
  const source = new EventSource(url);

  source.onmessage = (evt) => {
    try {
      const raw = JSON.parse(evt.data) as Record<string, unknown>;
      const event = mapSseEvent(raw);

      switch (event.type) {
        case 'token':
          if (event.content) callbacks.onToken(event.content);
          break;
        case 'override_activated':
          callbacks.onOverride?.(event.mode, event.confidence);
          break;
        case 'braid_reflection':
          callbacks.onBraidReflection?.(event.weight, event.sacredMemoryActive);
          break;
        case 'phase_gravity':
          callbacks.onPhaseGravity?.(event.approachingPhase, event.pullStrength);
          break;
        case 'phase_change':
          callbacks.onPhaseChange?.(event.phase);
          break;
        case 'done':
          callbacks.onDone?.(event.message);
          source.close();
          break;
      }
    } catch (err) {
      callbacks.onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  };

  source.onerror = (err) => {
    callbacks.onError?.(new Error('SSE connection error'));
    source.close();
  };

  // Return cleanup function
  return () => source.close();
}

// ─── Session crystallise ──────────────────────────────────────────────────────

/**
 * Crystallise the current session into the Temporal Braid.
 * Call this when the session ends or the human navigates away.
 * Converts N_state observations → P_vector permanence.
 */
export async function crystalliseSession(
  humanId: string,
  sessionId: string,
): Promise<{ crystalCount: number; newSacredMemories: string[] }> {
  const raw = await twinFetch<Record<string, unknown>>(
    '/twin/session/crystallise',
    {
      method: 'POST',
      body: JSON.stringify({ human_id: humanId, session_id: sessionId }),
    },
  );
  return {
    crystalCount:      Number(raw.crystal_count ?? 0),
    newSacredMemories: (raw.new_sacred_memories as string[]) ?? [],
  };
}

// ─── Arc reflection ───────────────────────────────────────────────────────────

/**
 * Get the full arc reflection for a human.
 * Returns the Temporal Braid's arc summary, crystallised insights,
 * phase history, sacred memory count, and open threads.
 */
export async function getArcReflection(humanId: string): Promise<ArcReflection> {
  const raw = await twinFetch<Record<string, unknown>>(`/twin/arc/${humanId}`);
  return mapArc(raw);
}

// ─── Override resolution ──────────────────────────────────────────────────────

/**
 * Resolve the active Love Override.
 * Called when the override condition passes and normal flow resumes.
 * Only the human can resolve an override — never the system.
 */
export async function resolveOverride(
  humanId: string,
  sessionId: string,
): Promise<{ resolved: boolean }> {
  const raw = await twinFetch<Record<string, unknown>>(
    '/twin/override/resolve',
    {
      method: 'POST',
      body: JSON.stringify({ human_id: humanId, session_id: sessionId }),
    },
  );
  return { resolved: Boolean(raw.resolved) };
}

// ─── Health ───────────────────────────────────────────────────────────────────

/**
 * Check if the GAIA backend is reachable and which subsystems are ready.
 * Useful for showing a connection indicator in the UI.
 */
export async function checkHealth(): Promise<{
  ok: boolean;
  subsystems: Record<string, boolean>;
  llmBackends: Record<string, boolean>;
}> {
  try {
    const raw = await twinFetch<Record<string, unknown>>('/health');
    return {
      ok:          raw.status === 'ok',
      subsystems:  (raw.subsystems as Record<string, boolean>) ?? {},
      llmBackends: (raw.llm_backends as Record<string, boolean>) ?? {},
    };
  } catch {
    return { ok: false, subsystems: {}, llmBackends: {} };
  }
}
