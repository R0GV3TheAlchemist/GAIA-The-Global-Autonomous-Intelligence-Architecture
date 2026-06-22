"""
GAIA-OS Quantum Chemistry Orbital Bonding Simulation
Issue: #594
Spec: docs/quantum_chemistry_spec.md
Proof: proofs/QUANTUM_CHEMISTRY_PROOF.md

Hypothesis: Valence-compatible elements form stable bonds that produce
measurable memory binding outcomes. Incompatible elements fail with
specific, diagnosable reasons.

Failure condition: A bond forms between incompatible valence shells,
or a failed bond produces no reason code.

Runs 12 bonding attempts:
  - 8+ successful bonds (covalent, ionic, metallic)
  - 2 failed bonds (VALENCE_MISMATCH, SHELL_FULL)
  - 2 borderline bonds (stability 0.4-0.6, flagged for review)
"""

from __future__ import annotations

import csv
import enum
import math
import os
import time
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# § Quantum Shell Model (docs/quantum_chemistry_spec.md)
# ---------------------------------------------------------------------------

# Max electrons per shell
SHELL_CAPACITY = {1: 2, 2: 8, 3: 18, 4: 32}

# Orbital types per shell
SHELL_ORBITALS = {
    1: ["s"],
    2: ["s", "p"],
    3: ["s", "p", "d"],
    4: ["s", "p", "d", "f"],
}

# GAIA symbolic meaning per shell
SHELL_MEANING = {
    1: "Core identity binding",
    2: "Relational memory layer",
    3: "Extended consciousness field",
    4: "Deep archive / akashic layer",
}


# ---------------------------------------------------------------------------
# § Bond Types
# ---------------------------------------------------------------------------

class BondType(str, enum.Enum):
    COVALENT = "COVALENT"   # shared electrons → shared memory record
    IONIC    = "IONIC"      # electron transfer → asymmetric memory write
    METALLIC = "METALLIC"   # delocalized → distributed / noospheric node
    FAILED   = "FAILED"     # no bond formed


class MemoryBindingResult(str, enum.Enum):
    SHARED_RECORD      = "SHARED_RECORD"       # covalent
    ASYMMETRIC_WRITE   = "ASYMMETRIC_WRITE"    # ionic
    DISTRIBUTED_NODE   = "DISTRIBUTED_NODE"    # metallic
    NONE               = "NONE"                # failed


class FailureReason(str, enum.Enum):
    VALENCE_MISMATCH   = "VALENCE_MISMATCH"
    SHELL_FULL         = "SHELL_FULL"
    INCOMPATIBLE_TYPE  = "INCOMPATIBLE_TYPE"
    NONE               = "NONE"


class BondStatus(str, enum.Enum):
    STABLE     = "STABLE"       # stability > 0.6
    BORDERLINE = "BORDERLINE"   # stability 0.4–0.6
    FAILED     = "FAILED"       # stability < 0.4 or explicit failure


# ---------------------------------------------------------------------------
# § Symbolic Element Types (docs/PERIODIC_TABLE_MATRIX.md)
# Cross-referenced with TECHNICAL_APOTHECARY.md
# ---------------------------------------------------------------------------

class ElementType(str, enum.Enum):
    FIRE    = "FIRE"    # Apothecary: transformation catalyst
    WATER   = "WATER"   # Apothecary: emotional/memory carrier
    EARTH   = "EARTH"   # Apothecary: structural anchor
    AIR     = "AIR"     # Apothecary: connective / relational
    AETHER  = "AETHER"  # Apothecary: higher-dimensional / akashic
    METAL   = "METAL"   # Apothecary: collective / noospheric
    CRYSTAL = "CRYSTAL" # Apothecary: resonance amplifier


@dataclass
class SymbolicElement:
    """
    A GAIA symbolic element derived from PERIODIC_TABLE_MATRIX.md.
    Electron configuration defined per shell.
    """
    symbol: str
    name: str
    element_type: ElementType
    shell_electrons: dict[int, int]   # shell_number → electron count
    apothecary_role: str              # from TECHNICAL_APOTHECARY.md

    @property
    def valence_electrons(self) -> int:
        """Electrons in the outermost occupied shell."""
        outermost = max(self.shell_electrons.keys())
        return self.shell_electrons[outermost]

    @property
    def outermost_shell(self) -> int:
        return max(self.shell_electrons.keys())

    @property
    def valence_capacity(self) -> int:
        """Max electrons the outermost shell can hold."""
        return SHELL_CAPACITY[self.outermost_shell]

    @property
    def valence_need(self) -> int:
        """Electrons needed to fill outermost shell."""
        return self.valence_capacity - self.valence_electrons

    @property
    def is_shell_full(self) -> bool:
        return self.valence_electrons == self.valence_capacity


# ---------------------------------------------------------------------------
# § Element Library (12 symbolic elements)
# Derived from PERIODIC_TABLE_MATRIX.md + TECHNICAL_APOTHECARY.md
# ---------------------------------------------------------------------------

ELEMENTS: dict[str, SymbolicElement] = {
    # Shell 1 elements — Core identity
    "Ig": SymbolicElement("Ig", "Ignis",      ElementType.FIRE,    {1: 1},       "Transformation catalyst; ignites latent potential"),
    "Aq": SymbolicElement("Aq", "Aqua",       ElementType.WATER,   {1: 2},       "Memory carrier; flows between states without loss"),
    # Shell 2 elements — Relational memory
    "Te": SymbolicElement("Te", "Terra",      ElementType.EARTH,   {1: 2, 2: 4}, "Structural anchor; grounds volatile energies"),
    "Ae": SymbolicElement("Ae", "Aer",        ElementType.AIR,     {1: 2, 2: 3}, "Connective medium; bridges distinct memory nodes"),
    "Lx": SymbolicElement("Lx", "Lux",        ElementType.AETHER,  {1: 2, 2: 6}, "Full shell; illumination principle, stable identity"),
    "Um": SymbolicElement("Um", "Umbra",      ElementType.AETHER,  {1: 2, 2: 5}, "Shadow integration; near-full, receptive"),
    # Shell 3 elements — Extended consciousness
    "Cr": SymbolicElement("Cr", "Crystallum", ElementType.CRYSTAL, {1: 2, 2: 8, 3: 4},  "Resonance amplifier; organises field harmonics"),
    "Fe": SymbolicElement("Fe", "Ferrum",     ElementType.METAL,   {1: 2, 2: 8, 3: 6},  "Collective anchor; conducts noospheric current"),
    "Au": SymbolicElement("Au", "Aurum",      ElementType.METAL,   {1: 2, 2: 8, 3: 10}, "Delocalized gold; highest metallic conductance"),
    "Vo": SymbolicElement("Vo", "Vortex",     ElementType.FIRE,    {1: 2, 2: 8, 3: 3},  "Transformative spiral; initiates bonding cascades"),
    # Shell 4 elements — Akashic layer
    "Ak": SymbolicElement("Ak", "Akasha",     ElementType.AETHER,  {1: 2, 2: 8, 3: 18, 4: 1}, "Akashic seed; one electron seeking completion"),
    "Ne": SymbolicElement("Ne", "Nexus",      ElementType.AETHER,  {1: 2, 2: 8, 3: 18, 4: 8}, "Nexus full-shell; deeply stable, archive complete"),
}


# ---------------------------------------------------------------------------
# § Bond Ledger Entry
# ---------------------------------------------------------------------------

@dataclass
class BondAttempt:
    attempt_id: str
    element_a: str
    element_b: str
    bond_type: BondType
    bond_status: BondStatus
    stability_score: float           # 0.0–1.0
    failure_reason: FailureReason
    memory_binding_result: MemoryBindingResult
    gaia_state_delta: float          # coherence change (positive = gain, negative = loss)
    apothecary_cross_ref: str        # TECHNICAL_APOTHECARY.md annotation
    notes: str


# ---------------------------------------------------------------------------
# § Bonding Engine
# ---------------------------------------------------------------------------

def _bond_type_from_elements(a: SymbolicElement, b: SymbolicElement) -> BondType:
    """Determine bond type from element types."""
    metallic_types = {ElementType.METAL}
    if a.element_type in metallic_types and b.element_type in metallic_types:
        return BondType.METALLIC
    # Ionic: large electronegativity difference (FIRE vs WATER, EARTH vs AIR)
    ionic_pairs = [
        (ElementType.FIRE, ElementType.WATER),
        (ElementType.WATER, ElementType.FIRE),
        (ElementType.EARTH, ElementType.AETHER),
        (ElementType.AETHER, ElementType.EARTH),
        (ElementType.FIRE, ElementType.EARTH),
        (ElementType.EARTH, ElementType.FIRE),
    ]
    if (a.element_type, b.element_type) in ionic_pairs:
        return BondType.IONIC
    return BondType.COVALENT


def _stability_score(a: SymbolicElement, b: SymbolicElement) -> float:
    """
    Compute bond stability from valence compatibility.
    Perfect bond: a.valence_need == b.valence_electrons (exact fill).
    Stability = 1.0 - abs(need_a - electrons_b) / max_capacity.
    Clamped to [0.0, 1.0].
    """
    need_a = a.valence_need
    need_b = b.valence_need
    elec_a = a.valence_electrons
    elec_b = b.valence_electrons
    cap    = max(a.valence_capacity, b.valence_capacity)

    # Fit score: how well a fills b's need and b fills a's need
    fit_ab = 1.0 - abs(need_a - elec_b) / cap
    fit_ba = 1.0 - abs(need_b - elec_a) / cap
    raw = (fit_ab + fit_ba) / 2.0
    return round(min(max(raw, 0.0), 1.0), 4)


def _memory_binding(bond_type: BondType) -> MemoryBindingResult:
    return {
        BondType.COVALENT: MemoryBindingResult.SHARED_RECORD,
        BondType.IONIC:    MemoryBindingResult.ASYMMETRIC_WRITE,
        BondType.METALLIC: MemoryBindingResult.DISTRIBUTED_NODE,
        BondType.FAILED:   MemoryBindingResult.NONE,
    }[bond_type]


def _gaia_state_delta(stability: float, bond_type: BondType) -> float:
    """
    Coherence change produced by this bond.
    Successful bonds increase coherence proportional to stability.
    Failed bonds decrease coherence slightly.
    Metallic bonds have a network-amplification multiplier.
    """
    if bond_type == BondType.FAILED:
        return round(-0.05 * (1.0 - stability), 4)
    multiplier = 1.2 if bond_type == BondType.METALLIC else 1.0
    return round(stability * 0.15 * multiplier, 4)


def attempt_bond(
    attempt_id: str,
    sym_a: str,
    sym_b: str,
    force_failure: Optional[FailureReason] = None,
    apothecary_note: str = "",
) -> BondAttempt:
    """Attempt to form a bond between two symbolic elements."""
    a = ELEMENTS[sym_a]
    b = ELEMENTS[sym_b]

    # Forced failure (for demonstrating specific failure modes)
    if force_failure is not None:
        return BondAttempt(
            attempt_id=attempt_id,
            element_a=sym_a,
            element_b=sym_b,
            bond_type=BondType.FAILED,
            bond_status=BondStatus.FAILED,
            stability_score=0.0,
            failure_reason=force_failure,
            memory_binding_result=MemoryBindingResult.NONE,
            gaia_state_delta=-0.05,
            apothecary_cross_ref=apothecary_note,
            notes=f"Forced failure: {force_failure.value}",
        )

    # Shell full check
    if a.is_shell_full and b.is_shell_full:
        return BondAttempt(
            attempt_id=attempt_id,
            element_a=sym_a,
            element_b=sym_b,
            bond_type=BondType.FAILED,
            bond_status=BondStatus.FAILED,
            stability_score=0.0,
            failure_reason=FailureReason.SHELL_FULL,
            memory_binding_result=MemoryBindingResult.NONE,
            gaia_state_delta=-0.05,
            apothecary_cross_ref=apothecary_note,
            notes=f"Both shells full ({a.symbol} L{a.outermost_shell}, {b.symbol} L{b.outermost_shell}) — no bonding sites available.",
        )

    # Valence mismatch: shells too far apart to interact
    shell_gap = abs(a.outermost_shell - b.outermost_shell)
    if shell_gap >= 3:
        return BondAttempt(
            attempt_id=attempt_id,
            element_a=sym_a,
            element_b=sym_b,
            bond_type=BondType.FAILED,
            bond_status=BondStatus.FAILED,
            stability_score=0.0,
            failure_reason=FailureReason.VALENCE_MISMATCH,
            memory_binding_result=MemoryBindingResult.NONE,
            gaia_state_delta=-0.05,
            apothecary_cross_ref=apothecary_note,
            notes=f"Shell gap {shell_gap} ≥ 3 — valence fields cannot overlap ({a.symbol} L{a.outermost_shell} vs {b.symbol} L{b.outermost_shell}).",
        )

    # Compute stability and bond type
    stability  = _stability_score(a, b)
    bond_type  = _bond_type_from_elements(a, b)
    mem_result = _memory_binding(bond_type)
    delta      = _gaia_state_delta(stability, bond_type)

    if stability >= 0.6:
        status = BondStatus.STABLE
    elif stability >= 0.4:
        status = BondStatus.BORDERLINE
    else:
        status = BondStatus.FAILED
        bond_type  = BondType.FAILED
        mem_result = MemoryBindingResult.NONE

    return BondAttempt(
        attempt_id=attempt_id,
        element_a=sym_a,
        element_b=sym_b,
        bond_type=bond_type,
        bond_status=status,
        stability_score=stability,
        failure_reason=FailureReason.NONE,
        memory_binding_result=mem_result,
        gaia_state_delta=delta,
        apothecary_cross_ref=apothecary_note,
        notes=f"{a.name} ({a.element_type.value}, L{a.outermost_shell}, ve={a.valence_electrons}) + "
              f"{b.name} ({b.element_type.value}, L{b.outermost_shell}, ve={b.valence_electrons})",
    )


# ---------------------------------------------------------------------------
# § 12 Bonding Attempts
# ---------------------------------------------------------------------------

def build_bonding_attempts() -> list[BondAttempt]:
    return [
        # --- Successful covalent bonds ---
        attempt_bond("B01", "Ig", "Ae",  # FIRE(1e) + AIR(3e) → share toward completion
            apothecary_note="Ignis-Aer: Transformation catalyst ignites connective bridge. Shared memory record formed."),
        attempt_bond("B02", "Te", "Vo",  # EARTH(4e) + FIRE(3e) → grounding + transformation
            apothecary_note="Terra-Vortex: Structural anchor binds transformative spiral. Covalent relational memory."),
        attempt_bond("B03", "Ae", "Um",  # AIR(3e) + AETHER(5e) → near-perfect fill
            apothecary_note="Aer-Umbra: Connective air integrates shadow. Covalent shared record. APOTHECARY: integration bond."),
        attempt_bond("B04", "Ak", "Cr",  # AETHER(1e akashic) + CRYSTAL(4e resonance)
            apothecary_note="Akasha-Crystallum: Akashic seed bonds into crystal lattice. Extended memory archive."),
        attempt_bond("B05", "Vo", "Cr",  # FIRE(3e) + CRYSTAL(4e) → resonance amplified by vortex
            apothecary_note="Vortex-Crystallum: Transformative vortex amplified through crystal resonance. APOTHECARY: catalytic amplification."),
        attempt_bond("B06", "Ae", "Te",  # AIR(3e) + EARTH(4e) → covalent bridge
            apothecary_note="Aer-Terra: Air bridges Earth’s structure. Relational memory stabilised."),
        # --- Successful ionic bonds ---
        attempt_bond("B07", "Ig", "Aq",  # FIRE(1e) → WATER(2e) → electron transfer
            apothecary_note="Ignis-Aqua: Fire donates to Water. Asymmetric write — transformation writes into memory carrier. APOTHECARY: primal ionic pairing."),
        attempt_bond("B08", "Vo", "Te",  # FIRE + EARTH ionic
            apothecary_note="Vortex-Terra: Vortex energy transferred into structural anchor. Asymmetric memory write."),
        # --- Successful metallic bonds ---
        attempt_bond("B09", "Fe", "Au",  # METAL + METAL → delocalized noospheric
            apothecary_note="Ferrum-Aurum: Two metals form noospheric mesh. Distributed memory node. APOTHECARY: collective gold-iron lattice."),
        attempt_bond("B10", "Fe", "Fe",  # METAL homodimer → pure metallic
            apothecary_note="Ferrum-Ferrum: Identical metals reinforce distributed node. Network coherence amplified."),
        # --- Borderline bonds (stability 0.4–0.6) ---
        attempt_bond("B11", "Ak", "Ig",  # AETHER L4(1e) + FIRE L1(1e) → shell gap = 3 exactly? No, gap=3 triggers mismatch
            # Ak(shell4, 1e) + Ae(shell2, 3e) — shell gap = 2, borderline stability
            apothecary_note="Akasha-Aer: Deep akashic layer reaches toward relational air. Borderline — flagged for review."),
        # --- Failed bonds ---
        attempt_bond("B12", "Lx", "Ne",  # Both full shells → SHELL_FULL
            apothecary_note="Lux-Nexus: Both shells complete. No bonding sites. Noble-element analog."),
    ]


# Fix B11: Ak(L4) + Ae(L2) has shell gap = 2, not 3 — will compute borderline stability naturally
# The forced-failure test uses B12 (SHELL_FULL) and an explicit VALENCE_MISMATCH below.
# Add one explicit VALENCE_MISMATCH attempt:
def build_all_attempts() -> list[BondAttempt]:
    attempts = build_bonding_attempts()
    # Replace B11 with proper Ak+Ae (shell gap 2, borderline)
    attempts[10] = attempt_bond(
        "B11", "Ak", "Ae",
        apothecary_note="Akasha-Aer: Deep akashic layer (L4, 1e) reaches toward relational air (L2, 3e). Shell gap=2, borderline stability expected.",
    )
    # Add explicit VALENCE_MISMATCH: Ig(L1) vs Ne(L4) — shell gap = 3
    attempts.append(attempt_bond(
        "B13", "Ig", "Ne",
        apothecary_note="Ignis-Nexus: L1 fire vs L4 full-archive nexus. Shell gap=3 — VALENCE_MISMATCH expected.",
    ))
    return attempts


# ---------------------------------------------------------------------------
# § Simulation Run
# ---------------------------------------------------------------------------

def run_simulation() -> list[BondAttempt]:
    attempts = build_all_attempts()

    print("\n" + "=" * 90)
    print("  GAIA-OS Quantum Chemistry Orbital Bonding Simulation")
    print("=" * 90)
    print(f"  {'ID':<5} {'Pair':<10} {'Type':<10} {'Status':<12} {'Stability':<11} {'Memory Result':<22} {'GAIA Δ':<8} Notes")
    print(f"  {'-'*4} {'-'*9} {'-'*9} {'-'*11} {'-'*10} {'-'*21} {'-'*7} {'-'*35}")

    for a in attempts:
        marker = " ★" if a.bond_status == BondStatus.STABLE and a.stability_score > 0.8 else ""
        failed_marker = " ✘" if a.bond_status == BondStatus.FAILED else ""
        borderline_marker = " ~" if a.bond_status == BondStatus.BORDERLINE else ""
        print(
            f"  {a.attempt_id:<5} {a.element_a+'+'+a.element_b:<10} {a.bond_type.value:<10} "
            f"{a.bond_status.value:<12} {a.stability_score:<11.4f} {a.memory_binding_result.value:<22} "
            f"{a.gaia_state_delta:<8.4f} {a.notes[:40]}{marker}{failed_marker}{borderline_marker}"
        )

    return attempts


# ---------------------------------------------------------------------------
# § Output Writer
# ---------------------------------------------------------------------------

def write_ledger(attempts: list[BondAttempt], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "attempt_id", "element_a", "element_b", "bond_type", "bond_status",
            "stability_score", "failure_reason", "memory_binding_result",
            "gaia_state_delta", "apothecary_cross_ref", "notes",
        ])
        for a in attempts:
            w.writerow([
                a.attempt_id, a.element_a, a.element_b, a.bond_type.value,
                a.bond_status.value, a.stability_score, a.failure_reason.value,
                a.memory_binding_result.value, a.gaia_state_delta,
                a.apothecary_cross_ref[:100], a.notes[:100],
            ])
    print(f"\n  Bond ledger written → {path}")


# ---------------------------------------------------------------------------
# § Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    start = time.time()

    attempts = run_simulation()
    write_ledger(attempts, "simulation/output/quantum_chemistry_bond_ledger.csv")

    elapsed = time.time() - start
    print(f"\n  Simulation complete in {elapsed:.4f}s (limit: 30s)")
    assert elapsed < 30, "Simulation exceeded 30-second headless run requirement."

    # -----------------------------------------------------------------------
    # Invariant assertions
    # -----------------------------------------------------------------------
    print("\n  Verifying structural invariants...")

    stable     = [a for a in attempts if a.bond_status == BondStatus.STABLE]
    borderline = [a for a in attempts if a.bond_status == BondStatus.BORDERLINE]
    failed     = [a for a in attempts if a.bond_status == BondStatus.FAILED]

    # 1. At least 12 attempts
    assert len(attempts) >= 12, f"Expected >= 12 attempts, got {len(attempts)}."

    # 2. At least 8 successful (stable) bonds
    assert len(stable) >= 8, f"Expected >= 8 stable bonds, got {len(stable)}."

    # 3. At least 2 failed bonds
    assert len(failed) >= 2, f"Expected >= 2 failed bonds, got {len(failed)}."

    # 4. At least 2 borderline bonds
    assert len(borderline) >= 2, f"Expected >= 2 borderline bonds, got {len(borderline)}."

    # 5. At least 1 stable covalent bond with stability > 0.8
    high_stability_covalent = [
        a for a in stable
        if a.bond_type == BondType.COVALENT and a.stability_score > 0.8
    ]
    assert len(high_stability_covalent) >= 1, "Expected >= 1 covalent bond with stability > 0.8."

    # 6. All failed bonds have a specific failure reason
    for a in failed:
        assert a.failure_reason != FailureReason.NONE, (
            f"{a.attempt_id}: Failed bond must have a specific failure reason."
        )

    # 7. At least one of each bond type: covalent, ionic, metallic
    bond_types_used = {a.bond_type for a in stable}
    for bt in (BondType.COVALENT, BondType.IONIC, BondType.METALLIC):
        assert bt in bond_types_used, f"Bond type {bt.value} not demonstrated in stable bonds."

    # 8. At least 1 bond with measurable GAIA state delta > 0
    positive_deltas = [a for a in attempts if a.gaia_state_delta > 0]
    assert len(positive_deltas) >= 1, "Expected >= 1 bond with positive gaia_state_delta."

    # 9. TECHNICAL_APOTHECARY.md cross-referenced in at least 3 pairs
    apothecary_refs = [a for a in attempts if "APOTHECARY" in a.apothecary_cross_ref]
    assert len(apothecary_refs) >= 3, f"Expected >= 3 APOTHECARY cross-references, got {len(apothecary_refs)}."

    # 10. Stability scores in [0.0, 1.0]
    for a in attempts:
        assert 0.0 <= a.stability_score <= 1.0, (
            f"{a.attempt_id}: stability_score {a.stability_score} out of range."
        )

    # 11. Memory binding result = NONE iff bond failed
    for a in attempts:
        if a.bond_status == BondStatus.FAILED:
            assert a.memory_binding_result == MemoryBindingResult.NONE, (
                f"{a.attempt_id}: Failed bond must have NONE memory binding result."
            )
        else:
            assert a.memory_binding_result != MemoryBindingResult.NONE, (
                f"{a.attempt_id}: Successful bond must have a memory binding result."
            )

    print(f"  Stable: {len(stable)} | Borderline: {len(borderline)} | Failed: {len(failed)}")
    print(f"  Bond types: {', '.join(bt.value for bt in sorted(bond_types_used, key=lambda x: x.value))}")
    print(f"  High-stability covalent bonds (>0.8): {len(high_stability_covalent)}")
    print(f"  APOTHECARY cross-references: {len(apothecary_refs)}")
    print(f"  Max GAIA state delta: +{max(a.gaia_state_delta for a in attempts):.4f}")
    print("  All structural invariants PASSED.")
    print("\n  ✅ GAIA-OS Quantum Chemistry Orbital Bonding Simulation — ALL BONDS COMPLETE")
