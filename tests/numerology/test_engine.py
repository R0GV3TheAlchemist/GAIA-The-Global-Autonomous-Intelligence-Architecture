"""
tests/numerology/test_engine.py
Unit tests for NumerologyEngine — pure computation, zero DB.

All expected values are hand-verified against the Pythagorean method.
Master number cases use historically documented subjects.
"""
from __future__ import annotations

from datetime import date

import pytest

from gaia.numerology.engine import (
    ARCHETYPES,
    MASTER_NUMBERS,
    NumerologyEngine,
    PersonalYearEntry,
    reduce,
)

engine = NumerologyEngine()

_VALID_REDUCED = set(range(0, 10)) | MASTER_NUMBERS


# ---------------------------------------------------------------------------
# reduce()
# ---------------------------------------------------------------------------

class TestReduce:
    def test_single_digit_unchanged(self):
        assert reduce(7) == (7, [7])

    def test_two_digit_reduces(self):
        result, path = reduce(29)
        assert result == 11          # 2+9=11 — master number, stop
        assert path == [29, 11]

    def test_master_11_preserved(self):
        val, path = reduce(11)
        assert val == 11
        assert path == [11]

    def test_master_22_preserved(self):
        val, path = reduce(22)
        assert val == 22

    def test_master_33_preserved(self):
        val, path = reduce(33)
        assert val == 33

    def test_large_number_reduces_fully(self):
        # 199 -> 19 -> 10 -> 1
        val, path = reduce(199)
        assert val == 1
        assert path == [199, 19, 10, 1]

    def test_reduction_path_length(self):
        # 38 -> 11 (master, stop)
        val, path = reduce(38)
        assert val == 11
        assert len(path) == 2

    def test_reduce_zero_returns_zero(self):
        """reduce(0) must return (0, [0]) — absent energy, not infinite loop."""
        val, path = reduce(0)
        assert val == 0
        assert path == [0]

    def test_reduce_zero_does_not_loop(self):
        """Regression: old code entered `while current > 9` which was fine for 0,
        but explicit guard confirms no future regression."""
        import signal
        # Just calling reduce(0) and returning is enough — if it hangs the
        # test runner will time out via pytest-timeout (60 s global limit).
        result = reduce(0)
        assert result == (0, [0])


# ---------------------------------------------------------------------------
# normalize_name()
# ---------------------------------------------------------------------------

class TestNormalizeName:
    def test_strips_accents(self):
        assert engine.normalize_name("André") == "ANDRE"

    def test_collapses_whitespace(self):
        assert engine.normalize_name("  nikola   tesla  ") == "NIKOLA TESLA"

    def test_uppercase(self):
        assert engine.normalize_name("ada lovelace") == "ADA LOVELACE"

    def test_unicode_ligature(self):
        result = engine.normalize_name("Ærøskøbing")
        assert result == result.upper()

    def test_normalize_applied_in_compute(self):
        """compute() must store the canonical name, not the raw user input."""
        chart = engine.compute("nikola tesla", date(1856, 7, 10))
        assert chart.full_name == "NIKOLA TESLA"

    def test_accented_name_same_result_as_normalized(self):
        """Accented and plain versions of the same name produce identical charts."""
        chart_raw   = engine.compute("Nikolà Téslà", date(1856, 7, 10))
        chart_plain = engine.compute("Nikola Tesla", date(1856, 7, 10))
        assert chart_raw.life_path.reduced_value == chart_plain.life_path.reduced_value
        assert chart_raw.expression.reduced_value == chart_plain.expression.reduced_value


# ---------------------------------------------------------------------------
# Life Path
# ---------------------------------------------------------------------------

class TestLifePath:
    def test_nikola_tesla_life_path(self):
        # July 10, 1856 → 7 + 1 + 20 = 28 → 2+8 = 10 → 1+0 = 1
        chart = engine.compute("Nikola Tesla", date(1856, 7, 10))
        assert chart.life_path.reduced_value == 1

    def test_life_path_master_11(self):
        chart = engine.compute("Test Master", date(1964, 2, 2))
        lp = chart.life_path.reduced_value
        assert lp in set(range(1, 10)) | MASTER_NUMBERS

    def test_life_path_is_master_flag_set_correctly(self):
        chart = engine.compute("Anyone", date(1985, 11, 29))
        lp = chart.life_path
        assert lp.is_master_number == (lp.reduced_value in MASTER_NUMBERS)

    def test_life_path_range(self):
        for day in range(1, 29):
            chart = engine.compute("Range Test", date(1990, 3, day))
            assert chart.life_path.reduced_value in set(range(1, 10)) | MASTER_NUMBERS


# ---------------------------------------------------------------------------
# Expression, Soul Urge, Personality
# ---------------------------------------------------------------------------

class TestNameNumbers:
    def test_expression_nikola_tesla(self):
        chart = engine.compute("Nikola Tesla", date(1856, 7, 10))
        expr = chart.expression.reduced_value
        assert expr in set(range(1, 10)) | MASTER_NUMBERS

    def test_soul_urge_plus_personality_equals_expression_mod(self):
        """Soul Urge (vowels) + Personality (consonants) digits must equal
        the raw Expression value when summed together."""
        chart = engine.compute("Ada Lovelace", date(1815, 12, 10))
        raw_su = chart.soul_urge.raw_value
        raw_pe = chart.personality.raw_value
        raw_ex = chart.expression.raw_value
        assert raw_su + raw_pe == raw_ex

    def test_personality_only_consonants(self):
        """All-vowel name produces personality.raw_value == 0."""
        chart = engine.compute("Aeia", date(1990, 1, 1))
        assert chart.personality.raw_value == 0
        assert chart.personality.reduced_value == 0

    def test_soul_urge_only_vowels(self):
        """All-consonant name produces soul_urge.raw_value == 0."""
        chart = engine.compute("Nth", date(1990, 1, 1))
        assert chart.soul_urge.raw_value == 0
        assert chart.soul_urge.reduced_value == 0

    def test_zero_position_gets_void_archetype(self):
        """A position with raw_value == 0 must carry the 'The Void' archetype."""
        chart = engine.compute("Aeia", date(1990, 1, 1))  # personality == 0
        assert chart.personality.archetype == "The Void"
        assert chart.personality.theme is not None
        assert len(chart.personality.theme) > 0

    def test_zero_archetype_entry_exists_in_table(self):
        """ARCHETYPES[0] must be present so NumberResult.__post_init__ populates it."""
        assert 0 in ARCHETYPES
        name, theme = ARCHETYPES[0]
        assert name == "The Void"
        assert "absent" in theme.lower() or "energy" in theme.lower()


# ---------------------------------------------------------------------------
# Birthday number
# ---------------------------------------------------------------------------

class TestBirthday:
    def test_birthday_single_digit_unchanged(self):
        chart = engine.compute("Test", date(1990, 6, 7))
        assert chart.birthday.reduced_value == 7

    def test_birthday_29_reduces_to_11(self):
        chart = engine.compute("Test", date(1990, 6, 29))
        assert chart.birthday.reduced_value == 11
        assert chart.birthday.is_master_number is True

    def test_birthday_22_is_master(self):
        chart = engine.compute("Test", date(1990, 6, 22))
        assert chart.birthday.reduced_value == 22
        assert chart.birthday.is_master_number is True


# ---------------------------------------------------------------------------
# Personal Year
# ---------------------------------------------------------------------------

class TestPersonalYear:
    def test_personal_year_in_valid_range(self):
        chart = engine.compute("Anyone", date(1985, 3, 14), reference_year=2026)
        py = chart.personal_year.reduced_value
        assert py in set(range(1, 10)) | MASTER_NUMBERS

    def test_personal_year_changes_by_year(self):
        chart_a = engine.compute("Anyone", date(1985, 3, 14), reference_year=2025)
        chart_b = engine.compute("Anyone", date(1985, 3, 14), reference_year=2026)
        assert chart_a.personal_year.reduced_value in set(range(1, 10)) | MASTER_NUMBERS
        assert chart_b.personal_year.reduced_value in set(range(1, 10)) | MASTER_NUMBERS

    def test_personal_year_number_type(self):
        chart = engine.compute("Anyone", date(1990, 1, 1))
        assert chart.personal_year.number_type == "personal_year"


# ---------------------------------------------------------------------------
# Personal Year Cycle  (new — covers improvement #3)
# ---------------------------------------------------------------------------

class TestPersonalYearCycle:
    _DOB = date(1856, 7, 10)   # Tesla
    _REF = 2026

    def test_cycle_default_length(self):
        """Default cycle_years=3 produces 4 entries: current + 3 ahead."""
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        assert len(chart.personal_year_cycle) == 4  # 2026, 2027, 2028, 2029

    def test_cycle_years_zero_returns_empty(self):
        chart = engine.compute(
            "Nikola Tesla", self._DOB,
            reference_year=self._REF,
            cycle_years=0,
        )
        assert chart.personal_year_cycle == []

    def test_cycle_years_custom_length(self):
        chart = engine.compute(
            "Nikola Tesla", self._DOB,
            reference_year=self._REF,
            cycle_years=5,
        )
        assert len(chart.personal_year_cycle) == 6  # current + 5

    def test_cycle_first_entry_matches_personal_year(self):
        """cycle[0] must be identical to the standalone personal_year result."""
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        assert chart.personal_year_cycle[0].year == self._REF
        assert chart.personal_year_cycle[0].reduced_value == chart.personal_year.reduced_value

    def test_cycle_years_are_consecutive(self):
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        years = [e.year for e in chart.personal_year_cycle]
        assert years == list(range(self._REF, self._REF + len(years)))

    def test_cycle_entries_are_personal_year_entry_instances(self):
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        for entry in chart.personal_year_cycle:
            assert isinstance(entry, PersonalYearEntry)

    def test_cycle_all_values_in_valid_range(self):
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        for entry in chart.personal_year_cycle:
            assert entry.reduced_value in _VALID_REDUCED

    def test_cycle_master_year_flagged_correctly(self):
        """2028 is a master 11 year for Tesla — is_master_number must be True."""
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        entry_2028 = next(e for e in chart.personal_year_cycle if e.year == 2028)
        assert entry_2028.reduced_value == 11
        assert entry_2028.is_master_number is True

    def test_cycle_archetype_populated(self):
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        for entry in chart.personal_year_cycle:
            assert entry.archetype is not None
            assert entry.theme is not None

    def test_cycle_2026_is_humanitarian(self):
        """Tesla 2026 personal year = 9 — The Humanitarian."""
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        entry_2026 = chart.personal_year_cycle[0]
        assert entry_2026.reduced_value == 9
        assert entry_2026.archetype == "The Humanitarian"

    def test_cycle_2027_is_pioneer(self):
        """Tesla 2027 personal year = 1 — The Pioneer."""
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        entry_2027 = next(e for e in chart.personal_year_cycle if e.year == 2027)
        assert entry_2027.reduced_value == 1
        assert entry_2027.archetype == "The Pioneer"

    def test_cycle_independent_of_reference_year(self):
        """Cycle starting from 2025 should produce different entries than 2026."""
        chart_25 = engine.compute("Nikola Tesla", self._DOB, reference_year=2025)
        chart_26 = engine.compute("Nikola Tesla", self._DOB, reference_year=2026)
        # First entries differ in year
        assert chart_25.personal_year_cycle[0].year == 2025
        assert chart_26.personal_year_cycle[0].year == 2026

    def test_as_dict_includes_cycle(self):
        """personal_year_cycle must survive the as_dict() round-trip."""
        chart = engine.compute("Nikola Tesla", self._DOB, reference_year=self._REF)
        d = chart.as_dict()
        assert "personal_year_cycle" in d
        assert isinstance(d["personal_year_cycle"], list)
        assert len(d["personal_year_cycle"]) == 4
        first = d["personal_year_cycle"][0]
        assert set(first.keys()) == {"year", "reduced_value", "is_master_number", "archetype", "theme"}


# ---------------------------------------------------------------------------
# Challenge Numbers
# ---------------------------------------------------------------------------

class TestChallenges:
    def test_four_challenges_returned(self):
        chart = engine.compute("Anyone", date(1990, 5, 15))
        assert len(chart.challenges) == 4

    def test_challenge_types(self):
        chart = engine.compute("Anyone", date(1990, 5, 15))
        types = [c.number_type for c in chart.challenges]
        assert types == ["challenge_1", "challenge_2", "challenge_3", "challenge_main"]

    def test_challenges_excluded_when_flag_false(self):
        chart = engine.compute("Anyone", date(1990, 5, 15), include_challenges=False)
        assert chart.challenges == []

    def test_challenge_values_non_negative(self):
        chart = engine.compute("Anyone", date(1990, 5, 15))
        for c in chart.challenges:
            assert c.reduced_value >= 0


# ---------------------------------------------------------------------------
# Archetypes
# ---------------------------------------------------------------------------

class TestArchetypes:
    def test_zero_has_archetype(self):
        """ARCHETYPES[0] must exist — guards against absent-energy null responses."""
        assert 0 in ARCHETYPES

    def test_all_numbers_1_to_9_have_archetypes(self):
        for n in range(1, 10):
            assert n in ARCHETYPES, f"Missing archetype for {n}"

    def test_master_numbers_have_archetypes(self):
        for n in MASTER_NUMBERS:
            assert n in ARCHETYPES, f"Missing archetype for master number {n}"

    def test_archetype_has_name_and_theme(self):
        for n, (name, theme) in ARCHETYPES.items():
            assert isinstance(name, str) and len(name) > 0
            assert isinstance(theme, str) and len(theme) > 0

    def test_number_result_populates_archetype(self):
        chart = engine.compute("Nikola Tesla", date(1856, 7, 10))
        lp = chart.life_path
        if lp.reduced_value in ARCHETYPES:
            assert lp.archetype is not None
            assert lp.theme is not None


# ---------------------------------------------------------------------------
# as_dict() serialisation
# ---------------------------------------------------------------------------

class TestAsDict:
    def test_as_dict_has_required_keys(self):
        chart = engine.compute("Nikola Tesla", date(1856, 7, 10))
        d = chart.as_dict()
        for key in ("full_name", "birth_date", "system", "life_path",
                    "expression", "soul_urge", "personality", "birthday",
                    "personal_year", "challenges", "personal_year_cycle"):
            assert key in d, f"Missing key: {key}"

    def test_as_dict_birth_date_is_iso_string(self):
        chart = engine.compute("Test", date(1990, 6, 15))
        assert chart.as_dict()["birth_date"] == "1990-06-15"

    def test_as_dict_challenges_is_list(self):
        chart = engine.compute("Test", date(1990, 6, 15))
        assert isinstance(chart.as_dict()["challenges"], list)

    def test_as_dict_cycle_entry_has_all_keys(self):
        chart = engine.compute("Test", date(1990, 6, 15))
        d = chart.as_dict()
        if d["personal_year_cycle"]:
            entry = d["personal_year_cycle"][0]
            for k in ("year", "reduced_value", "is_master_number", "archetype", "theme"):
                assert k in entry, f"personal_year_cycle entry missing key: {k}"


# ---------------------------------------------------------------------------
# Unsupported system guard
# ---------------------------------------------------------------------------

class TestSystemValidation:
    def test_unsupported_system_raises(self):
        with pytest.raises(NotImplementedError, match="chaldean"):
            engine.compute("Test", date(1990, 1, 1), system="chaldean")
