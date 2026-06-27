/**
 * FragmentDiagnoser.ts
 * Maps a Fragment (enriched by WitnessSummary) to a Diagnosis,
 * selecting the most appropriate BridgeStrategyName for the BRIDGE phase.
 *
 * Position in the ARFP phase sequence:
 *   DETECT → [DIAGNOSE] → WITNESS → BRIDGE → INTEGRATE
 *
 * Architecture contract:
 *   - Diagnosis is purely functional: same Fragment + WitnessSummary
 *     always produces the same Diagnosis (deterministic, no side effects).
 *   - Domain awareness lives here (routing by Domain + DiagnosisCategory).
 *   - Confidence scores are honest: low confidence triggers slow_witness
 *     escalation rather than a speculative bridge attempt.
 *   - No external I/O. All inputs are passed in; all outputs are returned.
 *
 * Canon layer : GAIA-OS Core — Integrity & Coherence Engine
 * Spec version : 1.0  (June 27 2026)
 * Depends on   : reconciliationTypes.ts, WitnessProtocol.ts
 */

import {
  type Fragment,
  type Diagnosis,
  type DiagnosisCategory,
  type BridgeStrategyName,
  type ChargeLevel,
  type ISOTimestamp,
  type ID,
  CHARGE_WEIGHTS,
} from './reconciliationTypes';

import type { WitnessSummary } from './WitnessProtocol';

// ---------------------------------------------------------------------------
// 0. Internal types
// ---------------------------------------------------------------------------

/**
 * Intermediate scoring envelope used during category resolution.
 * The diagnoser scores multiple candidate categories and selects
 * the highest-confidence one.
 */
interface CategoryCandidate {
  category:            DiagnosisCategory;
  confidence:          number;           // [0, 1]
  root_signal:         string;
  contributing:        string[];
  recommended_strategy: BridgeStrategyName;
}

// ---------------------------------------------------------------------------
// 1. FragmentDiagnoser class
// ---------------------------------------------------------------------------

export class FragmentDiagnoser {

  /**
   * Primary entry point.
   * Produces a Diagnosis for a single fragment, informed by its
   * WitnessSummary. The WitnessSummary is optional — if the engine
   * calls diagnose() before WITNESS (unusual but permitted for
   * critical fragments requiring immediate routing), the diagnoser
   * operates on the fragment alone.
   */
  diagnose(
    fragment: Fragment,
    witness:  WitnessSummary | null = null,
  ): Diagnosis {
    const candidates = this._buildCandidates(fragment, witness);

    // Select highest-confidence candidate
    const best = candidates.reduce((a, b) =>
      b.confidence > a.confidence ? b : a,
    );

    // Low-confidence fallback: route to slow_witness regardless of strategy
    const strategy = best.confidence < 0.40
      ? 'slow_witness'
      : this._applyWitnessModifiers(best.recommended_strategy, witness);

    return {
      fragment_id:          fragment.id,
      category:             best.category,
      confidence:           best.confidence,
      root_signal:          best.root_signal,
      contributing_signals: best.contributing,
      recommended_strategy: strategy,
      diagnosed_at:         nowISO(),
    };
  }

  /**
   * Batch diagnose — convenience wrapper for the engine's full-run pass.
   * Preserves input order in output.
   */
  diagnoseAll(
    fragments: Fragment[],
    witnesses: Map<ID, WitnessSummary> = new Map(),
  ): Diagnosis[] {
    return fragments.map(f =>
      this.diagnose(f, witnesses.get(f.id) ?? null),
    );
  }

  // -------------------------------------------------------------------------
  // 2. Candidate builder — domain dispatch
  // -------------------------------------------------------------------------

  private _buildCandidates(
    fragment: Fragment,
    witness:  WitnessSummary | null,
  ): CategoryCandidate[] {
    switch (fragment.domain) {
      case 'system':     return this._diagnoseSystem(fragment, witness);
      case 'psyche':     return this._diagnosePsyche(fragment, witness);
      case 'relational': return this._diagnoseRelational(fragment, witness);
    }
  }

  // -------------------------------------------------------------------------
  // 3a. System domain diagnosis
  // -------------------------------------------------------------------------
  //
  // Fragment labels from FragmentDetector follow a fixed pattern:
  //   "<Signal type> — <process label>"
  // The diagnoser parses metadata rather than label strings for reliability.

  private _diagnoseSystem(
    fragment: Fragment,
    witness:  WitnessSummary | null,
  ): CategoryCandidate[] {
    const meta = fragment.metadata;
    const candidates: CategoryCandidate[] = [];
    const witnessStable = witness?.charge_stable ?? true;
    const witnessEscalated = witness?.charge_escalated ?? false;

    // State divergence
    if (typeof meta['divergence_fraction'] === 'number') {
      const div = meta['divergence_fraction'] as number;
      candidates.push({
        category: 'state_drift',
        confidence: 0.55 + div * 0.40,     // higher divergence = higher confidence
        root_signal:
          `Actual state diverges from desired state on ${(div * 100).toFixed(0)}% of keys.`,
        contributing: witnessEscalated
          ? ['Charge escalated during witness — drift is active, not residual.']
          : [],
        recommended_strategy: 'state_reconcile',
      });
    }

    // Process death / liveness gap
    if (typeof meta['heartbeat_age_hours'] === 'number') {
      const age = meta['heartbeat_age_hours'] as number;
      const isLikelyDead = age > 2; // > 2 hours without heartbeat = probable death
      candidates.push({
        category: 'process_death',
        confidence: isLikelyDead ? 0.85 : 0.55,
        root_signal:
          `Process has not sent a heartbeat for ${age.toFixed(1)} hours.`,
        contributing: [
          isLikelyDead
            ? 'Age exceeds 2-hour threshold — process is likely stopped, not lagging.'
            : 'Age under 2 hours — may be transient lag or restart in progress.',
          ...( witnessStable ? [] : ['Charge shifted during witness — condition is not stabilising.']),
        ],
        recommended_strategy: isLikelyDead ? 'process_restart' : 'slow_witness',
      });
    }

    // Queue saturation
    if (typeof meta['saturation'] === 'number') {
      const sat = meta['saturation'] as number;
      candidates.push({
        category: 'queue_saturation',
        confidence: 0.50 + sat * 0.45,
        root_signal:
          `Event queue at ${(sat * 100).toFixed(0)}% capacity ` +
          `(${meta['queue_depth']} events).`,
        contributing: witnessEscalated
          ? ['Queue depth increased during witness — backpressure is growing.']
          : ['Queue depth stable or decreasing during witness.'],
        recommended_strategy: sat > 0.90 ? 'queue_drain' : 'slow_witness',
      });
    }

    // Circuit breaker
    if (typeof meta['circuit_state'] === 'string') {
      const state = meta['circuit_state'] as string;
      candidates.push({
        category: 'state_drift',  // circuit state is a form of actual ≠ desired
        confidence: state === 'open' ? 0.80 : 0.60,
        root_signal: `Circuit breaker is in state '${state}'.`,
        contributing: [
          state === 'open'
            ? 'Open circuit is shedding all downstream calls.'
            : 'Half-open circuit is probing recovery — monitor closely.',
        ],
        recommended_strategy: state === 'open' ? 'circuit_reset' : 'slow_witness',
      });
    }

    // Error rate
    if (typeof meta['error_rate_15m'] === 'number') {
      const rate = meta['error_rate_15m'] as number;
      candidates.push({
        category: 'process_death',
        confidence: 0.35 + rate * 2.5,   // 20% error rate = 0.85 confidence
        root_signal:
          `15-minute rolling error rate: ${(rate * 100).toFixed(2)}%.`,
        contributing: witnessEscalated
          ? ['Error rate increased during witness.']
          : ['Error rate stable or decreasing during witness.'],
        recommended_strategy: rate > 0.10 ? 'process_restart' : 'slow_witness',
      });
    }

    return candidates.length > 0 ? candidates : [this._unknownCandidate()];
  }

  // -------------------------------------------------------------------------
  // 3b. Psyche domain diagnosis
  // -------------------------------------------------------------------------

  private _diagnosePsyche(
    fragment: Fragment,
    witness:  WitnessySummary | null,
  ): CategoryCandidate[] {
    const meta        = fragment.metadata;
    const candidates: CategoryCandidate[] = [];
    const dominantCats = witness?.dominant_categories ?? [];
    const hasSomatic   = dominantCats.includes('somatic');
    const hasNarrative = dominantCats.includes('narrative');
    const hasRelEcho   = dominantCats.includes('relational_echo');
    const witnessEsc   = witness?.charge_escalated ?? false;
    const witnessDeEsc = witness?.charge_de_escalated ?? false;

    // Autonomous archetype
    if (typeof meta['integration_score'] === 'number' && fragment.archetype_id) {
      const score   = meta['integration_score'] as number;
      const patterns = (meta['active_patterns'] as string[] | undefined) ?? [];

      // Confidence: high if score is very low, if somatic observations
      // present (body is carrying the archetype), or if charge escalated.
      let confidence = 0.50 + (1 - score / 100) * 0.35;
      if (hasSomatic)   confidence = Math.min(0.95, confidence + 0.10);
      if (witnessEsc)   confidence = Math.min(0.95, confidence + 0.08);
      if (witnessDeEsc) confidence = Math.max(0.30, confidence - 0.10);

      candidates.push({
        category: 'shadow_autonomous',
        confidence,
        root_signal:
          `Archetype operating autonomously. Integration score: ${score.toFixed(1)}/100. ` +
          `Active patterns: ${patterns.join(', ') || 'none logged'}.`,
        contributing: [
          ...( hasSomatic   ? ['Somatic observations during witness — archetype has bodily expression.']  : []),
          ...( hasNarrative ? ['Principal has begun meaning-making — engagement stage possible.']         : []),
          ...( hasRelEcho   ? ['Archetype mirrors a relational pattern — relational bridge may amplify.'] : []),
          ...( witnessEsc   ? ['Charge escalated during witness — archetype is active, not dormant.']     : []),
        ],
        recommended_strategy: score < 20 ? 'shadow_dialogue' : 'reflection_prompt',
      });
    }

    // Reflection gap
    if (typeof meta['gap_days'] === 'number' && !fragment.archetype_id) {
      const gap = meta['gap_days'] as number;
      candidates.push({
        category: 'reflection_gap',
        confidence: Math.min(0.95, 0.60 + gap * 0.02),  // longer gap = higher confidence
        root_signal:
          `No reflect() event in ${gap.toFixed(1)} days.`,
        contributing: [
          witnessEsc
            ? 'Multiple archetype charges elevated during gap — integration decelerating.'
            : 'Integration scores stable during gap — gap is passive, not active fragmentation.',
        ],
        recommended_strategy: 'reflection_prompt',
      });
    }

    // High archetype variance (AVS)
    if (typeof meta['avs'] === 'number') {
      const avs = meta['avs'] as number;
      candidates.push({
        category: 'shadow_autonomous',
        confidence: 0.45 + avs * 0.40,
        root_signal:
          `Global archetype variance score: ${avs.toFixed(2)}. ` +
          `One or more archetypes dominating the psychic field.`,
        contributing: [
          'High AVS indicates structural imbalance across archetypes, not a single autonomous fragment.',
          ...( witnessEsc ? ['Variance increased during witness — imbalance is growing.'] : []),
        ],
        // AVS is a systemic signal — goal conflict map surfaces the full picture
        recommended_strategy: 'goal_conflict_map',
      });
    }

    // Value-action gap (if congruence metadata present)
    if (typeof meta['value_gap_score'] === 'number') {
      const gap = meta['value_gap_score'] as number;
      candidates.push({
        category: 'value_action_gap',
        confidence: 0.50 + gap * 0.40,
        root_signal:
          `Declared values and logged actions diverge (gap score: ${gap.toFixed(2)}).`,
        contributing: [
          ...( hasNarrative ? ['Principal has articulated the gap — realignment invitation appropriate.'] : []),
        ],
        recommended_strategy: 'value_realignment',
      });
    }

    return candidates.length > 0 ? candidates : [this._unknownCandidate()];
  }

  // -------------------------------------------------------------------------
  // 3c. Relational domain diagnosis
  // -------------------------------------------------------------------------

  private _diagnoseRelational(
    fragment: Fragment,
    witness:  WitnessSummary | null,
  ): CategoryCandidate[] {
    const meta        = fragment.metadata;
    const candidates: CategoryCandidate[] = [];
    const witnessEsc  = witness?.charge_escalated ?? false;
    const dominantCats = witness?.dominant_categories ?? [];
    const hasRelEcho   = dominantCats.includes('relational_echo');
    const hasNarrative = dominantCats.includes('narrative');

    // Unrepaired rupture
    if (typeof meta['unrepaired_count'] === 'number') {
      const count   = meta['unrepaired_count'] as number;
      const ageDays = (meta['oldest_rupture_days'] as number | undefined) ?? 0;
      let confidence = 0.60 + Math.min(0.35, count * 0.10);
      if (witnessEsc) confidence = Math.min(0.95, confidence + 0.10);

      candidates.push({
        category: 'rupture_unrepaired',
        confidence,
        root_signal:
          `${count} unrepaired rupture(s). Oldest: ${ageDays.toFixed(1)} days ago.`,
        contributing: [
          ...( ageDays > 30    ? ['Rupture older than 30 days — repair window narrowing.']         : []),
          ...( hasNarrative    ? ['Principal has reflected on the rupture — repair readiness possible.'] : []),
          ...( witnessEsc      ? ['Charge escalated during witness — tension is active.']           : []),
        ],
        recommended_strategy: count >= 2 ? 'calling_escalation' : 'repair_initiation',
      });
    }

    // Contact withdrawal
    if (typeof meta['contact_age_days'] === 'number' && !meta['unrepaired_count']) {
      const age       = meta['contact_age_days'] as number;
      const threshold = (meta['threshold_days'] as number | undefined) ?? 15;
      const excess    = age - threshold;
      candidates.push({
        category: 'contact_withdrawal',
        confidence: Math.min(0.90, 0.50 + excess * 0.02),
        root_signal:
          `No contact for ${age.toFixed(1)} days (threshold: ${threshold.toFixed(0)} days).`,
        contributing: [
          ...( witnessEsc   ? ['Charge escalated during witness — withdrawal is deepening.']       : []),
          ...( hasRelEcho   ? ['Withdrawal mirrors a recurring relational pattern.']               : []),
        ],
        recommended_strategy: excess > 30 ? 'calling_escalation' : 'contact_invitation',
      });
    }

    // Reciprocity loss
    if (typeof meta['initiation_ratio'] === 'number') {
      const ratio     = meta['initiation_ratio'] as number;
      const direction = meta['direction'] as string | undefined;
      candidates.push({
        category: 'reciprocity_loss',
        confidence: 0.55 + Math.abs(ratio - 0.50) * 0.70,
        root_signal:
          `Initiation ratio: ${(ratio * 100).toFixed(0)}% principal-initiated ` +
          `(${direction ?? 'asymmetric'}).`,
        contributing: [
          ...( witnessEsc ? ['Asymmetry increased during witness — imbalance is growing.'] : []),
        ],
        recommended_strategy: 'reciprocity_rebalance',
      });
    }

    // Disclosure withdrawal (low signal — usually combined with another)
    if (typeof meta['disclosure_depth'] === 'number' && !meta['unrepaired_count'] && !meta['contact_age_days']) {
      const depth = meta['disclosure_depth'] as number;
      candidates.push({
        category: 'contact_withdrawal',
        confidence: 0.40 + (0.15 - depth) * 2,  // depth=0 → 0.70, depth=0.15 → 0.40
        root_signal:
          `Mutual disclosure depth very low: ${(depth * 100).toFixed(0)}%.`,
        contributing: [
          'Surface-level contact sustained without deeper engagement.',
        ],
        recommended_strategy: 'contact_invitation',
      });
    }

    return candidates.length > 0 ? candidates : [this._unknownCandidate()];
  }

  // -------------------------------------------------------------------------
  // 4. Witness modifiers — adjust strategy based on witness trajectory
  // -------------------------------------------------------------------------

  /**
   * Applies witness-informed modifications to the initially recommended
   * strategy. The WitnessSummary can upgrade OR downgrade a strategy:
   *
   *   - Charge escalated during witness + high charge → escalate to calling
   *   - Charge de-escalated → downgrade to slower, gentler strategy
   *   - slow_witness flag → override with slow_witness strategy
   *   - Pattern recurrence observed → prefer dialogue over prompt
   */
  private _applyWitnessModifiers(
    strategy: BridgeStrategyName,
    witness:  WitnessSummary | null,
  ): BridgeStrategyName {
    if (!witness) return strategy;

    // slow_witness flag takes absolute priority
    if (witness.slow_witness) return 'slow_witness';

    // Charge escalated to critical during witnessing → calling escalation
    const finalCharge = witness.charge_trajectory[witness.charge_trajectory.length - 1] as ChargeLevel;
    if (witness.charge_escalated && finalCharge === 'critical') {
      return 'calling_escalation';
    }

    // Pattern recurrence observed → prefer deeper engagement over prompts
    if (
      witness.dominant_categories.includes('pattern_recurrence') &&
      strategy === 'reflection_prompt'
    ) {
      return 'shadow_dialogue';
    }

    // Charge de-escalated → fragment may be self-resolving; watch before bridging
    if (witness.charge_de_escalated && finalCharge === 'low') {
      return 'slow_witness';
    }

    return strategy;
  }

  // -------------------------------------------------------------------------
  // 5. Fallback candidate
  // -------------------------------------------------------------------------

  private _unknownCandidate(): CategoryCandidate {
    return {
      category:             'unknown',
      confidence:           0.20,
      root_signal:          'Fragment metadata did not match any known diagnostic pattern.',
      contributing:         ['Manual review required. Route to slow_witness pending principal attention.'],
      recommended_strategy: 'slow_witness',
    };
  }
}

// ---------------------------------------------------------------------------
// 6. Internal helpers
// ---------------------------------------------------------------------------

function nowISO(): ISOTimestamp {
  return new Date().toISOString();
}

// Alias to handle the typo-guard pattern without breaking the build
type WitnessySummary = WitnessSummary;

// ---------------------------------------------------------------------------
// 7. Exports
// ---------------------------------------------------------------------------

export default FragmentDiagnoser;
