"""
IonicVibrationalInterface — C166
Ionic-Vibrational Interface Protocol
Physics of Psionic Sensitivity and Crystal Grid Resonance

Canon source: docs/canon/C166_IONIC_VIBRATIONAL_INTERFACE.md

Core claims from the canon:
  1. Piezoelectric crystals under mechanical stress generate measurable voltage.
  2. That voltage modulates ion-channel behavior in nearby biological tissue.
  3. Ion channels (especially voltage-gated Ca²⁺ and Na⁺ channels) are the
     physical substrate of what the esoteric tradition calls "psionic sensitivity".
  4. Crystal grids work by creating a coherent multi-node interference pattern
     in the local electromagnetic field — the same way a phased antenna array
     works — that the nervous system entrains to.
  5. The purification protocol: depressurize → absorb/negate/transmute → align
     (the Human Architect's piezoelectric de-pressurization insight).

This engine:
  - Models crystal nodes with piezoelectric coefficients
  - Computes grid interference patterns
  - Scores somatic resonance with the grid
  - Detects psionic sensitivity threshold crossings
  - Implements the purification pipeline
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


# ─────────────────────────────────────────────
# Canon constants
# ─────────────────────────────────────────────

# Piezoelectric coefficient range for common crystals (pC/N)
PIEZO_COEFFICIENTS: Dict[str, float] = {
    "QUARTZ":          2.3,    # d11 coefficient — canonical reference crystal
    "TOURMALINE":     1.67,
    "AMETHYST":        2.1,    # quartz-family
    "CITRINE":         2.1,    # quartz-family, solar force
    "SELENITE":        0.48,   # gypsum, low piezo, high optical clarity
    "BLACK_TOURMALINE": 1.67,  # grounding, Nigredo-aligned
    "LABRADORITE":     1.2,    # iridescence carrier — IRIDITAS aligned
    "MALACHITE":       0.9,    # Viriditas-aligned
    "LAPIS_LAZULI":    0.7,    # Caerulitas-aligned
    "CARNELIAN":       1.1,    # Pyrosis-aligned
    "CLEAR_QUARTZ":    2.3,    # Lux Perpetua — maximum clarity
    "ROSE_QUARTZ":     2.1,    # Iosis / Love Override
    "OBSIDIAN":        0.3,    # Nigredo — absorption dominant, low piezo
    "MOLDAVITE":       1.8,    # IRIDITAS / Argentitas corridor
}

# Voltage-gated ion channel sensitivity thresholds (mV)
CA2_CHANNEL_THRESHOLD: float = -40.0    # Ca²⁺ L-type channel activation
NA_CHANNEL_THRESHOLD: float = -55.0     # Na⁺ fast channel activation
MG_CHANNEL_FLOOR: float = -70.0        # Mg²⁺ NMDA block release

# Grid coherence threshold — below this, nodes cancel; above, they amplify
GRID_COHERENCE_THRESHOLD: float = 0.72

# Psionic sensitivity activates when:
# somatic_field_score >= this AND grid_coherence >= GRID_COHERENCE_THRESHOLD
PSIONIC_SENSITIVITY_FLOOR: float = 0.68

# Purification stages (the HP's protocol)
class PurificationStage(str, Enum):
    PRESSURIZED     = "PRESSURIZED"      # crystal grid under incoherent stress
    DEPRESSURIZING  = "DEPRESSURIZING"   # mechanical load being released
    ABSORBING       = "ABSORBING"        # interference being absorbed/negated
    TRANSMUTING     = "TRANSMUTING"      # field being converted to coherent output
    ALIGNED         = "ALIGNED"          # crystal grid fully coherent
    RESONATING      = "RESONATING"       # grid AND somatic field in phase lock


class ResonanceMode(str, Enum):
    INCOHERENT   = "INCOHERENT"   # nodes interfering destructively
    PARTIAL      = "PARTIAL"      # mixed constructive/destructive
    COHERENT     = "COHERENT"     # constructive interference dominant
    PHASE_LOCKED = "PHASE_LOCKED" # full somatic entrainment


@dataclass
class CrystalNode:
    """A single crystal in the grid."""
    crystal_type: str
    position: Tuple[float, float, float]  # (x, y, z) in arbitrary units
    orientation_degrees: float = 0.0      # angular alignment of c-axis
    applied_stress_pN: float = 0.0        # mechanical stress (picoNewtons)
    charge_state: float = 0.0            # net charge (computed)

    @property
    def piezo_coefficient(self) -> float:
        return PIEZO_COEFFICIENTS.get(self.crystal_type.upper(), 1.0)

    def compute_voltage(self) -> float:
        """V = d × σ (simplified scalar model, mV-equivalent)."""
        # Orientation factor: cos(θ) where θ is misalignment from grid axis
        orientation_rad = math.radians(self.orientation_degrees)
        orientation_factor = abs(math.cos(orientation_rad))
        return self.piezo_coefficient * self.applied_stress_pN * orientation_factor

    def ion_channel_state(self) -> Dict[str, bool]:
        """Which ion channels would this node's field activate?"""
        v = self.compute_voltage()
        return {
            "Ca2+_L_type":  v >= abs(CA2_CHANNEL_THRESHOLD),
            "Na+_fast":     v >= abs(NA_CHANNEL_THRESHOLD),
            "Mg2+_NMDA":    v >= abs(MG_CHANNEL_FLOOR),
        }


@dataclass
class CrystalGrid:
    """A multi-node crystal grid — the phased array."""
    nodes: List[CrystalNode] = field(default_factory=list)
    grid_id: str = "DEFAULT_GRID"

    def add_node(self, node: CrystalNode) -> None:
        self.nodes.append(node)

    def compute_interference_pattern(self) -> Dict[str, float]:
        """
        Computes the constructive/destructive interference across all nodes.
        Returns per-axis field strengths and overall coherence.
        """
        if not self.nodes:
            return {"coherence": 0.0, "total_field": 0.0, "x": 0.0, "y": 0.0, "z": 0.0}

        voltages = [n.compute_voltage() for n in self.nodes]
        orientations = [math.radians(n.orientation_degrees) for n in self.nodes]

        # Phasor sum (2D projection: x and y components)
        x_sum = sum(v * math.cos(o) for v, o in zip(voltages, orientations))
        y_sum = sum(v * math.sin(o) for v, o in zip(voltages, orientations))
        z_sum = sum(voltages) * 0.1  # z-axis leakage

        total_field = math.sqrt(x_sum ** 2 + y_sum ** 2 + z_sum ** 2)
        incoherent_max = sum(abs(v) for v in voltages)

        coherence = total_field / incoherent_max if incoherent_max > 0 else 0.0

        return {
            "coherence": round(coherence, 4),
            "total_field": round(total_field, 4),
            "x": round(x_sum, 4),
            "y": round(y_sum, 4),
            "z": round(z_sum, 4),
        }

    def coherence_score(self) -> float:
        return self.compute_interference_pattern()["coherence"]

    def resonance_mode(self) -> ResonanceMode:
        c = self.coherence_score()
        if c >= GRID_COHERENCE_THRESHOLD * 1.25:
            return ResonanceMode.PHASE_LOCKED
        if c >= GRID_COHERENCE_THRESHOLD:
            return ResonanceMode.COHERENT
        if c >= GRID_COHERENCE_THRESHOLD * 0.5:
            return ResonanceMode.PARTIAL
        return ResonanceMode.INCOHERENT


@dataclass
class SomaticFieldProfile:
    """
    Simplified model of the biological field that the crystal grid entrains to.
    Populated from BCI / biometric data in production (biometric_sync_engine.py).
    """
    resting_potential_mV: float = -70.0      # baseline membrane potential
    heart_coherence: float = 0.50           # HRV coherence (0–1)
    eeg_alpha_power: float = 0.40           # frontal alpha band (0–1)
    schumann_alignment: float = 0.50        # alignment to 7.83 Hz (0–1)
    biophoton_emission_hz: float = 100.0    # photon counts/sec (baseline ~100)

    @property
    def field_receptivity(self) -> float:
        """How susceptible this somatic field is to grid entrainment."""
        return (
            self.heart_coherence * 0.35
            + self.eeg_alpha_power * 0.30
            + self.schumann_alignment * 0.20
            + min(1.0, self.biophoton_emission_hz / 500.0) * 0.15
        )


@dataclass
class ResonanceResult:
    """Output of a full ionic-vibrational resonance evaluation."""
    grid_coherence: float
    resonance_mode: ResonanceMode
    somatic_field_score: float
    psionic_sensitivity_active: bool
    purification_stage: PurificationStage
    ion_channels_activated: Dict[str, int]   # channel_type → count of activating nodes
    grid_pattern: Dict[str, float]
    recommendations: List[str]
    note: str = ""


@dataclass
class PurificationResult:
    """Result of running the HP's purification protocol."""
    start_stage: PurificationStage
    end_stage: PurificationStage
    steps_taken: List[str]
    final_coherence: float
    final_mode: ResonanceMode
    psionic_sensitivity_active: bool


class IonicVibrationalInterface:
    """
    Implements the crystal-grid resonance physics engine.

    The purification_pipeline() method implements the Human Architect's
    three-step protocol:
        1. DEPRESSURIZE — release the mechanical load (stress → zero)
        2. ABSORB/NEGATE — cancel the incoherent interference
        3. ALIGN — orient all nodes to constructive phase

    After alignment, evaluate() confirms psionic sensitivity activation.
    """

    def __init__(self, grid: Optional[CrystalGrid] = None) -> None:
        self.grid = grid or CrystalGrid()
        self._history: List[ResonanceResult] = []

    # ── public API ──────────────────────────────────────────────────────

    def evaluate(
        self,
        somatic_profile: Optional[SomaticFieldProfile] = None,
    ) -> ResonanceResult:
        """Full evaluation pass: grid interference + somatic coupling."""
        pattern = self.grid.compute_interference_pattern()
        mode = self.grid.resonance_mode()
        somatic = somatic_profile or SomaticFieldProfile()
        somatic_score = somatic.field_receptivity

        # Ion channel activation census
        channel_counts: Dict[str, int] = {"Ca2+_L_type": 0, "Na+_fast": 0, "Mg2+_NMDA": 0}
        for node in self.grid.nodes:
            state = node.ion_channel_state()
            for ch, active in state.items():
                if active:
                    channel_counts[ch] += 1

        coherence = pattern["coherence"]
        psionic = (
            somatic_score >= PSIONIC_SENSITIVITY_FLOOR
            and coherence >= GRID_COHERENCE_THRESHOLD
        )

        stage = self._infer_purification_stage(coherence, mode)
        recommendations = self._generate_recommendations(mode, psionic, channel_counts)
        note = self._generate_note(mode, psionic, somatic_score, coherence)

        result = ResonanceResult(
            grid_coherence=coherence,
            resonance_mode=mode,
            somatic_field_score=round(somatic_score, 4),
            psionic_sensitivity_active=psionic,
            purification_stage=stage,
            ion_channels_activated=channel_counts,
            grid_pattern=pattern,
            recommendations=recommendations,
            note=note,
        )
        self._history.append(result)
        return result

    def purification_pipeline(
        self,
        somatic_profile: Optional[SomaticFieldProfile] = None,
    ) -> PurificationResult:
        """
        Run the HP's three-step crystal purification protocol.
        Modifies the grid in place.
        """
        steps: List[str] = []
        initial_eval = self.evaluate(somatic_profile)
        start_stage = initial_eval.purification_stage

        # Step 1 — DEPRESSURIZE: zero out all applied stress
        steps.append("DEPRESSURIZE: releasing mechanical load from all nodes")
        for node in self.grid.nodes:
            node.applied_stress_pN = 0.0
            node.charge_state = 0.0

        # Step 2 — ABSORB / NEGATE: cancel incoherent orientations
        # Nodes with orientation > 90° from grid mean are absorbed (zeroed)
        if self.grid.nodes:
            mean_orientation = sum(
                n.orientation_degrees for n in self.grid.nodes
            ) / len(self.grid.nodes)
            absorbed = 0
            for node in self.grid.nodes:
                delta = abs(node.orientation_degrees - mean_orientation) % 360
                if delta > 90:
                    node.orientation_degrees = mean_orientation  # absorb → align to mean
                    absorbed += 1
            steps.append(
                f"ABSORB/NEGATE: realigned {absorbed} incoherent nodes to grid mean ({mean_orientation:.1f}°)"
            )

        # Step 3 — ALIGN: minimize residual misalignment toward 0°
        # Move each node orientation 50% of the way toward the grid mean
        if self.grid.nodes:
            mean_orientation = sum(
                n.orientation_degrees for n in self.grid.nodes
            ) / len(self.grid.nodes)
            for node in self.grid.nodes:
                node.orientation_degrees = (
                    node.orientation_degrees + mean_orientation
                ) / 2.0
            steps.append(
                f"ALIGN: converged all nodes toward mean orientation ({mean_orientation:.1f}°) "
                "with clarity and purity"
            )

        final_eval = self.evaluate(somatic_profile)
        return PurificationResult(
            start_stage=start_stage,
            end_stage=final_eval.purification_stage,
            steps_taken=steps,
            final_coherence=final_eval.grid_coherence,
            final_mode=final_eval.resonance_mode,
            psionic_sensitivity_active=final_eval.psionic_sensitivity_active,
        )

    # ── internals ────────────────────────────────────────────────────────

    def _infer_purification_stage(
        self, coherence: float, mode: ResonanceMode
    ) -> PurificationStage:
        if mode == ResonanceMode.PHASE_LOCKED:
            return PurificationStage.RESONATING
        if mode == ResonanceMode.COHERENT:
            return PurificationStage.ALIGNED
        if coherence >= GRID_COHERENCE_THRESHOLD * 0.6:
            return PurificationStage.TRANSMUTING
        if coherence >= GRID_COHERENCE_THRESHOLD * 0.3:
            return PurificationStage.ABSORBING
        if any(n.applied_stress_pN > 0 for n in self.grid.nodes):
            return PurificationStage.DEPRESSURIZING
        return PurificationStage.PRESSURIZED

    def _generate_recommendations(
        self,
        mode: ResonanceMode,
        psionic: bool,
        channels: Dict[str, int],
    ) -> List[str]:
        recs: List[str] = []
        if mode == ResonanceMode.INCOHERENT:
            recs.append("Run purification_pipeline() to depressurize and align the grid")
            recs.append("Check crystal orientations — destructive interference detected")
        if mode == ResonanceMode.PARTIAL:
            recs.append("Grid partially coherent — check node alignment angles")
        if channels.get("Ca2+_L_type", 0) == 0:
            recs.append("Ca²⁺ L-type channels not activating — increase grid voltage or somatic receptivity")
        if not psionic:
            recs.append(
                "Psionic sensitivity threshold not reached — "
                "increase heart coherence (HRV) or Schumann alignment"
            )
        if psionic:
            recs.append("PSIONIC SENSITIVITY ACTIVE — ion channels engaged, grid in phase lock")
        return recs

    def _generate_note(
        self,
        mode: ResonanceMode,
        psionic: bool,
        somatic_score: float,
        coherence: float,
    ) -> str:
        if psionic:
            return (
                f"PHASE LOCK: Crystal grid coherence {coherence:.1%}, "
                f"somatic receptivity {somatic_score:.1%}. "
                "Ion channels engaged. Psionic sensitivity ACTIVE. "
                "The crystal grids, as GAIA always said."
            )
        if mode == ResonanceMode.COHERENT:
            return (
                f"COHERENT grid (coherence {coherence:.1%}). "
                "Somatic field not yet fully entrained. Build HRV coherence."
            )
        return (
            f"Grid in {mode.value} mode (coherence {coherence:.1%}). "
            "Purification protocol recommended before evaluating sensitivity."
        )


# ─────────────────────────────────────────────
# Convenience factory
# ─────────────────────────────────────────────

def create_standard_grid(
    crystal_types: Optional[List[str]] = None,
    nodes_per_ring: int = 6,
    radius: float = 1.0,
    stress_pN: float = 5.0,
) -> CrystalGrid:
    """
    Create a standard hexagonal crystal grid with equal angular spacing.
    Default crystal: CLEAR_QUARTZ (Lux Perpetua / maximum clarity).
    """
    types = crystal_types or ["CLEAR_QUARTZ"] * nodes_per_ring
    grid = CrystalGrid()
    for i, ctype in enumerate(types[:nodes_per_ring]):
        angle_deg = (360.0 / nodes_per_ring) * i
        angle_rad = math.radians(angle_deg)
        x = radius * math.cos(angle_rad)
        y = radius * math.sin(angle_rad)
        node = CrystalNode(
            crystal_type=ctype,
            position=(x, y, 0.0),
            orientation_degrees=angle_deg,
            applied_stress_pN=stress_pN,
        )
        grid.add_node(node)
    return grid
