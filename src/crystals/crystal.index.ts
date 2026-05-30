/**
 * crystal.index.ts
 * ─────────────────────────────────────────────────────────────────────────────
 * Unified Crystal Database — the single import surface for all crystal data,
 * theory resolution, and validation across GAIA-OS.
 *
 * Closes Issue #107 (Crystal Theory Engine) — final file in the trilogy:
 *   1. crystal.theory.ts    — metaphysical resolution engine
 *   2. crystal.validator.ts — 12-rule intake guard
 *   3. crystal.index.ts     — THIS FILE: O(1) lookup maps + query helpers
 *
 * Usage:
 *   import {
 *     CRYSTAL_DB, getCrystalByName, getCrystalsByModule,
 *     getCrystalProfile, searchCrystals,
 *     resolveGAIAResonance, validateRecord,          // re-exported
 *   } from '@/crystals/crystal.index';
 *
 * ─────────────────────────────────────────────────────────────────────────────
 */

import { ALL_CRYSTALS } from './db/index';
import type { CrystalRecord } from './db/crystal.schema';
import { GAIAModule, RiskTier, ChakraPoint } from './db/crystal.schema';
import {
  resolveGAIAResonance,
  getSafetyProfile,
  getCrystalTheory,
  type TheoryResult,
} from './crystal.theory';
import {
  validateRecord,
  validateBatch,
  assertRecord,
  formatBatchReport,
  type ValidationResult,
  type BatchReport,
  type ValidationIssue,
  type IssueSeverity,
  ValidationError,
} from './crystal.validator';

// ─── Re-exports ───────────────────────────────────────────────────────────────
// Consumers can import everything from one path.
export {
  // crystal.theory.ts
  resolveGAIAResonance,
  getSafetyProfile,
  getCrystalTheory,
  type TheoryResult,
  // crystal.validator.ts
  validateRecord,
  validateBatch,
  assertRecord,
  formatBatchReport,
  ValidationError,
  type ValidationResult,
  type BatchReport,
  type ValidationIssue,
  type IssueSeverity,
  // schema enums (convenience pass-through)
  GAIAModule,
  RiskTier,
  ChakraPoint,
};
export type { CrystalRecord };

// ─── Primary Lookup Maps ──────────────────────────────────────────────────────

/**
 * CRYSTAL_DB
 * O(1) lookup by canonical crystal ID (e.g. "quartz-clear").
 * Authoritative source of truth — keyed by CrystalRecord.id.
 */
export const CRYSTAL_DB: ReadonlyMap<string, CrystalRecord> = (() => {
  const map = new Map<string, CrystalRecord>();
  for (const record of ALL_CRYSTALS) {
    map.set(record.id, record);
  }
  return map;
})();

/**
 * CRYSTAL_BY_NAME
 * O(1) case-insensitive lookup by primary crystal name.
 * Keys are lowercased. Aliases are NOT indexed here — use searchCrystals()
 * for alias-aware lookup.
 */
export const CRYSTAL_BY_NAME: ReadonlyMap<string, CrystalRecord> = (() => {
  const map = new Map<string, CrystalRecord>();
  for (const record of ALL_CRYSTALS) {
    map.set(record.name.toLowerCase(), record);
  }
  return map;
})();

/**
 * CRYSTAL_BY_MODULE
 * Multi-value map keyed by GAIAModule.
 * Each crystal appears under EVERY module resolved from its gaia_resonance
 * string — so a crystal with resonance "MEMORY|INTUITION" will appear in
 * both CRYSTAL_BY_MODULE.get(GAIAModule.MEMORY) and .get(GAIAModule.INTUITION).
 */
export const CRYSTAL_BY_MODULE: ReadonlyMap<GAIAModule, CrystalRecord[]> = (() => {
  const map = new Map<GAIAModule, CrystalRecord[]>();

  // Ensure every module has an array, even if empty
  for (const mod of Object.values(GAIAModule)) {
    map.set(mod, []);
  }

  for (const record of ALL_CRYSTALS) {
    const { modules } = resolveGAIAResonance(record.gaia_resonance);
    for (const mod of modules) {
      map.get(mod)!.push(record);
    }
  }

  return map;
})();

/**
 * CRYSTAL_BY_CHAKRA
 * Multi-value map keyed by ChakraPoint.
 * Derived from each record's primary_chakra and secondary_chakras fields.
 */
export const CRYSTAL_BY_CHAKRA: ReadonlyMap<ChakraPoint, CrystalRecord[]> = (() => {
  const map = new Map<ChakraPoint, CrystalRecord[]>();

  for (const chakra of Object.values(ChakraPoint)) {
    map.set(chakra, []);
  }

  for (const record of ALL_CRYSTALS) {
    if (record.primary_chakra) {
      map.get(record.primary_chakra)?.push(record);
    }
    for (const chakra of record.secondary_chakras ?? []) {
      // Avoid duplicates if primary === secondary
      if (chakra !== record.primary_chakra) {
        map.get(chakra)?.push(record);
      }
    }
  }

  return map;
})();

/**
 * CRYSTAL_BY_RISK_TIER
 * Multi-value map keyed by RiskTier.
 */
export const CRYSTAL_BY_RISK_TIER: ReadonlyMap<RiskTier, CrystalRecord[]> = (() => {
  const map = new Map<RiskTier, CrystalRecord[]>();
  for (const tier of Object.values(RiskTier)) {
    map.set(tier, []);
  }
  for (const record of ALL_CRYSTALS) {
    map.get(record.risk_tier)!.push(record);
  }
  return map;
})();

// ─── Query Helpers ────────────────────────────────────────────────────────────

/** Returns the CrystalRecord for the given ID, or undefined. */
export function getCrystalById(id: string): CrystalRecord | undefined {
  return CRYSTAL_DB.get(id);
}

/**
 * Returns the CrystalRecord whose primary name matches (case-insensitive),
 * or undefined. For alias matching, use searchCrystals().
 */
export function getCrystalByName(name: string): CrystalRecord | undefined {
  return CRYSTAL_BY_NAME.get(name.toLowerCase());
}

/** Returns all CrystalRecords associated with the given GAIAModule. */
export function getCrystalsByModule(module: GAIAModule): CrystalRecord[] {
  return CRYSTAL_BY_MODULE.get(module) ?? [];
}

/** Returns all CrystalRecords associated with the given ChakraPoint. */
export function getCrystalsByChakra(chakra: ChakraPoint): CrystalRecord[] {
  return CRYSTAL_BY_CHAKRA.get(chakra) ?? [];
}

/** Returns all CrystalRecords at the given RiskTier. */
export function getCrystalsByRiskTier(tier: RiskTier): CrystalRecord[] {
  return CRYSTAL_BY_RISK_TIER.get(tier) ?? [];
}

/** Returns the full array of every CrystalRecord in the database. */
export function getAllCrystals(): CrystalRecord[] {
  return ALL_CRYSTALS;
}

/** Returns the total number of crystals in the database. */
export function getCrystalCount(): number {
  return CRYSTAL_DB.size;
}

// ─── Search ───────────────────────────────────────────────────────────────────

export interface SearchOptions {
  /** Maximum results to return. Default: unlimited. */
  limit?: number;
  /** Restrict results to a specific GAIAModule. */
  module?: GAIAModule;
  /** Restrict results to a specific RiskTier. */
  riskTier?: RiskTier;
  /** Only return crystals safe for water use. */
  safeForWater?: boolean;
  /** Only return crystals safe for hardware/electronic use. */
  safeForHardware?: boolean;
}

/**
 * searchCrystals(query, options?)
 *
 * Full-text search across name, aliases, and keyword fields.
 * The query is matched case-insensitively against:
 *   - record.name
 *   - record.aliases[]    (if present)
 *   - record.keywords[]   (if present)
 *   - record.gaia_resonance (module text match)
 *
 * Results are ordered: name-match first, then alias-match, then keyword-match.
 * Optional filter bag (options) is applied after text matching.
 *
 * Returns an empty array when no records match.
 */
export function searchCrystals(
  query: string,
  options: SearchOptions = {},
): CrystalRecord[] {
  const q = query.toLowerCase().trim();
  if (!q) return [];

  type Scored = { record: CrystalRecord; score: number };
  const scored: Scored[] = [];

  for (const record of ALL_CRYSTALS) {
    // Apply filters first — skip records that don't pass
    if (options.module !== undefined) {
      const { modules } = resolveGAIAResonance(record.gaia_resonance);
      if (!modules.includes(options.module)) continue;
    }
    if (options.riskTier !== undefined && record.risk_tier !== options.riskTier) continue;
    if (options.safeForWater === true && record.safe_for_water === false) continue;
    if (options.safeForHardware === true && record.safe_for_hardware === false) continue;

    // Text scoring
    let score = 0;

    if (record.name.toLowerCase() === q) {
      score = 100; // Exact name match
    } else if (record.name.toLowerCase().includes(q)) {
      score = 80; // Partial name match
    } else {
      // Alias match
      const aliases: string[] = (record as any).aliases ?? [];
      if (aliases.some((a) => a.toLowerCase() === q)) {
        score = 60;
      } else if (aliases.some((a) => a.toLowerCase().includes(q))) {
        score = 40;
      } else {
        // Keyword match
        const keywords: string[] = (record as any).keywords ?? [];
        if (keywords.some((k) => k.toLowerCase().includes(q))) {
          score = 20;
        } else if (record.gaia_resonance.toLowerCase().includes(q)) {
          score = 10;
        }
      }
    }

    if (score > 0) {
      scored.push({ record, score });
    }
  }

  // Sort by score descending, then name ascending for ties
  scored.sort((a, b) =>
    b.score !== a.score
      ? b.score - a.score
      : a.record.name.localeCompare(b.record.name),
  );

  const results = scored.map((s) => s.record);
  return options.limit !== undefined ? results.slice(0, options.limit) : results;
}

// ─── CrystalProfile ───────────────────────────────────────────────────────────

/**
 * CrystalProfile
 * A convenience bundle combining the raw CrystalRecord with its pre-computed
 * TheoryResult and ValidationResult. Intended for UI components and GAIA
 * reasoning consumers that need the full picture in one object.
 */
export interface CrystalProfile {
  record: CrystalRecord;
  theory: TheoryResult;
  validation: ValidationResult;
  /** true iff validation.valid === true */
  isValid: boolean;
  /** Shorthand: the crystal's resolved primary GAIAModule */
  primaryModule: GAIAModule | null;
  /** Shorthand: safety profile summary */
  safetyProfile: ReturnType<typeof getSafetyProfile>;
}

/**
 * getCrystalProfile(id)
 *
 * Returns a fully resolved CrystalProfile for the given crystal ID, or
 * undefined if no crystal exists with that ID.
 *
 * Theory resolution and validation are run fresh on each call (not cached)
 * so the profile always reflects the current state of the record.
 */
export function getCrystalProfile(id: string): CrystalProfile | undefined {
  const record = CRYSTAL_DB.get(id);
  if (!record) return undefined;

  const theory = getCrystalTheory(record);
  const validation = validateRecord(record);

  return {
    record,
    theory,
    validation,
    isValid: validation.valid,
    primaryModule: theory.primary_module,
    safetyProfile: getSafetyProfile(record),
  };
}

// ─── Integrity Check ──────────────────────────────────────────────────────────

/**
 * runIntegrityCheck()
 *
 * Validates every record in CRYSTAL_DB using validateBatch().
 * Returns a BatchReport. Intended for use in CI pipelines and startup
 * health checks — not for hot paths.
 *
 * Example (CI):
 *   import { runIntegrityCheck, formatBatchReport } from '@/crystals/crystal.index';
 *   const report = runIntegrityCheck();
 *   if (report.totals.failed > 0) {
 *     console.error(formatBatchReport(report));
 *     process.exit(1);
 *   }
 */
export function runIntegrityCheck(): BatchReport {
  return validateBatch(ALL_CRYSTALS, 'FULL_DB_INTEGRITY_CHECK');
}
