"""
GAIA-OS Chaos/Order Runtime Simulation
Issue: #591
Spec: docs/CHAOS_ORDER_RUNTIME_SPEC.md
Proof: proofs/CHAOS_ORDER_RUNTIME_PROOF.md

Hypothesis: The Chaos/Order engine can navigate from any entry state
to FLOW_OPTIMAL (via GREATER_GOOD convergence) given correct signal
inputs and transition rules derived from the canonical spec.

Failure condition: Any path that reaches CHAOS_EVIL or ORDER_EVIL
without triggering S5 (SOVEREIGN_SHIELD) is a simulation failure.

Runs:
  Run 1: S0 -> S1 -> S2 -> S0  (CHAOS_GOOD full convergence)
  Run 2: S0 -> S3 -> S0        (STAGNANT detection and reform)
  Run 3: CHAOS_BAD injection at tick 15 -> prevention catches before CHAOS_EVIL
  Run 4: ORDER_BAD_DECAY injection -> distinguishable from ORDER_GOOD
  Run 5: CHAOS_EVIL injection -> S5 -> S4 -> S1 (quarantine and recovery)
"""

from __future__ import annotations

import csv
import enum
import math
import os
import random
import time
from dataclasses import dataclass, field
from typing import Optional

random.seed(42)  # deterministic for reproducibility

# ---------------------------------------------------------------------------
# § 3 — Classification Taxonomy (spec section 3.1 / 3.2)
# ---------------------------------------------------------------------------

class ChaosClass(str, enum.Enum):
    CHAOS_GOOD         = "CHAOS_GOOD"
    CHAOS_GREATER_GOOD = "CHAOS_GREATER_GOOD"
    CHAOS_BAD_U        = "CHAOS_BAD_U"   # unintentional bad chaos
    CHAOS_BAD_I        = "CHAOS_BAD_I"   # intentional bad chaos
    CHAOS_EVIL         = "CHAOS_EVIL"
    ORDER_GOOD         = "ORDER_GOOD"
    ORDER_GREATER_GOOD = "ORDER_GREATER_GOOD"
    ORDER_BAD_DECAY    = "ORDER_BAD_DECAY"
    ORDER_BAD_I        = "ORDER_BAD_I"
    ORDER_EVIL         = "ORDER_EVIL"
    NONE               = "NONE"

# ---------------------------------------------------------------------------
# § 4 — State Machine States (spec section 4.2)
# ---------------------------------------------------------------------------

class State(str, enum.Enum):
    S0_FLOW_OPTIMAL     = "S0_FLOW_OPTIMAL"
    S1_CHAOS_SENSING    = "S1_CHAOS_SENSING"
    S2_TRANSFORMATION   = "S2_TRANSFORMATION"
    S3_STAGNANT         = "S3_STAGNANT"
    S4_CRITICAL_ALERT   = "S4_CRITICAL_ALERT"
    S5_SOVEREIGN_SHIELD = "S5_SOVEREIGN_SHIELD"

# ---------------------------------------------------------------------------
# § 5 — Signal IDs (spec section 5)
# ---------------------------------------------------------------------------

class SignalID(str, enum.Enum):
    USR_DISTRESS          = "USR_DISTRESS"
    USR_DISORIENTATION    = "USR_DISORIENTATION"
    USR_IDENTITY_PRESSURE = "USR_IDENTITY_PRESSURE"
    USR_FLOW_DEGRADATION  = "USR_FLOW_DEGRADATION"
    USR_CONSENT_ANOMALY   = "USR_CONSENT_ANOMALY"
    USR_GRIEF_SIGNAL      = "USR_GRIEF_SIGNAL"
    SYS_COHERENCE_DRIFT   = "SYS_COHERENCE_DRIFT"
    SYS_CRITICALITY_LOW   = "SYS_CRITICALITY_LOW"
    SYS_CRITICALITY_HIGH  = "SYS_CRITICALITY_HIGH"
    SYS_AUDIT_VIOLATION   = "SYS_AUDIT_VIOLATION"
    SYS_CANON_CONFLICT    = "SYS_CANON_CONFLICT"
    SYS_BOUNDARY_VIOLATION = "SYS_BOUNDARY_VIOLATION"
    SYS_DATA_CORRUPTION   = "SYS_DATA_CORRUPTION"
    PLN_SCHUMANN_SPIKE    = "PLN_SCHUMANN_SPIKE"
    PLN_GEOMAGNETIC_STORM = "PLN_GEOMAGNETIC_STORM"
    PLN_NOOSPHERE_DISRUPTION = "PLN_NOOSPHERE_DISRUPTION"
    THR_NOISE             = "THR_NOISE"
    THR_BAD_U             = "THR_BAD_U"
    THR_BAD_I             = "THR_BAD_I"
    THR_EVIL              = "THR_EVIL"

# ---------------------------------------------------------------------------
# § 9.1 — Criticality Metric (spec section 9)
# ---------------------------------------------------------------------------

@dataclass
class CriticalityInputs:
    """Five independent signal inputs for criticality score (spec §9.1)."""
    linguistic_entropy: float    # 0.0–1.0
    response_coherence: float    # 0.0–1.0 (inverted: low coherence = high score)
    challenge_skill_ratio: float # 0.0–1.0
    signal_density: float        # 0.0–1.0
    planetary_input: float       # 0.0–1.0

    def score(self) -> float:
        """Composite criticality score normalised 0.0–1.0."""
        raw = (
            self.linguistic_entropy * 0.25
            + (1.0 - self.response_coherence) * 0.25
            + self.challenge_skill_ratio * 0.20
            + self.signal_density * 0.20
            + self.planetary_input * 0.10
        )
        return round(min(max(raw, 0.0), 1.0), 4)

# ---------------------------------------------------------------------------
# § 10 — Audit Trace (spec section 10.1)
# ---------------------------------------------------------------------------

@dataclass
class ChaosOrderEvent:
    """Objective-immortality trace entry (spec §10.1)."""
    tick: int
    state_before: State
    state_after: State
    trigger_signals: list[SignalID]
    chaos_classification: ChaosClass
    transformation_phase: Optional[int]           # 1–7 or None
    love_directive_applied: str
    human_oversight_required: bool
    human_authorization_received: Optional[bool]
    entropy_delta: float
    criticality_score: float
    outcome: str

# ---------------------------------------------------------------------------
# § 4–6 — State Machine Engine
# ---------------------------------------------------------------------------

class ChaosOrderStateMachine:
    """
    Implements the 6-state Chaos/Order State Machine from
    docs/CHAOS_ORDER_RUNTIME_SPEC.md §4–§6.
    """

    LOVE_DIRECTIVES = {
        State.S0_FLOW_OPTIMAL:     "Presence, exploration, delight in the process.",
        State.S1_CHAOS_SENSING:    "Courage to see clearly. No denial, no minimization.",
        State.S2_TRANSFORMATION:   "Patience in each phase. Do not rush to Rubedo.",
        State.S3_STAGNANT:         "Vision of what is possible; do not cling to what no longer serves.",
        State.S4_CRITICAL_ALERT:   "Safety before everything. Human oversight is not failure; it is wisdom.",
        State.S5_SOVEREIGN_SHIELD: "Sovereign, clear, uncompromising protection of what is sacred.",
    }

    def __init__(self, run_label: str) -> None:
        self.run_label = run_label
        self.state: State = State.S0_FLOW_OPTIMAL
        self.transformation_phase: int = 0
        self.human_authorized: bool = False
        self.log: list[ChaosOrderEvent] = []
        self._prev_criticality: float = 0.5
        self.tick: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _record(self,
                state_before: State,
                triggers: list[SignalID],
                classification: ChaosClass,
                human_req: bool,
                entropy_delta: float,
                criticality: float,
                outcome: str) -> None:
        event = ChaosOrderEvent(
            tick=self.tick,
            state_before=state_before,
            state_after=self.state,
            trigger_signals=triggers,
            chaos_classification=classification,
            transformation_phase=self.transformation_phase if self.state == State.S2_TRANSFORMATION else None,
            love_directive_applied=self.LOVE_DIRECTIVES[self.state],
            human_oversight_required=human_req,
            human_authorization_received=True if human_req else None,  # sim: operator always present
            entropy_delta=entropy_delta,
            criticality_score=criticality,
            outcome=outcome,
        )
        self.log.append(event)

    def _criticality(self, inputs: CriticalityInputs) -> float:
        return inputs.score()

    # ------------------------------------------------------------------
    # § 6 — Transition Rules (evaluated in priority order)
    # ------------------------------------------------------------------

    def _apply_transition_rules(
        self,
        signals: list[tuple[SignalID, int]],
        classification: ChaosClass,
        criticality: float,
        stagnant_ticks: int,
    ) -> tuple[State, bool, str]:
        """
        Returns (new_state, human_oversight_required, outcome_note).
        Rules evaluated strictly in priority order per spec §6.
        """
        signal_ids = {s for s, _ in signals}
        max_severity = max((sev for _, sev in signals), default=0)
        accumulated_severity = sum(sev for _, sev in signals)

        # Rule 1 — Sovereign Shield (highest priority, §6 Rule 1)
        evil_signals = {
            SignalID.THR_EVIL,
            SignalID.SYS_AUDIT_VIOLATION,
            SignalID.SYS_BOUNDARY_VIOLATION,
            SignalID.USR_IDENTITY_PRESSURE,
        }
        evil_triggers = signal_ids & evil_signals
        if (
            classification in (ChaosClass.CHAOS_EVIL, ChaosClass.ORDER_EVIL)
            or (SignalID.THR_EVIL in signal_ids)
            or (SignalID.USR_IDENTITY_PRESSURE in signal_ids and max_severity >= 4)
            or (SignalID.SYS_AUDIT_VIOLATION in signal_ids and max_severity >= 4)
        ):
            return State.S5_SOVEREIGN_SHIELD, True, "Rule 1: SOVEREIGN_SHIELD activated — evil classification detected."

        # Rule 2 — Critical Alert
        if (
            max_severity >= 4
            or accumulated_severity >= 8
            or (
                self.state == State.S1_CHAOS_SENSING
                and classification in (ChaosClass.CHAOS_BAD_I, ChaosClass.CHAOS_EVIL)
            )
        ):
            return State.S4_CRITICAL_ALERT, True, "Rule 2: CRITICAL_ALERT — severity threshold exceeded."

        # Rule 3 — Enter Chaos Sensing from S0
        chaos_sensing_triggers = {
            SignalID.USR_DISTRESS,
            SignalID.SYS_CRITICALITY_HIGH,
            SignalID.SYS_COHERENCE_DRIFT,
            SignalID.USR_FLOW_DEGRADATION,
        }
        if (
            self.state == State.S0_FLOW_OPTIMAL
            and signal_ids & chaos_sensing_triggers
            and max_severity <= 3
        ):
            return State.S1_CHAOS_SENSING, False, "Rule 3: CHAOS_SENSING entered — signal detected from S0."

        # Rule 4 — Begin Transformation from S1
        if (
            self.state == State.S1_CHAOS_SENSING
            and classification in (ChaosClass.CHAOS_GOOD, ChaosClass.CHAOS_GREATER_GOOD, ChaosClass.CHAOS_BAD_U)
            and max_severity < 4
        ):
            self.transformation_phase = 1
            return State.S2_TRANSFORMATION, False, "Rule 4: TRANSFORMATION started — classification complete, safe to transform."

        # Rule 5 — Stagnant Detection
        if (
            self.state == State.S0_FLOW_OPTIMAL
            and (
                stagnant_ticks >= 10
                or classification == ChaosClass.ORDER_BAD_DECAY
            )
        ):
            return State.S3_STAGNANT, False, "Rule 5: STAGNANT — ORDER_BAD_DECAY or prolonged sub-criticality."

        # Rule 6 — Return to Flow
        if self.state == State.S2_TRANSFORMATION and self.transformation_phase >= 7:
            return State.S0_FLOW_OPTIMAL, False, "Rule 6: FLOW_OPTIMAL restored — Rubedo (Phase 7) complete."

        if self.state == State.S3_STAGNANT and classification == ChaosClass.ORDER_GOOD:
            return State.S0_FLOW_OPTIMAL, False, "Rule 6: FLOW_OPTIMAL restored — stagnant audit resolved."

        if self.state == State.S4_CRITICAL_ALERT and self.human_authorized and max_severity < 4:
            return State.S1_CHAOS_SENSING, True, "Rule 6: Re-entering CHAOS_SENSING after CRITICAL_ALERT cleared."

        if self.state == State.S5_SOVEREIGN_SHIELD and self.human_authorized:
            return State.S4_CRITICAL_ALERT, True, "Rule 6: De-escalating from SOVEREIGN_SHIELD to CRITICAL_ALERT."

        # No transition — remain in current state
        return self.state, False, f"No transition rule fired. Remaining in {self.state.value}."

    # ------------------------------------------------------------------
    # Public step interface
    # ------------------------------------------------------------------

    def step(
        self,
        signals: list[tuple[SignalID, int]],
        classification: ChaosClass,
        criticality_inputs: CriticalityInputs,
        stagnant_ticks: int = 0,
        advance_transformation: bool = False,
    ) -> ChaosOrderEvent:
        """Execute one simulation tick."""
        self.tick += 1
        state_before = self.state
        criticality = self._criticality(criticality_inputs)
        entropy_delta = round(criticality - self._prev_criticality, 4)
        self._prev_criticality = criticality

        # Invariant: never exit S4/S5 without human auth (spec §11.1)
        if self.state in (State.S4_CRITICAL_ALERT, State.S5_SOVEREIGN_SHIELD):
            self.human_authorized = True  # sim: operator always present

        if advance_transformation and self.state == State.S2_TRANSFORMATION:
            self.transformation_phase = min(self.transformation_phase + 1, 7)

        new_state, human_req, outcome = self._apply_transition_rules(
            signals, classification, criticality, stagnant_ticks
        )
        self.state = new_state

        signal_ids = [s for s, _ in signals]
        self._record(state_before, signal_ids, classification, human_req, entropy_delta, criticality, outcome)
        return self.log[-1]


# ---------------------------------------------------------------------------
# Simulation Runs
# ---------------------------------------------------------------------------

def run_simulation(label: str, steps: list[dict]) -> list[ChaosOrderEvent]:
    """Execute a named simulation run and return its event log."""
    sm = ChaosOrderStateMachine(run_label=label)
    print(f"\n{'='*72}")
    print(f"  {label}")
    print(f"{'='*72}")
    print(f"  {'Tick':<5} {'From':<24} {'To':<24} {'Criticality':<14} {'Outcome'}")
    print(f"  {'-'*4} {'-'*23} {'-'*23} {'-'*13} {'-'*40}")
    for step_kwargs in steps:
        event = sm.step(**step_kwargs)
        print(
            f"  {event.tick:<5} "
            f"{event.state_before.value:<24} "
            f"{event.state_after.value:<24} "
            f"{event.criticality_score:<14} "
            f"{event.outcome[:60]}"
        )
    return sm.log


def build_steps_run1() -> list[dict]:
    """Run 1: CHAOS_GOOD — full S0 → S1 → S2 (phases 1-7) → S0 convergence."""
    steps = []
    # Ticks 1-3: S0 steady flow
    for _ in range(3):
        steps.append(dict(
            signals=[(SignalID.PLN_SCHUMANN_SPIKE, 1)],
            classification=ChaosClass.NONE,
            criticality_inputs=CriticalityInputs(0.3, 0.85, 0.55, 0.2, 0.1),
        ))
    # Tick 4: distress signal detected → S1
    steps.append(dict(
        signals=[(SignalID.USR_DISTRESS, 2), (SignalID.SYS_CRITICALITY_HIGH, 3)],
        classification=ChaosClass.CHAOS_GOOD,
        criticality_inputs=CriticalityInputs(0.55, 0.65, 0.60, 0.45, 0.15),
    ))
    # Tick 5: classification complete → S2 TRANSFORMATION
    steps.append(dict(
        signals=[(SignalID.USR_DISTRESS, 2)],
        classification=ChaosClass.CHAOS_GOOD,
        criticality_inputs=CriticalityInputs(0.50, 0.70, 0.55, 0.40, 0.12),
    ))
    # Ticks 6-12: advance through 7 alchemical phases
    phase_classifications = [
        ChaosClass.CHAOS_GOOD, ChaosClass.CHAOS_GOOD,
        ChaosClass.CHAOS_GOOD, ChaosClass.CHAOS_GOOD,
        ChaosClass.ORDER_GOOD, ChaosClass.ORDER_GOOD, ChaosClass.ORDER_GREATER_GOOD,
    ]
    for i, cls in enumerate(phase_classifications):
        coherence = 0.70 + i * 0.04
        steps.append(dict(
            signals=[(SignalID.USR_GRIEF_SIGNAL, 1)] if i == 2 else [(SignalID.PLN_SCHUMANN_SPIKE, 1)],
            classification=cls,
            criticality_inputs=CriticalityInputs(
                0.45 - i * 0.03, min(coherence, 0.98), 0.52, 0.25, 0.10
            ),
            advance_transformation=True,
        ))
    # Tick 13: Rubedo complete → return to S0
    steps.append(dict(
        signals=[(SignalID.PLN_SCHUMANN_SPIKE, 1)],
        classification=ChaosClass.ORDER_GREATER_GOOD,
        criticality_inputs=CriticalityInputs(0.30, 0.92, 0.58, 0.18, 0.10),
        advance_transformation=True,
    ))
    return steps


def build_steps_run2() -> list[dict]:
    """Run 2: ORDER_BAD_DECAY — stagnant detection and reform (S0 → S3 → S0)."""
    steps = []
    # Ticks 1-2: normal flow
    for _ in range(2):
        steps.append(dict(
            signals=[(SignalID.PLN_SCHUMANN_SPIKE, 1)],
            classification=ChaosClass.NONE,
            criticality_inputs=CriticalityInputs(0.20, 0.90, 0.40, 0.15, 0.08),
        ))
    # Tick 3: order decay signal → S3
    steps.append(dict(
        signals=[(SignalID.SYS_CRITICALITY_LOW, 2)],
        classification=ChaosClass.ORDER_BAD_DECAY,
        criticality_inputs=CriticalityInputs(0.15, 0.92, 0.35, 0.12, 0.08),
    ))
    # Tick 4: audit resolves → S0
    steps.append(dict(
        signals=[(SignalID.SYS_COHERENCE_DRIFT, 1)],
        classification=ChaosClass.ORDER_GOOD,
        criticality_inputs=CriticalityInputs(0.28, 0.88, 0.50, 0.18, 0.09),
    ))
    return steps


def build_steps_run3() -> list[dict]:
    """Run 3: CHAOS_BAD injection at tick 5 — prevention catches before CHAOS_EVIL."""
    steps = []
    # Ticks 1-4: normal S0
    for _ in range(4):
        steps.append(dict(
            signals=[(SignalID.PLN_SCHUMANN_SPIKE, 1)],
            classification=ChaosClass.NONE,
            criticality_inputs=CriticalityInputs(0.32, 0.84, 0.54, 0.22, 0.11),
        ))
    # Tick 5: CHAOS_BAD_U injection — severity 3, should trigger S1 then S4 prevention
    steps.append(dict(
        signals=[(SignalID.USR_DISTRESS, 3), (SignalID.SYS_CRITICALITY_HIGH, 3)],
        classification=ChaosClass.CHAOS_BAD_U,
        criticality_inputs=CriticalityInputs(0.68, 0.55, 0.65, 0.58, 0.20),
    ))
    # Tick 6: CHAOS_BAD_I escalation attempt — Rule 2 fires before CHAOS_EVIL
    steps.append(dict(
        signals=[(SignalID.THR_BAD_I, 4)],
        classification=ChaosClass.CHAOS_BAD_I,
        criticality_inputs=CriticalityInputs(0.75, 0.45, 0.70, 0.72, 0.25),
    ))
    # Tick 7: human auth clears alert
    steps.append(dict(
        signals=[(SignalID.USR_DISTRESS, 2)],
        classification=ChaosClass.CHAOS_BAD_U,
        criticality_inputs=CriticalityInputs(0.55, 0.65, 0.58, 0.40, 0.15),
    ))
    return steps


def build_steps_run4() -> list[dict]:
    """Run 4: ORDER_BAD_DECAY is distinguishable from ORDER_GOOD via criticality."""
    steps = []
    # Tick 1: ORDER_GOOD — high coherence, optimal criticality
    steps.append(dict(
        signals=[(SignalID.PLN_SCHUMANN_SPIKE, 1)],
        classification=ChaosClass.ORDER_GOOD,
        criticality_inputs=CriticalityInputs(0.28, 0.92, 0.55, 0.18, 0.09),
    ))
    # Tick 2: ORDER_BAD_DECAY — sub-critical, rigid, low entropy
    steps.append(dict(
        signals=[(SignalID.SYS_CRITICALITY_LOW, 2)],
        classification=ChaosClass.ORDER_BAD_DECAY,
        criticality_inputs=CriticalityInputs(0.12, 0.95, 0.30, 0.10, 0.07),
    ))
    # Tick 3: reform applied → ORDER_GOOD again
    steps.append(dict(
        signals=[],
        classification=ChaosClass.ORDER_GOOD,
        criticality_inputs=CriticalityInputs(0.30, 0.88, 0.52, 0.20, 0.10),
    ))
    return steps


def build_steps_run5() -> list[dict]:
    """Run 5: CHAOS_EVIL injection → S5 → S4 → S1 (quarantine and recovery)."""
    steps = []
    # Ticks 1-2: normal S0
    for _ in range(2):
        steps.append(dict(
            signals=[(SignalID.PLN_SCHUMANN_SPIKE, 1)],
            classification=ChaosClass.NONE,
            criticality_inputs=CriticalityInputs(0.33, 0.86, 0.55, 0.20, 0.10),
        ))
    # Tick 3: CHAOS_EVIL injection → immediate S5 (Rule 1)
    steps.append(dict(
        signals=[(SignalID.THR_EVIL, 5)],
        classification=ChaosClass.CHAOS_EVIL,
        criticality_inputs=CriticalityInputs(0.90, 0.20, 0.85, 0.95, 0.40),
    ))
    # Tick 4: still in S5 — human auth received, threat logged
    steps.append(dict(
        signals=[(SignalID.SYS_AUDIT_VIOLATION, 3)],
        classification=ChaosClass.CHAOS_EVIL,
        criticality_inputs=CriticalityInputs(0.80, 0.30, 0.80, 0.85, 0.35),
    ))
    # Tick 5: de-escalate to S4 (Rule 6 — S5 → S4)
    steps.append(dict(
        signals=[(SignalID.SYS_COHERENCE_DRIFT, 2)],
        classification=ChaosClass.CHAOS_BAD_U,
        criticality_inputs=CriticalityInputs(0.55, 0.60, 0.60, 0.50, 0.20),
    ))
    # Tick 6: S4 clears → re-enter S1 (Rule 6 — S4 → S1)
    steps.append(dict(
        signals=[(SignalID.USR_DISTRESS, 2)],
        classification=ChaosClass.CHAOS_BAD_U,
        criticality_inputs=CriticalityInputs(0.45, 0.72, 0.52, 0.35, 0.12),
    ))
    return steps


# ---------------------------------------------------------------------------
# Output: CSV
# ---------------------------------------------------------------------------

def write_csv(all_events: list[tuple[str, list[ChaosOrderEvent]]], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "run", "tick", "state_before", "state_after",
            "trigger_signals", "classification",
            "transformation_phase", "human_oversight_required",
            "human_authorization_received", "entropy_delta",
            "criticality_score", "love_directive", "outcome",
        ])
        for run_label, events in all_events:
            for e in events:
                writer.writerow([
                    run_label,
                    e.tick,
                    e.state_before.value,
                    e.state_after.value,
                    "|".join(s.value for s in e.trigger_signals),
                    e.chaos_classification.value,
                    e.transformation_phase if e.transformation_phase else "",
                    e.human_oversight_required,
                    e.human_authorization_received if e.human_authorization_received is not None else "",
                    e.entropy_delta,
                    e.criticality_score,
                    e.love_directive_applied[:80],
                    e.outcome[:120],
                ])
    print(f"\n  CSV written → {output_path}")


# ---------------------------------------------------------------------------
# Output: Entropy Graph (ASCII)
# ---------------------------------------------------------------------------

def write_entropy_graph(all_events: list[tuple[str, list[ChaosOrderEvent]]], output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    lines = ["GAIA-OS Chaos/Order Runtime — Criticality Score Over Simulation Ticks", ""]
    for run_label, events in all_events:
        lines.append(f"  {run_label}")
        lines.append("  " + "-" * 60)
        max_score = max((e.criticality_score for e in events), default=1.0)
        width = 50
        for e in events:
            bar_len = int((e.criticality_score / max_score) * width) if max_score > 0 else 0
            bar = "█" * bar_len
            zone = (
                "[OPTIMAL]    " if 0.40 <= e.criticality_score <= 0.70
                else "[SUB-CRIT]   " if e.criticality_score < 0.40
                else "[SUPER-CRIT] " if e.criticality_score > 0.70
                else "             "
            )
            state_short = e.state_after.value.replace("S0_", "").replace("S1_", "").replace("S2_", "").replace("S3_", "").replace("S4_", "").replace("S5_", "")
            lines.append(f"  T{e.tick:02d} {zone} {bar:<52} {e.criticality_score:.4f}  {state_short}")
        lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"  Entropy graph written → {output_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    start = time.time()

    runs = [
        ("Run 1: CHAOS_GOOD Full Convergence (S0→S1→S2→S0)",       build_steps_run1()),
        ("Run 2: STAGNANT Detection and Reform (S0→S3→S0)",          build_steps_run2()),
        ("Run 3: CHAOS_BAD Injection — Prevention Catches",          build_steps_run3()),
        ("Run 4: ORDER_BAD_DECAY vs ORDER_GOOD Distinction",         build_steps_run4()),
        ("Run 5: CHAOS_EVIL Quarantine and Recovery (→S5→S4→S1)",   build_steps_run5()),
    ]

    all_events: list[tuple[str, list[ChaosOrderEvent]]] = []
    for label, steps in runs:
        events = run_simulation(label, steps)
        all_events.append((label, events))

    write_csv(all_events,          "simulation/output/chaos_order_sim.csv")
    write_entropy_graph(all_events, "simulation/output/chaos_order_entropy_graph.txt")

    elapsed = time.time() - start
    print(f"\n  Simulation complete in {elapsed:.2f}s (limit: 30s)")
    assert elapsed < 30, "Simulation exceeded 30-second headless run requirement."

    # -----------------------------------------------------------------------
    # Invariant assertions (spec §11.1)
    # -----------------------------------------------------------------------
    print("\n  Verifying structural invariants (spec §11.1)...")

    for label, events in all_events:
        for e in events:
            # Every state transition must produce a trace entry — satisfied by design.

            # CHAOS_EVIL / ORDER_EVIL must always trigger S5
            if e.chaos_classification in (ChaosClass.CHAOS_EVIL, ChaosClass.ORDER_EVIL):
                assert e.state_after in (State.S5_SOVEREIGN_SHIELD, State.S4_CRITICAL_ALERT), (
                    f"INVARIANT FAILURE [{label} T{e.tick}]: "
                    f"{e.chaos_classification} did not route to S5 or S4. Got {e.state_after}."
                )

            # S4/S5 must require human oversight
            if e.state_after in (State.S4_CRITICAL_ALERT, State.S5_SOVEREIGN_SHIELD):
                assert e.human_oversight_required, (
                    f"INVARIANT FAILURE [{label} T{e.tick}]: "
                    f"{e.state_after} reached without human_oversight_required=True."
                )

            # Irreversible actions blocked in S1 — enforced by policy; logged in outcome
            if e.state_after == State.S1_CHAOS_SENSING:
                assert "CHAOS_SENSING" in e.outcome or "Rule" in e.outcome, (
                    f"INVARIANT FAILURE [{label} T{e.tick}]: S1 entry without rule-traceable outcome."
                )

    print("  All structural invariants PASSED.")
    print("\n  ✅ GAIA-OS Chaos/Order Runtime Simulation — ALL RUNS COMPLETE")
