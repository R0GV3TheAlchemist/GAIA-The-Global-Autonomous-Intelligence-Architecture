"""
core/canon/canon_validator.py
=============================
Batch validation and conflict detection for CanonEntry collections.

CanonValidator is the gate that stands between raw Canon authorship and
ingestion into plan().  It rejects entries that are malformed OR that
contradict one another before any of them can influence GAIA's behaviour.

Design principles
-----------------
C01 — Sovereignty: the Canon is the Gaian's explicit value system.
      Only well-formed, non-conflicting entries reach the planner.
C30 — No silent failures: every validation error is surfaced in the
      ValidationResult, never swallowed silently.
C32 — Synergy Doctrine: cross-entry conflict detection ensures the
      Canon's signal is coherent, not self-contradictory.

Usage
-----
    validator = CanonValidator()
    result = validator.validate_batch(entries)
    if not result.is_valid:
        for err in result.errors:
            print(err)

For single-entry validation prefer CanonEntry.validate() directly.
CanonValidator.validate_entry() wraps that and formats the result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.canon.canon_entry import CanonEntry, CanonEntryError, RegisterSignal


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class CanonConflictError(ValueError):
    """
    Raised when the Canon batch contains entries whose declared
    register_signals are irreconcilably contradictory — e.g. two entries
    with the SAME ref_id but DIFFERENT register_signals.

    This is treated as a values-alignment bug (C01), not just a warning.
    """


# ---------------------------------------------------------------------------
# ValidationResult
# ---------------------------------------------------------------------------

@dataclass
class ValidationResult:
    """
    Structured result of a CanonValidator run.

    Attributes
    ----------
    is_valid    : True only when errors is empty.
    errors      : Hard failures — entries that must not be ingested.
    warnings    : Soft issues that should be reviewed but won't block ingestion.
    entry_count : Number of entries that were validated.
    """
    errors:      List[str] = field(default_factory=list)
    warnings:    List[str] = field(default_factory=list)
    entry_count: int       = 0

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        status = "VALID" if self.is_valid else "INVALID"
        return (
            f"[CanonValidator] {status} — "
            f"{self.entry_count} entries, "
            f"{len(self.errors)} error(s), "
            f"{len(self.warnings)} warning(s)."
        )


# ---------------------------------------------------------------------------
# CanonValidator
# ---------------------------------------------------------------------------

class CanonValidator:
    """
    Validates individual CanonEntry objects and full batches.

    Single-entry validation
    -----------------------
        result = validator.validate_entry(entry)

    Batch validation (cross-entry conflict detection included)
    ----------------------------------------------------------
        result = validator.validate_batch(entries)

    Raising on conflict
    -------------------
        validator.validate_batch(entries, raise_on_conflict=True)
        # raises CanonConflictError if any cross-entry conflict is found
    """

    # Minimum body length (chars) below which a warning is emitted even
    # if the entry technically passes the 10-char floor in CanonEntry.
    _BODY_RICHNESS_FLOOR = 40

    def validate_entry(
        self,
        entry: CanonEntry,
        result: Optional[ValidationResult] = None,
    ) -> ValidationResult:
        """
        Validate a single CanonEntry.  Appends findings to *result*
        (creating a new one if not supplied).  Does not raise — all
        findings go into result.errors / result.warnings.
        """
        if result is None:
            result = ValidationResult()
        result.entry_count += 1

        # Run CanonEntry's own validate() for field-level checks.
        try:
            entry.validate()
        except CanonEntryError as exc:
            result.errors.append(str(exc))
            return result

        # Soft checks that go into warnings.
        if len(entry.body.strip()) < self._BODY_RICHNESS_FLOOR:
            result.warnings.append(
                f"Entry '{entry.ref_id}' body is short "
                f"({len(entry.body.strip())} chars). "
                f"Consider expanding for richer Canon grounding."
            )

        if entry.register_signal == RegisterSignal.UNSPECIFIED:
            result.warnings.append(
                f"Entry '{entry.ref_id}' has register_signal=UNSPECIFIED. "
                f"Declare an explicit signal for deterministic plan() behaviour."
            )

        return result

    def validate_batch(
        self,
        entries: List[CanonEntry],
        raise_on_conflict: bool = False,
    ) -> ValidationResult:
        """
        Validate a list of CanonEntry objects.

        Per-entry validation
        --------------------
        Each entry is validated with validate_entry().

        Cross-entry conflict detection
        ------------------------------
        1. Duplicate ref_ids: same ref_id appearing more than once is an
           error — schema-level enforcement prevents accidental overloading.

        2. Signal conflicts: if two entries share the same ref_id but
           declare different (non-UNSPECIFIED) register_signals, that is a
           CanonConflictError / error — the Canon cannot say "rest" and
           "build" with the same identifier.

        Parameters
        ----------
        entries           : List of CanonEntry objects to validate.
        raise_on_conflict : If True, raises CanonConflictError on any
                            cross-entry signal conflict instead of only
                            appending to result.errors.

        Returns
        -------
        ValidationResult with all findings.
        """
        result = ValidationResult()

        # Per-entry validation
        for entry in entries:
            self.validate_entry(entry, result)

        # Cross-entry: group by ref_id
        ref_id_map: Dict[str, List[CanonEntry]] = {}
        for entry in entries:
            ref_id_map.setdefault(entry.ref_id, []).append(entry)

        for ref_id, group in ref_id_map.items():
            if len(group) > 1:
                result.errors.append(
                    f"Duplicate ref_id '{ref_id}': {len(group)} entries share "
                    f"this identifier. Canon ref_ids must be unique."
                )

            # Check for signal conflicts within this ref_id group
            signals = [
                e.register_signal
                for e in group
                if e.register_signal != RegisterSignal.UNSPECIFIED
            ]
            unique_signals = set(signals)
            if len(unique_signals) > 1:
                conflict_msg = (
                    f"Signal conflict on ref_id '{ref_id}': entries declare "
                    f"conflicting register_signals "
                    f"{[s.value for s in unique_signals]}. "
                    f"The Canon cannot simultaneously instruct "
                    f"'{unique_signals.pop().value}' and '{unique_signals.pop().value}'. "
                    f"Resolve before ingesting into plan()."
                )
                if raise_on_conflict:
                    raise CanonConflictError(conflict_msg)
                result.errors.append(conflict_msg)

        return result

    def filter_valid(
        self,
        entries: List[CanonEntry],
    ) -> Tuple[List[CanonEntry], ValidationResult]:
        """
        Convenience method: validate all entries and return only those
        that pass (no errors).  Invalid entries are excluded.

        Returns
        -------
        (valid_entries, result)  — valid_entries is safe to ingest.
        """
        result = self.validate_batch(entries)
        # Collect ref_ids of entries with errors
        error_ref_ids = set()
        for err in result.errors:
            # Extract ref_id from error strings that contain it
            for entry in entries:
                if entry.ref_id in err:
                    error_ref_ids.add(entry.ref_id)

        valid = [e for e in entries if e.ref_id not in error_ref_ids]
        return valid, result
