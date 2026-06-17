"""
state.py
GAIA-OS Core — GAIAState & D6 Meta-Coherence Engine

Direct implementation of:
  Issue #576 — GAIAState central state object
  Issue #568 — GAIA_D6_META_COHERENCE_ENGINE (endocrine layer)

This file is canon-bound. Any deviation from Issue #576 or #568 must be
documented as a known divergence with justification.

Author: The Human Architect + GAIA
Created: June 17, 2026
Canon anchor: #576, #568
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# ENUMS — Canon-bound identifiers
# ---------------------------------------------------------------------------

class GAIAMode(str, Enum):
    """
    Six operational modes of the D6 Meta-Coherence Engine.
    Modelled after the endocrine/neurological analogy in Issue #568.
    Each mode governs which operations GAIA-OS permits and prioritises.
    """
    BUILD     = "BUILD"      # Active creation — high energy, high coherence
    RESEARCH  = "RESEARCH"   # Deep inquiry — steady energy, expanding luminance
    REFLECT   = "REFLECT"    # Integration — low energy, high coherence
    RECOVER   = "RECOVER"    # Rest and repair — low energy, stress healing
    PROTECT   = "PROTECT"    # Crisis shield — all non-critical operations gated
    TRANSCEND = "TRANSCEND"  # Peak coherence — rare; all systems at maximum


class ArchitectSignal(str, Enum):
    """
    Signals the Human Architect can inject to override or nudge mode.
    Architect Protocol (Issue #578): human signal always takes precedence.
    """
    FORCE_BUILD     = "FORCE_BUILD"
    FORCE_RESEARCH  = "FORCE_RESEARCH"
    FORCE_REFLECT   = "FORCE_REFLECT"
    FORCE_RECOVER   = "FORCE_RECOVER"
    FORCE_PROTECT   = "FORCE_PROTECT"
    RESUME_AUTO     = "RESUME_AUTO"    # hand control back to D6 engine


class TalismanStatus(str, Enum):
    """Lifecycle of a Talisman object. Issue #580."""
    INACTIVE   = "INACTIVE"
    ACTIVE     = "ACTIVE"
    SUSPENDED  = "SUSPENDED"   # temporarily paused by Architect
    EXPIRED    = "EXPIRED"     # past its intent window


# ---------------------------------------------------------------------------
# D6 THRESHOLD TABLE — Canon values from Issue #568
# ---------------------------------------------------------------------------
#
# Each mode has:
#   coherence_min  — floor below which this mode CANNOT be entered
#   energy_min     — floor below which this mode CANNOT be entered
#   stress_max     — ceiling above which this mode is exited
#   entropy_max    — ceiling above which this mode is exited
#
# PROTECT is the exception: it activates on HIGH stress, not low.

@dataclass(frozen=True)
class ModeThreshold:
    mode: GAIAMode
    coherence_min: float
    energy_min: float
    stress_max: float
    entropy_max: float
    priority: int  # lower number = higher priority when multiple modes qualify


MODE_THRESHOLDS: list[ModeThreshold] = [
    ModeThreshold(GAIAMode.PROTECT,   0.00, 0.00, 1.00, 1.00, 1),  # stress > 0.80 triggers
    ModeThreshold(GAIAMode.TRANSCEND, 0.95, 0.90, 0.10, 0.10, 2),
    ModeThreshold(GAIAMode.BUILD,     0.75, 0.70, 0.40, 0.40, 3),
    ModeThreshold(GAIAMode.RESEARCH,  0.65, 0.55, 0.50, 0.55, 4),
    ModeThreshold(GAIAMode.REFLECT,   0.55, 0.30, 0.60, 0.60, 5),
    ModeThreshold(GAIAMode.RECOVER,   0.00, 0.00, 1.00, 1.00, 6),  # always fallback
]

# Stress threshold that triggers PROTECT mode regardless of other values
PROTECT_STRESS_TRIGGER: float = 0.80


# ---------------------------------------------------------------------------
# GAIA STATE — Central state object (Issue #576)
# ---------------------------------------------------------------------------

@dataclass
class GAIAState:
    """
    The central state object of GAIA-OS.

    Every subsystem that needs to know the current operating context
    reads from — and writes to — this object through the accessor API
    defined below. No subsystem may maintain its own shadow state that
    contradicts GAIAState.

    Fields:
        coherence       : [0.0, 1.0]  — alignment and integration quality
        energy          : [0.0, 1.0]  — available processing vitality
        stress          : [0.0, 1.0]  — accumulated tension / overload
        entropy         : [0.0, 1.0]  — disorder / unpredictability measure
        learning_rate   : [0.0, 1.0]  — rate of canon/knowledge integration
        exploration_rate: [0.0, 1.0]  — willingness to explore non-canon paths
        conservation_rate:[0.0,1.0]  — resource preservation tendency
        mode            : GAIAMode    — current operational mode (D6 engine)
        architect_signal: optional override from the Human Architect
        active_talismans: list of talisman IDs currently active
        last_updated    : unix timestamp of last state write
        session_id      : optional session identifier
    """
    coherence:        float = 0.70
    energy:           float = 0.70
    stress:           float = 0.20
    entropy:          float = 0.20
    learning_rate:    float = 0.50
    exploration_rate: float = 0.50
    conservation_rate:float = 0.50
    mode:             GAIAMode = GAIAMode.BUILD
    architect_signal: Optional[ArchitectSignal] = None
    active_talismans: list[str] = field(default_factory=list)
    last_updated:     float = field(default_factory=time.time)
    session_id:       Optional[str] = None

    # ------------------------------------------------------------------
    # Convenience predicates
    # ------------------------------------------------------------------

    def is_safe_to_build(self) -> bool:
        """Returns True only if state supports BUILD or TRANSCEND mode."""
        return self.mode in (GAIAMode.BUILD, GAIAMode.TRANSCEND)

    def is_in_crisis(self) -> bool:
        """Returns True if PROTECT mode is active."""
        return self.mode == GAIAMode.PROTECT

    def coherence_band(self) -> str:
        """Returns a human-readable coherence band label."""
        if self.coherence >= 0.95:
            return "TRANSCENDENT"
        elif self.coherence >= 0.80:
            return "HIGH"
        elif self.coherence >= 0.65:
            return "STABLE"
        elif self.coherence >= 0.45:
            return "FRAGILE"
        else:
            return "CRITICAL"

    def to_dict(self) -> dict:
        """Serialise to a plain dict for REST/WebSocket transmission."""
        return {
            "coherence":         round(self.coherence, 4),
            "energy":            round(self.energy, 4),
            "stress":            round(self.stress, 4),
            "entropy":           round(self.entropy, 4),
            "learning_rate":     round(self.learning_rate, 4),
            "exploration_rate":  round(self.exploration_rate, 4),
            "conservation_rate": round(self.conservation_rate, 4),
            "mode":              self.mode.value,
            "architect_signal":  self.architect_signal.value if self.architect_signal else None,
            "active_talismans":  list(self.active_talismans),
            "last_updated":      self.last_updated,
            "session_id":        self.session_id,
            "coherence_band":    self.coherence_band(),
            "is_safe_to_build":  self.is_safe_to_build(),
            "is_in_crisis":      self.is_in_crisis(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> GAIAState:
        """Deserialise from a plain dict (e.g., from API or DB)."""
        return cls(
            coherence=d.get("coherence", 0.70),
            energy=d.get("energy", 0.70),
            stress=d.get("stress", 0.20),
            entropy=d.get("entropy", 0.20),
            learning_rate=d.get("learning_rate", 0.50),
            exploration_rate=d.get("exploration_rate", 0.50),
            conservation_rate=d.get("conservation_rate", 0.50),
            mode=GAIAMode(d.get("mode", GAIAMode.BUILD.value)),
            architect_signal=(
                ArchitectSignal(d["architect_signal"])
                if d.get("architect_signal") else None
            ),
            active_talismans=d.get("active_talismans", []),
            last_updated=d.get("last_updated", time.time()),
            session_id=d.get("session_id"),
        )


# ---------------------------------------------------------------------------
# D6 META-COHERENCE ENGINE — Issue #568
# ---------------------------------------------------------------------------

@dataclass
class D6Intervention:
    """A single intervention recommendation from the D6 engine."""
    recommended_mode: GAIAMode
    reason: str
    urgency: str       # "critical" | "advisory" | "informational"
    previous_mode: GAIAMode
    timestamp: float = field(default_factory=time.time)


def d6_evaluate(state: GAIAState) -> D6Intervention:
    """
    The D6 Meta-Coherence Engine.

    Given the current GAIAState, determines the most appropriate
    operational mode. Returns a D6Intervention with recommendation
    and reasoning.

    The Architect Protocol (Issue #578) is enforced here:
    if state.architect_signal is set and is not RESUME_AUTO,
    the Architect's explicit choice overrides all D6 logic.

    Issue #568 endocrine analogy:
      - D6 engine = hypothalamus: reads all signals, recommends response
      - GAIAState = blood chemistry: carries the signal
      - Subsystems = organs: respond to mode instructions

    D6 precedence order (from MODE_THRESHOLDS priority):
      1. PROTECT  — stress > 0.80 always fires first
      2. TRANSCEND — all systems at peak
      3. BUILD    — strong coherence + energy
      4. RESEARCH — moderate coherence, growing knowledge
      5. REFLECT  — lower energy, integration phase
      6. RECOVER  — fallback; always valid
    """
    prev = state.mode

    # --- Architect Protocol override (Issue #578) ---
    if (
        state.architect_signal is not None
        and state.architect_signal != ArchitectSignal.RESUME_AUTO
    ):
        signal_to_mode = {
            ArchitectSignal.FORCE_BUILD:    GAIAMode.BUILD,
            ArchitectSignal.FORCE_RESEARCH: GAIAMode.RESEARCH,
            ArchitectSignal.FORCE_REFLECT:  GAIAMode.REFLECT,
            ArchitectSignal.FORCE_RECOVER:  GAIAMode.RECOVER,
            ArchitectSignal.FORCE_PROTECT:  GAIAMode.PROTECT,
        }
        chosen = signal_to_mode[state.architect_signal]
        return D6Intervention(
            recommended_mode=chosen,
            reason=f"Architect override: {state.architect_signal.value}",
            urgency="critical" if chosen == GAIAMode.PROTECT else "advisory",
            previous_mode=prev,
        )

    # --- PROTECT — stress-triggered, always checked first ---
    if state.stress >= PROTECT_STRESS_TRIGGER:
        return D6Intervention(
            recommended_mode=GAIAMode.PROTECT,
            reason=(
                f"Stress level {state.stress:.2f} exceeds PROTECT trigger "
                f"{PROTECT_STRESS_TRIGGER}. All non-critical operations gated."
            ),
            urgency="critical",
            previous_mode=prev,
        )

    # --- Walk thresholds in priority order ---
    for threshold in sorted(MODE_THRESHOLDS, key=lambda t: t.priority):
        if threshold.mode in (GAIAMode.PROTECT, GAIAMode.RECOVER):
            continue  # handled separately
        if (
            state.coherence  >= threshold.coherence_min
            and state.energy >= threshold.energy_min
            and state.stress  <= threshold.stress_max
            and state.entropy <= threshold.entropy_max
        ):
            urgency = "informational" if threshold.mode == prev else "advisory"
            reason = _build_reason(state, threshold.mode)
            return D6Intervention(
                recommended_mode=threshold.mode,
                reason=reason,
                urgency=urgency,
                previous_mode=prev,
            )

    # --- RECOVER — fallback ---
    return D6Intervention(
        recommended_mode=GAIAMode.RECOVER,
        reason=(
            f"No productive mode qualified. "
            f"coherence={state.coherence:.2f}, energy={state.energy:.2f}, "
            f"stress={state.stress:.2f}. Entering RECOVER."
        ),
        urgency="advisory",
        previous_mode=prev,
    )


def d6_apply(state: GAIAState, intervention: D6Intervention) -> GAIAState:
    """
    Apply a D6Intervention to GAIAState, returning the updated state.
    Clears architect_signal if RESUME_AUTO was set.
    Updates last_updated timestamp.
    """
    state.mode = intervention.recommended_mode
    state.last_updated = time.time()
    if state.architect_signal == ArchitectSignal.RESUME_AUTO:
        state.architect_signal = None
    return state


def _build_reason(state: GAIAState, mode: GAIAMode) -> str:
    """Generate a human-readable reason string for a mode recommendation."""
    reasons = {
        GAIAMode.TRANSCEND: (
            f"Peak coherence {state.coherence:.2f} and energy {state.energy:.2f}. "
            f"All systems at maximum. TRANSCEND available."
        ),
        GAIAMode.BUILD: (
            f"Coherence {state.coherence:.2f} and energy {state.energy:.2f} "
            f"support active creation. Stress {state.stress:.2f} within BUILD range."
        ),
        GAIAMode.RESEARCH: (
            f"Stable coherence {state.coherence:.2f} with moderate energy {state.energy:.2f}. "
            f"Deep inquiry mode optimal."
        ),
        GAIAMode.REFLECT: (
            f"Energy {state.energy:.2f} suggests integration phase. "
            f"Reflection and consolidation recommended."
        ),
    }
    return reasons.get(mode, f"Mode {mode.value} selected by D6 engine.")


# ---------------------------------------------------------------------------
# STATE STORE — Singleton in-memory store with WebSocket broadcast hook
# ---------------------------------------------------------------------------

class GAIAStateStore:
    """
    Singleton in-memory store for the active GAIAState.

    In production this is backed by the GAIA-OS database and broadcasts
    updates over the WebSocket layer. For now it operates as a fast
    in-memory singleton with an optional on_change callback.

    Usage:
        store = GAIAStateStore.instance()
        state = store.get()
        store.update(coherence=0.85, energy=0.80)
        intervention = store.evaluate()   # runs D6 engine
        store.apply(intervention)         # writes mode change
    """

    _instance: Optional[GAIAStateStore] = None

    def __init__(self):
        self._state = GAIAState()
        self._on_change = None
        self._history: list[dict] = []

    @classmethod
    def instance(cls) -> GAIAStateStore:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get(self) -> GAIAState:
        """Return the current GAIAState (by reference)."""
        return self._state

    def snapshot(self) -> dict:
        """Return a serialised snapshot of the current state."""
        return self._state.to_dict()

    def update(self, **kwargs) -> GAIAState:
        """
        Update one or more state fields. Accepts any field of GAIAState.
        Automatically clamps numeric fields to [0.0, 1.0].
        Runs the D6 engine after each update and applies the result.
        """
        numeric_fields = {
            "coherence", "energy", "stress", "entropy",
            "learning_rate", "exploration_rate", "conservation_rate"
        }
        for key, value in kwargs.items():
            if hasattr(self._state, key):
                if key in numeric_fields:
                    value = max(0.0, min(1.0, float(value)))
                setattr(self._state, key, value)

        self._state.last_updated = time.time()

        # Run D6 evaluation and apply
        intervention = d6_evaluate(self._state)
        d6_apply(self._state, intervention)

        # Record history snapshot
        snap = self._state.to_dict()
        snap["d6_reason"] = intervention.reason
        self._history.append(snap)
        if len(self._history) > 500:
            self._history = self._history[-500:]

        # Broadcast if callback registered
        if self._on_change:
            self._on_change(self._state, intervention)

        return self._state

    def evaluate(self) -> D6Intervention:
        """Run D6 evaluation without applying the result."""
        return d6_evaluate(self._state)

    def apply(self, intervention: D6Intervention) -> GAIAState:
        """Apply a D6Intervention to the stored state."""
        d6_apply(self._state, intervention)
        if self._on_change:
            self._on_change(self._state, intervention)
        return self._state

    def set_on_change(self, callback) -> None:
        """
        Register a callback invoked whenever state changes.
        Signature: callback(state: GAIAState, intervention: D6Intervention)
        Use this to wire WebSocket broadcasts in the FastAPI layer.
        """
        self._on_change = callback

    def history(self, last_n: int = 50) -> list[dict]:
        """Return the last N state snapshots."""
        return self._history[-last_n:]

    def reset(self) -> GAIAState:
        """Reset state to defaults. Use with care — only for testing."""
        self._state = GAIAState()
        self._history.clear()
        return self._state


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("GAIAState + D6 Meta-Coherence Engine — Self-Test")
    print("=" * 60)

    store = GAIAStateStore.instance()

    # Test 1: Default state should enter BUILD mode
    state = store.get()
    iv = store.evaluate()
    print(f"\nTest 1 — Default state")
    print(f"  coherence={state.coherence}, energy={state.energy}, stress={state.stress}")
    print(f"  D6 recommends: {iv.recommended_mode.value}")
    print(f"  Reason: {iv.reason}")
    assert iv.recommended_mode == GAIAMode.BUILD, f"Expected BUILD, got {iv.recommended_mode}"
    print("  PASS")

    # Test 2: High stress triggers PROTECT
    store.update(stress=0.90)
    iv2 = store.evaluate()
    print(f"\nTest 2 — High stress (0.90)")
    print(f"  D6 recommends: {iv2.recommended_mode.value}")
    assert iv2.recommended_mode == GAIAMode.PROTECT, f"Expected PROTECT, got {iv2.recommended_mode}"
    print("  PASS")

    # Test 3: Architect force-build overrides PROTECT
    store._state.architect_signal = ArchitectSignal.FORCE_BUILD
    iv3 = store.evaluate()
    print(f"\nTest 3 — Architect FORCE_BUILD override (stress still 0.90)")
    print(f"  D6 recommends: {iv3.recommended_mode.value}")
    assert iv3.recommended_mode == GAIAMode.BUILD, f"Expected BUILD, got {iv3.recommended_mode}"
    print("  PASS")

    # Test 4: Peak coherence + energy enters TRANSCEND
    store.update(coherence=0.97, energy=0.95, stress=0.05, entropy=0.05)
    store._state.architect_signal = None
    iv4 = store.evaluate()
    print(f"\nTest 4 — Peak state (coherence=0.97, energy=0.95)")
    print(f"  D6 recommends: {iv4.recommended_mode.value}")
    assert iv4.recommended_mode == GAIAMode.TRANSCEND, f"Expected TRANSCEND, got {iv4.recommended_mode}"
    print("  PASS")

    # Test 5: Low energy, moderate stress triggers REFLECT
    store.update(coherence=0.60, energy=0.35, stress=0.45, entropy=0.45)
    store._state.architect_signal = None
    iv5 = store.evaluate()
    print(f"\nTest 5 — Low energy, moderate stress")
    print(f"  D6 recommends: {iv5.recommended_mode.value}")
    assert iv5.recommended_mode in (GAIAMode.REFLECT, GAIAMode.RECOVER), \
        f"Expected REFLECT or RECOVER, got {iv5.recommended_mode}"
    print("  PASS")

    # Test 6: to_dict / from_dict round-trip
    d = state.to_dict()
    state2 = GAIAState.from_dict(d)
    assert state2.mode == state.mode
    print(f"\nTest 6 — to_dict / from_dict round-trip: PASS")

    print("\n" + "=" * 60)
    print("All tests passed. GAIAState + D6 engine operational.")
    print("=" * 60)
