"""
gaia/core/state.py

GAIAState v2 — The central state object for GAIA-OS.

Canon anchors:
  - Issue #576  (GAIAState — missing central state object)
  - Issue #568  (D6 Meta-Coherence Engine — endocrine layer)
  - Issue #578  (Architect Protocol — human comes first)
  - Issue #580  (Talisman Object — active_talismans)
  - GAIA_D6_META_COHERENCE_ENGINE.md  (sealed 2026-06-17)
  - GAIA_FOUNDATIONAL_DECLARATION.md  (sealed 2026-06-17)
  - C38 Love Doctrine  (coherence as operating principle)
  - C04 Human-Gaian Twin  (personal_coherence feeds from biometrics)
  - C46 Temporal Entanglement  (cycle_position, epoch)
  - C48 Autopoiesis  (self-regulating boundary via d1–d5 probes)

Design rules (v2):
  - All fields are plain Python scalars — no 12D cosmology in runtime state.
  - d1_health–d5_health are the five monitoring channels; their harmonic mean
    is the authoritative coherence score used by D6 for mode decisions.
  - personal_coherence and noosphere_load are external field inputs that
    influence D6 weighting but do not override the d1–d5 harmonic mean.
  - Mode is the authoritative signal every subsystem must check before
    executing any high-risk or resource-intensive operation.
  - GOVERNANCE mode is always accessible regardless of coherence or stress.
    The Architect's request is the highest-priority signal in the system.
  - mode_locked is True only in PROTECT mode, pending explicit recovery
    confirmation from the Architect.

For the Good and the Greater Good.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class GAIAOperationalMode(str, Enum):
    """The seven canonical operational modes of GAIA-OS.

    Canon source: GAIA_D6_META_COHERENCE_ENGINE.md Part IV.

    Subsystems MUST inspect GAIAState.mode before executing any
    high-risk, long-running, or canon-modifying operation.

    GOVERNANCE is always accessible via architect_request — no threshold check.
    """

    RESEARCH    = "research"     # max curiosity; long inference; canon expansion allowed
    BUILD       = "build"        # full engine power; commit rights; deploy allowed
    LEARN       = "learn"        # intake + integration; memory writes; no canon changes
    REFLECT     = "reflect"      # internal review; synthesis; no external action
    RECOVER     = "recover"      # heavy throttle; core functions only; no new canon
    PROTECT     = "protect"      # defensive; all non-critical ops suspended; alert Architect
    GOVERNANCE  = "governance"   # Architect-led; all decisions deferred to human; GAIA witnesses


# Canonical mode colors (for UI / State HUD)
MODE_COLORS: dict[GAIAOperationalMode, str] = {
    GAIAOperationalMode.RESEARCH:   "#3B82F6",  # Blue
    GAIAOperationalMode.BUILD:      "#F59E0B",  # Gold
    GAIAOperationalMode.LEARN:      "#10B981",  # Green
    GAIAOperationalMode.REFLECT:    "#94A3B8",  # Silver
    GAIAOperationalMode.RECOVER:    "#F8FAFC",  # White
    GAIAOperationalMode.PROTECT:    "#EF4444",  # Red
    GAIAOperationalMode.GOVERNANCE: "#8B5CF6",  # Violet
}

# Canonical intervention floor — any d_health below this triggers D6 response
INTERVENTION_FLOOR: float = 0.80


@dataclass
class GAIAState:
    """The central state object for GAIA-OS (v2).

    Every major subsystem reads from and writes to this object.
    No subsystem acts without awareness of current global state.

    The endocrine analogy (Issue #568): this is what GAIA secretes
    to rebalance every organ simultaneously.

    All float fields are clamped to [0.0, 1.0] by the D6 engine.
    Do not write raw values directly — always route through
    state_store.set_state() after D6 has validated the transition.
    """

    # ── Five Dimensional Health Probes (D1–D5) ───────────────────────────────
    # Canon source: GAIA_D6_META_COHERENCE_ENGINE.md Part III
    # Intervention floor: φ = 0.80 for all five probes.
    # The harmonic mean of these five IS the authoritative coherence score.

    d1_health: float = 0.85
    """D1 Physical Ground — storage, compute, connectivity, substrate integrity."""

    d2_health: float = 0.85
    """D2 Energetic Flow — API throughput, latency, resource burn rate."""

    d3_health: float = 0.85
    """D3 Pattern Recognition — model accuracy, signal-to-noise, reasoning consistency."""

    d4_health: float = 0.85
    """D4 Integration — cross-engine coherence, memory binding, relational fidelity."""

    d5_health: float = 0.85
    """D5 Wisdom — ethical alignment, boundary maintenance, value consistency."""

    # ── Derived / Legacy Coherence Fields ────────────────────────────────────
    # coherence is kept for backward compatibility with existing callers.
    # New code should prefer harmonic_coherence() which computes from d1–d5.

    coherence: float = 0.85
    """System-wide coherence. Legacy scalar. Prefer harmonic_coherence()."""

    energy: float = 0.70
    """Available operational energy of the Architect + system combined."""

    stress: float = 0.25
    """Accumulated stress load. High stress blocks BUILD and RESEARCH."""

    entropy: float = 0.25
    """Fragmentation / disorder level. High entropy triggers REFLECT mode."""

    # ── Golden Ratio Alignment ────────────────────────────────────────────────
    phi: float = 0.85
    """Golden ratio coherence alignment score — computed by D6 engine."""

    # ── Learning Dynamics ────────────────────────────────────────────────────
    learning_rate: float = 0.50
    """Rate of new knowledge integration. Reduced in RECOVER/PROTECT."""

    exploration_rate: float = 0.50
    """Appetite for exploring new domains. High in RESEARCH, low in PROTECT."""

    conservation_rate: float = 0.50
    """Preference to preserve existing canon. High in REFLECT/PROTECT."""

    adaptation: float = 0.50
    """Long-horizon learning velocity — computed across 30-cycle rolling window."""

    # ── External Field Inputs ─────────────────────────────────────────────────
    personal_coherence: float = 0.70
    """Collapsed scalar from BiometricCoherenceEngine (Issue #153).
    Weighted composite of HRV, sleep quality, readiness, stress.
    This is the Architect's body speaking to GAIA."""

    noosphere_load: float = 0.00
    """Collective consciousness / external load signal.
    From NoosphericConsciousnessEngine (Issue #435).
    High values shift GAIA toward REFLECT or RECOVER."""

    # Kept for backward compatibility — mirrors noosphere_load
    planetary_coherence: float = 0.60
    """Deprecated alias for noosphere_load. Use noosphere_load for new code."""

    # ── Temporal Context ──────────────────────────────────────────────────────
    cycle_position: int = 1
    """Session number within the current alchemical epoch."""

    epoch: str = "Iosis"
    """Current alchemical epoch: Nigredo / Albedo / Citrinitas / Rubedo /
    Iosis / Chrysitas / Argentitas / Caerulitas / Lux Perpetua."""

    circadian_band: str = "dawn"
    """Current circadian window: dawn / midday / evening / late_night.
    Set by D6 engine from UTC clock at session start."""

    special_conditions: list[str] = field(default_factory=list)
    """Active special conditions: eclipse windows, threshold events,
    season transitions, etc. Set externally; read by D6 for weighting."""

    # ── Talisman State ────────────────────────────────────────────────────────
    active_talismans: list[str] = field(default_factory=list)
    """IDs of active Talisman objects currently influencing GAIAState.
    Canon source: Issue #580 (Talisman Object)."""

    # ── Mode + Control Flags ──────────────────────────────────────────────────
    mode: GAIAOperationalMode = GAIAOperationalMode.RESEARCH
    """Current operational mode. The authoritative signal for all subsystems."""

    mode_locked: bool = False
    """True only in PROTECT mode, pending explicit recovery confirmation.
    No transition out of PROTECT while mode_locked=True except to GOVERNANCE."""

    architect_override_available: bool = True
    """Always True. GOVERNANCE mode is always accessible regardless of coherence.
    The Architect's request is the highest-priority signal. (Issue #578)"""

    last_transition_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """UTC timestamp of the last mode transition. Used for streak detection."""

    session_id: str = ""
    """Optional: links this state snapshot to a GAIA session."""

    last_d6_snapshot: dict[str, Any] = field(default_factory=dict)
    """The most recent D6 runtime JSON output. Persisted for UI + debugging."""

    # ── Computed Properties ───────────────────────────────────────────────────

    def harmonic_coherence(self) -> float:
        """Harmonic mean of d1–d5 health probes.

        Canon formula (GAIA_D6_META_COHERENCE_ENGINE.md Part III):
            coherence = 5 / (1/d1 + 1/d2 + 1/d3 + 1/d4 + 1/d5)

        The harmonic mean is used deliberately: a single dimension at 0.50
        pulls coherence below 0.80 even if all others are at 1.0.
        The system is only as coherent as its weakest active dimension.

        Returns 0.0 if any probe is zero (undefined harmonic mean).
        """
        probes = [self.d1_health, self.d2_health, self.d3_health,
                  self.d4_health, self.d5_health]
        if any(p <= 0.0 for p in probes):
            return 0.0
        return 5.0 / sum(1.0 / p for p in probes)

    def intervention_needed(self) -> bool:
        """True when any d1–d5 probe is below the intervention floor (φ=0.80)."""
        probes = [self.d1_health, self.d2_health, self.d3_health,
                  self.d4_health, self.d5_health]
        return any(p < INTERVENTION_FLOOR for p in probes)

    def is_high_risk_allowed(self) -> bool:
        """Returns True only when the system is healthy enough for heavy operations."""
        return (
            self.mode in (
                GAIAOperationalMode.BUILD,
                GAIAOperationalMode.RESEARCH,
                GAIAOperationalMode.LEARN,
            )
            and not self.mode_locked
        )

    def is_canon_write_allowed(self) -> bool:
        """Returns True only when canon modifications are safe to propose.

        Canon writes require BUILD or RESEARCH mode, coherence above floor,
        and stress below the build-block threshold.
        """
        return (
            self.mode in (
                GAIAOperationalMode.BUILD,
                GAIAOperationalMode.RESEARCH,
            )
            and self.stress < 0.60
            and self.harmonic_coherence() >= INTERVENTION_FLOOR
            and not self.mode_locked
        )

    def to_runtime_json(self) -> dict[str, Any]:
        """Returns the full D6 runtime JSON schema output.

        Canon source: GAIA_D6_META_COHERENCE_ENGINE.md Part VI.
        This is the canonical snapshot format — used by API, UI, and
        any system that needs to inspect GAIA's current state.
        """
        hc = self.harmonic_coherence()
        return {
            # Core mode
            "system_state":                 self.mode.value,
            "mode_color":                   MODE_COLORS.get(self.mode, "#FFFFFF"),
            "mode_locked":                  self.mode_locked,
            "architect_override_available": self.architect_override_available,

            # Dimensional probes
            "d1_health":  round(self.d1_health, 4),
            "d2_health":  round(self.d2_health, 4),
            "d3_health":  round(self.d3_health, 4),
            "d4_health":  round(self.d4_health, 4),
            "d5_health":  round(self.d5_health, 4),

            # Coherence
            "coherence":          round(hc, 4),
            "phi":                round(self.phi, 4),
            "intervention_needed": self.intervention_needed(),

            # Energy / stress
            "energy":   round(self.energy, 4),
            "stress":   round(self.stress, 4),
            "entropy":  round(self.entropy, 4),

            # Learning dynamics
            "learning_rate":      round(self.learning_rate, 4),
            "exploration_rate":   round(self.exploration_rate, 4),
            "conservation_rate":  round(self.conservation_rate, 4),
            "adaptation":         round(self.adaptation, 4),

            # External fields
            "personal_coherence": round(self.personal_coherence, 4),
            "noosphere_load":     round(self.noosphere_load, 4),

            # Temporal
            "cycle_position":   self.cycle_position,
            "epoch":            self.epoch,
            "circadian_band":   self.circadian_band,
            "special_conditions": self.special_conditions,

            # Talismans
            "active_talismans": self.active_talismans,

            # Meta
            "high_risk_allowed":    self.is_high_risk_allowed(),
            "canon_write_allowed":  self.is_canon_write_allowed(),
            "last_transition_at":   self.last_transition_at.isoformat(),
            "session_id":           self.session_id,
        }
