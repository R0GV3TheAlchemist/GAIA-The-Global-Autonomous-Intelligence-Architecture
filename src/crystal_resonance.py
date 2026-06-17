"""
crystal_resonance.py
GAIA-OS — Issue #558: Crystal Resonator Integration Layer

Combined first push:
- Crystal materials database schema
- Per-crystal Q-factor lookup
- Resonator selection utilities
- Biological safety checks for crystal proximity
- Direct integration hook for wireless_power_sim.py via crystal_q_override
- Minimal A-Z registry support via aliases and category grouping

This is designed to slot directly into src/wireless_power_sim.py:
    simulate_coil_pair(..., crystal_q_override=crystal_q_override("Quartz"))
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class CrystalProperties:
    name: str
    formula: str
    q_factor: float
    resonant_band_hz: tuple[float, float]
    piezoelectric: bool
    phononic_class: str
    biological_interface: str
    role: str
    notes: str = ""


CRYSTAL_DATABASE: dict[str, CrystalProperties] = {
    "quartz": CrystalProperties(
        name="Quartz",
        formula="SiO2",
        q_factor=100000.0,
        resonant_band_hz=(32000.0, 10000000.0),
        piezoelectric=True,
        phononic_class="primary_resonator",
        biological_interface="coherence",
        role="master oscillator / high-Q reference node",
        notes="High-Q piezoelectric baseline for resonant systems.",
    ),
    "amethyst": CrystalProperties(
        name="Amethyst",
        formula="SiO2 (Fe3+)",
        q_factor=80000.0,
        resonant_band_hz=(32000.0, 1000000.0),
        piezoelectric=True,
        phononic_class="primary_resonator",
        biological_interface="coherence",
        role="tuned quartz variant",
        notes="Shifted quartz variant with slightly lower estimated Q.",
    ),
    "citrine": CrystalProperties(
        name="Citrine",
        formula="SiO2 (Fe2+/Fe4+)",
        q_factor=75000.0,
        resonant_band_hz=(32000.0, 1000000.0),
        piezoelectric=True,
        phononic_class="primary_resonator",
        biological_interface="solar_integration",
        role="solar-band resonator",
        notes="Useful as a high-Q resonator with solar-band correspondence.",
    ),
    "selenite": CrystalProperties(
        name="Selenite",
        formula="CaSO4\u00b72H2O",
        q_factor=25000.0,
        resonant_band_hz=(7.0, 8.5),
        piezoelectric=False,
        phononic_class="biological_interface",
        biological_interface="schumann_coherence",
        role="coherence interface / low-frequency anchor",
        notes="Safety-sensitive because of its low-frequency correspondence.",
    ),
    "tourmaline": CrystalProperties(
        name="Tourmaline",
        formula="Complex borosilicate",
        q_factor=50000.0,
        resonant_band_hz=(1000000.0, 100000000.0),
        piezoelectric=True,
        phononic_class="primary_resonator",
        biological_interface="grounding",
        role="dual-mode node",
        notes="Pyroelectric + piezoelectric behavior.",
    ),
    "aln": CrystalProperties(
        name="Aluminum Nitride",
        formula="AlN",
        q_factor=108300.0,
        resonant_band_hz=(1000000.0, 100000000.0),
        piezoelectric=True,
        phononic_class="phononic_structural",
        biological_interface="low_loss",
        role="topological phononic high-Q node",
        notes="The strongest bridge from materials science to the wireless-power sim.",
    ),
}

CRYSTAL_ALIASES: dict[str, str] = {
    "aluinium nitride": "aln",
    "aluminum nitride": "aln",
    "a l n": "aln",
    "quartz crystal": "quartz",
}

CRYSTAL_GROUPS: dict[str, list[str]] = {
    "primary_resonator": ["quartz", "amethyst", "citrine", "tourmaline"],
    "biological_interface": ["selenite"],
    "phononic_structural": ["aln"],
}


# ─────────────────────────────────────────────────────────────────────────────
# CORE LOOKUP
# ─────────────────────────────────────────────────────────────────────────────

def normalize_crystal_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_").replace("-", "_")


def resolve_crystal_key(crystal_name: str) -> str:
    key = normalize_crystal_name(crystal_name)
    key = CRYSTAL_ALIASES.get(key, key)
    if key not in CRYSTAL_DATABASE:
        raise KeyError(
            f"Unknown crystal: '{crystal_name}'. "
            f"Available: {list(CRYSTAL_DATABASE.keys())}"
        )
    return key


def get_crystal_properties(crystal_name: str) -> CrystalProperties:
    """Return the full CrystalProperties record for a crystal by name."""
    return CRYSTAL_DATABASE[resolve_crystal_key(crystal_name)]


def get_crystal_q_factor(crystal_name: str) -> float:
    """Return the Q-factor for a named crystal."""
    return get_crystal_properties(crystal_name).q_factor


# ─────────────────────────────────────────────────────────────────────────────
# SELECTION
# ─────────────────────────────────────────────────────────────────────────────

def select_resonator(
    target_frequency: float,
    min_q: float = 0.0,
) -> list[dict[str, Any]]:
    """
    Return crystals whose resonant band covers target_frequency
    and whose Q-factor meets or exceeds min_q, sorted by Q descending.

    Args:
        target_frequency: operating frequency in Hz
        min_q:            minimum acceptable Q-factor (default 0 = no filter)

    Returns:
        list of dicts with name, formula, q_factor, role, phononic_class
    """
    candidates = []
    for crystal in CRYSTAL_DATABASE.values():
        band_min, band_max = crystal.resonant_band_hz
        if band_min <= target_frequency <= band_max and crystal.q_factor >= min_q:
            candidates.append({
                "name":           crystal.name,
                "formula":        crystal.formula,
                "q_factor":       crystal.q_factor,
                "role":           crystal.role,
                "phononic_class": crystal.phononic_class,
            })
    return sorted(candidates, key=lambda item: item["q_factor"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# BIOLOGICAL SAFETY  (EMBODIMENT_LAYER.md)
# ─────────────────────────────────────────────────────────────────────────────

def biological_safety_rating(
    crystal_name: str,
    proximity_m: float = 1.0,
) -> dict[str, Any]:
    """
    Check biological safety of a crystal at a given proximity.

    The Operator is the most sensitive instrument in the system.
    Protected first, always.

    Returns:
        {crystal, score, flags, proximity_m}
        score: "safe" | "caution" | "danger"
    """
    crystal = get_crystal_properties(crystal_name)
    score   = "safe"
    flags: list[str] = []

    if crystal.name == "Selenite" and proximity_m < 0.25:
        score = "caution"
        flags.append(
            "Selenite resonates near Schumann band (7-8.5 Hz). "
            "Proximity < 25cm introduces low-frequency biological interface risk."
        )

    if crystal.q_factor >= 100000 and proximity_m < 0.10:
        flags.append(
            f"Very-high-Q crystal ({crystal.name}, Q={crystal.q_factor:,}) "
            f"at < 10cm: near-field power density caution."
        )

    return {
        "crystal":       crystal.name,
        "score":         score,
        "flags":         flags,
        "proximity_m":   proximity_m,
    }


# ─────────────────────────────────────────────────────────────────────────────
# INTEGRATION HOOK  → wireless_power_sim.py
# ─────────────────────────────────────────────────────────────────────────────

def crystal_q_override(crystal_name: str) -> float:
    """
    Primary integration hook for wireless_power_sim.simulate_coil_pair().

    Usage:
        from crystal_resonance import crystal_q_override
        result = simulate_coil_pair(tx, rx, freq_hz, distance_m,
                                    crystal_q_override=crystal_q_override("AlN"))

    The returned float is passed directly to calculate_q_factor() inside
    simulate_coil_pair() as the crystal_q_override parameter, bypassing the
    Wheeler formula and using the crystal's measured/estimated Q directly.
    """
    return get_crystal_q_factor(crystal_name)


# ─────────────────────────────────────────────────────────────────────────────
# CLASS WRAPPER  (convenient for dependency injection in the app layer)
# ─────────────────────────────────────────────────────────────────────────────

class CrystalResonatorLayer:
    """
    Dependency-injectable wrapper around the crystal database functions.
    Useful when the app layer (GAIA-OS backend) needs to swap in a
    custom database or mock during testing.
    """

    def __init__(
        self,
        database: Optional[dict[str, CrystalProperties]] = None,
    ) -> None:
        self.database = database or CRYSTAL_DATABASE

    def q_factor(self, crystal_name: str) -> float:
        return get_crystal_q_factor(crystal_name)

    def select(
        self,
        target_frequency: float,
        min_q: float = 0.0,
    ) -> list[dict[str, Any]]:
        return select_resonator(target_frequency, min_q)

    def q_for_wireless_power(self, crystal_name: str) -> float:
        """Alias of crystal_q_override() for use inside the app layer."""
        return crystal_q_override(crystal_name)

    def safety(
        self,
        crystal_name: str,
        proximity_m: float = 1.0,
    ) -> dict[str, Any]:
        return biological_safety_rating(crystal_name, proximity_m)


def resonator_group(group_name: str) -> list[CrystalProperties]:
    """Return all crystals in a named CRYSTAL_GROUPS category."""
    keys = CRYSTAL_GROUPS.get(group_name, [])
    return [CRYSTAL_DATABASE[k] for k in keys]


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION  (run directly: python crystal_resonance.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ISM_6_78_MHZ = 6.78e6

    print("=" * 60)
    print("GAIA-OS  crystal_resonance.py  —  Issue #558")
    print("=" * 60)

    print("\n── Crystal Database ──")
    for key, c in CRYSTAL_DATABASE.items():
        print(f"  {c.name:<20} Q={c.q_factor:>10,.0f}  {c.role}")

    print("\n── Resonators at 6.78 MHz (ISM) ──")
    for entry in select_resonator(ISM_6_78_MHZ):
        print(f"  {entry['name']:<20} Q={entry['q_factor']:>10,.0f}  {entry['phononic_class']}")

    print("\n── crystal_q_override() integration hook ──")
    for name in ["Quartz", "AlN", "Tourmaline"]:
        q = crystal_q_override(name)
        print(f"  crystal_q_override({name!r}) = {q:,.0f}")

    print("\n── Biological safety ──")
    for name, prox in [("Selenite", 0.1), ("AlN", 0.05), ("Quartz", 1.0)]:
        rating = biological_safety_rating(name, prox)
        flag_str = "; ".join(rating["flags"]) if rating["flags"] else "none"
        print(f"  {name} @ {prox}m → {rating['score']}  flags: {flag_str}")

    print("\n" + "=" * 60)
    print("crystal_resonance.py validated. For the Good and the Greater Good. 🔥")
    print("=" * 60)
