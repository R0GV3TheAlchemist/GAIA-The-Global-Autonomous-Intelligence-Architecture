"""
tests/test_canon_entry.py
=========================
Unit tests for CanonEntry, CanonValidator, and the updated
_analyse_canon_context() integration.

Covers
------
- CanonEntry field validation (all error paths)
- RegisterSignal enum values
- Keywords-vs-declared-signal conflict detection
- to_dict() / from_dict() round-trip
- to_context_string() and embedded_canon_refs()
- CanonValidator single-entry and batch paths
- Duplicate ref_id detection
- Cross-entry signal conflict detection (raise_on_conflict=True)
- CanonValidator.filter_valid() convenience method
- _analyse_canon_context() with CanonEntry input (explicit signal)
- _analyse_canon_context() with CanonEntry input (UNSPECIFIED — keyword fallback)
- _analyse_canon_context() with plain string (legacy path unchanged)

Canon refs: C01, C30, C32
"""

import pytest

from core.canon.canon_entry import CanonEntry, CanonEntryError, RegisterSignal
from core.canon.canon_validator import CanonConflictError, CanonValidator, ValidationResult
from core.synergy_engine import _analyse_canon_context, CanonPlanHint


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

VALID_KWARGS = dict(
    ref_id="C32",
    author="R0GV3TheAlchemist",
    timestamp="2026-06-08T12:00:00Z",
    version="1.0.0",
    body="Build and create the resonance layer with purpose.",
    register_signal=RegisterSignal.EXECUTIVE,
)


def make_entry(**overrides) -> CanonEntry:
    kwargs = {**VALID_KWARGS, **overrides}
    return CanonEntry(**kwargs)


# ---------------------------------------------------------------------------
# CanonEntry — construction and basic validation
# ---------------------------------------------------------------------------

class TestCanonEntryValidation:

    def test_valid_entry_passes(self):
        entry = make_entry()
        assert entry.validate() is entry  # returns self

    def test_blank_ref_id_raises(self):
        with pytest.raises(CanonEntryError, match="ref_id"):
            make_entry(ref_id="").validate()

    def test_whitespace_ref_id_raises(self):
        with pytest.raises(CanonEntryError, match="whitespace"):
            make_entry(ref_id="C 32").validate()

    def test_blank_author_raises(self):
        with pytest.raises(CanonEntryError, match="author"):
            make_entry(author="").validate()

    def test_invalid_timestamp_raises(self):
        with pytest.raises(CanonEntryError, match="ISO-8601"):
            make_entry(timestamp="June 8 2026").validate()

    def test_blank_version_raises(self):
        with pytest.raises(CanonEntryError, match="version"):
            make_entry(version="").validate()

    def test_empty_body_raises(self):
        with pytest.raises(CanonEntryError, match="body"):
            make_entry(body="").validate()

    def test_short_body_raises(self):
        with pytest.raises(CanonEntryError, match="short"):
            make_entry(body="too short").validate()  # < 10 chars stripped

    def test_keyword_conflict_raises(self):
        """Body says rest+sleep (minimal), declared signal is EXECUTIVE."""
        with pytest.raises(CanonEntryError, match="Values-alignment conflict"):
            make_entry(
                body="rest and sleep and pause to restore your energy and capacity",
                register_signal=RegisterSignal.EXECUTIVE,
            ).validate()

    def test_unspecified_signal_no_conflict_check(self):
        """UNSPECIFIED bypasses keyword conflict check — no error."""
        entry = make_entry(
            body="rest and sleep and pause to restore your energy today",
            register_signal=RegisterSignal.UNSPECIFIED,
        )
        assert entry.validate() is entry

    def test_same_group_no_conflict(self):
        """executive body + EXECUTIVE signal — no conflict."""
        entry = make_entry(
            body="research and build the new resonance integration layer",
            register_signal=RegisterSignal.EXECUTIVE,
        )
        assert entry.validate() is entry


# ---------------------------------------------------------------------------
# RegisterSignal enum
# ---------------------------------------------------------------------------

class TestRegisterSignal:

    def test_values_are_lowercase_strings(self):
        assert RegisterSignal.REFLECTIVE.value == "reflective"
        assert RegisterSignal.EXECUTIVE.value  == "executive"
        assert RegisterSignal.MINIMAL.value    == "minimal"
        assert RegisterSignal.UNSPECIFIED.value == "unspecified"

    def test_string_comparison(self):
        """Values compare equal to plan() register strings."""
        assert RegisterSignal.EXECUTIVE.value == "executive"


# ---------------------------------------------------------------------------
# Serialisation
# ---------------------------------------------------------------------------

class TestCanonEntrySerialization:

    def test_to_dict_roundtrip(self):
        entry = make_entry(tags=["core"], metadata={"priority": 1})
        d = entry.to_dict()
        restored = CanonEntry.from_dict(d)
        assert restored.ref_id          == entry.ref_id
        assert restored.author          == entry.author
        assert restored.timestamp       == entry.timestamp
        assert restored.version         == entry.version
        assert restored.body            == entry.body
        assert restored.register_signal == entry.register_signal
        assert restored.tags            == entry.tags
        assert restored.metadata        == entry.metadata

    def test_from_dict_unknown_signal_defaults_unspecified(self):
        entry = CanonEntry.from_dict({**VALID_KWARGS, "register_signal": "BOGUS"})
        assert entry.register_signal == RegisterSignal.UNSPECIFIED

    def test_to_context_string_includes_ref_id(self):
        entry = make_entry()
        ctx = entry.to_context_string()
        assert "C32" in ctx
        assert entry.body in ctx

    def test_embedded_canon_refs(self):
        entry = make_entry(body="This passage references C01 and C30 as grounding.")
        refs = entry.embedded_canon_refs()
        assert "C01" in refs
        assert "C30" in refs


# ---------------------------------------------------------------------------
# CanonValidator — single entry
# ---------------------------------------------------------------------------

class TestCanonValidatorSingleEntry:
    validator = CanonValidator()

    def test_valid_entry_no_errors(self):
        result = self.validator.validate_entry(make_entry())
        assert result.is_valid
        assert result.errors == []

    def test_invalid_entry_captured_as_error(self):
        bad = make_entry(ref_id="")
        result = self.validator.validate_entry(bad)
        assert not result.is_valid
        assert any("ref_id" in e for e in result.errors)

    def test_short_body_warns(self):
        short = make_entry(body="short body text")
        result = self.validator.validate_entry(short)
        # short body < 40 chars → warning (not error)
        assert any("short" in w.lower() for w in result.warnings)

    def test_unspecified_signal_warns(self):
        entry = make_entry(register_signal=RegisterSignal.UNSPECIFIED)
        result = self.validator.validate_entry(entry)
        assert any("UNSPECIFIED" in w for w in result.warnings)


# ---------------------------------------------------------------------------
# CanonValidator — batch
# ---------------------------------------------------------------------------

class TestCanonValidatorBatch:
    validator = CanonValidator()

    def test_clean_batch_valid(self):
        entries = [
            make_entry(ref_id="C01"),
            make_entry(ref_id="C30"),
            make_entry(ref_id="C32"),
        ]
        result = self.validator.validate_batch(entries)
        assert result.is_valid
        assert result.entry_count == 3

    def test_duplicate_ref_id_is_error(self):
        entries = [
            make_entry(ref_id="C01"),
            make_entry(ref_id="C01"),  # duplicate
        ]
        result = self.validator.validate_batch(entries)
        assert not result.is_valid
        assert any("Duplicate" in e for e in result.errors)

    def test_signal_conflict_is_error(self):
        entries = [
            make_entry(ref_id="C99", register_signal=RegisterSignal.EXECUTIVE),
            make_entry(ref_id="C99", register_signal=RegisterSignal.MINIMAL),
        ]
        result = self.validator.validate_batch(entries)
        assert not result.is_valid
        assert any("conflict" in e.lower() for e in result.errors)

    def test_signal_conflict_raises_with_flag(self):
        entries = [
            make_entry(ref_id="C99", register_signal=RegisterSignal.EXECUTIVE),
            make_entry(ref_id="C99", register_signal=RegisterSignal.REFLECTIVE),
        ]
        with pytest.raises(CanonConflictError):
            self.validator.validate_batch(entries, raise_on_conflict=True)

    def test_filter_valid_removes_invalid(self):
        entries = [
            make_entry(ref_id="GOOD"),
            make_entry(ref_id=""),       # invalid — blank ref_id
        ]
        valid, result = self.validator.filter_valid(entries)
        assert len(valid) == 1
        assert valid[0].ref_id == "GOOD"
        assert not result.is_valid


# ---------------------------------------------------------------------------
# _analyse_canon_context() — CanonEntry integration
# ---------------------------------------------------------------------------

class TestAnalyseCanonContextWithEntry:

    def test_explicit_executive_signal_used_directly(self):
        entry = make_entry(
            ref_id="C32",
            body="Build and create the resonance integration layer.",
            register_signal=RegisterSignal.EXECUTIVE,
        )
        hint = _analyse_canon_context(entry)
        assert hint.present is True
        assert hint.register_nudge == "executive"
        assert "canon-entry:C32:executive" in hint.nudge_label
        assert hint.entry_ref_id == "C32"

    def test_explicit_minimal_signal_used_directly(self):
        entry = make_entry(
            ref_id="CANON-REST",
            body="Take time to rest and restore your energy field.",
            register_signal=RegisterSignal.MINIMAL,
        )
        hint = _analyse_canon_context(entry)
        assert hint.register_nudge == "minimal"
        assert hint.entry_ref_id == "CANON-REST"

    def test_unspecified_falls_back_to_keyword_scan(self):
        entry = make_entry(
            ref_id="C-UNKNOWN",
            body="research and explore and build the new layer",
            register_signal=RegisterSignal.UNSPECIFIED,
        )
        hint = _analyse_canon_context(entry)
        # keyword scan should find executive group
        assert hint.register_nudge == "executive"
        assert hint.present is True

    def test_canon_ref_id_in_canon_refs(self):
        entry = make_entry(ref_id="C01")
        hint = _analyse_canon_context(entry)
        assert "C01" in hint.canon_refs

    def test_empty_body_returns_not_present(self):
        entry = make_entry(body="placeholder")
        entry.body = ""  # bypass validate() to test the analyse function directly
        hint = _analyse_canon_context(entry)
        assert hint.present is False


# ---------------------------------------------------------------------------
# _analyse_canon_context() — legacy string path unchanged
# ---------------------------------------------------------------------------

class TestAnalyseCanonContextLegacyString:

    def test_none_returns_not_present(self):
        hint = _analyse_canon_context(None)
        assert hint.present is False

    def test_empty_string_returns_not_present(self):
        hint = _analyse_canon_context("")
        assert hint.present is False

    def test_executive_keyword_string(self):
        hint = _analyse_canon_context("Build and research the canon layer.")
        assert hint.register_nudge == "executive"
        assert hint.present is True
        assert hint.entry_ref_id is None

    def test_ref_extraction_from_string(self):
        hint = _analyse_canon_context("Grounded in C01 and C32 principles.")
        assert "C01" in hint.canon_refs
        assert "C32" in hint.canon_refs
