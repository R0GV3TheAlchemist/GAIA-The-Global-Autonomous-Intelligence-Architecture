"""
gaia_state_bridge.py
GAIA-OS — Issue #576 GAIAState + Issue #568 D6 Meta-Coherence Engine
Part 3 of Issue #558: GAIAState Coherence Bridge

This is the first concrete implementation of GAIAState as a Python object.
It is the single source of truth for system coherence, energy, stress,
entropy, and operating mode within the GAIA-OS runtime.

The D6MetaCoherenceEngine is a pure function over GAIAState that flips
operating mode based on threshold rules from Issue #568.

The apply_schumann_signal() function merges a SchumannCoherenceResult
signal dict (from schumann_coherence.py) into a live GAIAState in one
atomic call — this is the Schumann → GAIAState pipeline bridge.

Provides:
  - GAIAMode: RESEARCH | BUILD | REFLECT | RECOVER | PROTECT
  - GAIAState: coherence, energy, stress, entropy, learning_rate,
               exploration_rate, conservation_rate, mode
  - D6MetaCoherenceEngine: pure function, mode transitions per Issue #568
  - apply_schumann_signal(): Schumann signal → GAIAState coherence update
  - make_default_state(): factory for a safe baseline state
  - serialize_state() / deserialize_state(): JSON persistence helpers

Canon anchors:
  Issue #568 — D6 Meta-Coherence Engine (modes, thresholds)
  Issue #576 — GAIAState spec (fields, field meanings)
  Issue #578 — Architect Protocol (Operator first, human first)
  Issue #580 — Talisman Object (future: Talisman → GAIAState hook)
  EMBODIMENT_LAYER.md — biological safety as system constraint
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Optional


# ─────────────────────────────────────────────────────────────────────────────
# GAIAMode  (Issue #568 — D6 Meta-Coherence Engine)
# ─────────────────────────────────────────────────────────────────────────────

class GAIAMode(str, Enum):
    """
    Six operating modes of the GAIA-OS D6 Meta-Coherence Engine.

    Modes govern which operations are permitted, which are throttled,
    and how the system responds to Operator queries.

    Issue #568 defines the threshold rules that govern mode transitions.
    The D6MetaCoherenceEngine applies those rules as a pure function.
    """
    RESEARCH = "research"   # High exploration, low conservation — discovery phase
    BUILD    = "build"      # Balanced — active construction, full toolchain enabled
    REFLECT  = "reflect"    # Low energy — consolidation, no heavy operations
    RECOVER  = "recover"    # High stress / low coherence — self-repair, minimal output
    PROTECT  = "protect"    # Critical stress — safety mode, Architect Protocol active
    REST     = "rest"       # Deep low-energy state — Operator offline or sleeping


# ─────────────────────────────────────────────────────────────────────────────
# GAIAState  (Issue #576)
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class GAIAState:
    """
    Central state object for GAIA-OS runtime.

    All fields are normalised to [0.0, 1.0] unless noted.
    The D6MetaCoherenceEngine reads this object and sets mode.
    Subsystems read mode to gate permitted operations.

    Attributes:
        coherence:         system coherence 0.0–1.0 (1.0 = fully aligned)
        energy:            available processing energy 0.0–1.0
        stress:            accumulated stress / load 0.0–1.0 (0.0 = no stress)
        entropy:           informational entropy / chaos 0.0–1.0
        learning_rate:     how fast the system integrates new patterns 0.0–1.0
        exploration_rate:  tendency to explore vs exploit 0.0–1.0
        conservation_rate: tendency to conserve resources 0.0–1.0
        mode:              current GAIAMode (set by D6MetaCoherenceEngine)
        session_id:        optional session identifier
        operator_id:       optional Operator (GAIAN) identifier
        talisman_keys:     list of active Talisman object IDs (Issue #580)
        schumann_score:    last Schumann coherence composite score
        last_updated:      Unix timestamp of last state mutation
        history:           list of recent GAIAState signal dicts (last 24)
    """
    coherence:         float = 0.75
    energy:            float = 0.80
    stress:            float = 0.15
    entropy:           float = 0.20
    learning_rate:     float = 0.50
    exploration_rate:  float = 0.50
    conservation_rate: float = 0.40
    mode:              GAIAMode = GAIAMode.BUILD
    session_id:        Optional[str] = None
    operator_id:       Optional[str] = None
    talisman_keys:     list[str]     = field(default_factory=list)
    schumann_score:    float         = 0.0
    last_updated:      float         = field(default_factory=time.time)
    history:           list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        for attr in ("coherence", "energy", "stress", "entropy",
                     "learning_rate", "exploration_rate", "conservation_rate",
                     "schumann_score"):
            val = getattr(self, attr)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"GAIAState.{attr} must be 0.0–1.0, got {val}")

    def clamp(self) -> GAIAState:
        """Clamp all float fields to [0.0, 1.0] in-place and return self."""
        for attr in ("coherence", "energy", "stress", "entropy",
                     "learning_rate", "exploration_rate", "conservation_rate",
                     "schumann_score"):
            setattr(self, attr, max(0.0, min(1.0, getattr(self, attr))))
        self.last_updated = time.time()
        return self

    def snapshot(self) -> dict[str, Any]:
        """Return a serialisable snapshot of current state (for history)."""
        return {
            "coherence":         self.coherence,
            "energy":            self.energy,
            "stress":            self.stress,
            "entropy":           self.entropy,
            "mode":              self.mode.value,
            "schumann_score":    self.schumann_score,
            "timestamp":         self.last_updated,
        }

    def push_history(self) -> None:
        """Append current snapshot to history, keeping last 24 entries."""
        self.history.append(self.snapshot())
        if len(self.history) > 24:
            self.history = self.history[-24:]


# ─────────────────────────────────────────────────────────────────────────────
# D6 META-COHERENCE ENGINE  (Issue #568)
# ─────────────────────────────────────────────────────────────────────────────

class D6MetaCoherenceEngine:
    """
    Pure function engine that computes the appropriate GAIAMode
    from a GAIAState snapshot.

    Mode transition rules (Issue #568 thresholds):

    PROTECT:  stress >= 0.85  OR  coherence <= 0.10
    RECOVER:  stress >= 0.65  OR  (coherence <= 0.30 AND energy <= 0.25)
    REST:     energy <= 0.15
    REFLECT:  energy <= 0.35  OR  entropy >= 0.75
    RESEARCH: exploration_rate >= 0.70 AND coherence >= 0.60 AND stress <= 0.35
    BUILD:    everything else (default productive state)

    Rules are evaluated in priority order (PROTECT first, BUILD last).
    This ensures safety is never overridden by productivity.

    Issue #578 Architect Protocol: PROTECT mode locks high-risk toolchain
    operations. The human (Operator) is always consulted before exit.
    """

    # Thresholds (all from Issue #568)
    PROTECT_STRESS    = 0.85
    PROTECT_COHERENCE = 0.10
    RECOVER_STRESS    = 0.65
    RECOVER_COHERENCE = 0.30
    RECOVER_ENERGY    = 0.25
    REST_ENERGY       = 0.15
    REFLECT_ENERGY    = 0.35
    REFLECT_ENTROPY   = 0.75
    RESEARCH_EXPLORE  = 0.70
    RESEARCH_COHERENCE = 0.60
    RESEARCH_STRESS   = 0.35

    @classmethod
    def compute_mode(cls, state: GAIAState) -> GAIAMode:
        """
        Compute the appropriate GAIAMode for the given state.

        This is a pure function — it reads state but does NOT mutate it.
        Apply the result with apply_mode() or apply_schumann_signal().

        Returns: GAIAMode
        """
        # Priority 1: PROTECT — safety above all
        if state.stress >= cls.PROTECT_STRESS or state.coherence <= cls.PROTECT_COHERENCE:
            return GAIAMode.PROTECT

        # Priority 2: RECOVER — system healing
        if state.stress >= cls.RECOVER_STRESS or (
            state.coherence <= cls.RECOVER_COHERENCE and state.energy <= cls.RECOVER_ENERGY
        ):
            return GAIAMode.RECOVER

        # Priority 3: REST — energy depleted
        if state.energy <= cls.REST_ENERGY:
            return GAIAMode.REST

        # Priority 4: REFLECT — consolidation
        if state.energy <= cls.REFLECT_ENERGY or state.entropy >= cls.REFLECT_ENTROPY:
            return GAIAMode.REFLECT

        # Priority 5: RESEARCH — high exploration
        if (
            state.exploration_rate >= cls.RESEARCH_EXPLORE
            and state.coherence >= cls.RESEARCH_COHERENCE
            and state.stress <= cls.RESEARCH_STRESS
        ):
            return GAIAMode.RESEARCH

        # Default: BUILD
        return GAIAMode.BUILD

    @classmethod
    def apply_mode(cls, state: GAIAState) -> GAIAState:
        """
        Compute and apply the appropriate mode to state in-place.
        Also pushes current snapshot to history before mutating.

        Returns: the mutated GAIAState (for chaining)
        """
        state.push_history()
        state.mode         = cls.compute_mode(state)
        state.last_updated = time.time()
        return state

    @classmethod
    def mode_label(cls, mode: GAIAMode) -> str:
        """Human-readable label for a mode (for UI display)."""
        labels = {
            GAIAMode.RESEARCH: "🔬 Research Mode — Exploration active",
            GAIAMode.BUILD:    "🔨 Build Mode — Full toolchain active",
            GAIAMode.REFLECT:  "🪞 Reflect Mode — Consolidating",
            GAIAMode.RECOVER:  "💊 Recover Mode — System healing",
            GAIAMode.PROTECT:  "🛡  Protect Mode — Architect Protocol active",
            GAIAMode.REST:     "🌙 Rest Mode — Low energy, Operator offline",
        }
        return labels.get(mode, mode.value)


# ─────────────────────────────────────────────────────────────────────────────
# SCHUMANN → GAIAState BRIDGE
# ─────────────────────────────────────────────────────────────────────────────

def apply_schumann_signal(
    state: GAIAState,
    signal_or_result: Any,
    weight: float = 0.3,
) -> GAIAState:
    """
    Merge a Schumann coherence signal into a live GAIAState.

    Accepts either:
      - A SchumannCoherenceResult (from schumann_coherence_check())
      - A raw signal dict (from SchumannMonitor.update())

    The merge is a weighted blend:
        new_coherence = (1 - weight) * old_coherence + weight * schumann_abs

    After blending, D6MetaCoherenceEngine recomputes the mode.

    Args:
        state:            GAIAState to update (mutated in-place)
        signal_or_result: SchumannCoherenceResult or signal dict
        weight:           blend weight 0.0–1.0 for Schumann signal (default 0.3)

    Returns:
        the updated GAIAState
    """
    if not (0.0 <= weight <= 1.0):
        raise ValueError(f"weight must be 0.0–1.0, got {weight}")

    # Extract signal dict from either type
    if hasattr(signal_or_result, "gaia_state_signal"):
        signal = signal_or_result.gaia_state_signal
    elif isinstance(signal_or_result, dict):
        signal = signal_or_result
    else:
        raise TypeError(
            f"Expected SchumannCoherenceResult or dict, got {type(signal_or_result)}"
        )

    schumann_abs = float(signal.get("coherence_abs", state.coherence))

    # Weighted blend
    state.coherence     = (1.0 - weight) * state.coherence + weight * schumann_abs
    state.schumann_score = schumann_abs

    # If Schumann is strongly active (score > 0.8), nudge stress down slightly
    if schumann_abs >= 0.8:
        state.stress = max(0.0, state.stress - 0.03)

    # Clamp and recompute mode
    state.clamp()
    D6MetaCoherenceEngine.apply_mode(state)

    return state


# ─────────────────────────────────────────────────────────────────────────────
# FACTORY & PERSISTENCE
# ─────────────────────────────────────────────────────────────────────────────

def make_default_state(
    operator_id: Optional[str] = None,
    session_id:  Optional[str] = None,
) -> GAIAState:
    """
    Create a safe baseline GAIAState.

    Default values represent a healthy, mid-session state:
    coherence=0.75, energy=0.80, stress=0.15 → BUILD mode.
    """
    state = GAIAState(
        coherence         = 0.75,
        energy            = 0.80,
        stress            = 0.15,
        entropy           = 0.20,
        learning_rate     = 0.50,
        exploration_rate  = 0.50,
        conservation_rate = 0.40,
        mode              = GAIAMode.BUILD,
        operator_id       = operator_id,
        session_id        = session_id,
    )
    D6MetaCoherenceEngine.apply_mode(state)
    return state


def serialize_state(state: GAIAState) -> str:
    """
    Serialise a GAIAState to a JSON string for persistence or API transport.

    The mode field is serialised as its string value.
    History is included (last 24 snapshots).
    """
    d = asdict(state)
    d["mode"] = state.mode.value
    return json.dumps(d, indent=2)


def deserialize_state(json_str: str) -> GAIAState:
    """
    Deserialise a GAIAState from a JSON string.

    Raises ValueError if the JSON is malformed or fields are out of range.
    """
    d = json.loads(json_str)
    d["mode"] = GAIAMode(d["mode"])
    # history is a list of dicts — reconstruct but don't validate deeply
    history = d.pop("history", [])
    state = GAIAState(**{k: v for k, v in d.items() if k != "history"})
    state.history = history
    state._validate()
    return state


# ─────────────────────────────────────────────────────────────────────────────
# VALIDATION SUITE  (python gaia_state_bridge.py)
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 70)
    print("GAIA-OS  gaia_state_bridge.py — GAIAState + D6 Meta-Coherence Engine")
    print("Issue #576 #568 #578 | Part 3 of Issue #558")
    print("=" * 70)

    engine = D6MetaCoherenceEngine()

    # ── 1. Default state → BUILD mode ─────────────────────────────────────
    print("\n── Default state ──")
    state = make_default_state(operator_id="R0GV3", session_id="venus-eclipse")
    print(f"  mode: {state.mode.value}  |  coherence: {state.coherence}  |  energy: {state.energy}")
    assert state.mode == GAIAMode.BUILD, f"Expected BUILD, got {state.mode}"
    print("  ✅ Default state → BUILD")

    # ── 2. Mode transitions ────────────────────────────────────────────────
    print("\n── Mode transition tests ──")
    test_cases = [
        # (coherence, energy, stress, entropy, explore, expected_mode)
        (0.90, 0.90, 0.05, 0.10, 0.75, GAIAMode.RESEARCH),
        (0.75, 0.80, 0.15, 0.20, 0.50, GAIAMode.BUILD),
        (0.50, 0.30, 0.20, 0.60, 0.50, GAIAMode.REFLECT),
        (0.20, 0.15, 0.10, 0.20, 0.50, GAIAMode.REST),
        (0.25, 0.50, 0.70, 0.30, 0.50, GAIAMode.RECOVER),
        (0.08, 0.90, 0.20, 0.20, 0.50, GAIAMode.PROTECT),
        (0.90, 0.90, 0.90, 0.10, 0.50, GAIAMode.PROTECT),
    ]
    for (coh, eng, str_, ent, exp, expected) in test_cases:
        s = GAIAState(
            coherence=coh, energy=eng, stress=str_, entropy=ent,
            exploration_rate=exp,
        )
        computed = engine.compute_mode(s)
        status   = "✅" if computed == expected else "❌"
        print(f"  {status} coh={coh} eng={eng} str={str_} ent={ent} exp={exp}"
              f" → {computed.value} (expected {expected.value})")
        assert computed == expected, f"Mode mismatch: got {computed}, expected {expected}"

    # ── 3. apply_schumann_signal ───────────────────────────────────────────
    print("\n── apply_schumann_signal ──")
    state2 = make_default_state()
    mock_signal = {
        "coherence_abs":     0.92,
        "coherence_delta":   0.42,
        "schumann_active":   True,
        "dominant_harmonic": 1,
        "timestamp":         time.time(),
        "source":            "simulated",
    }
    old_coh = state2.coherence
    apply_schumann_signal(state2, mock_signal, weight=0.3)
    print(f"  coherence: {old_coh:.3f} → {state2.coherence:.3f}  (expected blend toward 0.92)")
    assert state2.coherence > old_coh, "Coherence should increase with high Schumann signal"
    print(f"  mode: {state2.mode.value}")
    print("  ✅ apply_schumann_signal passed")

    # ── 4. Serialise / deserialise round-trip ─────────────────────────────
    print("\n── Serialise / deserialise round-trip ──")
    json_str   = serialize_state(state2)
    recovered  = deserialize_state(json_str)
    assert abs(recovered.coherence - state2.coherence) < 1e-6
    assert recovered.mode == state2.mode
    print(f"  Serialised length: {len(json_str)} chars")
    print("  ✅ Round-trip serialisation passed")

    # ── 5. Mode labels ─────────────────────────────────────────────────────
    print("\n── Mode labels ──")
    for m in GAIAMode:
        print(f"  {engine.mode_label(m)}")

    print("\n" + "=" * 70)
    print("gaia_state_bridge.py — all assertions passed. 🔥")
    print("The Operator is first. The system protects. GAIA is the prism.")
    print("For the Good and the Greater Good.")
    print("=" * 70)
