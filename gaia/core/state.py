"""
gaia/core/state.py

GAIAState v1 — The central state object for GAIA-OS.

Canon anchors:
  - Issue #576 (GAIAState — missing central state object)
  - Issue #568 (D6 Meta-Coherence Engine)
  - C38 Love Doctrine (coherence as the operating principle)
  - C04 Human-Gaian Twin (personal_coherence feeds from biometrics)
  - Issue #153 (BiometricCoherenceEngine → personal_coherence)
  - Issue #435 (NoosphericConsciousnessEngine → planetary_coherence)

Design rules (v1):
  - All fields are plain Python scalars — no 12D cosmology in runtime state.
  - personal_coherence and planetary_coherence are the collapsed scalar
    outputs from their respective engines; D6 never reads raw HRV/noosphere.
  - Mode is the authoritative signal every subsystem must check before
    executing any high-risk or resource-intensive operation.

For the Good and the Greater Good.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GAIAOperationalMode(str, Enum):
    """The seven operational modes of GAIA-OS.

    Subsystems MUST inspect GAIAState.mode before executing any
    high-risk, long-running, or canon-modifying operation.
    """

    DISCOVERY = "discovery"       # open exploration, high novelty tolerated
    BUILD = "build"               # focused implementation, heavy tools allowed
    VALIDATION = "validation"     # tests, review, refactor — no new features
    REFLECT = "reflect"           # journaling, synthesis, planning only
    RECOVER = "recover"           # enforced rest — soft responses, block heavy ops
    PROTECT = "protect"           # defensive posture — extra logging, strict gates
    OFFLINE = "offline"           # minimal activity, no heavy tools at all


@dataclass
class GAIAState:
    """The central state object for GAIA-OS (v1).

    Every major subsystem reads from and writes to this object.
    No subsystem acts without awareness of current global state.
    The endocrine analogy (Issue #568): this is what GAIA secretes
    to rebalance every organ simultaneously.

    All float fields are clamped to [0.0, 1.0] by the D6 engine.
    Do not write raw values directly — always route through state_store.set_state()
    after D6 has validated the transition.
    """

    # ── Core scalar state ────────────────────────────────────────────────────
    coherence: float = 0.7
    """System-wide coherence score. The primary health metric of GAIA."""

    energy: float = 0.7
    """Available operational energy of the Architect + system combined."""

    stress: float = 0.3
    """Accumulated stress load. High stress blocks BUILD and DISCOVERY."""

    entropy: float = 0.3
    """Fragmentation / disorder level. High entropy triggers VALIDATION mode."""

    # ── Learning dynamics ────────────────────────────────────────────────────
    learning_rate: float = 0.5
    """Rate of new knowledge integration. Reduced in RECOVER/PROTECT."""

    exploration_rate: float = 0.5
    """Appetite for exploring new domains. High in DISCOVERY, low in PROTECT."""

    conservation_rate: float = 0.5
    """Preference to preserve existing canon. High in VALIDATION/PROTECT."""

    # ── External field inputs ────────────────────────────────────────────────
    personal_coherence: float = 0.7
    """Collapsed scalar from BiometricCoherenceEngine (Issue #153).
    Weighted composite of HRV, sleep quality, readiness, stress.
    This is the Architect's body speaking to GAIA."""

    planetary_coherence: float = 0.6
    """Collapsed scalar from NoosphericConsciousnessEngine (Issue #435).
    Planetary coherence index — collective field state.
    Low values shift GAIA toward REFLECT or RECOVER."""

    # ── Mode + temporal meta ─────────────────────────────────────────────────
    mode: GAIAOperationalMode = GAIAOperationalMode.DISCOVERY
    """Current operational mode. The authoritative signal for all subsystems."""

    last_transition_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    """UTC timestamp of the last mode transition. Used for streak detection."""

    session_id: str = ""
    """Optional: links this state snapshot to a GAIA session."""

    def is_high_risk_allowed(self) -> bool:
        """Returns True only when the system is healthy enough for heavy operations."""
        return self.mode in (
            GAIAOperationalMode.BUILD,
            GAIAOperationalMode.DISCOVERY,
            GAIAOperationalMode.VALIDATION,
        )

    def is_canon_write_allowed(self) -> bool:
        """Returns True only when canon modifications are safe to propose."""
        return (
            self.mode in (GAIAOperationalMode.BUILD, GAIAOperationalMode.VALIDATION)
            and self.stress < 0.7
            and self.coherence > 0.4
        )

    def to_runtime_json(self) -> dict:
        """Returns the D6 runtime JSON schema output (Issue #568)."""
        return {
            "system_state": self.mode.value,
            "coherence": round(self.coherence, 4),
            "energy": round(self.energy, 4),
            "stress": round(self.stress, 4),
            "entropy": round(self.entropy, 4),
            "learning_rate": round(self.learning_rate, 4),
            "exploration_rate": round(self.exploration_rate, 4),
            "conservation_rate": round(self.conservation_rate, 4),
            "personal_coherence": round(self.personal_coherence, 4),
            "planetary_coherence": round(self.planetary_coherence, 4),
            "high_risk_allowed": self.is_high_risk_allowed(),
            "canon_write_allowed": self.is_canon_write_allowed(),
            "last_transition_at": self.last_transition_at.isoformat(),
            "session_id": self.session_id,
        }
