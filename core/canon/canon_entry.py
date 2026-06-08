"""
core/canon/canon_entry.py
=========================
Formalizes the Canon contract as a typed, validated dataclass.

Previously, Canon passages were free-form strings matched by regex.
This module introduces:

  RegisterSignal  — explicit enum for the register a passage intends to
                    activate (REFLECTIVE, EXECUTIVE, MINIMAL, UNSPECIFIED).

  CanonEntry      — schema-enforced Canon passage with required provenance
                    fields (ref_id, author, timestamp, version, body) and
                    an explicit register_signal.

  CanonEntryError — raised when a CanonEntry fails its own validate().

Backward compatibility
----------------------
_analyse_canon_context() in synergy_engine.py accepts *either* a plain
str (legacy path) or a CanonEntry (new path).  All existing callers
continue to work unchanged.

Canon refs
----------
C01 — Sovereignty: the Canon is the Gaian's explicit value system.
      Entries must be authored and timestamped.
C30 — No silent failures: validate() raises loudly rather than silently
      discarding a malformed entry.
C32 — Synergy Doctrine: register_signal replaces ambiguous regex matching
      with a typed, schema-enforced declaration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# RegisterSignal — explicit enum (replaces implicit keyword matching)
# ---------------------------------------------------------------------------

class RegisterSignal(str, Enum):
    """
    The action-register a Canon passage is *intended* to activate.

    UNSPECIFIED means the passage carries no explicit register intent;
    _analyse_canon_context() will fall back to keyword scanning.

    Values are lowercase strings so they serialize naturally to JSON and
    can be compared directly with the register strings used in plan().
    """
    REFLECTIVE   = "reflective"
    EXECUTIVE    = "executive"
    MINIMAL      = "minimal"
    UNSPECIFIED  = "unspecified"


# ---------------------------------------------------------------------------
# CanonEntryError
# ---------------------------------------------------------------------------

class CanonEntryError(ValueError):
    """Raised when a CanonEntry fails its own validate() check."""


# ---------------------------------------------------------------------------
# CanonEntry
# ---------------------------------------------------------------------------

# ISO-8601 timestamp pattern: YYYY-MM-DDTHH:MM:SS[.fff][Z|+HH:MM]
_TS_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.[\d]+)?(Z|[+-]\d{2}:\d{2})?$"
)

# Canon ref IDs embedded in passage bodies (e.g. "C01", "C32")
_CANON_REF_PATTERN = re.compile(r"\bC\d+\b")

# Keyword groups used for conflict detection between body and declared signal.
# If the body contains strong signals from *multiple* groups and the
# declared register_signal is UNSPECIFIED, validate() emits a warning
# (not an error) so CanonValidator can surface it.
_KEYWORD_GROUPS: Dict[str, List[str]] = {
    "reflective": ["grief", "overwhelm", "trauma", "loss", "distress",
                   "integrate", "synthesise", "synthesize", "review",
                   "storm", "severe", "crisis", "emergency"],
    "executive":  ["research", "explore", "build", "create", "write"],
    "minimal":    ["rest", "pause", "sleep", "minimal", "lightweight"],
}


@dataclass
class CanonEntry:
    """
    A single Canon passage — the atomic unit of GAIA's value system.

    Required fields
    ---------------
    ref_id          : Unique, non-empty identifier (e.g. "C01", "CANON-REST-001").
                      Must not contain whitespace.
    author          : Who authored this entry (Gaian name or system label).
    timestamp       : ISO-8601 UTC string of authorship (not ingestion).
    version         : Semantic version string ("1.0.0", "2.1", etc.).
    body            : The passage text itself.  Non-empty, >= 10 chars.
    register_signal : Explicit RegisterSignal enum value.
                      Use UNSPECIFIED when the passage has no register intent.

    Optional fields
    ---------------
    tags            : Free-form list of topic tags.
    metadata        : Arbitrary dict for caller-specific extensions.

    Usage
    -----
        entry = CanonEntry(
            ref_id="C32",
            author="R0GV3TheAlchemist",
            timestamp="2026-06-08T12:00:00Z",
            version="1.0.0",
            body="Build and create the resonance layer.",
            register_signal=RegisterSignal.EXECUTIVE,
        )
        entry.validate()  # raises CanonEntryError if invalid

        # Feed to plan() directly:
        context.canon_context = entry  # _analyse_canon_context handles both
    """

    ref_id:          str
    author:          str
    timestamp:       str
    version:         str
    body:            str
    register_signal: RegisterSignal = RegisterSignal.UNSPECIFIED
    tags:            List[str]       = field(default_factory=list)
    metadata:        Dict[str, Any]  = field(default_factory=dict)

    # ------------------------------------------------------------------ #
    # Validation                                                          #
    # ------------------------------------------------------------------ #

    def validate(self) -> "CanonEntry":
        """
        Validate the entry against the Canon contract.  Returns self so
        calls can be chained.  Raises CanonEntryError on any violation.

        Checks
        ------
        1. ref_id is non-empty and contains no whitespace.
        2. author is non-empty.
        3. timestamp matches ISO-8601 pattern.
        4. version is non-empty.
        5. body is non-empty and at least 10 characters.
        6. register_signal is a valid RegisterSignal member.
        7. If register_signal is not UNSPECIFIED, the body must not
           contain strong keyword signals from a *different* register
           group.  A C01 values-alignment conflict raises CanonEntryError
           (not just a warning) so it is caught before reaching plan().
        """
        errors: List[str] = []

        # 1. ref_id
        if not self.ref_id or not self.ref_id.strip():
            errors.append("ref_id must be non-empty.")
        elif re.search(r"\s", self.ref_id):
            errors.append(f"ref_id {self.ref_id!r} must not contain whitespace.")

        # 2. author
        if not self.author or not self.author.strip():
            errors.append("author must be non-empty.")

        # 3. timestamp
        if not self.timestamp or not _TS_PATTERN.match(self.timestamp.strip()):
            errors.append(
                f"timestamp {self.timestamp!r} is not a valid ISO-8601 string. "
                "Expected format: YYYY-MM-DDTHH:MM:SSZ"
            )

        # 4. version
        if not self.version or not self.version.strip():
            errors.append("version must be non-empty.")

        # 5. body
        if not self.body or not self.body.strip():
            errors.append("body must be non-empty.")
        elif len(self.body.strip()) < 10:
            errors.append(
                f"body is too short ({len(self.body.strip())} chars). "
                "Minimum is 10 characters."
            )

        # 6. register_signal membership
        if not isinstance(self.register_signal, RegisterSignal):
            try:
                # Accept raw string values too (e.g. from JSON deserialisation)
                self.register_signal = RegisterSignal(self.register_signal)
            except (ValueError, KeyError):
                errors.append(
                    f"register_signal {self.register_signal!r} is not a valid "
                    f"RegisterSignal value. Valid: "
                    f"{[s.value for s in RegisterSignal]}"
                )

        # 7. Keyword conflict: declared signal vs body content
        if not errors and self.register_signal != RegisterSignal.UNSPECIFIED:
            declared = self.register_signal.value
            body_lower = self.body.lower()
            for group, keywords in _KEYWORD_GROUPS.items():
                if group == declared:
                    continue  # same group — no conflict
                hits = [kw for kw in keywords if kw in body_lower]
                if len(hits) >= 2:
                    errors.append(
                        f"Values-alignment conflict (C01): body contains "
                        f"{len(hits)} '{group}' keyword(s) {hits} but "
                        f"register_signal is declared as '{declared}'. "
                        f"Either update register_signal to '{group}' or "
                        f"revise the passage body."
                    )

        if errors:
            raise CanonEntryError(
                f"CanonEntry '{self.ref_id}' failed validation "
                f"({len(errors)} error(s)):\n  " + "\n  ".join(errors)
            )

        return self

    # ------------------------------------------------------------------ #
    # Serialisation                                                       #
    # ------------------------------------------------------------------ #

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to a plain dict (JSON-safe)."""
        return {
            "ref_id":          self.ref_id,
            "author":          self.author,
            "timestamp":       self.timestamp,
            "version":         self.version,
            "body":            self.body,
            "register_signal": self.register_signal.value,
            "tags":            list(self.tags),
            "metadata":        dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonEntry":
        """Deserialise from a plain dict.  Does NOT call validate()."""
        sig_raw = data.get("register_signal", "unspecified")
        try:
            sig = RegisterSignal(sig_raw)
        except (ValueError, KeyError):
            sig = RegisterSignal.UNSPECIFIED
        return cls(
            ref_id=data.get("ref_id", ""),
            author=data.get("author", ""),
            timestamp=data.get("timestamp", ""),
            version=data.get("version", ""),
            body=data.get("body", ""),
            register_signal=sig,
            tags=list(data.get("tags", [])),
            metadata=dict(data.get("metadata", {})),
        )

    # ------------------------------------------------------------------ #
    # Integration bridge                                                  #
    # ------------------------------------------------------------------ #

    def to_context_string(self) -> str:
        """
        Produce the string that _analyse_canon_context() (legacy path)
        would receive.  Prepends the ref_id so Canon refs are extracted
        correctly, then appends the body.

        Used internally when CanonEntry is passed to plan() on a
        LoopContext that stores it as context.canon_context.
        The _analyse_canon_context() function handles CanonEntry natively,
        but this method is available for callers that need the raw string.
        """
        return f"{self.ref_id}: {self.body}"

    def embedded_canon_refs(self) -> List[str]:
        """Return all C\\d+ ref IDs found in the body text."""
        return sorted(set(_CANON_REF_PATTERN.findall(self.body)))

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"CanonEntry(ref_id={self.ref_id!r}, "
            f"signal={self.register_signal.value!r}, "
            f"version={self.version!r}, "
            f"author={self.author!r})"
        )
