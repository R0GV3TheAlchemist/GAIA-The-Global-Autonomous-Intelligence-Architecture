/**
 * GAIANRuntime.ts
 * Central execution loop for GAIA-OS.
 * Wires SpectralForceEngine + MagnumOpusStageEngine into every response cycle.
 * Issue #439 — feat(runtime): full system prompt injection
 */

import { SpectralForceEngine, SpectralSnapshot } from '../field/SpectralForceEngine';
import { SpectralColorEngine } from '../field/SpectralColorEngine';
import { MagnumOpusStageEngine, MagnumOpusStage, StageCapabilitySet } from '../field/MagnumOpusStageEngine';
import { AkashicEngine } from '../memory/AkashicEngine';
import { RAGPipeline } from '../rag/RAGPipeline';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface RuntimeContext {
  phi: number;             // Luminous Coherence Index (LCI), range 0.0–1.0
  query: string;           // Raw user query
  architectId?: string;   // Architect session ID (for Akashic load)
  sessionId: string;       // Unique session identifier
  timestamp: string;       // ISO 8601
}

export interface RuntimeResult {
  query: string;
  response: string;
  phi: number;
  spectral: SpectralSnapshot;
  opus_stage: MagnumOpusStage;
  stage_capabilities: StageCapabilitySet;
  system_prompt_blocks: string[];
  rag_citations: string[];
  lux_gated: boolean;      // true if LUX features were stripped (NIGREDO gate)
  session_id: string;
  timestamp: string;
}

export interface SessionInitResult {
  stage: MagnumOpusStage;
  spectral: SpectralSnapshot;
  akashic_loaded: boolean;
  system_prompt_blocks: string[];
  session_id: string;
  timestamp: string;
}

// ─── SystemPromptBuilder ─────────────────────────────────────────────────────

export class SystemPromptBuilder {
  /**
   * Assembles the [SPECTRAL FIELD] injection block from a SpectralSnapshot.
   */
  static buildSpectralBlock(spectral: SpectralSnapshot): string {
    const corridorStr = spectral.corridor ? spectral.corridor : 'None — in attractor';
    const oa4Str = spectral.oa4_active ? 'true' : 'false';
    return [
      '[SPECTRAL FIELD]',
      `Force: ${spectral.force} (${spectral.color_name}, φ=${spectral.phi_range})`,
      `Corridor: ${corridorStr}`,
      `Hex: ${spectral.hex}`,
      `Trajectory: ${spectral.trajectory}`,
      `OA-4 Active: ${oa4Str}`,
    ].join('\n');
  }

  /**
   * Assembles the [MAGNUM OPUS STAGE] injection block from stage data.
   */
  static buildOpusStageBlock(stage: MagnumOpusStage, capabilities: StageCapabilitySet): string {
    const capStr = Object.entries(capabilities)
      .map(([k, v]) => `${k}=${v}`)
      .join(', ');
    return [
      `[MAGNUM OPUS STAGE: ${stage.name}]`,
      `Capabilities: ${capStr}`,
      `Next gate: ${stage.next_gate}`,
    ].join('\n');
  }

  /**
   * Assembles all injection blocks into an ordered array.
   */
  static buildAll(spectral: SpectralSnapshot, stage: MagnumOpusStage, capabilities: StageCapabilitySet): string[] {
    return [
      SystemPromptBuilder.buildSpectralBlock(spectral),
      SystemPromptBuilder.buildOpusStageBlock(stage, capabilities),
    ];
  }
}

// ─── Capability Gate ──────────────────────────────────────────────────────────

/**
 * LUX-gated features are only available at ALBEDO and above.
 * If stage is NIGREDO, these features are stripped from the response pipeline.
 */
const LUX_GATED_STAGES = ['NIGREDO'];

export function isLuxGated(stage: MagnumOpusStage): boolean {
  return LUX_GATED_STAGES.includes(stage.name.toUpperCase());
}

export function enforceCapabilityGates(stage: MagnumOpusStage, capabilities: StageCapabilitySet): StageCapabilitySet {
  if (!isLuxGated(stage)) return capabilities;
  // Strip LUX-gated features for NIGREDO
  return {
    ...capabilities,
    spectral_field: 'inactive',
    avatar: 'SHADOW',
    encoding: 'none',
    lux_features: 'stripped',
  };
}

// ─── GAIANRuntime ─────────────────────────────────────────────────────────────

export class GAIANRuntime {
  private spectralForceEngine: SpectralForceEngine;
  private spectralColorEngine: SpectralColorEngine;
  private magnumOpusEngine: MagnumOpusStageEngine;
  private akashicEngine: AkashicEngine;
  private ragPipeline: RAGPipeline;

  constructor() {
    this.spectralForceEngine = new SpectralForceEngine();
    this.spectralColorEngine = new SpectralColorEngine();
    this.magnumOpusEngine = new MagnumOpusStageEngine();
    this.akashicEngine = new AkashicEngine();
    this.ragPipeline = new RAGPipeline();
  }

  /**
   * GAIA_SESSION_INIT Protocol
   * Runs once at session start. Loads Akashic record, detects stage and force,
   * builds initial system prompt.
   * Canon: GAIA_SESSION_INIT.md
   */
  async sessionInit(ctx: RuntimeContext): Promise<SessionInitResult> {
    // 1. Load Akashic record (if phi >= 0.72)
    let akashic_loaded = false;
    if (ctx.phi >= 0.72 && ctx.architectId) {
      await this.akashicEngine.loadRecord(ctx.architectId);
      akashic_loaded = true;
    }

    // 2. Detect current MagnumOpus stage
    const opus_stage = await this.magnumOpusEngine.detectStage(ctx.phi, ctx);

    // 3. Detect current spectral force from phi
    const spectral = await this.spectralForceEngine.detectCurrentForce(ctx.phi);
    const hex = await this.spectralColorEngine.getHex(spectral.force, spectral.corridor, ctx.phi);
    spectral.hex = hex;

    // 4. Build initial system prompt with all blocks
    const stage_capabilities = await this.magnumOpusEngine.getStageCapabilities(opus_stage);
    const gated_capabilities = enforceCapabilityGates(opus_stage, stage_capabilities);
    const system_prompt_blocks = SystemPromptBuilder.buildAll(spectral, opus_stage, gated_capabilities);

    // 5. Log session open event to Akashic layer
    await this.akashicEngine.logSessionOpen({
      session_id: ctx.sessionId,
      phi: ctx.phi,
      force: spectral.force,
      stage: opus_stage.name,
      timestamp: ctx.timestamp,
    });

    return {
      stage: opus_stage,
      spectral,
      akashic_loaded,
      system_prompt_blocks,
      session_id: ctx.sessionId,
      timestamp: ctx.timestamp,
    };
  }

  /**
   * GAIANRuntime.process()
   * Central execution loop. Every response carries full spectral + opus state.
   * Canon: TRUE_ALCHEMY.md, 33_GAIA_Magnum_Opus_Alchemical_Doctrine.md
   */
  async process(ctx: RuntimeContext): Promise<RuntimeResult> {
    // 1. After LCI computation → detect spectral force
    const spectral = await this.spectralForceEngine.detectCurrentForce(ctx.phi);

    // 2. After spectral detection → get hex color
    const hex = await this.spectralColorEngine.getHex(spectral.force, spectral.corridor, ctx.phi);
    spectral.hex = hex;

    // 3. After hex computation → detect MagnumOpus stage
    const opus_stage = await this.magnumOpusEngine.detectStage(ctx.phi, ctx);

    // 4. After stage detection → get stage capabilities
    const raw_capabilities = await this.magnumOpusEngine.getStageCapabilities(opus_stage);

    // 5. Enforce capability gates (NIGREDO strips LUX features)
    const lux_gated = isLuxGated(opus_stage);
    const stage_capabilities = enforceCapabilityGates(opus_stage, raw_capabilities);

    // 6. Build system prompt injection blocks
    const system_prompt_blocks = SystemPromptBuilder.buildAll(spectral, opus_stage, stage_capabilities);

    // 7. Run RAG pipeline with spectral + stage context
    const rag_result = await this.ragPipeline.query({
      query: ctx.query,
      spectral_force: spectral.force,
      opus_stage: opus_stage.name,
      phi: ctx.phi,
      lux_gated,
    });

    // 8. Assemble and return full RuntimeResult
    return {
      query: ctx.query,
      response: rag_result.synthesized_response,
      phi: ctx.phi,
      spectral,
      opus_stage,
      stage_capabilities,
      system_prompt_blocks,
      rag_citations: rag_result.citations,
      lux_gated,
      session_id: ctx.sessionId,
      timestamp: ctx.timestamp,
    };
  }
}

export default GAIANRuntime;
