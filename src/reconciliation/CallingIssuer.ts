/**
 * CallingIssuer.ts
 * Manages the full lifecycle of CALLINGs: creation, escalation, acknowledgement,
 * dismissal, and expiry. A CALLING is a structured, persistent invitation
 * from the system to the principal — not a notification, not an alert.
 *
 * Architecture contract:
 *   - A CALLING is never created without a fragment_id and a reason.
 *   - Escalation is automatic when a CALLING ages past its threshold
 *     without acknowledgement. The ladder: NOTICE → PROMPT → SUMMONS → CRITICAL.
 *   - Only the principal can acknowledge or dismiss a CALLING.
 *     The system can escalate and expire, but never silently dismiss.
 *   - CRITICAL CALLINGs do not expire. They remain until acknowledged.
 *   - CallingIssuer never modifies Fragment state. Fragment charge is
 *     updated by the engine after a CALLING state change.
 *
 * Canon layer : GAIA-OS Core — Integrity & Coherence Engine
 * Spec version : 1.0  (June 27 2026)
 * Depends on   : reconciliationTypes.ts, ReconciliationMemory.ts
 */

import {
  type ID,
  type ISOTimestamp,
  type ChargeLevel,
} from './reconciliationTypes';

import type { RecurrenceRecord } from './ReconciliationMemory';

// ---------------------------------------------------------------------------
// 0. CALLING types
// ---------------------------------------------------------------------------

/** The four levels of a CALLING, ordered by urgency. */
export type CallingLevel = 'NOTICE' | 'PROMPT' | 'SUMMONS' | 'CRITICAL';

/** The lifecycle state of a CALLING. */
export type CallingState =
  | 'ACTIVE'        // issued, awaiting acknowledgement
  | 'ESCALATED'     // level has been raised since initial issue
  | 'ACKNOWLEDGED'  // principal has seen and accepted the CALLING
  | 'DISMISSED'     // principal has consciously set aside the CALLING
  | 'EXPIRED';      // aged out (NOTICE/PROMPT/SUMMONS only; CRITICAL never expires)

export interface Calling {
  id:                 ID;
  principal_id:       ID;
  fragment_id:        ID;
  fragment_label:     string;
  domain:             'system' | 'psyche' | 'relational';
  level:              CallingLevel;
  state:              CallingState;
  reason:             string;
  witness_notes:      string[];
  issued_at:          ISOTimestamp;
  escalated_at:       ISOTimestamp | null;   // most recent escalation timestamp
  acknowledged_at:    ISOTimestamp | null;
  dismissed_at:       ISOTimestamp | null;
  expires_at:         ISOTimestamp | null;   // null for CRITICAL
  escalation_history: EscalationEntry[];
  recurrence_count:   number;               // how many times this fragment has recurred
}

export interface EscalationEntry {
  from_level:    CallingLevel;
  to_level:      CallingLevel;
  escalated_at:  ISOTimestamp;
  reason:        string;
}

// ---------------------------------------------------------------------------
// 1. Storage adapter
// ---------------------------------------------------------------------------

export interface CallingStorageAdapter {
  saveCalling(calling: Calling): Promise<void>;
  loadCalling(callingId: ID): Promise<Calling | null>;
  loadActiveCallings(principalId: ID): Promise<Calling[]>;
  loadCallingForFragment(principalId: ID, fragmentId: ID): Promise<Calling | null>;
  loadAllCallings(principalId: ID): Promise<Calling[]>;
}

// ---------------------------------------------------------------------------
// 2. Delivery adapter
// ---------------------------------------------------------------------------

/**
 * Delivers a CALLING to the principal's interface.
 * Implementations vary by surface (desktop, mobile, voice, ambient).
 * The issuer does not care how delivery happens — only that it does.
 */
export interface CallingDeliveryAdapter {
  deliver(calling: Calling): Promise<void>;
  deliverEscalation(calling: Calling, entry: EscalationEntry): Promise<void>;
  deliverAcknowledgement(callingId: ID, principalId: ID): Promise<void>;
}

// ---------------------------------------------------------------------------
// 3. Escalation configuration
// ---------------------------------------------------------------------------

/**
 * How long (in hours) a CALLING may remain at each level before
 * the system escalates it to the next level.
 * CRITICAL has no threshold — it does not auto-escalate.
 */
export interface EscalationConfig {
  NOTICE_to_PROMPT_hours:   number;  // default: 24
  PROMPT_to_SUMMONS_hours:  number;  // default: 48
  SUMMONS_to_CRITICAL_hours: number; // default: 72
}

export const DEFAULT_ESCALATION_CONFIG: EscalationConfig = {
  NOTICE_to_PROMPT_hours:    24,
  PROMPT_to_SUMMONS_hours:   48,
  SUMMONS_to_CRITICAL_hours: 72,
};

/**
 * How long (in hours) a CALLING may exist at each level before expiring
 * without acknowledgement. CRITICAL never expires.
 * Expiry only applies if the principal has not acknowledged.
 */
export interface ExpiryConfig {
  NOTICE_expires_hours:   number;  // default: 72
  PROMPT_expires_hours:   number;  // default: 120
  SUMMONS_expires_hours:  number;  // default: 168  (7 days)
  // CRITICAL: no expiry
}

export const DEFAULT_EXPIRY_CONFIG: ExpiryConfig = {
  NOTICE_expires_hours:   72,
  PROMPT_expires_hours:   120,
  SUMMONS_expires_hours:  168,
};

// ---------------------------------------------------------------------------
// 4. CallingIssuer class
// ---------------------------------------------------------------------------

export class CallingIssuer {
  private readonly store:      CallingStorageAdapter;
  private readonly delivery:   CallingDeliveryAdapter;
  private readonly escalation: EscalationConfig;
  private readonly expiry:     ExpiryConfig;

  constructor(
    adapters: {
      store:    CallingStorageAdapter;
      delivery: CallingDeliveryAdapter;
    },
    config: {
      escalation?: Partial<EscalationConfig>;
      expiry?:     Partial<ExpiryConfig>;
    } = {},
  ) {
    this.store      = adapters.store;
    this.delivery   = adapters.delivery;
    this.escalation = { ...DEFAULT_ESCALATION_CONFIG, ...config.escalation };
    this.expiry     = { ...DEFAULT_EXPIRY_CONFIG, ...config.expiry };
  }

  // =========================================================================
  // ISSUANCE
  // =========================================================================

  /**
   * Issue a new CALLING for a fragment.
   * If an active CALLING already exists for this fragment, escalates it
   * rather than creating a duplicate.
   * Returns the created or escalated Calling.
   */
  async issue(
    principalId:    ID,
    fragmentId:     ID,
    fragmentLabel:  string,
    domain:         Calling['domain'],
    level:          CallingLevel,
    reason:         string,
    witnessNotes:   string[] = [],
    recurrenceCount: number = 0,
  ): Promise<Calling> {
    // Check for existing active CALLING for this fragment
    const existing = await this.store.loadCallingForFragment(principalId, fragmentId);
    if (existing && isActive(existing)) {
      return this._escalateExisting(existing, level, reason);
    }

    const now      = nowISO();
    const expiresAt = level !== 'CRITICAL'
      ? addHours(now, this._expiryHours(level))
      : null;

    const calling: Calling = {
      id:                 generateId(),
      principal_id:       principalId,
      fragment_id:        fragmentId,
      fragment_label:     fragmentLabel,
      domain,
      level,
      state:              'ACTIVE',
      reason,
      witness_notes:      witnessNotes,
      issued_at:          now,
      escalated_at:       null,
      acknowledged_at:    null,
      dismissed_at:       null,
      expires_at:         expiresAt,
      escalation_history: [],
      recurrence_count:   recurrenceCount,
    };

    await this.store.saveCalling(calling);
    await this.delivery.deliver(calling);
    return calling;
  }

  // =========================================================================
  // ESCALATION
  // =========================================================================

  /**
   * Tick function — called by the engine on each scheduled run.
   * Checks all active CALLINGs for a principal and escalates those
   * that have aged past their threshold without acknowledgement.
   * Also marks expired CALLINGs as EXPIRED.
   * Returns the list of CALLINGs that were escalated or expired.
   */
  async tick(principalId: ID): Promise<Calling[]> {
    const active   = await this.store.loadActiveCallings(principalId);
    const changed: Calling[] = [];

    for (const calling of active) {
      if (!isActive(calling)) continue;

      const now = Date.now();

      // Check expiry first (does not apply to CRITICAL)
      if (calling.expires_at && new Date(calling.expires_at).getTime() <= now) {
        calling.state = 'EXPIRED';
        await this.store.saveCalling(calling);
        changed.push(calling);
        continue;
      }

      // Check escalation threshold
      const nextLevel = this._nextLevel(calling.level);
      if (!nextLevel) continue; // CRITICAL — no escalation

      const thresholdHours = this._escalationThreshold(calling.level);
      const referenceTime  = calling.escalated_at ?? calling.issued_at;
      const elapsed        = (now - new Date(referenceTime).getTime()) / 3_600_000;

      if (elapsed >= thresholdHours) {
        const escalated = await this._escalateExisting(
          calling, nextLevel,
          `Auto-escalated after ${elapsed.toFixed(1)}h without acknowledgement ` +
          `(threshold: ${thresholdHours}h).`,
        );
        changed.push(escalated);
      }
    }

    return changed;
  }

  /**
   * Manually escalate a specific CALLING to the given level.
   * Used by the engine when a fragment's charge increases after issuance.
   */
  async escalate(
    callingId: ID,
    toLevel:   CallingLevel,
    reason:    string,
  ): Promise<Calling> {
    const calling = await this._requireCalling(callingId);
    return this._escalateExisting(calling, toLevel, reason);
  }

  // =========================================================================
  // PRINCIPAL ACTIONS
  // =========================================================================

  /**
   * Acknowledge a CALLING.
   * Acknowledgement means the principal has seen the CALLING and is
   * choosing to engage. It does not mean the fragment is resolved —
   * that is determined by IntegrationVerifier.
   */
  async acknowledge(callingId: ID, principalId: ID): Promise<Calling> {
    const calling = await this._requireCalling(callingId);

    if (!isActive(calling)) {
      throw new Error(
        `CallingIssuer: cannot acknowledge CALLING '${callingId}' ` +
        `— state is '${calling.state}'.`,
      );
    }

    calling.state           = 'ACKNOWLEDGED';
    calling.acknowledged_at = nowISO();

    await this.store.saveCalling(calling);
    await this.delivery.deliverAcknowledgement(callingId, principalId);
    return calling;
  }

  /**
   * Dismiss a CALLING.
   * Dismissal is a conscious principal decision to set the CALLING aside.
   * It is not the same as resolution. The fragment remains in the system;
   * the engine will re-detect it if the condition persists.
   * CRITICAL CALLINGs cannot be dismissed — only acknowledged.
   */
  async dismiss(callingId: ID): Promise<Calling> {
    const calling = await this._requireCalling(callingId);

    if (calling.level === 'CRITICAL') {
      throw new Error(
        `CallingIssuer: CRITICAL CALLINGs cannot be dismissed. ` +
        `Acknowledge or resolve the underlying fragment.`,
      );
    }

    if (!isActive(calling)) {
      throw new Error(
        `CallingIssuer: cannot dismiss CALLING '${callingId}' ` +
        `— state is '${calling.state}'.`,
      );
    }

    calling.state        = 'DISMISSED';
    calling.dismissed_at = nowISO();

    await this.store.saveCalling(calling);
    return calling;
  }

  // =========================================================================
  // QUERIES
  // =========================================================================

  /** Returns all active CALLINGs for a principal, ordered by urgency then age. */
  async activeCallings(principalId: ID): Promise<Calling[]> {
    const callings = await this.store.loadActiveCallings(principalId);
    return callings
      .filter(isActive)
      .sort(byUrgencyThenAge);
  }

  /** Returns the active CALLING for a specific fragment, if any. */
  async callingForFragment(principalId: ID, fragmentId: ID): Promise<Calling | null> {
    const calling = await this.store.loadCallingForFragment(principalId, fragmentId);
    return calling && isActive(calling) ? calling : null;
  }

  /** Returns the full CALLING history for a principal. */
  async history(principalId: ID): Promise<Calling[]> {
    const all = await this.store.loadAllCallings(principalId);
    return all.sort((a, b) =>
      new Date(b.issued_at).getTime() - new Date(a.issued_at).getTime(),
    );
  }

  /**
   * Returns a summary of the current CALLING state for a principal.
   * Consumed by IntegrityIndex.
   */
  async summary(principalId: ID): Promise<CallingSummary> {
    const all    = await this.store.loadAllCallings(principalId);
    const active = all.filter(isActive);

    const byLevel: Record<CallingLevel, number> = {
      NOTICE: 0, PROMPT: 0, SUMMONS: 0, CRITICAL: 0,
    };
    active.forEach(c => { byLevel[c.level]++; });

    const criticals       = active.filter(c => c.level === 'CRITICAL');
    const oldest          = active.sort(byUrgencyThenAge)[0] ?? null;
    const totalIssued     = all.length;
    const totalAcknowledged = all.filter(c => c.state === 'ACKNOWLEDGED').length;
    const acknowledgementRate = totalIssued > 0
      ? totalAcknowledged / totalIssued
      : 1; // no CALLINGs ever = perfect acknowledgement rate

    return {
      principal_id:          principalId,
      active_count:          active.length,
      by_level:              byLevel,
      critical_fragments:    criticals.map(c => ({
        calling_id:    c.id,
        fragment_id:   c.fragment_id,
        fragment_label: c.fragment_label,
        issued_at:     c.issued_at,
      })),
      oldest_active:         oldest ? {
        calling_id:    oldest.id,
        fragment_id:   oldest.fragment_id,
        fragment_label: oldest.fragment_label,
        level:         oldest.level,
        issued_at:     oldest.issued_at,
      } : null,
      total_issued:          totalIssued,
      acknowledgement_rate:  acknowledgementRate,
      computed_at:           nowISO(),
    };
  }

  // =========================================================================
  // INTERNAL
  // =========================================================================

  private async _escalateExisting(
    calling:  Calling,
    toLevel:  CallingLevel,
    reason:   string,
  ): Promise<Calling> {
    // Never downgrade
    if (LEVEL_ORDER[toLevel] <= LEVEL_ORDER[calling.level]) {
      return calling;
    }

    const entry: EscalationEntry = {
      from_level:   calling.level,
      to_level:     toLevel,
      escalated_at: nowISO(),
      reason,
    };

    calling.level              = toLevel;
    calling.state              = 'ESCALATED';
    calling.escalated_at       = entry.escalated_at;
    calling.escalation_history = [...calling.escalation_history, entry];

    // Recalculate expiry for new level (CRITICAL = no expiry)
    calling.expires_at = toLevel !== 'CRITICAL'
      ? addHours(entry.escalated_at, this._expiryHours(toLevel))
      : null;

    await this.store.saveCalling(calling);
    await this.delivery.deliverEscalation(calling, entry);
    return calling;
  }

  private _nextLevel(level: CallingLevel): CallingLevel | null {
    const levels: CallingLevel[] = ['NOTICE', 'PROMPT', 'SUMMONS', 'CRITICAL'];
    const idx = levels.indexOf(level);
    return idx < levels.length - 1 ? levels[idx + 1] : null;
  }

  private _escalationThreshold(level: CallingLevel): number {
    switch (level) {
      case 'NOTICE':  return this.escalation.NOTICE_to_PROMPT_hours;
      case 'PROMPT':  return this.escalation.PROMPT_to_SUMMONS_hours;
      case 'SUMMONS': return this.escalation.SUMMONS_to_CRITICAL_hours;
      default:        return Infinity;
    }
  }

  private _expiryHours(level: CallingLevel): number {
    switch (level) {
      case 'NOTICE':  return this.expiry.NOTICE_expires_hours;
      case 'PROMPT':  return this.expiry.PROMPT_expires_hours;
      case 'SUMMONS': return this.expiry.SUMMONS_expires_hours;
      default:        return Infinity;
    }
  }

  private async _requireCalling(callingId: ID): Promise<Calling> {
    const calling = await this.store.loadCalling(callingId);
    if (!calling) {
      throw new Error(`CallingIssuer: CALLING '${callingId}' not found.`);
    }
    return calling;
  }
}

// ---------------------------------------------------------------------------
// 5. Summary type
// ---------------------------------------------------------------------------

export interface CallingSummary {
  principal_id:         ID;
  active_count:         number;
  by_level:             Record<CallingLevel, number>;
  critical_fragments:   Array<{
    calling_id:     ID;
    fragment_id:    ID;
    fragment_label: string;
    issued_at:      ISOTimestamp;
  }>;
  oldest_active:        {
    calling_id:     ID;
    fragment_id:    ID;
    fragment_label: string;
    level:          CallingLevel;
    issued_at:      ISOTimestamp;
  } | null;
  total_issued:         number;
  acknowledgement_rate: number;   // [0, 1]
  computed_at:          ISOTimestamp;
}

// ---------------------------------------------------------------------------
// 6. In-memory storage adapter
// ---------------------------------------------------------------------------

export class InMemoryCallingStorage implements CallingStorageAdapter {
  private _callings      = new Map<ID, Calling>();
  private _byPrincipal   = new Map<ID, Set<ID>>();
  private _byFragment    = new Map<string, ID>(); // `${principalId}:${fragmentId}` → callingId

  async saveCalling(calling: Calling): Promise<void> {
    this._callings.set(calling.id, { ...calling });
    if (!this._byPrincipal.has(calling.principal_id))
      this._byPrincipal.set(calling.principal_id, new Set());
    this._byPrincipal.get(calling.principal_id)!.add(calling.id);
    const key = `${calling.principal_id}:${calling.fragment_id}`;
    this._byFragment.set(key, calling.id);
  }

  async loadCalling(callingId: ID): Promise<Calling | null> {
    return this._callings.get(callingId) ?? null;
  }

  async loadActiveCallings(principalId: ID): Promise<Calling[]> {
    return this._forPrincipal(principalId).filter(isActive);
  }

  async loadCallingForFragment(principalId: ID, fragmentId: ID): Promise<Calling | null> {
    const key = `${principalId}:${fragmentId}`;
    const id  = this._byFragment.get(key);
    return id ? (this._callings.get(id) ?? null) : null;
  }

  async loadAllCallings(principalId: ID): Promise<Calling[]> {
    return this._forPrincipal(principalId);
  }

  private _forPrincipal(principalId: ID): Calling[] {
    const ids = this._byPrincipal.get(principalId) ?? new Set();
    return [...ids].map(id => this._callings.get(id)!).filter(Boolean);
  }

  snapshot(): Calling[] {
    return [...this._callings.values()];
  }
}

// ---------------------------------------------------------------------------
// 7. Internal helpers
// ---------------------------------------------------------------------------

const LEVEL_ORDER: Record<CallingLevel, number> = {
  NOTICE: 0, PROMPT: 1, SUMMONS: 2, CRITICAL: 3,
};

function isActive(c: Calling): boolean {
  return c.state === 'ACTIVE' || c.state === 'ESCALATED';
}

function byUrgencyThenAge(a: Calling, b: Calling): number {
  const levelDiff = LEVEL_ORDER[b.level] - LEVEL_ORDER[a.level];
  if (levelDiff !== 0) return levelDiff;
  return new Date(a.issued_at).getTime() - new Date(b.issued_at).getTime();
}

function nowISO(): ISOTimestamp {
  return new Date().toISOString();
}

function addHours(iso: ISOTimestamp, hours: number): ISOTimestamp {
  return new Date(new Date(iso).getTime() + hours * 3_600_000).toISOString();
}

function generateId(): ID {
  return `call-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 9)}`;
}

// ---------------------------------------------------------------------------
// 8. Exports
// ---------------------------------------------------------------------------

export default CallingIssuer;
