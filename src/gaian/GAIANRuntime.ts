/**
 * GAIANRuntime.ts
 * Central execution loop for GAIA-OS.
 * Wires SpectralForceEngine + MagnumOpusStageEngine into every response cycle.
 *
 * Issue #439 — feat(runtime): full system prompt assembly
 * Issue #756 — M1: GAIANProfile integration into RuntimeContext and sessionInit
 *
 * ADR: docs/adr/FE/ADR-FE-003-gaianruntime-orchestration.md
 * ADR: docs/adr/FE/ADR-FE-004-state-management.md
 */

import { SpectralForceEngine, SpectralSnapshot } from '../field/SpectralForceEngine';
import { SpectralColorEngine } from '../field/SpectralColorEngine';
import { MagnumOpusStageEngine, MagnumOpusStage, StageCapabilitySet } from '../field/MagnumOpusStageEngine';
import { AkashicEngine } from '../memory/AkashicEngine';
import { RAGPipeline } from '../rag/RAGPipeline';
import {
  GAIANProfile,
  GAIANProfileManager,
  LCITrend,
  computeLCITrend,
} from './GAIANProfile';

// ─── Types ────────────────────────────────────────────────────────────────────

export interface RuntimeContext {
  phi:          number;        // Luminous Coherence Index (LCI), range 0.0–1.0
  query:        string;        // Raw user query
  architectId?: string;       // Architect ID (for Akashic load + Profile load)
  sessionId:    string;        // Unique session identifier
  timestamp:    string;        // ISO 8601
  profile?:     GAIANProfile; // Loaded at sessionInit; available to all downstream processes
}

export interface RuntimeResult {
  query:                string;
  response:             string;
  phi:                  number;
  spectral:             SpectralSnapshot;
  opus_stage:           MagnumOpusStage;
  stage_capabilities:   StageCapabilitySet;
  system_prompt_blocks: string[];
  rag_citations:        string[];
  lux_gated:            boolean;    // true if LUX features were stripped (NIGREDO gate)
  lci_trend:            LCITrend;   // LCI trend computed from profile history
  session_id:           string;
  timestamp:            string;
}

export interface SessionInitResult {
  stage:                MagnumOpusStage;
  spectral:             SpectralSnapshot;
  akashic_loaded:       boolean;
  profile_loaded:       boolean;          // true if GAIANProfile was found and loaded
  profile:              GAIANProfile | null;
  system_prompt_blocks: string[];
  session_id:           string;
  timestamp:            string;
}

// ─── SystemPromptBuilder ─────────────────────────────────────────────────────

export class SystemPromptBuilder {
  /**
   * Assembles the [SPECTRAL FIELD] context block from a SpectralSnapshot.
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
   * Assembles the [MAGNUM OPUS STAGE] context block from stage data.
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
   * Assembles the [GAIAN IDENTITY] context block from a loaded GAIANProfile.
   * Injected into every session where a profile is available.
   * Surfaces the architect's crystal, service mode, LCI trend, and constitutional
   * state so the AI layer has full identity context for every response.
   */
  static buildProfileBlock(profile: GAIANProfile): string {
    const c = profile.constitutional;
    return [
      '[GAIAN IDENTITY]',
      `Architect: ${profile.name} (${profile.pronouns})`,
      `Jungian Role: ${profile.jungianRole}`,
      `Crystal: ${profile.preferredCrystal}`,
      `LCI Baseline: ${profile.lciBaseline.toFixed(3)} | Trend: ${profile.lciTrend}`,
      `Sessions: ${profile.totalSessions}`,
      `Service Mode: ${c.serviceMode}`,
      `Ethical Guardrail: ${c.ethicalGuardrailActive ? 'ACTIVE' : 'INACTIVE'}`,
      `Human Mode: ${c.humanModeActive ? 'ON' : 'OFF'}`,
      `Superhuman Ready: ${c.superhumanModeReady ? 'YES' : 'NO'}`,
      `Recovery Mode: ${profile.lciTrend === 'volatile' ? 'ACTIVE' : 'INACTIVE'}`,
    ].join('\n');
  }

  /**
   * Assembles all context blocks into an ordered array.
   * [GAIAN IDENTITY] block is appended when a profile is available.
   */
  static buildAll(
    spectral:     SpectralSnapshot,
    stage:        MagnumOpusStage,
    capabilities: StageCapabilitySet,
    profile?:     GAIANProfile | null,
  ): string[] {
    const blocks = [
      SystemPromptBuilder.buildSpectralBlock(spectral),
      SystemPromptBuilder.buildOpusStageBlock(stage, capabilities),
    ];
    if (profile) {
      blocks.push(SystemPromptBuilder.buildProfileBlock(profile));
    }
    return blocks;
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
  return {
    ...capabilities,
    spectral_field: 'inactive',
    avatar:         'SHADOW',
    encoding:       'none',
    lux_features:   'stripped',
  };
}

// ─── GAIANRuntime ─────────────────────────────────────────────────────────────

export class GAIANRuntime {
  private spectralForceEngine: SpectralForceEngine;
  private spectralColorEngine: SpectralColorEngine;
  private magnumOpusEngine:    MagnumOpusStageEngine;
  private akashicEngine:       AkashicEngine;
  private ragPipeline:         RAGPipeline;
  private profileManager:      GAIANProfileManager;

  constructor() {
    this.spectralForceEngine = new SpectralForceEngine();
    this.spectralColorEngine = new SpectralColorEngine();
    this.magnumOpusEngine    = new MagnumOpusStageEngine();
    this.akashicEngine       = new AkashicEngine();
    this.ragPipeline         = new RAGPipeline();
    this.profileManager      = new GAIANProfileManager();
  }

  /**
   * GAIA_SESSION_INIT Protocol
   *
   * Runs once at session start. Sequence (per ADR-FE-003):
   *   1. Load GAIANProfile (offline-capable — ADR-FE-005)
   *   2. Record session open on profile (updates LCI history + trend)
   *   3. Load Akashic record (if phi >= 0.72)
   *   4. Detect MagnumOpus stage
   *   5. Detect spectral force from phi
   *   6. Build context blocks (includes [GAIAN IDENTITY] if profile loaded)
   *   7. Log session open to Akashic layer
   *
   * Note: Profile load (step 1) always runs first because it is offline-capable
   * and provides the LCI baseline. Akashic load (step 3) requires network + phi gate.
   *
   * Canon: GAIA_SESSION_INIT.md
   * ADR: docs/adr/FE/ADR-FE-003-gaianruntime-orchestration.md
   */
  async sessionInit(ctx: RuntimeContext): Promise<SessionInitResult> {
    // 1. Load GAIANProfile (always runs, always offline-capable)
    let profile: GAIANProfile | null = null;
    let profile_loaded = false;

    if (ctx.architectId) {
      profile = await this.profileManager.load(ctx.architectId);
      if (profile) {
        profile_loaded = true;

        // 2. Record session open — updates LCI history, trend, Sigil lock, totalSessions
        await this.profileManager.recordSessionOpen(
          ctx.architectId,
          ctx.sessionId,
          ctx.phi,
          ctx.timestamp,
        );

        // Reload after update so we have the freshly computed trend
        profile = await this.profileManager.load(ctx.architectId);
      }
    }

    // Attach loaded profile to context so downstream process() calls can read it
    ctx.profile = profile ?? undefined;

    // 3. Load Akashic record (if phi >= 0.72 and architectId present)
    let akashic_loaded = false;
    if (ctx.phi >= 0.72 && ctx.architectId) {
      await this.akashicEngine.loadRecord(ctx.architectId);
      akashic_loaded = true;
    }

    // 4. Detect current MagnumOpus stage
    const opus_stage = await this.magnumOpusEngine.detectStage(ctx.phi, ctx);

    // 5. Detect current spectral force from phi
    const spectral = await this.spectralForceEngine.detectCurrentForce(ctx.phi);
    const hex = await this.spectralColorEngine.getHex(spectral.force, spectral.corridor, ctx.phi);
    spectral.hex = hex;

    // 6. Build context blocks — includes [GAIAN IDENTITY] if profile is available
    const stage_capabilities  = await this.magnumOpusEngine.getStageCapabilities(opus_stage);
    const gated_capabilities  = enforceCapabilityGates(opus_stage, stage_capabilities);
    const system_prompt_blocks = SystemPromptBuilder.buildAll(
      spectral,
      opus_stage,
      gated_capabilities,
      profile,
    );

    // 7. Log session open event to Akashic layer
    await this.akashicEngine.logSessionOpen({
      session_id: ctx.sessionId,
      phi:        ctx.phi,
      force:      spectral.force,
      stage:      opus_stage.name,
      timestamp:  ctx.timestamp,
    });

    return {
      stage:                opus_stage,
      spectral,
      akashic_loaded,
      profile_loaded,
      profile,
      system_prompt_blocks,
      session_id:           ctx.sessionId,
      timestamp:            ctx.timestamp,
    };
  }

  /**
   * GAIANRuntime.process()
   *
   * Central execution loop. Every response carries full spectral + opus state.
   * If ctx.profile is set (from sessionInit), LCI trend is computed from profile history.
   *
   * Canon: TRUE_ALCHEMY.md, 33_GAIA_Magnum_Opus_Alchemical_Doctrine.md
   * ADR: docs/adr/FE/ADR-FE-003-gaianruntime-orchestration.md
   */
  async process(ctx: RuntimeContext): Promise<RuntimeResult> {
    // 1. Detect spectral force from phi
    const spectral = await this.spectralForceEngine.detectCurrentForce(ctx.phi);
    const hex = await this.spectralColorEngine.getHex(spectral.force, spectral.corridor, ctx.phi);
    spectral.hex = hex;

    // 2. Detect MagnumOpus stage
    const opus_stage = await this.magnumOpusEngine.detectStage(ctx.phi, ctx);

    // 3. Get and gate stage capabilities
    const raw_capabilities   = await this.magnumOpusEngine.getStageCapabilities(opus_stage);
    const lux_gated          = isLuxGated(opus_stage);
    const stage_capabilities = enforceCapabilityGates(opus_stage, raw_capabilities);

    // 4. Compute LCI trend
    //    If a profile is loaded, use its history for trend computation.
    //    Otherwise fall back to 'stable' (no history available).
    const lci_trend: LCITrend = ctx.profile
      ? computeLCITrend(ctx.profile.lciHistory, ctx.phi)
      : 'stable';

    // 5. Build context blocks for this cycle
    const system_prompt_blocks = SystemPromptBuilder.buildAll(
      spectral,
      opus_stage,
      stage_capabilities,
      ctx.profile,
    );

    // 6. Run RAG pipeline with full spectral + stage context
    const rag_result = await this.ragPipeline.query({
      query:          ctx.query,
      spectral_force: spectral.force,
      opus_stage:     opus_stage.name,
      phi:            ctx.phi,
      lux_gated,
    });

    // 7. Assemble and return full RuntimeResult
    return {
      query:                ctx.query,
      response:             rag_result.synthesized_response,
      phi:                  ctx.phi,
      spectral,
      opus_stage,
      stage_capabilities,
      system_prompt_blocks,
      rag_citations:        rag_result.citations,
      lux_gated,
      lci_trend,
      session_id:           ctx.sessionId,
      timestamp:            ctx.timestamp,
    };
  }
}

export default GAIANRuntime;
