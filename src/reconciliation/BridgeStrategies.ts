/**
 * BridgeStrategies.ts
 * Executes named bridge strategies for the ARFP reconciliation engine.
 *
 * Position in the ARFP phase sequence:
 *   DETECT → DIAGNOSE → WITNESS → [BRIDGE] → INTEGRATE
 *
 * Architecture contract:
 *   - Each strategy handler is a pure async function: inputs in, BridgeResult out.
 *   - No strategy modifies Fragment state directly — all mutations are expressed
 *     as BridgeResult fields, which the engine applies.
 *   - Strategies that require principal attention emit an action payload;
 *     they do not block waiting for a response (non-blocking, event-driven).
 *   - The `calling_escalation` and `slow_witness` strategies are terminal:
 *     they hand control to the principal and halt automated progression.
 *
 * Canon layer : GAIA-OS Core — Integrity & Coherence Engine
 * Spec version : 1.0  (June 27 2026)
 * Depends on   : reconciliationTypes.ts, WitnessProtocol.ts
 */

import {
  type Fragment,
  type Diagnosis,
  type BridgeResult,
  type BridgeStrategyName,
  type ReconciliationPhase,
  type ARFPConfig,
  type ID,
  type ISOTimestamp,
  DEFAULT_ARFP_CONFIG,
} from './reconciliationTypes';

import type { WitnessSummary } from './WitnessProtocol';

// ---------------------------------------------------------------------------
// 0. Adapter interfaces
// ---------------------------------------------------------------------------
// BridgeStrategies reads from and writes to external subsystems through
// these adapters. Injected at construction — no direct subsystem coupling.

/** Adapter for system process control operations. */
export interface SystemControlAdapter {
  /** Re-declare desired state; controller will converge actual to desired. */
  reconcileState(processId: ID, desiredState: Record<string, unknown>): Promise<void>;
  /** Initiate a controlled process restart with health gate. */
  restartProcess(processId: ID): Promise<void>;
  /** Shed low-priority events to reduce queue depth. */
  drainQueue(processId: ID, priorityThreshold: 'low' | 'medium'): Promise<number>;
  /** Attempt circuit breaker half-open probe. */
  resetCircuit(processId: ID): Promise<'open' | 'half_open' | 'closed'>;
}

/** Adapter for surfacing prompts and dialogues to the principal. */
export interface PrincipalSurfaceAdapter {
  /** Surface a targeted reflection prompt in the principal’s interface. */
  surfaceReflectionPrompt(principalId: ID, prompt: ReflectionPrompt): Promise<void>;
  /** Open a shadow dialogue session with a specific archetype. */
  openShadowDialogue(principalId: ID, dialogue: ShadowDialoguePayload): Promise<void>;
  /** Surface a value-action gap for conscious renegotiation. */
  surfaceValueRealignment(principalId: ID, payload: ValueRealignmentPayload): Promise<void>;
  /** Surface a goal conflict map for prioritisation. */
  surfaceGoalConflictMap(principalId: ID, payload: GoalConflictMapPayload): Promise<void>;
  /** Surface a repair invitation for a relational rupture. */
  surfaceRepairInvitation(principalId: ID, payload: RepairInvitationPayload): Promise<void>;
  /** Surface a contact invitation for a withdrawn relationship. */
  surfaceContactInvitation(principalId: ID, payload: ContactInvitationPayload): Promise<void>;
  /** Surface a reciprocity rebalance prompt. */
  surfaceReciprocityRebalance(principalId: ID, payload: ReciprocityRebalancePayload): Promise<void>;
  /** Issue a CALLING to the principal (used by calling_escalation strategy). */
  issueCallingSurface(principalId: ID, payload: CallingPayload): Promise<void>;
}

// ---------------------------------------------------------------------------
// 1. Payload types for principal-surface actions
// ---------------------------------------------------------------------------

export interface ReflectionPrompt {
  fragment_id:    ID;
  archetype_id:   ID | null;
  prompt_text:    string;
  context:        string;
  suggested_mode: 'written' | 'spoken' | 'somatic' | 'any';
}

export interface ShadowDialoguePayload {
  fragment_id:    ID;
  archetype_id:   ID;
  archetype_label: string;
  opening_frame:  string;   // the system’s invitation into the dialogue
  active_patterns: string[];
  witness_context: string;  // distilled from WitnessSummary
}

export interface ValueRealignmentPayload {
  fragment_id:    ID;
  gap_description: string;
  conflicting_values: string[];
  recent_actions:    string[];
  invitation:        string;
}

export interface GoalConflictMapPayload {
  fragment_id:    ID;
  conflicting_goals: Array<{ label: string; tension: string }>;
  invitation:        string;
}

export interface RepairInvitationPayload {
  fragment_id:    ID;
  pair_id:        ID;
  partner_label:  string;
  rupture_count:  number;
  oldest_rupture_days: number;
  invitation:     string;
}

export interface ContactInvitationPayload {
  fragment_id:    ID;
  pair_id:        ID;
  partner_label:  string;
  contact_gap_days: number;
  invitation:     string;
}

export interface ReciprocityRebalancePayload {
  fragment_id:     ID;
  pair_id:         ID;
  partner_label:   string;
  initiation_ratio: number;
  direction:        string;
  invitation:       string;
}

export interface CallingPayload {
  fragment_id:    ID;
  level:          'NOTICE' | 'PROMPT' | 'SUMMONS' | 'CRITICAL';
  reason:         string;
  witness_notes:  string[];
}

// ---------------------------------------------------------------------------
// 2. Strategy context envelope
// ---------------------------------------------------------------------------

/**
 * Full context passed to every strategy handler.
 * Handlers destructure only what they need.
 */
export interface StrategyContext {
  principalId: ID;
  fragment:    Fragment;
  diagnosis:   Diagnosis;
  witness:     WitnessSummary | null;
  config:      ARFPConfig;
  system:      SystemControlAdapter;
  surface:     PrincipalSurfaceAdapter;
}

// ---------------------------------------------------------------------------
// 3. BridgeStrategies class
// ---------------------------------------------------------------------------

export class BridgeStrategies {
  private readonly config:  ARFPConfig;
  private readonly system:  SystemControlAdapter;
  private readonly surface: PrincipalSurfaceAdapter;

  constructor(
    adapters: { system: SystemControlAdapter; surface: PrincipalSurfaceAdapter },
    config: Partial<ARFPConfig> = {},
  ) {
    this.config  = { ...DEFAULT_ARFP_CONFIG, ...config };
    this.system  = adapters.system;
    this.surface = adapters.surface;
  }

  /**
   * Primary entry point. Dispatches to the named strategy handler.
   * Returns a BridgeResult expressing the outcome; the engine applies it.
   */
  async execute(
    principalId: ID,
    fragment:    Fragment,
    diagnosis:   Diagnosis,
    witness:     WitnessSummary | null = null,
  ): Promise<BridgeResult> {
    const ctx: StrategyContext = {
      principalId,
      fragment,
      diagnosis,
      witness,
      config:  this.config,
      system:  this.system,
      surface: this.surface,
    };

    const strategy = diagnosis.recommended_strategy;

    switch (strategy) {
      // System
      case 'state_reconcile':      return this._stateReconcile(ctx);
      case 'process_restart':      return this._processRestart(ctx);
      case 'queue_drain':          return this._queueDrain(ctx);
      case 'circuit_reset':        return this._circuitReset(ctx);
      // Psyche
      case 'shadow_dialogue':      return this._shadowDialogue(ctx);
      case 'reflection_prompt':    return this._reflectionPrompt(ctx);
      case 'value_realignment':    return this._valueRealignment(ctx);
      case 'goal_conflict_map':    return this._goalConflictMap(ctx);
      // Relational
      case 'repair_initiation':    return this._repairInitiation(ctx);
      case 'contact_invitation':   return this._contactInvitation(ctx);
      case 'reciprocity_rebalance': return this._reciprocityRebalance(ctx);
      // Escalation
      case 'slow_witness':         return this._slowWitness(ctx);
      case 'calling_escalation':   return this._callingEscalation(ctx);
      default:
        return this._unknownStrategy(ctx, strategy as BridgeStrategyName);
    }
  }

  // =========================================================================
  // SYSTEM STRATEGIES
  // =========================================================================

  /**
   * state_reconcile — re-declare desired state and let the controller converge.
   * The lightest-touch system bridge: does not restart, does not shed events.
   * Appropriate when divergence is modest and the process is still alive.
   */
  private async _stateReconcile(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis } = ctx;
    const processId    = fragment.metadata['process_id'] as ID;
    const desiredState = fragment.metadata['desired_state'] as Record<string, unknown> | undefined
      ?? {};

    try {
      await ctx.system.reconcileState(processId, desiredState);
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `State reconciliation initiated for process '${fragment.label}'. ` +
        `Controller convergence in progress.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `State reconciliation failed: ${String(err)}. Routing to slow_witness.`,
        'WITNESS',
      );
    }
  }

  /**
   * process_restart — controlled restart with health gate.
   * Used when a process is likely dead or in an unrecoverable error state.
   * The adapter implementation is responsible for the health check before
   * returning — this strategy trusts the adapter’s gate.
   */
  private async _processRestart(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis } = ctx;
    const processId = fragment.metadata['process_id'] as ID;

    try {
      await ctx.system.restartProcess(processId);
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Process '${fragment.label}' restarted successfully and passed health gate.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Process restart failed: ${String(err)}. Routing to calling_escalation.`,
        'WITNESS', // engine will re-diagnose as calling_escalation
      );
    }
  }

  /**
   * queue_drain — shed low-priority events to reduce queue depth.
   * Preserves medium and high-priority events; drops low-priority backlog.
   * Returns the number of events shed in the BridgeResult notes.
   */
  private async _queueDrain(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis } = ctx;
    const processId = fragment.metadata['process_id'] as ID;

    try {
      const shed = await ctx.system.drainQueue(processId, 'low');
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Queue drain complete for '${fragment.label}'. ` +
        `${shed} low-priority events shed. Medium and high-priority events preserved.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Queue drain failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  /**
   * circuit_reset — probe the circuit breaker with a half-open test.
   * If the probe succeeds (circuit closes), routes to INTEGRATE.
   * If it fails or remains open, routes back to WITNESS.
   */
  private async _circuitReset(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis } = ctx;
    const processId = fragment.metadata['process_id'] as ID;

    try {
      const newState = await ctx.system.resetCircuit(processId);
      const success  = newState === 'closed';
      return buildResult(fragment, diagnosis.recommended_strategy, success,
        success
          ? `Circuit for '${fragment.label}' closed successfully. Downstream calls resuming.`
          : `Circuit probe returned state '${newState}'. Downstream not yet stable. Returning to witness.`,
        success ? 'INTEGRATE' : 'WITNESS',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Circuit reset failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  // =========================================================================
  // PSYCHE STRATEGIES
  // =========================================================================

  /**
   * shadow_dialogue — open a structured encounter between ego and archetype.
   * This is the deepest psyche bridge. It surfaces a dialogue frame to the
   * principal’s interface and waits for principal engagement.
   * The strategy itself succeeds when the surface call completes (the prompt
   * is delivered). Integration is confirmed by IntegrationVerifier later.
   */
  private async _shadowDialogue(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, witness, principalId } = ctx;
    const archetypeId    = fragment.archetype_id!;
    const archetypeLabel = fragment.label.replace('Autonomous archetype — ', '');
    const patterns       = (fragment.metadata['active_patterns'] as string[] | undefined) ?? [];

    const witnessContext = witness
      ? buildWitnessContextString(witness)
      : 'No witness observations recorded.';

    const openingFrame = composeDialogueFrame(archetypeLabel, patterns, witness);

    try {
      await ctx.surface.openShadowDialogue(principalId, {
        fragment_id:     fragment.id,
        archetype_id:    archetypeId,
        archetype_label: archetypeLabel,
        opening_frame:   openingFrame,
        active_patterns: patterns,
        witness_context: witnessContext,
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Shadow dialogue opened for archetype '${archetypeLabel}'. ` +
        `Awaiting principal engagement. Integration pending verification.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Shadow dialogue surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  /**
   * reflection_prompt — surface a targeted prompt to the principal.
   * Lighter than shadow_dialogue — appropriate for reflection gaps and
   * archetypes in early awareness stage where direct dialogue is premature.
   */
  private async _reflectionPrompt(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, witness, principalId } = ctx;
    const gapDays = fragment.metadata['gap_days'] as number | undefined;
    const score   = fragment.metadata['integration_score'] as number | undefined;

    const promptText = gapDays != null
      ? composeReflectionGapPrompt(gapDays, witness)
      : composeArchetypeReflectionPrompt(fragment.label, score ?? 50, witness);

    const context = witness?.notable_observations.join(' | ')
      ?? diagnosis.root_signal;

    try {
      await ctx.surface.surfaceReflectionPrompt(principalId, {
        fragment_id:    fragment.id,
        archetype_id:   fragment.archetype_id,
        prompt_text:    promptText,
        context,
        suggested_mode: witness?.dominant_categories.includes('somatic') ? 'somatic' : 'any',
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Reflection prompt delivered. ` +
        `Suggested mode: ${witness?.dominant_categories.includes('somatic') ? 'somatic' : 'any'}.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Reflection prompt surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  /**
   * value_realignment — surface a value-action gap for conscious renegotiation.
   * Does not tell the principal what to do. Surfaces the gap and invites
   * conscious choice about which to honour or renegotiate.
   */
  private async _valueRealignment(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, principalId } = ctx;

    try {
      await ctx.surface.surfaceValueRealignment(principalId, {
        fragment_id:        fragment.id,
        gap_description:    diagnosis.root_signal,
        conflicting_values: (fragment.metadata['conflicting_values'] as string[] | undefined) ?? [],
        recent_actions:     (fragment.metadata['recent_actions'] as string[] | undefined) ?? [],
        invitation:
          'A gap has appeared between what you’ve said matters and what you’ve been doing. ' +
          'Neither is wrong. Which one is asking to be honoured right now?',
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        'Value-action gap surfaced for conscious renegotiation.',
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Value realignment surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  /**
   * goal_conflict_map — visualise conflicting goals and invite prioritisation.
   * Used when high archetype variance indicates structural imbalance rather
   * than a single autonomous fragment.
   */
  private async _goalConflictMap(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, principalId } = ctx;
    const scores = fragment.metadata['scores'] as Record<string, number> | undefined ?? {};

    const conflictingGoals = Object.entries(scores)
      .sort((a, b) => a[1] - b[1])
      .map(([label, score]) => ({
        label,
        tension: score < 30
          ? `Integration very low (${score.toFixed(0)}) — may be operating autonomously`
          : `Integration moderate (${score.toFixed(0)}) — partial engagement`,
      }))
      .slice(0, 4); // surface the 4 most divergent

    try {
      await ctx.surface.surfaceGoalConflictMap(principalId, {
        fragment_id:       fragment.id,
        conflicting_goals: conflictingGoals,
        invitation:
          'These parts of you are pulling in different directions. ' +
          'Which one has been waiting the longest to be heard?',
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Goal conflict map surfaced. ${conflictingGoals.length} archetypes shown.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Goal conflict map surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  // =========================================================================
  // RELATIONAL STRATEGIES
  // =========================================================================

  /**
   * repair_initiation — surface a repair invitation for a relational rupture.
   * The system does not tell the principal how to repair — it names the
   * rupture clearly and invites the principal to initiate contact.
   */
  private async _repairInitiation(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, principalId } = ctx;
    const pairId       = fragment.relational_pair_id!;
    const partnerLabel = fragment.label.replace('Unrepaired rupture — ', '');
    const count        = fragment.metadata['unrepaired_count'] as number;
    const ageDays      = fragment.metadata['oldest_rupture_days'] as number;

    try {
      await ctx.surface.surfaceRepairInvitation(principalId, {
        fragment_id:         fragment.id,
        pair_id:             pairId,
        partner_label:       partnerLabel,
        rupture_count:       count,
        oldest_rupture_days: ageDays,
        invitation:
          `Something broke between you and ${partnerLabel} ` +
          `${ageDays.toFixed(0)} day${ageDays !== 1 ? 's' : ''} ago and hasn’t been tended. ` +
          `This is an invitation to reach out — not to fix it, just to acknowledge it.`,
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Repair invitation delivered for relationship with '${partnerLabel}'.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Repair invitation surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  /**
   * contact_invitation — surface a re-engagement invitation for a withdrawn relationship.
   * Lower urgency than repair_initiation — no rupture, just distance.
   */
  private async _contactInvitation(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, principalId } = ctx;
    const pairId        = fragment.relational_pair_id!;
    const partnerLabel  = fragment.label.replace('Contact withdrawal — ', '')
                                        .replace('Disclosure withdrawal — ', '');
    const gapDays       = fragment.metadata['contact_age_days'] as number | undefined ?? 0;

    try {
      await ctx.surface.surfaceContactInvitation(principalId, {
        fragment_id:      fragment.id,
        pair_id:          pairId,
        partner_label:    partnerLabel,
        contact_gap_days: gapDays,
        invitation:
          `It’s been a while since you’ve been in real contact with ${partnerLabel}. ` +
          `Not a task — just a nudge. What would a small gesture of connection look like?`,
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Contact invitation delivered for '${partnerLabel}'.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Contact invitation surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  /**
   * reciprocity_rebalance — surface the asymmetry and invite a conversation.
   * The system names the pattern without judgment and invites the principal
   * to bring it into awareness with the other person.
   */
  private async _reciprocityRebalance(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, principalId } = ctx;
    const pairId       = fragment.relational_pair_id!;
    const partnerLabel = fragment.label.replace('Reciprocity loss — ', '');
    const ratio        = fragment.metadata['initiation_ratio'] as number;
    const direction    = fragment.metadata['direction'] as string;

    try {
      await ctx.surface.surfaceReciprocityRebalance(principalId, {
        fragment_id:      fragment.id,
        pair_id:          pairId,
        partner_label:    partnerLabel,
        initiation_ratio: ratio,
        direction,
        invitation:
          `Your connection with ${partnerLabel} has become mostly ${direction}. ` +
          `That’s not a problem to solve — it’s a pattern to notice. ` +
          `Would it feel right to name this together?`,
      });
      return buildResult(fragment, diagnosis.recommended_strategy, true,
        `Reciprocity rebalance prompt delivered for '${partnerLabel}'.`,
        'INTEGRATE',
      );
    } catch (err) {
      return buildResult(fragment, diagnosis.recommended_strategy, false,
        `Reciprocity rebalance surface failed: ${String(err)}.`,
        'WITNESS',
      );
    }
  }

  // =========================================================================
  // ESCALATION STRATEGIES
  // =========================================================================

  /**
   * slow_witness — canary path; bridge deferred until principal engagement.
   * This strategy does not attempt integration. It keeps the fragment in
   * WITNESS indefinitely and surfaces a NOTICE-level CALLING to ensure
   * the principal is aware the fragment exists.
   * Always succeeds — deferral is not failure.
   */
  private async _slowWitness(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, principalId } = ctx;

    await ctx.surface.issueCallingSurface(principalId, {
      fragment_id:   fragment.id,
      level:         'NOTICE',
      reason:
        `Fragment '${fragment.label}' is being held in slow witness. ` +
        `Automated bridging has been deferred. Your attention is invited when ready.`,
      witness_notes: ctx.witness?.notable_observations ?? [],
    });

    return buildResult(fragment, 'slow_witness', true,
      `Fragment deferred to slow_witness. NOTICE CALLING issued. ` +
      `No automated bridge will be attempted until principal engages.`,
      'WITNESS', // returns to WITNESS — not INTEGRATE
    );
  }

  /**
   * calling_escalation — automation hard limit.
   * Issues a CALLING at the appropriate level and halts all automated
   * reconciliation for this fragment. The BRIDGE phase is marked complete
   * (success=true, next_phase=WITNESS) to signal that the engine has done
   * what it can — the next action belongs to the principal.
   *
   * CALLING level is determined by fragment charge:
   *   low → PROMPT | medium → PROMPT | high → SUMMONS | critical → CRITICAL
   */
  private async _callingEscalation(ctx: StrategyContext): Promise<BridgeResult> {
    const { fragment, diagnosis, witness, principalId } = ctx;

    const level = fragment.charge === 'critical' ? 'CRITICAL'
      : fragment.charge === 'high'     ? 'SUMMONS'
      : 'PROMPT';

    const reason =
      `Fragment '${fragment.label}' requires your direct attention. ` +
      `Automated reconciliation has reached its limit. \n\n` +
      `Diagnosis: ${diagnosis.root_signal}\n` +
      `Contributing signals: ${diagnosis.contributing_signals.join('; ')}`;

    await ctx.surface.issueCallingSurface(principalId, {
      fragment_id:   fragment.id,
      level,
      reason,
      witness_notes: witness?.notable_observations ?? [],
    });

    return buildResult(fragment, 'calling_escalation', true,
      `CALLING issued at level ${level}. Automated reconciliation halted. ` +
      `Fragment held until principal acknowledges.`,
      'WITNESS',
    );
  }

  /**
   * Fallback for unrecognised strategy names — should never fire in
   * production since BridgeStrategyName is an exhaustive union, but
   * guards against runtime gaps during development.
   */
  private async _unknownStrategy(
    ctx:      StrategyContext,
    strategy: BridgeStrategyName,
  ): Promise<BridgeResult> {
    return buildResult(ctx.fragment, strategy, false,
      `Unknown bridge strategy '${strategy}'. Routing to slow_witness.`,
      'WITNESS',
    );
  }
}

// ---------------------------------------------------------------------------
// 4. Result builder
// ---------------------------------------------------------------------------

function buildResult(
  fragment:   Fragment,
  strategy:   BridgeStrategyName,
  success:    boolean,
  notes:      string,
  nextPhase:  ReconciliationPhase,
): BridgeResult {
  return {
    fragment_id:   fragment.id,
    strategy,
    success,
    notes,
    next_phase:    nextPhase,
    completed_at:  nowISO(),
  };
}

// ---------------------------------------------------------------------------
// 5. Prompt composers
// ---------------------------------------------------------------------------

function composeDialogueFrame(
  archetypeLabel: string,
  patterns:       string[],
  witness:        WitnessSummary | null,
): string {
  const patternText = patterns.length
    ? `It has been showing up as: ${patterns.join(', ')}.`
    : 'Its patterns have not yet been named.';

  const witnessText = witness && witness.observation_count > 0
    ? `During a period of witness, the following was noticed: ${witness.notable_observations.join(' ')}`
    : '';

  return [
    `There is a part of you known as ${archetypeLabel}.`,
    patternText,
    witnessText,
    `This is an invitation to meet it — not to fix it, not to silence it, but to make contact.`,
    `What does ${archetypeLabel} want you to know right now?`,
  ].filter(Boolean).join(' ');
}

function composeReflectionGapPrompt(
  gapDays: number,
  witness: WitnessSummary | null,
): string {
  const urgency = gapDays > 14 ? 'a long time' : gapDays > 7 ? 'some time' : 'a little while';
  const witnessNote = witness?.notable_observations[0]
    ? ` Something observed in that time: “${witness.notable_observations[0]}”`
    : '';
  return (
    `It’s been ${urgency} since you last reflected.${witnessNote} ` +
    `Not a task — just a moment of turning inward. What’s been present that hasn’t been named yet?`
  );
}

function composeArchetypeReflectionPrompt(
  fragmentLabel: string,
  score:         number,
  witness:       WitnessSummary | null,
): string {
  const label = fragmentLabel.replace('Autonomous archetype — ', '').replace('Dormant archetype — ', '');
  const witnessNote = witness?.notable_observations[0]
    ? ` Recently noticed: “${witness.notable_observations[0]}”`
    : '';
  return (
    `${label} (integration: ${score.toFixed(0)}%) has been quiet lately.${witnessNote} ` +
    `What has this part of you been experiencing that you haven’t had a chance to hear?`
  );
}

function buildWitnessContextString(witness: WitnessSummary): string {
  const trajectory = witness.charge_trajectory.join(' → ');
  const cats       = witness.dominant_categories.join(', ');
  return [
    `Charge trajectory: ${trajectory}.`,
    cats ? `Dominant observation types: ${cats}.` : '',
    ...witness.notable_observations.map(o => `Observed: “${o}”`),
  ].filter(Boolean).join(' ');
}

// ---------------------------------------------------------------------------
// 6. Internal helpers
// ---------------------------------------------------------------------------

function nowISO(): ISOTimestamp {
  return new Date().toISOString();
}

// ---------------------------------------------------------------------------
// 7. Exports
// ---------------------------------------------------------------------------

export default BridgeStrategies;
