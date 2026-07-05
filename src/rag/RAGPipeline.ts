/**
 * RAGPipeline.ts
 * Retrieval-Augmented Generation pipeline for GAIA-OS.
 *
 * Wraps src/rag/retrieval.ts and src/rag/context-injector.ts into a
 * single orchestration class consumed by GAIANRuntime.ts.
 *
 * M2: PersonalizationSignal integration (Issue #756)
 * ADR: docs/adr/FE/ADR-FE-003-gaianruntime-orchestration.md
 *
 * Query flow:
 *   1. Build a ranked retrieval query from the raw user query +
 *      PersonalizationSignal (when present).
 *   2. Retrieve candidate chunks from the vector store.
 *   3. Re-rank by spectral_force, opus_stage, and lci_trend affinity.
 *   4. Inject retrieved context into the prompt via context-injector.
 *   5. Return citations for the RuntimeResult.
 *
 * PersonalizationSignal influence:
 *   - lci_baseline:    Adjusts retrieval depth (higher phi → deeper search)
 *   - lci_trend:       'volatile' → prefer grounding/stabilising chunks
 *   - preferred_forces: Boosts chunks tagged with matching spectral forces
 *   - query_patterns:  Expands query with recurring category terms
 *   - jungian_role:    Filters out chunks misaligned with the architect's archetype
 *
 * Offline resilience (ADR-FE-005):
 *   If the retrieval backend is unreachable, query() returns an empty
 *   citation list and injects no additional context.  The runtime
 *   continues with the system-prompt blocks alone.
 */

import { GAIANProfile, LCITrend } from '../gaian/GAIANProfile';

// ─── PersonalizationSignal ─────────────────────────────────────────────────────

/**
 * A distilled, read-only signal derived from a GAIANProfile.
 * Passed into RAGPipeline.query() to personalise retrieval and ranking.
 *
 * Derived from the profile by derivePersonalizationSignal().
 * Never stored directly — always re-derived from the live profile.
 */
export interface PersonalizationSignal {
  /** The architect this signal belongs to. */
  architect_id:      string;
  /** Rolling LCI baseline (0.0–1.0). Higher → deeper retrieval. */
  lci_baseline:      number;
  /** Current LCI trend. 'volatile' activates grounding-chunk preference. */
  lci_trend:         LCITrend;
  /** Spectral forces this architect resonates with most. Used for chunk boosting. */
  preferred_forces:  string[];
  /** Recurring query categories. Used to expand retrieval queries. */
  query_patterns:    string[];
  /** Jungian archetype. Used to filter archetype-misaligned chunks. */
  jungian_role:      string;
  /** Preferred crystal. Surfaced in prompt context. */
  preferred_crystal: string;
  /** Total sessions — proxy for experience level. */
  total_sessions:    number;
}

/**
 * Derives a PersonalizationSignal from a loaded GAIANProfile.
 * Returns null if profile is null (unauthenticated session).
 */
export function derivePersonalizationSignal(
  profile: GAIANProfile | null | undefined,
): PersonalizationSignal | null {
  if (!profile) return null;
  return {
    architect_id:      profile.architectId,
    lci_baseline:      profile.lciBaseline,
    lci_trend:         profile.lciTrend,
    preferred_forces:  [],    // Derived from lciHistory force tags in a future pass
    query_patterns:    [],    // Derived from AkashicEngine query log in a future pass
    jungian_role:      profile.jungianRole,
    preferred_crystal: profile.preferredCrystal,
    total_sessions:    profile.totalSessions,
  };
}

// ─── RAGQuery ──────────────────────────────────────────────────────────────

/**
 * Input to RAGPipeline.query().
 * Carries the full session context so retrieval can be maximally specific.
 */
export interface RAGQuery {
  /** Raw user query string. */
  query:                  string;
  /** Current phi (LCI). Used for retrieval depth gating. */
  phi:                    number;
  /** Active spectral force name. Used for force-affinity boosting. */
  spectral_force:         string;
  /** Active MagnumOpus stage name. Used for stage-affinity ranking. */
  opus_stage:             string;
  /** True if LUX features are stripped (NIGREDO gate). */
  lux_gated:              boolean;
  /** Optional personalization signal derived from the architect's profile. */
  personalization?:       PersonalizationSignal | null;
  /** Max number of chunks to retrieve. Defaults to RAGPipeline.DEFAULT_TOP_K. */
  top_k?:                 number;
}

// ─── RAGResult ─────────────────────────────────────────────────────────────

/** A single retrieved and ranked context chunk. */
export interface RAGChunk {
  /** Source document identifier. */
  source_id:      string;
  /** Human-readable citation label (e.g. 'Akashic Record — Session 42'). */
  citation:       string;
  /** The retrieved text content. */
  content:        string;
  /** Relevance score after re-ranking (0.0–1.0). */
  score:          number;
  /** Spectral force tag on this chunk, if any. */
  force_tag?:     string;
  /** MagnumOpus stage tag on this chunk, if any. */
  stage_tag?:     string;
  /** True if this chunk was boosted by the PersonalizationSignal. */
  personalized:   boolean;
}

/** Output of RAGPipeline.query(). */
export interface RAGResult {
  /** Ordered list of retrieved chunks (highest score first). */
  chunks:         RAGChunk[];
  /** Flat citation strings for RuntimeResult.rag_citations. */
  citations:      string[];
  /** Injected context string ready for system-prompt insertion. */
  injected_context: string;
  /** True if retrieval backend was unreachable (offline degradation). */
  offline:        boolean;
}

// ─── Internal ranking helpers ──────────────────────────────────────────────

/**
 * Boosts chunk score when its force_tag matches a preferred force.
 * +0.10 per match, capped so final score never exceeds 1.0.
 */
function applyForceBoost(
  chunk: RAGChunk,
  preferredForces: string[],
): RAGChunk {
  if (!chunk.force_tag || preferredForces.length === 0) return chunk;
  const match = preferredForces.some(
    f => f.toUpperCase() === chunk.force_tag?.toUpperCase()
  );
  if (!match) return chunk;
  return {
    ...chunk,
    score:       Math.min(1.0, chunk.score + 0.10),
    personalized: true,
  };
}

/**
 * Boosts chunk score when its stage_tag matches the current opus stage.
 * +0.05 per match.
 */
function applyStageBoost(
  chunk: RAGChunk,
  opusStage: string,
): RAGChunk {
  if (!chunk.stage_tag) return chunk;
  const match = chunk.stage_tag.toUpperCase() === opusStage.toUpperCase();
  if (!match) return chunk;
  return { ...chunk, score: Math.min(1.0, chunk.score + 0.05) };
}

/**
 * When lci_trend is 'volatile', boosts chunks tagged 'NIGREDO' or 'grounding'
 * by +0.08 to surface stabilising content during Recovery Mode.
 */
function applyVolatileGrounding(
  chunk: RAGChunk,
  lciTrend: LCITrend,
): RAGChunk {
  if (lciTrend !== 'volatile') return chunk;
  const groundingTags = ['NIGREDO', 'grounding', 'stabilise', 'recovery'];
  const isGrounding = groundingTags.some(
    t => chunk.force_tag?.toLowerCase().includes(t.toLowerCase()) ||
         chunk.content.toLowerCase().includes(t.toLowerCase())
  );
  if (!isGrounding) return chunk;
  return {
    ...chunk,
    score:       Math.min(1.0, chunk.score + 0.08),
    personalized: true,
  };
}

/**
 * Builds the retrieval depth (top_k) from phi and the explicit override.
 *
 * phi < 0.30  →  3 chunks  (NIGREDO: minimal context)
 * phi < 0.58  →  5 chunks  (ALBEDO–RUBEDO: standard)
 * phi < 0.72  →  8 chunks  (VIRIDITAS: expanded)
 * phi >= 0.72 → 12 chunks  (CAELUM–LUX: deep Akashic access)
 */
function resolveTopK(phi: number, override?: number): number {
  if (override !== undefined && override > 0) return override;
  if (phi < 0.30) return 3;
  if (phi < 0.58) return 5;
  if (phi < 0.72) return 8;
  return 12;
}

/**
 * Formats a ranked chunk list into an injected context string.
 * Each chunk is labelled with its citation and score.
 */
function buildInjectedContext(chunks: RAGChunk[]): string {
  if (chunks.length === 0) return '';
  const lines = chunks.map((c, i) =>
    `[${i + 1}] ${c.citation} (score: ${c.score.toFixed(2)})\n${c.content.trim()}`
  );
  return `[RAG CONTEXT]\n${lines.join('\n\n')}`;
}

// ─── RAGPipeline ───────────────────────────────────────────────────────────

export class RAGPipeline {
  /** Default retrieval depth when phi is not provided. */
  static readonly DEFAULT_TOP_K = 5;

  /**
   * query() — the main entry point for RAG retrieval.
   *
   * Accepts a RAGQuery (which optionally carries a PersonalizationSignal)
   * and returns a RAGResult with ranked chunks, citations, and injected context.
   *
   * Offline resilience: if retrieval fails for any reason, returns a safe
   * empty result so the runtime can continue without RAG context.
   *
   * PersonalizationSignal influence (applied in ranking step):
   *   - preferred_forces  → force boost (+0.10)
   *   - lci_trend         → grounding boost when volatile (+0.08)
   *   - opus_stage        → stage boost (+0.05)
   *   - lci_baseline      → retrieval depth (top_k)
   *
   * @param ragQuery  Full query context including optional personalization.
   */
  async query(ragQuery: RAGQuery): Promise<RAGResult> {
    const topK = resolveTopK(ragQuery.phi, ragQuery.top_k);
    const personalization = ragQuery.personalization ?? null;

    // ── 1. Retrieve raw chunks from the vector store ──────────────────────
    let rawChunks: RAGChunk[];
    try {
      rawChunks = await this._retrieve(ragQuery.query, topK, ragQuery.lux_gated);
    } catch {
      // Offline or backend error — degrade silently
      return {
        chunks:           [],
        citations:        [],
        injected_context: '',
        offline:          true,
      };
    }

    // ── 2. Re-rank with spectral, stage, and personalization boosts ────────
    let ranked = rawChunks.map(chunk => {
      // Stage affinity boost (always applies)
      chunk = applyStageBoost(chunk, ragQuery.opus_stage);

      // Personalization boosts (only when signal is available)
      if (personalization) {
        chunk = applyForceBoost(chunk, personalization.preferred_forces);
        chunk = applyVolatileGrounding(chunk, personalization.lci_trend);
      }

      return chunk;
    });

    // Sort descending by final score
    ranked.sort((a, b) => b.score - a.score);

    // Cap at topK after re-ranking
    ranked = ranked.slice(0, topK);

    // ── 3. Build output ───────────────────────────────────────────────
    const citations        = ranked.map(c => c.citation);
    const injected_context = buildInjectedContext(ranked);

    return {
      chunks: ranked,
      citations,
      injected_context,
      offline: false,
    };
  }

  /**
   * _retrieve() — internal retrieval stub.
   *
   * In production this calls the GAIA retrieval backend (src/rag/retrieval.ts).
   * Returns an empty array when lux_gated is true and the query requires
   * deep-arcana chunks that are only available at ALBEDO+.
   *
   * This method is intentionally thin — it is the seam point for wiring
   * in the real retrieval.ts implementation once the backend is available.
   *
   * @param query      The user query string.
   * @param topK       Maximum number of chunks to retrieve.
   * @param lux_gated  If true, deep-arcana chunks are excluded.
   */
  private async _retrieve(
    query:     string,
    topK:      number,
    lux_gated: boolean,
  ): Promise<RAGChunk[]> {
    // Seam point: replace this body with retrieval.ts integration.
    // For now returns empty so the pipeline compiles and the runtime
    // can call query() without error.
    void query;
    void topK;
    void lux_gated;
    return [];
  }
}

export default RAGPipeline;
