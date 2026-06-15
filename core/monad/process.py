"""
Process Monad — core/monad/process.py
Canon: ProcessContext formalisation, session state tracking

Tracks turn-by-turn session state and formalises the ProcessContext
contract into the harmonize() output.
Outputs: turn_count, stage_depth, context_coherence
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


class ProcessMonad(GaiaMonad):
    """
    Tracks session-level process state: turn count, stage depth, coherence.

    Stage depth increases as phi rises through attractor zones.
    Context coherence is derived from phi trend direction.
    """

    monad_type = "process"

    # Stage thresholds mapped to phi ranges from SpectralForceEngine
    _STAGE_THRESHOLDS: list[tuple[float, str]] = [
        (0.05,  "stage_0_nigredo"),
        (0.15,  "stage_1_pyrosis"),
        (0.28,  "stage_2_citrinitas"),
        (0.42,  "stage_3_viriditas"),
        (0.58,  "stage_4_caerulitas"),
        (0.72,  "stage_5_rubedo"),
        (0.85,  "stage_6_iosis"),
        (0.92,  "stage_7_albedo"),
        (0.95,  "stage_8_chrysitas"),
        (0.97,  "stage_9_argentitas"),
        (1.00,  "stage_10_lux_perpetua"),
    ]

    def harmonize(self, ctx: "ProcessContext") -> Optional[dict]:
        phi = getattr(ctx, "coherence_phi", 0.0)
        turn = getattr(ctx, "turn_number", 0) or 0
        session_id = getattr(ctx, "session_id", "unknown")

        # Derive current stage from phi
        current_stage = "stage_0_nigredo"
        stage_depth = 0
        for depth, (threshold, stage_name) in enumerate(self._STAGE_THRESHOLDS):
            if phi <= threshold:
                current_stage = stage_name
                stage_depth = depth
                break
        else:
            current_stage = "stage_10_lux_perpetua"
            stage_depth = 10

        # Context coherence: how stable the current phi is relative to session
        # High turn count with high phi = high context coherence
        context_coherence = round(
            min(1.0, (phi * 0.7) + (min(turn, 20) / 20.0 * 0.3)), 4
        )

        # Session age tier
        if turn < 5:
            session_age = "nascent"
        elif turn < 15:
            session_age = "active"
        elif turn < 40:
            session_age = "deep"
        else:
            session_age = "veteran"

        return {
            "turn_count": turn,
            "stage_depth": stage_depth,
            "current_stage": current_stage,
            "context_coherence": context_coherence,
            "session_id": session_id,
            "session_age": session_age,
        }
