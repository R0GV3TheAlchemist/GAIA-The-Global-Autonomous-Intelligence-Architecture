"""
Shadow Engine — ShadowTimingGate  (Issue #67)

The timing gate is the ONLY place the Shadow Engine decides whether to
surface an observation to the user.  It blocks surfacing when:

  1. Stage < 2 (OBSERVATION) — user not ready
  2. Stage == 1 (OFF) — hard block
  3. alignment_score < MIN_ALIGNMENT_SCORE (default 30) — too dysregulated
  4. arc_stability < MIN_ARC_STABILITY (default 0.25) — emotional arc too volatile
  5. The same observation pattern_type was surfaced within COOLDOWN_DAYS

NOTE: The gate NEVER blocks detection — patterns are always accumulated.
      It only controls the surfacing step.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .types import ShadowMode, STAGE_TO_MODE, ShadowObservation

# ────────────────────────
# Gate thresholds (tune per product spec)
# ────────────────────────
MIN_ALIGNMENT_SCORE : int   = 30      # below this → gate closed
MIN_ARC_STABILITY   : float = 0.25    # below this → gate closed
COOLDOWN_DAYS       : int   = 7       # days between surfacing same pattern_type
MS_PER_DAY          : int   = 86_400_000


@dataclass
class GateResult:
    allowed        : bool
    mode           : ShadowMode
    blocked_reason : Optional[str] = None  # human-readable reason if blocked


class ShadowTimingGate:
    """
    Evaluates whether shadow observations may be surfaced right now.

    Args (constructor):
        min_alignment_score : int    — minimum Schumann alignment score (default 30)
        min_arc_stability   : float  — minimum arc_stability (default 0.25)
        cooldown_days       : int    — inter-surfacing cooldown in days (default 7)
    """

    def __init__(
        self,
        min_alignment_score : int   = MIN_ALIGNMENT_SCORE,
        min_arc_stability   : float = MIN_ARC_STABILITY,
        cooldown_days       : int   = COOLDOWN_DAYS,
    ) -> None:
        self.min_alignment_score = min_alignment_score
        self.min_arc_stability   = min_arc_stability
        self.cooldown_ms         = cooldown_days * MS_PER_DAY

    def evaluate(
        self,
        current_stage      : int,
        alignment_score    : float,
        arc_stability      : float,
        last_surfaced_at   : Optional[int],   # unix ms of last surfacing for this pattern_type
        now_ms             : int,
    ) -> GateResult:
        """
        Returns GateResult.allowed == True only when ALL conditions pass.

        Stage 1 → always blocked (OFF mode).
        Stage 2 → detection allowed but surfacing blocked (OBSERVATION mode).
        Stages 3–5 → surfacing allowed if alignment and stability pass.
        """
        mode = STAGE_TO_MODE.get(current_stage, ShadowMode.OFF)

        if mode == ShadowMode.OFF:
            return GateResult(allowed=False, mode=mode,
                              blocked_reason="Stage 1: Shadow Engine is OFF")

        if mode == ShadowMode.OBSERVATION:
            return GateResult(allowed=False, mode=mode,
                              blocked_reason="Stage 2: observation only — patterns detected but not surfaced")

        if alignment_score < self.min_alignment_score:
            return GateResult(allowed=False, mode=mode,
                              blocked_reason=f"Alignment score {alignment_score:.1f} < {self.min_alignment_score} (gate threshold)")

        if arc_stability < self.min_arc_stability:
            return GateResult(allowed=False, mode=mode,
                              blocked_reason=f"Arc stability {arc_stability:.3f} < {self.min_arc_stability} (emotionally unstable)")

        if last_surfaced_at is not None:
            elapsed = now_ms - last_surfaced_at
            if elapsed < self.cooldown_ms:
                days_remaining = round((self.cooldown_ms - elapsed) / MS_PER_DAY, 1)
                return GateResult(allowed=False, mode=mode,
                                  blocked_reason=f"Cooldown: {days_remaining} days remaining")

        return GateResult(allowed=True, mode=mode)

    def filter(
        self,
        observations        : List[ShadowObservation],
        current_stage       : int,
        alignment_score     : float,
        arc_stability       : float,
        last_surfaced_map   : dict[str, int],  # pattern_type → last surfaced_at ms
        now_ms              : int,
    ) -> tuple[List[ShadowObservation], List[GateResult]]:
        """
        Filter a list of observations through the gate.

        Returns:
            (allowed_observations, gate_results_for_all)
        """
        allowed = []
        results = []
        for obs in observations:
            last = last_surfaced_map.get(obs.pattern_type)
            result = self.evaluate(
                current_stage=current_stage,
                alignment_score=alignment_score,
                arc_stability=arc_stability,
                last_surfaced_at=last,
                now_ms=now_ms,
            )
            results.append(result)
            if result.allowed:
                allowed.append(obs)
        return allowed, results
