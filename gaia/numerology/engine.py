"""Pure-function numerology calculation engine.

No database, no I/O.  All computation is deterministic and testable
in isolation.  See canon/C160 for the doctrinal rules encoded here.

Pythagorean mapping formula: A=1, B=2, ... I=9, J=1, K=2 ... Z=8
  ch_value = ((ord(ch) - ord('A')) % 9) + 1
Spot-check: A=1, E=5, I=9, J=1, S=1, Z=8  ← verified against
standard Pythagorean tables.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Pythagorean letter -> digit mapping
# Formula: ((ord(ch) - ord('A')) % 9) + 1  produces standard wrap at 9.
# Spot-checks (do not remove — guards against silent formula drift):
#   A=1 B=2 C=3 D=4 E=5 F=6 G=7 H=8 I=9
#   J=1 K=2 L=3 M=4 N=5 O=6 P=7 Q=8 R=9
#   S=1 T=2 U=3 V=4 W=5 X=6 Y=7 Z=8
PYTHAGOREAN: Dict[str, int] = {
    ch: ((ord(ch) - ord("A")) % 9) + 1
    for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
}

# Assertion guard — fails fast if the formula is ever accidentally changed.
_SPOT_CHECKS = {"A": 1, "E": 5, "I": 9, "J": 1, "S": 1, "Z": 8, "Y": 7}
assert all(
    PYTHAGOREAN[k] == v for k, v in _SPOT_CHECKS.items()
), f"PYTHAGOREAN table is corrupted: {PYTHAGOREAN}"

VOWELS = frozenset("AEIOU")
MASTER_NUMBERS = frozenset({11, 22, 33})

ARCHETYPES: Dict[int, Tuple[str, str]] = {
    0:  ("The Void",           "Absent energy — no letter expression present for this position"),
    1:  ("The Pioneer",        "Independence, leadership, initiation, willpower"),
    2:  ("The Diplomat",       "Partnership, sensitivity, balance, cooperation"),
    3:  ("The Creator",        "Expression, joy, communication, creativity"),
    4:  ("The Builder",        "Structure, discipline, foundation, practicality"),
    5:  ("The Freedom Seeker", "Change, adventure, versatility, experience"),
    6:  ("The Nurturer",       "Responsibility, love, harmony, service to family"),
    7:  ("The Seeker",         "Introspection, wisdom, solitude, spiritual inquiry"),
    8:  ("The Manifestor",     "Power, abundance, authority, material mastery"),
    9:  ("The Humanitarian",   "Completion, compassion, universality, release"),
    11: ("The Illuminator",    "Intuition, inspiration, idealism, spiritual messenger"),
    22: ("The Master Builder", "Grand vision, practical idealism, legacy-scale creation"),
    33: ("The Master Teacher", "Unconditional love, healing, cosmic responsibility"),
}


# ---------------------------------------------------------------------------
# Reduction helpers
# ---------------------------------------------------------------------------

def _digit_sum(n: int) -> int:
    """Sum the digits of a non-negative integer."""
    return sum(int(d) for d in str(abs(n)))


def reduce(n: int) -> Tuple[int, List[int]]:
    """Reduce n to a single digit or Master Number.

    0 is returned as-is (absent energy — caller decides how to present).

    Returns:
        (reduced_value, reduction_path)
        reduction_path includes the original n and every intermediate value.
    """
    if n == 0:
        return 0, [0]
    path: List[int] = [n]
    current = n
    while current > 9 and current not in MASTER_NUMBERS:
        current = _digit_sum(current)
        path.append(current)
    return current, path


# ---------------------------------------------------------------------------
# Name parsing helpers
# ---------------------------------------------------------------------------

def _is_vowel(ch: str, next_ch: Optional[str]) -> bool:
    """Return True if ch is a vowel, treating Y as a vowel only when it is
    the sole vowel sound in a syllable (approximated by: Y is a vowel if
    no standard vowel immediately precedes or follows it in the same word).
    """
    ch = ch.upper()
    if ch in VOWELS:
        return True
    if ch == "Y":
        # Treat Y as vowel when next character is a consonant or end-of-word
        return next_ch is None or next_ch.upper() not in VOWELS
    return False


def _letters(name: str) -> str:
    """Strip everything except A-Z from a name string."""
    return "".join(ch for ch in name.upper() if ch.isalpha())


def _vowel_values(name: str) -> List[int]:
    letters = _letters(name)
    values = []
    for i, ch in enumerate(letters):
        nxt = letters[i + 1] if i + 1 < len(letters) else None
        if _is_vowel(ch, nxt):
            values.append(PYTHAGOREAN[ch])
    return values


def _consonant_values(name: str) -> List[int]:
    letters = _letters(name)
    values = []
    for i, ch in enumerate(letters):
        nxt = letters[i + 1] if i + 1 < len(letters) else None
        if not _is_vowel(ch, nxt):
            values.append(PYTHAGOREAN[ch])
    return values


def _all_letter_values(name: str) -> List[int]:
    return [PYTHAGOREAN[ch] for ch in _letters(name)]


# ---------------------------------------------------------------------------
# Data classes for computed results
# ---------------------------------------------------------------------------

@dataclass
class NumberResult:
    number_type: str
    raw_value: int
    reduced_value: int
    is_master_number: bool
    reduction_path: List[int]
    archetype: Optional[str] = None
    theme: Optional[str] = None

    def __post_init__(self) -> None:
        arc = ARCHETYPES.get(self.reduced_value)
        if arc and self.archetype is None:
            self.archetype, self.theme = arc


@dataclass
class PersonalYearEntry:
    """A single year in a personal year cycle."""
    year: int
    reduced_value: int
    is_master_number: bool
    archetype: Optional[str] = None
    theme: Optional[str] = None

    def __post_init__(self) -> None:
        arc = ARCHETYPES.get(self.reduced_value)
        if arc and self.archetype is None:
            self.archetype, self.theme = arc


@dataclass
class ChartResult:
    """Full computed numerology chart."""
    full_name: str
    birth_date: date
    system: str
    life_path: NumberResult
    expression: NumberResult
    soul_urge: NumberResult
    personality: NumberResult
    birthday: NumberResult
    personal_year: NumberResult
    challenges: List[NumberResult] = field(default_factory=list)
    # Next N years of personal year progressions (default: 3 years ahead)
    personal_year_cycle: List[PersonalYearEntry] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Serialise for storage in raw_chart JSONB column."""
        def _nr(r: NumberResult) -> dict:
            return {
                "number_type": r.number_type,
                "raw_value": r.raw_value,
                "reduced_value": r.reduced_value,
                "is_master_number": r.is_master_number,
                "reduction_path": r.reduction_path,
                "archetype": r.archetype,
                "theme": r.theme,
            }

        def _pye(e: PersonalYearEntry) -> dict:
            return {
                "year": e.year,
                "reduced_value": e.reduced_value,
                "is_master_number": e.is_master_number,
                "archetype": e.archetype,
                "theme": e.theme,
            }

        return {
            "full_name": self.full_name,
            "birth_date": self.birth_date.isoformat(),
            "system": self.system,
            "life_path": _nr(self.life_path),
            "expression": _nr(self.expression),
            "soul_urge": _nr(self.soul_urge),
            "personality": _nr(self.personality),
            "birthday": _nr(self.birthday),
            "personal_year": _nr(self.personal_year),
            "challenges": [_nr(c) for c in self.challenges],
            "personal_year_cycle": [_pye(e) for e in self.personal_year_cycle],
        }


# ---------------------------------------------------------------------------
# NumerologyEngine
# ---------------------------------------------------------------------------

class NumerologyEngine:
    """Stateless computation core.  Instantiate once; call compute() many times."""

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compute(
        self,
        full_name: str,
        birth_date: date,
        reference_year: Optional[int] = None,
        system: str = "pythagorean",
        include_challenges: bool = True,
        cycle_years: int = 3,
    ) -> ChartResult:
        """Compute a full numerology chart.

        Args:
            full_name:          Birth name exactly as registered.
            birth_date:         Date of birth.
            reference_year:     Year for Personal Year calculation (defaults to current year).
            system:             'pythagorean' only for now.
            include_challenges: Whether to compute Challenge Numbers.
            cycle_years:        How many future years to include in personal_year_cycle.
                                Set to 0 to omit. Default 3.

        Returns:
            ChartResult dataclass with all positions populated.
        """
        if system != "pythagorean":
            raise NotImplementedError(f"System '{system}' is not yet implemented. Use 'pythagorean'.")

        # Normalise name so DB stores canonical form and calculation is clean.
        canonical_name = self.normalize_name(full_name)

        ref_year = reference_year or date.today().year

        life_path     = self._life_path(birth_date)
        expression    = self._expression(canonical_name)
        soul_urge     = self._soul_urge(canonical_name)
        personality   = self._personality(canonical_name)
        birthday      = self._birthday(birth_date)
        personal_year = self._personal_year(birth_date, ref_year)
        challenges    = self._challenges(birth_date) if include_challenges else []
        py_cycle      = self._personal_year_cycle(birth_date, ref_year, cycle_years)

        return ChartResult(
            full_name=canonical_name,
            birth_date=birth_date,
            system=system,
            life_path=life_path,
            expression=expression,
            soul_urge=soul_urge,
            personality=personality,
            birthday=birthday,
            personal_year=personal_year,
            challenges=challenges,
            personal_year_cycle=py_cycle,
        )

    def normalize_name(self, name: str) -> str:
        """Return the normalised (ASCII-safe, uppercased, collapsed-whitespace)
        form of a name for storage and computation.
        """
        import unicodedata
        nfkd = unicodedata.normalize("NFKD", name)
        ascii_str = nfkd.encode("ascii", "ignore").decode("ascii")
        return " ".join(ascii_str.upper().split())

    # ------------------------------------------------------------------
    # Private calculation methods
    # ------------------------------------------------------------------

    def _make_result(self, number_type: str, raw: int) -> NumberResult:
        reduced, path = reduce(raw)
        return NumberResult(
            number_type=number_type,
            raw_value=raw,
            reduced_value=reduced,
            is_master_number=reduced in MASTER_NUMBERS,
            reduction_path=path,
        )

    def _life_path(self, birth_date: date) -> NumberResult:
        """Sum month + day + year (each reduced independently), then reduce total.

        This is the standard independent-reduction Pythagorean method.
        Month, day, and year are each reduced to a single digit or master number
        before being summed — this preserves master numbers that might otherwise
        be lost by summing all digits at once.
        """
        m_reduced, _ = reduce(birth_date.month)
        d_reduced, _ = reduce(birth_date.day)
        y_reduced, _ = reduce(sum(int(d) for d in str(birth_date.year)))
        total = m_reduced + d_reduced + y_reduced
        return self._make_result("life_path", total)

    def _expression(self, name: str) -> NumberResult:
        total = sum(_all_letter_values(name))
        return self._make_result("expression", total)

    def _soul_urge(self, name: str) -> NumberResult:
        total = sum(_vowel_values(name))
        return self._make_result("soul_urge", total)

    def _personality(self, name: str) -> NumberResult:
        total = sum(_consonant_values(name))
        return self._make_result("personality", total)

    def _birthday(self, birth_date: date) -> NumberResult:
        return self._make_result("birthday", birth_date.day)

    def _personal_year(self, birth_date: date, ref_year: int) -> NumberResult:
        m_reduced, _ = reduce(birth_date.month)
        d_reduced, _ = reduce(birth_date.day)
        y_reduced, _ = reduce(sum(int(d) for d in str(ref_year)))
        total = m_reduced + d_reduced + y_reduced
        return self._make_result("personal_year", total)

    def _personal_year_cycle(
        self,
        birth_date: date,
        ref_year: int,
        cycle_years: int,
    ) -> List[PersonalYearEntry]:
        """Pre-compute personal year values for the current + next N years.

        This gives GAIA's guidance layer a ready-made progression sequence
        without requiring additional API calls.  The current year (ref_year)
        is included as the first entry.

        Example output for Tesla, starting 2026 (cycle_years=3):
          [{year: 2026, reduced_value: 9, archetype: 'The Humanitarian'},
           {year: 2027, reduced_value: 1, archetype: 'The Pioneer'},
           {year: 2028, reduced_value: 11, archetype: 'The Illuminator'},
           {year: 2029, reduced_value: 3, archetype: 'The Creator'}]
        """
        if cycle_years <= 0:
            return []

        entries: List[PersonalYearEntry] = []
        for offset in range(cycle_years + 1):  # +1 includes current year
            yr = ref_year + offset
            result = self._personal_year(birth_date, yr)
            entries.append(
                PersonalYearEntry(
                    year=yr,
                    reduced_value=result.reduced_value,
                    is_master_number=result.is_master_number,
                )
            )
        return entries

    def _challenges(self, birth_date: date) -> List[NumberResult]:
        m, _ = reduce(birth_date.month)
        d, _ = reduce(birth_date.day)
        y, _ = reduce(sum(int(ch) for ch in str(birth_date.year)))

        c1_raw = abs(m - d)
        c2_raw = abs(d - y)
        c3_raw = abs(c1_raw - c2_raw)
        c4_raw = abs(m - y)

        return [
            self._make_result("challenge_1", c1_raw),
            self._make_result("challenge_2", c2_raw),
            self._make_result("challenge_3", c3_raw),
            self._make_result("challenge_main", c4_raw),
        ]
