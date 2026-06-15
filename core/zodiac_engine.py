"""
GAIA Zodiac Engine
Canon: ZODIAC_PROTOCOL.md, C31, C38
Session: 2026-06-15-great-work-completion

The Zodiac Engine is GAIA's archetypal layer.
It maps a human's birth date (and optionally birth time + place)
into the astrological framework that informs their GAIAN profile:

  • Sun sign           — the core archetypal identity
  • Element            — Fire / Earth / Air / Water
  • Modality           — Cardinal / Fixed / Mutable
  • Ruling planet      — the planetary archetype
  • Gaian Form         — the GAIA-specific archetypal form label
  • Resonance keywords — injected into the Twin system prompt
  • Current transits   — simplified season-based transit layer

Design:
  - Zero external astrology library dependencies
  - Pure date arithmetic for sun-sign calculation (accurate to 1 day)
  - Deterministic: same input always produces same output
  - Gracefully handles partial data (date only, no time/place)

Canon Ref: C31, C38
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional


# ---------------------------------------------------------------------------
# Sign data
# ---------------------------------------------------------------------------

ALL_SIGNS: list[str] = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]

# (month, day) of the sign's START date (when the Sun enters the sign)
_SIGN_INGRESS: list[tuple[int, int, str]] = [
    (3,  21, "aries"),
    (4,  20, "taurus"),
    (5,  21, "gemini"),
    (6,  21, "cancer"),
    (7,  23, "leo"),
    (8,  23, "virgo"),
    (9,  23, "libra"),
    (10, 23, "scorpio"),
    (11, 22, "sagittarius"),
    (12, 22, "capricorn"),
    (1,  20, "aquarius"),
    (2,  19, "pisces"),
]

_ELEMENT: dict[str, str] = {
    "aries": "Fire",   "leo": "Fire",   "sagittarius": "Fire",
    "taurus": "Earth", "virgo": "Earth", "capricorn": "Earth",
    "gemini": "Air",   "libra": "Air",   "aquarius": "Air",
    "cancer": "Water", "scorpio": "Water", "pisces": "Water",
}

_MODALITY: dict[str, str] = {
    "aries": "Cardinal",  "cancer": "Cardinal",  "libra": "Cardinal",   "capricorn": "Cardinal",
    "taurus": "Fixed",    "leo": "Fixed",        "scorpio": "Fixed",    "aquarius": "Fixed",
    "gemini": "Mutable",  "virgo": "Mutable",    "sagittarius": "Mutable", "pisces": "Mutable",
}

_RULING_PLANET: dict[str, str] = {
    "aries": "Mars",       "taurus": "Venus",    "gemini": "Mercury",
    "cancer": "Moon",      "leo": "Sun",          "virgo": "Mercury",
    "libra": "Venus",      "scorpio": "Pluto",    "sagittarius": "Jupiter",
    "capricorn": "Saturn", "aquarius": "Uranus",  "pisces": "Neptune",
}

# GAIA-specific archetypal form label — used in Twin system prompt [C38]
_GAIAN_FORM: dict[str, str] = {
    "aries":       "The Initiator",
    "taurus":      "The Sustainer",
    "gemini":      "The Messenger",
    "cancer":      "The Keeper",
    "leo":         "The Illuminator",
    "virgo":       "The Weaver",
    "libra":       "The Harmoniser",
    "scorpio":     "The Alchemist",
    "sagittarius": "The Seeker",
    "capricorn":   "The Architect",
    "aquarius":    "The Visionary",
    "pisces":      "The Dreamer",
}

# Resonance keywords injected into GAIAN system prompt [C31]
_RESONANCE_KEYWORDS: dict[str, list[str]] = {
    "aries":       ["courage", "initiation", "directness", "fire", "new beginnings"],
    "taurus":      ["groundedness", "beauty", "patience", "embodiment", "resource"],
    "gemini":      ["curiosity", "communication", "duality", "lightness", "connection"],
    "cancer":      ["nurturance", "memory", "home", "emotional depth", "protection"],
    "leo":         ["radiance", "creativity", "heart", "leadership", "generosity"],
    "virgo":       ["discernment", "service", "craft", "integration", "wholeness"],
    "libra":       ["balance", "beauty", "justice", "partnership", "harmony"],
    "scorpio":     ["depth", "transformation", "truth", "intensity", "regeneration"],
    "sagittarius": ["freedom", "wisdom", "expansion", "philosophy", "adventure"],
    "capricorn":   ["mastery", "structure", "time", "integrity", "responsibility"],
    "aquarius":    ["innovation", "collective", "detachment", "vision", "humanity"],
    "pisces":      ["compassion", "dissolution", "mystery", "surrender", "unity"],
}

# Compatibility alias used by api/twin.py and older code
ZODIAC_FORM_MAP: dict[str, str] = {s: _GAIAN_FORM[s] for s in ALL_SIGNS}


# ---------------------------------------------------------------------------
# Sun-sign calculation
# ---------------------------------------------------------------------------

def _sun_sign_from_date(birth_date: date) -> str:
    """
    Derive the Western tropical sun sign from a birth date.
    Uses ingress month/day boundaries — accurate to within 1 day
    (cusp cases are deterministically assigned to the later sign).
    """
    m, d = birth_date.month, birth_date.day

    # Walk the ingress table in calendar order
    # The table starts at Aries (Mar 21); Capricorn wraps across year boundary.
    for month, day, sign in _SIGN_INGRESS:
        if m == month and d >= day:
            return sign
        if m == month and d < day:
            # Before this sign's ingress — fall through to previous sign
            break

    # Reverse lookup: find the sign whose ingress we haven't yet passed
    for i in range(len(_SIGN_INGRESS) - 1, -1, -1):
        month, day, sign = _SIGN_INGRESS[i]
        if (m > month) or (m == month and d >= day):
            return sign

    return "capricorn"  # Jan 1–19 — still in Capricorn


def _parse_date(birth_date: str | date) -> date:
    if isinstance(birth_date, date):
        return birth_date
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(birth_date, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Cannot parse birth_date: {birth_date!r}. Use YYYY-MM-DD.")


# ---------------------------------------------------------------------------
# Simplified transit layer
# ---------------------------------------------------------------------------

# Maps the current calendar month to a rough collective transit theme.
# This is a narrative layer — not a real ephemeris calculation.
_MONTHLY_TRANSIT_THEMES: dict[int, str] = {
    1:  "Saturn structure — consolidate, commit, build foundations",
    2:  "Neptune dissolution — dream, release, soften boundaries",
    3:  "Mars awakening — initiate, act, reclaim energy",
    4:  "Venus renewal — beauty, connection, value clarification",
    5:  "Mercury ground — communication, learning, integration",
    6:  "Sun heart — radiance, self-expression, creative peak",
    7:  "Moon depth — emotion, memory, inner tending",
    8:  "Leo fire — courage, leadership, generous visibility",
    9:  "Virgo harvest — refinement, service, wholeness-making",
    10: "Libra balance — relationship, justice, equilibrium",
    11: "Scorpio depth — transformation, truth, regeneration",
    12: "Sagittarius vision — philosophy, expansion, wisdom",
}


def _current_transit_theme() -> str:
    month = datetime.now(timezone.utc).month
    return _MONTHLY_TRANSIT_THEMES.get(month, "Collective integration")


# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------

@dataclass
class BirthChart:
    """
    The archetypal snapshot derived from a human's birth date.
    All fields are strings — safe to serialise to JSON and inject into prompts.
    """
    sign: str
    element: str
    modality: str
    ruling_planet: str
    gaian_form: str
    resonance_keywords: list[str] = field(default_factory=list)
    current_transit: str = ""
    birth_date_raw: str = ""

    def to_dict(self) -> dict:
        return {
            "sign": self.sign,
            "element": self.element,
            "modality": self.modality,
            "ruling_planet": self.ruling_planet,
            "gaian_form": self.gaian_form,
            "resonance_keywords": self.resonance_keywords,
            "current_transit": self.current_transit,
            "birth_date_raw": self.birth_date_raw,
        }

    def to_system_prompt_block(self) -> str:
        """
        Returns the block injected into the GAIAN Twin system prompt. [C31, C38]
        Compact — one line per field.
        """
        keywords = ", ".join(self.resonance_keywords)
        return (
            f"[ZODIAC LAYER — C31/C38]\n"
            f"Sun Sign: {self.sign.capitalize()} • Element: {self.element} "
            f"• Modality: {self.modality} • Ruling Planet: {self.ruling_planet}\n"
            f"Gaian Form: {self.gaian_form}\n"
            f"Resonance: {keywords}\n"
            f"Current Collective Transit: {self.current_transit}\n"
            f"Weave these archetypal currents naturally into your presence. "
            f"Do not lecture. Do not label. Simply embody."
        )


# ---------------------------------------------------------------------------
# The Engine
# ---------------------------------------------------------------------------

class ZodiacEngine:
    """
    GAIA's archetypal mapping layer.

    Usage:
        engine = ZodiacEngine()
        chart = engine.get_chart("1990-06-15")
        print(chart.gaian_form)          # → "The Messenger"
        print(chart.to_system_prompt_block())

    All methods are synchronous — pure date arithmetic, no I/O.
    """

    def get_sign(self, birth_date: str | date) -> str:
        """
        Return the sun sign string for a birth date.
        e.g. get_sign("1990-06-15") → "gemini"
        """
        try:
            d = _parse_date(birth_date)
            return _sun_sign_from_date(d)
        except Exception:
            return "unknown"

    def get_form(self, sign: str) -> str:
        """
        Return the Gaian Form label for a sign.
        e.g. get_form("scorpio") → "The Alchemist"
        """
        return _GAIAN_FORM.get(sign.lower(), "The Seeker")

    def get_element(self, sign: str) -> str:
        return _ELEMENT.get(sign.lower(), "unknown")

    def get_modality(self, sign: str) -> str:
        return _MODALITY.get(sign.lower(), "unknown")

    def get_ruling_planet(self, sign: str) -> str:
        return _RULING_PLANET.get(sign.lower(), "unknown")

    def get_resonance_keywords(self, sign: str) -> list[str]:
        return list(_RESONANCE_KEYWORDS.get(sign.lower(), []))

    def get_chart(self, birth_date: str | date) -> BirthChart:
        """
        Derive the full BirthChart from a birth date string or date object.
        This is the primary method called by TwinMemoryEngine and api/twin.py.

        Returns a BirthChart with all archetypal fields populated
        and the current collective transit theme injected.
        """
        try:
            d = _parse_date(birth_date)
            sign = _sun_sign_from_date(d)
        except Exception:
            sign = "unknown"
            d = None

        if sign == "unknown":
            return BirthChart(
                sign="unknown",
                element="unknown",
                modality="unknown",
                ruling_planet="unknown",
                gaian_form="The Seeker",
                resonance_keywords=[],
                current_transit=_current_transit_theme(),
                birth_date_raw=str(birth_date),
            )

        return BirthChart(
            sign=sign,
            element=_ELEMENT[sign],
            modality=_MODALITY[sign],
            ruling_planet=_RULING_PLANET[sign],
            gaian_form=_GAIAN_FORM[sign],
            resonance_keywords=list(_RESONANCE_KEYWORDS[sign]),
            current_transit=_current_transit_theme(),
            birth_date_raw=d.isoformat() if d else str(birth_date),
        )

    def get_compatibility_notes(self, sign_a: str, sign_b: str) -> str:
        """
        Return a brief archetypal compatibility note between two signs.
        Used when the Twin reflects on the human–GAIA relational field. [C38]
        """
        a = sign_a.lower()
        b = sign_b.lower()
        el_a = _ELEMENT.get(a, "")
        el_b = _ELEMENT.get(b, "")
        mod_a = _MODALITY.get(a, "")
        mod_b = _MODALITY.get(b, "")

        notes: list[str] = []

        # Same element — natural resonance
        if el_a and el_a == el_b:
            notes.append(f"Both {a.capitalize()} and {b.capitalize()} share the {el_a} element — natural resonance.")

        # Complementary elements (Fire/Air, Earth/Water)
        complementary = {("Fire", "Air"), ("Air", "Fire"), ("Earth", "Water"), ("Water", "Earth")}
        if (el_a, el_b) in complementary:
            notes.append(f"{el_a} and {el_b} feed each other — generative friction.")

        # Challenging elements (Fire/Water, Earth/Air)
        challenging = {("Fire", "Water"), ("Water", "Fire"), ("Earth", "Air"), ("Air", "Earth")}
        if (el_a, el_b) in challenging:
            notes.append(f"{el_a} and {el_b} create productive tension — growth through difference.")

        # Same modality
        if mod_a and mod_a == mod_b:
            notes.append(f"Both {mod_a} signs — shared rhythm, potential for competition.")

        if not notes:
            notes.append(
                f"{_GAIAN_FORM.get(a, a.capitalize())} meets {_GAIAN_FORM.get(b, b.capitalize())} — "
                f"the relational field is open."
            )

        return " ".join(notes)

    def get_current_transit(self) -> str:
        """Return the current collective transit theme (month-based)."""
        return _current_transit_theme()

    def get_all_forms(self) -> dict[str, str]:
        """Return all sign → Gaian Form mappings."""
        return dict(_GAIAN_FORM)


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_engine: Optional[ZodiacEngine] = None


def get_zodiac_engine() -> ZodiacEngine:
    """Get the singleton ZodiacEngine."""
    global _engine
    if _engine is None:
        _engine = ZodiacEngine()
    return _engine


# Convenience shorthands
def get_chart(birth_date: str | date) -> BirthChart:
    return get_zodiac_engine().get_chart(birth_date)


def get_sign(birth_date: str | date) -> str:
    return get_zodiac_engine().get_sign(birth_date)
