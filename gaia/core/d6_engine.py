"""
gaia/core/d6_engine.py
======================
D6 Meta-Coherence Engine — Standalone Layer
Canon reference: GAIA_D6_META_COHERENCE_ENGINE.md, C52 Part II
Issues: #576, #571

This module extracts the D6 mode recommendation logic from GAIAState and
elevates it into a standalone engine with:
  - External probe support (biometrics, Noosphere load, Schumann)
  - Intervention event logging
  - Mode transition history
  - Dimensional health reporting
  - Talisman-aware mode adjustment

Design principle:
  GAIAState is the DATA layer (what is the state).
  D6Engine is the DECISION layer (what should happen given the state).
  They are cleanly separated. D6Engine reads GAIAState; it does not IS GAIAState.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable

from gaia.core.state import GAIAState, GAIAMode


# ---------------------------------------------------------------------------
# Probe types
# ---------------------------------------------------------------------------

@dataclass
class EngineProbes:
    """
    External signals that supplement GAIAState scalar fields.
    All values are optional — the engine degrades gracefully to
    pure GAIAState-based decisions when probes are absent.
    """

    # Biometric probes (C153 / Embodiment Layer)
    heart_rate_variability: Optional[float] = None   # 0.0 (low) → 1.0 (high) normalized
    sleep_quality: Optional[float] = None            # 0.0 → 1.0
    movement_today: Optional[float] = None           # 0.0 → 1.0 normalized daily step count

    # Noosphere probes (C43, #435)
    noosphere_load: Optional[float] = None           # 0.0 (calm) → 1.0 (high collective stress)
    collective_coherence: Optional[float] = None     # 0.0 → 1.0

    # Environmental probes
    schumann_coherence: Optional[float] = None       # 0.0 → 1.0 normalized Schumann resonance quality
    lunar_phase_load: Optional[float] = None         # 0.0 (new, calm) → 1.0 (full, amplified)

    # Session probes
    session_duration_hours: Optional[float] = None  # how long current session has been active
    time_since_rest_hours: Optional[float] = None   # hours since last REST/RECOVER mode

    def to_dict(self) -> Dict[str, Any]:
        return {
            "heart_rate_variability": self.heart_rate_variability,
            "sleep_quality": self.sleep_quality,
            "movement_today": self.movement_today,
            "noosphere_load": self.noosphere_load,
            "collective_coherence": self.collective_coherence,
            "schumann_coherence": self.schumann_coherence,
            "lunar_phase_load": self.lunar_phase_load,
            "session_duration_hours": self.session_duration_hours,
            "time_since_rest_hours": self.time_since_rest_hours,
        }


# ---------------------------------------------------------------------------
# Intervention Event
# ---------------------------------------------------------------------------

@dataclass
class InterventionEvent:
    """
    Logged when D6Engine recommends a mode change or flags a concern.
    These events form the engine's decision audit trail.
    """
    t: float = field(default_factory=time.time)
    previous_mode: Optional[GAIAMode] = None
    recommended_mode: Optional[GAIAMode] = None
    trigger: str = ""           # human-readable reason for the recommendation
    dimensional_flags: Dict[str, bool] = field(default_factory=dict)
    probe_signals: Dict[str, Any] = field(default_factory=dict)
    severity: str = "INFO"      # INFO | WARN | CRITICAL
    auto_applied: bool = False   # whether the engine auto-applied the mode change

    def to_dict(self) -> Dict[str, Any]:
        return {
            "t": self.t,
            "previous_mode": self.previous_mode.value if self.previous_mode else None,
            "recommended_mode": self.recommended_mode.value if self.recommended_mode else None,
            "trigger": self.trigger,
            "dimensional_flags": self.dimensional_flags,
            "probe_signals": self.probe_signals,
            "severity": self.severity,
            "auto_applied": self.auto_applied,
        }


# ---------------------------------------------------------------------------
# D6 Meta-Coherence Engine
# ---------------------------------------------------------------------------

class D6Engine:
    """
    The D6 Meta-Coherence Engine — GAIA's operational awareness layer.

    Responsibilities:
      1. Read GAIAState + external probes
      2. Determine the correct operational mode
      3. Log intervention events with full audit trail
      4. Optionally auto-apply mode changes (configurable)
      5. Provide dimensional health report for frontend HUD

    Usage:
        engine = D6Engine(auto_apply=True)
        event = engine.evaluate(state, probes)
        if event.recommended_mode != state.mode:
            # engine already applied if auto_apply=True
            pass
        report = engine.health_report(state, probes)
    """

    def __init__(
        self,
        auto_apply: bool = False,
        on_intervention: Optional[Callable[[InterventionEvent], None]] = None,
    ):
        """
        Args:
            auto_apply: if True, the engine automatically applies its
              recommended mode to GAIAState. If False, it only logs and
              returns the recommendation.
            on_intervention: optional callback called whenever an
              intervention event is generated. Use for webhooks, logging,
              or real-time frontend notifications.
        """
        self.auto_apply = auto_apply
        self.on_intervention = on_intervention
        self.intervention_log: List[InterventionEvent] = []

    # ------------------------------------------------------------------
    # Core evaluation
    # ------------------------------------------------------------------

    def evaluate(
        self,
        state: GAIAState,
        probes: Optional[EngineProbes] = None,
    ) -> InterventionEvent:
        """
        Evaluate the current state + probes and return an InterventionEvent.
        The event contains the recommended mode, trigger reason, flags, and severity.
        If auto_apply is True, the mode change is applied to state immediately.
        """
        probes = probes or EngineProbes()
        flags = state.dimensional_health

        # --- Probe-augmented overrides ---
        # These can override the pure GAIAState recommendation
        probe_override: Optional[GAIAMode] = self._probe_override(state, probes)

        # --- Base recommendation from GAIAState ---
        base_recommendation = state.recommended_mode()

        # --- Final recommendation ---
        recommended = probe_override if probe_override is not None else base_recommendation

        # --- Determine trigger and severity ---
        trigger, severity = self._explain(state, probes, flags, probe_override)

        event = InterventionEvent(
            previous_mode=state.mode,
            recommended_mode=recommended,
            trigger=trigger,
            dimensional_flags=flags,
            probe_signals={k: v for k, v in probes.to_dict().items() if v is not None},
            severity=severity,
        )

        # --- Auto-apply ---
        if self.auto_apply and recommended != state.mode:
            state.update(mode=recommended)
            event.auto_applied = True

        self.intervention_log.append(event)
        if self.on_intervention:
            self.on_intervention(event)

        return event

    # ------------------------------------------------------------------
    # Probe-augmented override logic
    # ------------------------------------------------------------------

    def _probe_override(
        self,
        state: GAIAState,
        probes: EngineProbes,
    ) -> Optional[GAIAMode]:
        """
        Check external probes for conditions that override the base recommendation.
        Returns a mode override if a probe condition is critical, else None.
        """
        # Long session without rest → REST override
        if (
            probes.session_duration_hours is not None
            and probes.session_duration_hours > 6.0
            and probes.time_since_rest_hours is not None
            and probes.time_since_rest_hours > 5.0
        ):
            return GAIAMode.REST

        # Very low HRV → RECOVER
        if (
            probes.heart_rate_variability is not None
            and probes.heart_rate_variability < 0.2
        ):
            return GAIAMode.RECOVER

        # Poor sleep → REST or RECOVER depending on energy
        if (
            probes.sleep_quality is not None
            and probes.sleep_quality < 0.25
        ):
            return GAIAMode.RECOVER if state.energy < 0.4 else GAIAMode.REST

        # High Noosphere load → PROTECT
        if (
            probes.noosphere_load is not None
            and probes.noosphere_load > 0.8
            and state.mode not in (GAIAMode.PROTECT, GAIAMode.REST, GAIAMode.RECOVER)
        ):
            return GAIAMode.PROTECT

        # Schumann coherence very low → REFLECT (environmental grounding needed)
        if (
            probes.schumann_coherence is not None
            and probes.schumann_coherence < 0.2
            and state.mode in (GAIAMode.BUILD, GAIAMode.CREATE)
        ):
            return GAIAMode.REFLECT

        return None

    # ------------------------------------------------------------------
    # Trigger explanation
    # ------------------------------------------------------------------

    def _explain(
        self,
        state: GAIAState,
        probes: EngineProbes,
        flags: Dict[str, bool],
        probe_override: Optional[GAIAMode],
    ) -> tuple:
        """Returns (trigger: str, severity: str)."""
        if flags["D1_critical"]:
            return "D1 Physical critical — energy below 15%. REST required.", "CRITICAL"
        if flags["D2_distress"] and state.energy < 0.4:
            return "D2 Emotional distress + low energy. RECOVER required.", "CRITICAL"
        if flags["D2_distress"]:
            return "D2 Emotional distress. Stress above 75%. PROTECT or RECOVER.", "WARN"
        if flags["D3_saturated"]:
            return "D3 Mental saturated. High entropy + low energy. Simplify or rest.", "WARN"
        if probe_override == GAIAMode.REST and probes.session_duration_hours:
            return (
                f"Session active {probes.session_duration_hours:.1f}h without rest. "
                f"Human sovereignty requires recovery. (Architect Protocol #578)",
                "WARN",
            )
        if probe_override == GAIAMode.RECOVER and probes.heart_rate_variability:
            return "Low HRV detected. Physiological recovery signal.", "WARN"
        if probe_override == GAIAMode.PROTECT and probes.noosphere_load:
            return (
                f"High Noosphere load ({probes.noosphere_load:.2f}). "
                "Collective field stress — boundary holding recommended.",
                "INFO",
            )
        if flags["D6_approaching"]:
            return "D6 Unity approaching. Meta-Field conditions optimal. INTEGRATE.", "INFO"
        if state.mode == state.recommended_mode():
            return "Current mode is optimal for present state.", "INFO"
        return "Mode recommendation based on GAIAState field analysis.", "INFO"

    # ------------------------------------------------------------------
    # Health report
    # ------------------------------------------------------------------

    def health_report(
        self,
        state: GAIAState,
        probes: Optional[EngineProbes] = None,
    ) -> Dict[str, Any]:
        """
        Full dimensional health report for the frontend HUD.
        This is the primary data payload for the State HUD component.
        """
        probes = probes or EngineProbes()
        event = self.evaluate(state, probes)

        return {
            "state": state.to_dict(include_history=False),
            "dimensional_health": state.dimensional_health,
            "priority_dimension": state.priority_dimension,
            "current_mode": state.mode.value,
            "recommended_mode": event.recommended_mode.value if event.recommended_mode else None,
            "mode_is_optimal": state.mode == event.recommended_mode,
            "latest_intervention": event.to_dict(),
            "intervention_count": len(self.intervention_log),
            "probe_signals": probes.to_dict(),
            "report_time": time.time(),
        }

    # ------------------------------------------------------------------
    # Intervention log access
    # ------------------------------------------------------------------

    def recent_interventions(
        self, n: int = 10
    ) -> List[Dict[str, Any]]:
        """Return the n most recent intervention events as dicts."""
        return [e.to_dict() for e in self.intervention_log[-n:]]

    def critical_interventions(self) -> List[Dict[str, Any]]:
        """Return all CRITICAL interventions from this session."""
        return [
            e.to_dict()
            for e in self.intervention_log
            if e.severity == "CRITICAL"
        ]
