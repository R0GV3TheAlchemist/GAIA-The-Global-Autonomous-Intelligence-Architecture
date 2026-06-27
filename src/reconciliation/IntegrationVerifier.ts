/**
 * IntegrationVerifier.ts
 * Confirms whether a bridge outcome has produced genuine integration,
 * or whether the fragment requires re-entry into the reconciliation cycle.
 *
 * Position in the ARFP phase sequence:
 *   DETECT → DIAGNOSE → WITNESS → BRIDGE → [INTEGRATE]
 *
 * Architecture contract:
 *   - Verification is purely observational: it reads current state and
 *     compares against the pre-bridge baseline. It never modifies fragments.
 *   - Each domain (system, psyche, relational) has its own verification
 *     logic, because "integration" means something different in each domain.
 *   - A verification that cannot be completed (missing data, adapter error)
 *     routes to RE_ENTRY rather than silently succeeding.
 *   - Re-entry increments the fragment's recurrence_count in the engine;
 *     IntegrationVerifier only returns the verdict.
 *
 * Canon layer : GAIA-OS Core — Integrity & Coherence Engine
 * Spec version : 1.0  (June 27 2026)
 * Depends on   : reconciliationTypes.ts, BridgeStrategies.ts
 */

import {
  type Fragment,
  type Diagnosis,
  type BridgeResult,
  type IntegrationRecord,
  type VerificationVerdict,
  type ChargeLevel,
  type ID,
  type ISOTimestamp,
  CHARGE_WEIGHTS,
} from './reconciliationTypes';

import type { BridgeStrategyName } from './reconciliationTypes';

// ---------------------------------------------------------------------------
// 0. Adapter interface
// ---------------------------------------------------------------------------

/**
 * Adapter for reading current state during verification.
 * The verifier reads; it never writes.
 */
export interface VerificationAdapter {
  // System
  /** Returns the current actual state of a process keyed by processId. */
  readActualState(processId: ID): Promise<Record<string, unknown>>;
  /** Returns the current process liveness signal (true = alive). */
  readProcessAlive(processId: ID): Promise<boolean>;
  /** Returns current queue depth as a fraction [0, 1]. */
  readQueueSaturation(processId: ID): Promise<number>;
  /** Returns the current circuit breaker state. */
  readCircuitState(processId: ID): Promise<'open' | 'half_open' | 'closed'>;

  // Psyche
  /** Returns the current integration score [0, 100] for an archetype. */
  readArchetypeScore(archetypeId: ID): Promise<number>;
  /** Returns the timestamp of the most recent reflect() event. */
  readLastReflectionTimestamp(principalId: ID): Promise<ISOTimestamp | null>;
  /** Returns the current value-action gap score [0, 1]. */
  readValueGapScore(principalId: ID): Promise<number>;
  /** Returns current archetype variance score (AVS) [0, 1]. */
  readAVS(principalId: ID): Promise<number>;

  // Relational
  /** Returns the number of unrepaired ruptures for a relational pair. */
  readUnrepairedRuptures(pairId: ID): Promise<number>;
  /** Returns days since last contact for a relational pair. */
  readContactAge(pairId: ID): Promise<number>;
  /** Returns the current initiation ratio [0, 1] for a pair. */
  readInitiationRatio(pairId: ID): Promise<number>;

  // Principal engagement
  /** Returns true if the principal has engaged with the surface action
   *  (opened a dialogue, submitted a reflection, etc.) since the given timestamp. */
  readPrincipalEngagement(
    principalId: ID,
    fragmentId: ID,
    since: ISOTimestamp,
  ): Promise<boolean>;
}

// ---------------------------------------------------------------------------
// 1. Verification result types
// ---------------------------------------------------------------------------

export type VerificationStatus =
  | 'INTEGRATED'   // fragment charge resolved; cycle complete
  | 'RE_ENTRY'     // improvement insufficient; re-enter cycle
  | 'PENDING'      // too soon to verify (called before min window elapsed)
  | 'DEFERRED';    // principal engagement required before verdict possible

export interface VerificationResult {
  fragment_id:     ID;
  status:          VerificationStatus;
  verdict:         VerificationVerdict;  // from reconciliationTypes
  confidence:      number;               // [0, 1]
  notes:           string;
  metric_before:   number | null;        // pre-bridge baseline
  metric_after:    number | null;        // post-bridge reading
  delta:           number | null;        // after − before
  verified_at:     ISOTimestamp;
  re_entry_reason: string | null;        // set if status === 'RE_ENTRY'
}

// ---------------------------------------------------------------------------
// 2. Verification windows by strategy (hours)
// ---------------------------------------------------------------------------
// How long must elapse after bridge completion before verification is valid?
// Verifying too soon produces false negatives (system hasn't had time to converge).

const VERIFICATION_WINDOWS_HOURS: Record<BridgeStrategyName, number> = {
  state_reconcile:       0.25,  //  15 min  — controller convergence is fast
  process_restart:       0.10,  //   6 min  — health gate is synchronous
  queue_drain:           0.10,  //   6 min  — immediate result
  circuit_reset:         0.25,  //  15 min  — probe result is near-immediate
  shadow_dialogue:      48.00,  //  48 hr   — integration is slow
  reflection_prompt:    24.00,  //  24 hr   — reflection takes time
  value_realignment:    48.00,  //  48 hr   — conscious renegotiation is slow
  goal_conflict_map:    72.00,  //  72 hr   — structural realignment is slowest
  repair_initiation:    72.00,  //  72 hr   — relational repair takes days
  contact_invitation:   48.00,  //  48 hr   — re-engagement takes time
  reciprocity_rebalance: 72.00, //  72 hr   — pattern shifts are gradual
  slow_witness:          0.00,  //   0 hr   — no verification; always DEFERRED
  calling_escalation:    0.00,  //   0 hr   — no verification; always DEFERRED
};

// ---------------------------------------------------------------------------
// 3. Integration thresholds
// ---------------------------------------------------------------------------
// Minimum improvement required for a INTEGRATED verdict.
// Expressed as a fraction of the pre-bridge baseline delta.

const INTEGRATION_THRESHOLDS = {
  // System: state divergence fraction must drop by at least 60%
  state_divergence_improvement: 0.60,
  // System: queue saturation must drop below 70%
  queue_saturation_target: 0.70,
  // Psyche: archetype score must improve by at least 5 points
  archetype_score_min_improvement: 5,
  // Psyche: reflection gap must be broken (any reflect() event counts)
  reflection_gap_broken: true,
  // Psyche: value gap score must drop by at least 20%
  value_gap_improvement: 0.20,
  // Psyche: AVS must drop by at least 15%
  avs_improvement: 0.15,
  // Relational: rupture count must decrease by at least 1
  rupture_min_decrease: 1,
  // Relational: contact age must drop below threshold (re-read from metadata)
  contact_age_met: true,
  // Relational: initiation ratio must move toward 0.50 by at least 0.10
  reciprocity_min_improvement: 0.10,
  // Principal engagement: any engagement counts for psyche/relational
  engagement_required_strategies: [
    'shadow_dialogue',
    'reflection_prompt',
    'value_realignment',
    'goal_conflict_map',
    'repair_initiation',
    'contact_invitation',
    'reciprocity_rebalance',
  ] as BridgeStrategyName[],
};

// ---------------------------------------------------------------------------
// 4. IntegrationVerifier class
// ---------------------------------------------------------------------------

export class IntegrationVerifier {
  private readonly adapter: VerificationAdapter;

  constructor(adapter: VerificationAdapter) {
    this.adapter = adapter;
  }

  /**
   * Primary entry point.
   * Verifies whether the bridge outcome for a fragment represents genuine
   * integration. Returns a VerificationResult with status and metrics.
   */
  async verify(
    principalId: ID,
    fragment:    Fragment,
    diagnosis:   Diagnosis,
    bridge:      BridgeResult,
  ): Promise<VerificationResult> {
    const strategy = bridge.strategy;

    // Escalation / deferred strategies never verify automatically
    if (strategy === 'slow_witness' || strategy === 'calling_escalation') {
      return this._deferred(fragment, strategy);
    }

    // Check verification window
    const windowHours = VERIFICATION_WINDOWS_HOURS[strategy] ?? 24;
    const elapsed     = hoursSince(bridge.completed_at);
    if (elapsed < windowHours) {
      return this._pending(fragment, strategy, windowHours, elapsed);
    }

    // Check principal engagement for psyche/relational strategies
    if (INTEGRATION_THRESHOLDS.engagement_required_strategies.includes(strategy)) {
      const engaged = await this.adapter.readPrincipalEngagement(
        principalId, fragment.id, bridge.completed_at,
      );
      if (!engaged) {
        return this._deferred(fragment, strategy,
          'Bridge was delivered but principal has not yet engaged. Holding at DEFERRED.');
      }
    }

    // Domain dispatch
    switch (fragment.domain) {
      case 'system':     return this._verifySystem(fragment, diagnosis, bridge);
      case 'psyche':     return this._verifyPsyche(principalId, fragment, diagnosis, bridge);
      case 'relational': return this._verifyRelational(principalId, fragment, diagnosis, bridge);
    }
  }

  /**
   * Batch verify — convenience wrapper for the engine's integration pass.
   */
  async verifyAll(
    principalId: ID,
    items: Array<{ fragment: Fragment; diagnosis: Diagnosis; bridge: BridgeResult }>,
  ): Promise<VerificationResult[]> {
    return Promise.all(
      items.map(({ fragment, diagnosis, bridge }) =>
        this.verify(principalId, fragment, diagnosis, bridge),
      ),
    );
  }

  // =========================================================================
  // SYSTEM VERIFICATION
  // =========================================================================

  private async _verifySystem(
    fragment:  Fragment,
    diagnosis: Diagnosis,
    bridge:    BridgeResult,
  ): Promise<VerificationResult> {
    const processId = fragment.metadata['process_id'] as ID;
    const strategy  = bridge.strategy;

    try {
      switch (strategy) {
        case 'state_reconcile': {
          const desired  = fragment.metadata['desired_state'] as Record<string, unknown> ?? {};
          const actual   = await this.adapter.readActualState(processId);
          const beforeDiv = fragment.metadata['divergence_fraction'] as number ?? 1;
          const afterDiv  = computeDivergenceFraction(desired, actual);
          const improved  = (beforeDiv - afterDiv) / (beforeDiv || 1);

          return this._buildResult(
            fragment, strategy,
            improved >= INTEGRATION_THRESHOLDS.state_divergence_improvement,
            beforeDiv, afterDiv,
            improved >= INTEGRATION_THRESHOLDS.state_divergence_improvement
              ? `State converged. Divergence reduced by ${(improved * 100).toFixed(0)}%.`
              : `Divergence reduced by only ${(improved * 100).toFixed(0)}% — threshold is ` +
                `${(INTEGRATION_THRESHOLDS.state_divergence_improvement * 100).toFixed(0)}%.`,
            improved >= INTEGRATION_THRESHOLDS.state_divergence_improvement ? null
              : 'Convergence insufficient. Re-enter with higher charge weight.',
          );
        }

        case 'process_restart': {
          const alive = await this.adapter.readProcessAlive(processId);
          return this._buildResult(
            fragment, strategy, alive,
            0, alive ? 1 : 0,
            alive
              ? `Process '${fragment.label}' is alive and responding.`
              : `Process '${fragment.label}' is still unresponsive after restart.`,
            alive ? null : 'Process did not recover. Escalate to calling_escalation.',
          );
        }

        case 'queue_drain': {
          const sat    = await this.adapter.readQueueSaturation(processId);
          const before = fragment.metadata['saturation'] as number ?? 1;
          const ok     = sat <= INTEGRATION_THRESHOLDS.queue_saturation_target;
          return this._buildResult(
            fragment, strategy, ok,
            before, sat,
            ok
              ? `Queue saturation at ${(sat * 100).toFixed(0)}% — within target.`
              : `Queue saturation at ${(sat * 100).toFixed(0)}% — target is ` +
                `${(INTEGRATION_THRESHOLDS.queue_saturation_target * 100).toFixed(0)}%.`,
            ok ? null : 'Queue still pressured. Consider process_restart or calling_escalation.',
          );
        }

        case 'circuit_reset': {
          const state = await this.adapter.readCircuitState(processId);
          const ok    = state === 'closed';
          return this._buildResult(
            fragment, strategy, ok,
            null, null,
            ok
              ? `Circuit closed. Downstream calls flowing normally.`
              : `Circuit still in state '${state}'. Not yet stable.`,
            ok ? null : 'Circuit did not close. Re-enter with state_reconcile or process_restart.',
          );
        }

        default:
          return this._unknownStrategy(fragment, strategy);
      }
    } catch (err) {
      return this._adapterError(fragment, strategy, String(err));
    }
  }

  // =========================================================================
  // PSYCHE VERIFICATION
  // =========================================================================

  private async _verifyPsyche(
    principalId: ID,
    fragment:    Fragment,
    diagnosis:   Diagnosis,
    bridge:      BridgeResult,
  ): Promise<VerificationResult> {
    const strategy = bridge.strategy;

    try {
      switch (strategy) {
        case 'shadow_dialogue':
        case 'reflection_prompt': {
          // Primary signal: did the archetype integration score improve?
          if (fragment.archetype_id) {
            const before = fragment.metadata['integration_score'] as number ?? 0;
            const after  = await this.adapter.readArchetypeScore(fragment.archetype_id);
            const delta  = after - before;
            const ok     = delta >= INTEGRATION_THRESHOLDS.archetype_score_min_improvement;
            return this._buildResult(
              fragment, strategy, ok,
              before, after,
              ok
                ? `Integration score improved by ${delta.toFixed(1)} points ` +
                  `(${before.toFixed(0)} → ${after.toFixed(0)}).`
                : `Integration score changed by ${delta.toFixed(1)} points — ` +
                  `minimum improvement is ${INTEGRATION_THRESHOLDS.archetype_score_min_improvement}.`,
              ok ? null
                : delta > 0
                  ? 'Some improvement — not yet threshold. Extend witness window.'
                  : 'No improvement. Fragment may need deeper engagement. Re-enter.',
            );
          }
          // Fallback: was there any reflection event?
          const ts = await this.adapter.readLastReflectionTimestamp(principalId);
          const reflected = ts !== null && ts > bridge.completed_at;
          return this._buildResult(
            fragment, strategy, reflected,
            null, null,
            reflected
              ? 'Principal reflected after bridge delivery.'
              : 'No reflection event recorded since bridge delivery.',
            reflected ? null : 'Reflection not yet observed. Hold at DEFERRED.',
          );
        }

        case 'value_realignment': {
          const before = fragment.metadata['value_gap_score'] as number ?? 1;
          const after  = await this.adapter.readValueGapScore(principalId);
          const improvement = (before - after) / (before || 1);
          const ok = improvement >= INTEGRATION_THRESHOLDS.value_gap_improvement;
          return this._buildResult(
            fragment, strategy, ok,
            before, after,
            ok
              ? `Value-action gap reduced by ${(improvement * 100).toFixed(0)}%.`
              : `Gap reduced by ${(improvement * 100).toFixed(0)}% — ` +
                `threshold is ${(INTEGRATION_THRESHOLDS.value_gap_improvement * 100).toFixed(0)}%.`,
            ok ? null : 'Gap narrowing but below threshold. Extend witness or re-enter.',
          );
        }

        case 'goal_conflict_map': {
          const before = fragment.metadata['avs'] as number ?? 1;
          const after  = await this.adapter.readAVS(principalId);
          const improvement = (before - after) / (before || 1);
          const ok = improvement >= INTEGRATION_THRESHOLDS.avs_improvement;
          return this._buildResult(
            fragment, strategy, ok,
            before, after,
            ok
              ? `Archetype variance score reduced by ${(improvement * 100).toFixed(0)}%.`
              : `AVS reduced by ${(improvement * 100).toFixed(0)}% — ` +
                `threshold is ${(INTEGRATION_THRESHOLDS.avs_improvement * 100).toFixed(0)}%.`,
            ok ? null : 'Variance still elevated. Structural realignment ongoing — extend window.',
          );
        }

        default:
          return this._unknownStrategy(fragment, strategy);
      }
    } catch (err) {
      return this._adapterError(fragment, strategy, String(err));
    }
  }

  // =========================================================================
  // RELATIONAL VERIFICATION
  // =========================================================================

  private async _verifyRelational(
    principalId: ID,
    fragment:    Fragment,
    diagnosis:   Diagnosis,
    bridge:      BridgeResult,
  ): Promise<VerificationResult> {
    const strategy = bridge.strategy;
    const pairId   = fragment.relational_pair_id!;

    try {
      switch (strategy) {
        case 'repair_initiation': {
          const before = fragment.metadata['unrepaired_count'] as number ?? 1;
          const after  = await this.adapter.readUnrepairedRuptures(pairId);
          const ok     = (before - after) >= INTEGRATION_THRESHOLDS.rupture_min_decrease;
          return this._buildResult(
            fragment, strategy, ok,
            before, after,
            ok
              ? `Unrepaired ruptures reduced from ${before} to ${after}.`
              : `Rupture count unchanged at ${after}. Repair not yet initiated.`,
            ok ? null : 'No repair observed. Re-enter with longer witness window or calling_escalation.',
          );
        }

        case 'contact_invitation': {
          const threshold = fragment.metadata['threshold_days'] as number ?? 15;
          const before    = fragment.metadata['contact_age_days'] as number ?? threshold;
          const after     = await this.adapter.readContactAge(pairId);
          const ok        = after < threshold;
          return this._buildResult(
            fragment, strategy, ok,
            before, after,
            ok
              ? `Contact re-established. Gap reduced to ${after.toFixed(1)} days (threshold: ${threshold}).`
              : `Contact gap still ${after.toFixed(1)} days (threshold: ${threshold}).`,
            ok ? null : 'Contact not yet re-established. Hold or re-enter.',
          );
        }

        case 'reciprocity_rebalance': {
          const before = fragment.metadata['initiation_ratio'] as number ?? 0;
          const after  = await this.adapter.readInitiationRatio(pairId);
          // Movement toward 0.5 is positive regardless of direction
          const beforeDev = Math.abs(before - 0.5);
          const afterDev  = Math.abs(after  - 0.5);
          const improvement = beforeDev - afterDev;
          const ok = improvement >= INTEGRATION_THRESHOLDS.reciprocity_min_improvement;
          return this._buildResult(
            fragment, strategy, ok,
            before, after,
            ok
              ? `Initiation ratio moved toward balance (${before.toFixed(2)} → ${after.toFixed(2)}).`
              : `Ratio moved by ${improvement.toFixed(2)} — threshold is ` +
                `${INTEGRATION_THRESHOLDS.reciprocity_min_improvement}. Pattern still asymmetric.`,
            ok ? null : 'Balance not yet restored. Extend observation window.',
          );
        }

        default:
          return this._unknownStrategy(fragment, strategy);
      }
    } catch (err) {
      return this._adapterError(fragment, strategy, String(err));
    }
  }

  // =========================================================================
  // RESULT BUILDERS
  // =========================================================================

  private _buildResult(
    fragment:      Fragment,
    strategy:      BridgeStrategyName,
    integrated:    boolean,
    metricBefore:  number | null,
    metricAfter:   number | null,
    notes:         string,
    reEntryReason: string | null,
  ): VerificationResult {
    const delta = metricBefore !== null && metricAfter !== null
      ? metricAfter - metricBefore
      : null;

    return {
      fragment_id:   fragment.id,
      status:        integrated ? 'INTEGRATED' : 'RE_ENTRY',
      verdict:       integrated ? 'integrated' : 're_entry',
      confidence:    integrated ? 0.85 : 0.75,
      notes,
      metric_before: metricBefore,
      metric_after:  metricAfter,
      delta,
      verified_at:   nowISO(),
      re_entry_reason: reEntryReason,
    };
  }

  private _pending(
    fragment:     Fragment,
    strategy:     BridgeStrategyName,
    windowHours:  number,
    elapsedHours: number,
  ): VerificationResult {
    const remaining = (windowHours - elapsedHours).toFixed(1);
    return {
      fragment_id:     fragment.id,
      status:          'PENDING',
      verdict:         'pending',
      confidence:      0,
      notes:
        `Verification window for '${strategy}' is ${windowHours}h. ` +
        `Only ${elapsedHours.toFixed(1)}h elapsed. Check again in ~${remaining}h.`,
      metric_before:   null,
      metric_after:    null,
      delta:           null,
      verified_at:     nowISO(),
      re_entry_reason: null,
    };
  }

  private _deferred(
    fragment: Fragment,
    strategy: BridgeStrategyName,
    reason    = 'Strategy requires principal engagement before automated verification is possible.',
  ): VerificationResult {
    return {
      fragment_id:     fragment.id,
      status:          'DEFERRED',
      verdict:         'deferred',
      confidence:      0,
      notes:           reason,
      metric_before:   null,
      metric_after:    null,
      delta:           null,
      verified_at:     nowISO(),
      re_entry_reason: null,
    };
  }

  private _adapterError(
    fragment: Fragment,
    strategy: BridgeStrategyName,
    error:    string,
  ): VerificationResult {
    return {
      fragment_id:     fragment.id,
      status:          'RE_ENTRY',
      verdict:         're_entry',
      confidence:      0.30,
      notes:           `Adapter error during verification: ${error}`,
      metric_before:   null,
      metric_after:    null,
      delta:           null,
      verified_at:     nowISO(),
      re_entry_reason: `Verification adapter threw: ${error}. Cannot confirm integration.`,
    };
  }

  private _unknownStrategy(
    fragment: Fragment,
    strategy: BridgeStrategyName,
  ): VerificationResult {
    return {
      fragment_id:     fragment.id,
      status:          'RE_ENTRY',
      verdict:         're_entry',
      confidence:      0.20,
      notes:           `No verification logic for strategy '${strategy}'.`,
      metric_before:   null,
      metric_after:    null,
      delta:           null,
      verified_at:     nowISO(),
      re_entry_reason: `Unknown strategy '${strategy}' — cannot verify. Route to slow_witness.`,
    };
  }
}

// ---------------------------------------------------------------------------
// 5. Internal helpers
// ---------------------------------------------------------------------------

function nowISO(): ISOTimestamp {
  return new Date().toISOString();
}

function hoursSince(iso: ISOTimestamp): number {
  return (Date.now() - new Date(iso).getTime()) / 3_600_000;
}

/**
 * Computes the fraction of keys in `desired` whose values differ from `actual`.
 * Keys present in desired but absent in actual count as diverged.
 */
function computeDivergenceFraction(
  desired: Record<string, unknown>,
  actual:  Record<string, unknown>,
): number {
  const keys = Object.keys(desired);
  if (keys.length === 0) return 0;
  const diverged = keys.filter(k => JSON.stringify(desired[k]) !== JSON.stringify(actual[k]));
  return diverged.length / keys.length;
}

// ---------------------------------------------------------------------------
// 6. Exports
// ---------------------------------------------------------------------------

export default IntegrationVerifier;
