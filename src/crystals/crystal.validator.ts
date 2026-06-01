/**
 * src/crystals/crystal.validator.ts
 * GAIA-OS Crystal Intelligence Engine — Intake Guard
 *
 * This module is the validation layer for the crystal database.
 * It runs against every CrystalRecord before a batch is committed,
 * ensuring schema contracts are upheld and data quality is maintained.
 *
 * ─── DESIGN PHILOSOPHY ────────────────────────────────────────────────────────
 *
 * The validator is OPINIONATED but GRADUATED.
 * Not every problem is an error — some are warnings that require human review.
 * The severity system has three tiers:
 *
 *   ERROR    — record cannot be safely used; must be fixed before commit
 *   WARNING  — data gap or inconsistency that degrades reasoning quality
 *   INFO     — advisory note; does not block commit
 *
 * The validator NEVER throws on data problems. It collects all issues and
 * returns them in a structured ValidationResult. Only `assertRecord()` throws,
 * and only for use in test suites that want fast-fail behaviour.
 *
 * ─── CHECKS PERFORMED ─────────────────────────────────────────────────────────
 *
 * Domain A — GAIA Resonance
 *   A1  gaia_resonance parses to at least one valid GAIAModule            ERROR
 *   A2  no unknown tokens in gaia_resonance string                        WARNING
 *   A3  primary module consistent with CHAKRA_MODULE_MAP                  WARNING
 *
 * Domain B — Angel Number
 *   B1  angel_number is a registered AngelNumber value or null            ERROR
 *   B2  angel_number gaia_module matches primary resolved module          WARNING
 *
 * Domain C — Safety Coherence
 *   C1  safe_for_water=false requires non-null safety_warning             ERROR
 *   C2  safe_for_hardware=false requires non-null safety_warning          ERROR
 *   C3  CRITICAL/HIGH RiskTier requires safety_warning present            ERROR
 *   C4  safety_warning present on a NONE-tier record                      WARNING
 *
 * Domain D — Physical Consistency
 *   D1  hardness_min <= hardness_max when both non-null                   ERROR
 *   D2  specific_gravity_min <= specific_gravity_max when both non-null   ERROR
 *   D3  ri_min <= ri_max when both non-null                               ERROR
 *
 * ─── EXPORTS ──────────────────────────────────────────────────────────────────
 *
 *   validateRecord(record)         — full validation, returns ValidationResult
 *   validateBatch(records, label)  — validates array, returns BatchReport
 *   assertRecord(record)           — throws ValidationError on first ERROR
 *
 * Author: GAIA-OS Crystal Intelligence Engine
 * Date:   2026-05-30
 * Schema: CrystalRecord v1.8
 */

import type { CrystalRecord, AngelNumber } from './db/crystal.schema';
import {
  ANGEL_NUMBER_MAP,
  CHAKRA_MODULE_MAP,
} from './db/metaphysical.data';
import {
  resolveGAIAResonance,
  getSafetyProfile,
} from './crystal.theory';

// ─────────────────────────────────────────────────────────────────────────────
// TYPES
// ─────────────────────────────────────────────────────────────────────────────

export type IssueSeverity = 'ERROR' | 'WARNING' | 'INFO';

export interface ValidationIssue {
  code:     string;
  severity: IssueSeverity;
  message:  string;
  field:    string;
  actual:   string;
  expected: string;
}

export interface ValidationResult {
  crystal_name: string;
  valid: boolean;
  issues: ValidationIssue[];
  counts: {
    errors:   number;
    warnings: number;
    info:     number;
  };
}

export interface BatchReport {
  label:          string;
  run_at:         string;
  total:          number;
  passed:         number;
  failed:         number;
  batch_valid:    boolean;
  results:        ValidationResult[];
  all_errors:     ValidationIssue[];
  totals: {
    errors:   number;
    warnings: number;
    info:     number;
  };
}

export class ValidationError extends Error {
  constructor(
    public readonly result: ValidationResult
  ) {
    const errorList = result.issues
      .filter(i => i.severity === 'ERROR')
      .map(i => `[${i.code}] ${i.message}`)
      .join('; ');
    super(
      `Crystal validation failed for "${result.crystal_name}": ${errorList}`
    );
    this.name = 'ValidationError';
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// INTERNAL HELPERS
// ─────────────────────────────────────────────────────────────────────────────

function issue(
  code:     string,
  severity: IssueSeverity,
  message:  string,
  field:    string,
  actual:   string,
  expected: string
): ValidationIssue {
  return { code, severity, message, field, actual, expected };
}

const LEGAL_ANGEL_NUMBERS: Set<number | string | null> = new Set<number | string | null>([
  null,
  1, 2, 3, 4, 5, 6, 7, 8, 9,
  11, 22, 33,
  23, 44, 55, 66, 77, 88, 99,
  111, 222, 333, 444, 555, 666, 777, 888, 999,
  1111,
  404, 707, 808,
  '000',
]);

// ─────────────────────────────────────────────────────────────────────────────
// DOMAIN A — GAIA RESONANCE
// ─────────────────────────────────────────────────────────────────────────────

function checkResonanceDomain(record: CrystalRecord): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const resonance = resolveGAIAResonance(record);
  const rawField  = 'metaphysical.gaia_resonance';
  const rawValue  = record.metaphysical.gaia_resonance ?? '<null>';

  if (resonance.has_unknown_token && resonance.all_modules.length === 0) {
    issues.push(issue(
      'A1', 'ERROR',
      `gaia_resonance "${rawValue}" contains no recognisable GAIAModule ids. ` +
      `Valid ids: ClarusLens, AnchorPrism, SomnusVeil, SovereignCore, ViriditasHeart, Noosphere, QuantumNexus.`,
      rawField,
      rawValue,
      'At least one valid GAIAModule id'
    ));
  }

  if (resonance.has_unknown_token && resonance.unknown_tokens.length > 0) {
    issues.push(issue(
      'A2', 'WARNING',
      `gaia_resonance contains unrecognised token(s): ${resonance.unknown_tokens.join(', ')}. ` +
      `These will be ignored by the reasoning engine.`,
      rawField,
      resonance.unknown_tokens.join(', '),
      'Only valid GAIAModule ids'
    ));
  }

  const expectedModule = CHAKRA_MODULE_MAP[record.metaphysical.chakra_primary];
  const actualPrimary  = resonance.primary_module;
  if (expectedModule && actualPrimary !== expectedModule) {
    issues.push(issue(
      'A3', 'WARNING',
      `Primary module "${actualPrimary}" does not match the canonical ` +
      `CHAKRA_MODULE_MAP assignment for chakra "${record.metaphysical.chakra_primary}" ` +
      `(expected "${expectedModule}"). This may be an intentional override — verify.`,
      rawField,
      actualPrimary ?? '<null>',
      expectedModule
    ));
  }

  return issues;
}

// ─────────────────────────────────────────────────────────────────────────────
// DOMAIN B — ANGEL NUMBER
// ─────────────────────────────────────────────────────────────────────────────

function checkAngelNumberDomain(record: CrystalRecord): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const angelNumber = record.metaphysical.angel_number as number | string | null;
  const field       = 'metaphysical.angel_number';

  if (!LEGAL_ANGEL_NUMBERS.has(angelNumber)) {
    issues.push(issue(
      'B1', 'ERROR',
      `angel_number ${angelNumber} is not a valid AngelNumber. ` +
      `Allowed values: null, 1-9, 11, 22, 33, 23, 44-99 (sacred), 111-999 (sequences), 1111, 404, 707, 808, '000'.`,
      field,
      String(angelNumber),
      'A registered AngelNumber value or null'
    ));
  }

  if (angelNumber != null && LEGAL_ANGEL_NUMBERS.has(angelNumber)) {
    // Cast is safe: angelNumber has already passed LEGAL_ANGEL_NUMBERS.has() guard,
    // meaning it is a valid member of the AngelNumber union.
    const angelDef      = ANGEL_NUMBER_MAP.get(angelNumber as AngelNumber);
    const resonance     = resolveGAIAResonance(record);
    const primaryModule = resonance.primary_module;

    if (angelDef && angelDef.gaia_module !== primaryModule) {
      issues.push(issue(
        'B2', 'WARNING',
        `angel_number ${angelNumber} ("${angelDef.name}") is associated with ` +
        `module "${angelDef.gaia_module}" in the registry, but the crystal's ` +
        `primary module resolves to "${primaryModule}". This may be intentional — verify.`,
        field,
        `${angelNumber} → ${angelDef.gaia_module}`,
        `${angelNumber} → ${primaryModule}`
      ));
    }
  }

  return issues;
}

// ─────────────────────────────────────────────────────────────────────────────
// DOMAIN C — SAFETY COHERENCE
// ─────────────────────────────────────────────────────────────────────────────

function checkSafetyDomain(record: CrystalRecord): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const { safe_for_water, safe_for_hardware } = record.physical;
  const warning = record.metaphysical.safety_warning;
  const safety  = getSafetyProfile(record);

  if (!safe_for_water && warning == null) {
    issues.push(issue(
      'C1', 'ERROR',
      `safe_for_water is false but safety_warning is null. ` +
      `Every water-unsafe stone must carry an explicit safety_warning.`,
      'metaphysical.safety_warning',
      'null',
      'Non-null safety_warning describing the water hazard'
    ));
  }

  if (!safe_for_hardware && warning == null) {
    issues.push(issue(
      'C2', 'ERROR',
      `safe_for_hardware is false but safety_warning is null. ` +
      `Every hardware-unsafe stone must carry an explicit safety_warning.`,
      'metaphysical.safety_warning',
      'null',
      'Non-null safety_warning describing the hardware hazard'
    ));
  }

  if (
    (safety.risk_tier === 'CRITICAL' || safety.risk_tier === 'HIGH') &&
    warning == null
  ) {
    issues.push(issue(
      'C3', 'ERROR',
      `RiskTier is ${safety.risk_tier} but safety_warning is null. ` +
      `CRITICAL and HIGH risk stones must always carry an explicit warning.`,
      'metaphysical.safety_warning',
      'null',
      `Non-null safety_warning (RiskTier: ${safety.risk_tier})`
    ));
  }

  if (safety.risk_tier === 'NONE' && warning != null) {
    issues.push(issue(
      'C4', 'WARNING',
      `safety_warning is present but RiskTier computed as NONE. ` +
      `Either the warning text should contain keywords that elevate the tier, ` +
      `or the warning may be unnecessary. Review the warning text.`,
      'metaphysical.safety_warning',
      // warning is string here (not null) — safe to slice
      `"${warning.slice(0, 60)}${warning.length > 60 ? '...' : ''}"`,
      'Either elevate with hazard keywords or remove the warning'
    ));
  }

  return issues;
}

// ─────────────────────────────────────────────────────────────────────────────
// DOMAIN D — PHYSICAL CONSISTENCY
// ─────────────────────────────────────────────────────────────────────────────

function checkPhysicalDomain(record: CrystalRecord): ValidationIssue[] {
  const issues: ValidationIssue[] = [];
  const p = record.physical;

  if (
    p.hardness_min != null && p.hardness_max != null &&
    p.hardness_min > p.hardness_max
  ) {
    issues.push(issue(
      'D1', 'ERROR',
      `hardness_min (${p.hardness_min}) is greater than hardness_max (${p.hardness_max}).`,
      'physical.hardness_min / physical.hardness_max',
      `${p.hardness_min} > ${p.hardness_max}`,
      'hardness_min ≤ hardness_max'
    ));
  }

  if (
    p.specific_gravity_min != null && p.specific_gravity_max != null &&
    p.specific_gravity_min > p.specific_gravity_max
  ) {
    issues.push(issue(
      'D2', 'ERROR',
      `specific_gravity_min (${p.specific_gravity_min}) is greater than ` +
      `specific_gravity_max (${p.specific_gravity_max}).`,
      'physical.specific_gravity_min / physical.specific_gravity_max',
      `${p.specific_gravity_min} > ${p.specific_gravity_max}`,
      'specific_gravity_min ≤ specific_gravity_max'
    ));
  }

  if (
    p.ri_min != null && p.ri_max != null &&
    p.ri_min > p.ri_max
  ) {
    issues.push(issue(
      'D3', 'ERROR',
      `ri_min (${p.ri_min}) is greater than ri_max (${p.ri_max}).`,
      'physical.ri_min / physical.ri_max',
      `${p.ri_min} > ${p.ri_max}`,
      'ri_min ≤ ri_max'
    ));
  }

  return issues;
}

// ─────────────────────────────────────────────────────────────────────────────
// PUBLIC API
// ─────────────────────────────────────────────────────────────────────────────

export function validateRecord(record: CrystalRecord): ValidationResult {
  const allIssues: ValidationIssue[] = [
    ...checkResonanceDomain(record),
    ...checkAngelNumberDomain(record),
    ...checkSafetyDomain(record),
    ...checkPhysicalDomain(record),
  ];

  const errors   = allIssues.filter(i => i.severity === 'ERROR').length;
  const warnings = allIssues.filter(i => i.severity === 'WARNING').length;
  const info     = allIssues.filter(i => i.severity === 'INFO').length;

  return {
    crystal_name: record.name,
    valid:        errors === 0,
    issues:       allIssues,
    counts:       { errors, warnings, info },
  };
}

export function validateBatch(
  records: CrystalRecord[],
  label: string
): BatchReport {
  const results = records.map(r => validateRecord(r));

  results.sort((a, b) => {
    if (!a.valid && b.valid)  return -1;
    if (a.valid  && !b.valid) return 1;
    return b.counts.errors - a.counts.errors;
  });

  const passed    = results.filter(r => r.valid).length;
  const failed    = results.length - passed;
  const allErrors = results.flatMap(r => r.issues.filter(i => i.severity === 'ERROR'));

  const totals = results.reduce(
    (acc, r) => ({
      errors:   acc.errors   + r.counts.errors,
      warnings: acc.warnings + r.counts.warnings,
      info:     acc.info     + r.counts.info,
    }),
    { errors: 0, warnings: 0, info: 0 }
  );

  return {
    label,
    run_at:      new Date().toISOString(),
    total:       records.length,
    passed,
    failed,
    batch_valid: failed === 0,
    results,
    all_errors:  allErrors,
    totals,
  };
}

export function assertRecord(record: CrystalRecord): void {
  const result = validateRecord(record);
  if (!result.valid) {
    throw new ValidationError(result);
  }
}

export function formatBatchReport(report: BatchReport): string {
  const lines: string[] = [
    `╔${'═'.repeat(66)}`,
    `║ GAIA Crystal Validator — Batch Report`,
    `║ Batch : ${report.label}`,
    `║ Run at: ${report.run_at}`,
    `║ Result: ${
      report.batch_valid
        ? '✅ ALL RECORDS VALID'
        : `❌ ${report.failed} of ${report.total} RECORDS FAILED`
    }`,
    `║ Totals: ${report.total} records · ` +
      `${report.totals.errors} errors · ` +
      `${report.totals.warnings} warnings · ` +
      `${report.totals.info} info`,
    `╚${'═'.repeat(66)}`,
  ];

  if (!report.batch_valid) {
    lines.push('');
    lines.push('FAILED RECORDS:');
    lines.push('');

    for (const result of report.results.filter(r => !r.valid)) {
      lines.push(`  ❌ ${result.crystal_name} — ${result.counts.errors} error(s), ${result.counts.warnings} warning(s)`);
      for (const iss of result.issues) {
        const icon = iss.severity === 'ERROR' ? '✗' : iss.severity === 'WARNING' ? '⚠' : 'ℹ';
        lines.push(`      ${icon} [${iss.code}] ${iss.message}`);
        lines.push(`          field   : ${iss.field}`);
        lines.push(`          actual  : ${iss.actual}`);
        lines.push(`          expected: ${iss.expected}`);
      }
      lines.push('');
    }
  }

  if (report.totals.warnings > 0 && report.batch_valid) {
    lines.push('');
    lines.push('WARNINGS (batch passed, but review recommended):');
    lines.push('');

    for (const result of report.results.filter(r => r.counts.warnings > 0)) {
      lines.push(`  ⚠  ${result.crystal_name} — ${result.counts.warnings} warning(s)`);
      for (const iss of result.issues.filter(i => i.severity === 'WARNING')) {
        lines.push(`      ⚠ [${iss.code}] ${iss.message}`);
      }
      lines.push('');
    }
  }

  return lines.join('\n');
}
