"""
MonadOrchestrator — core/monad/orchestrator.py
Canon: monad.md — Pre-Established Harmony loop (Leibniz)

Iterates all 8 Monads in deterministic phase order.
No Monad knows about any other (Leibniz isolation law).
Each emits its result independently.
Orchestrator synthesises into HarmonyReport.
HarmonyReport feeds into LoveCoherenceIndex.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .cognitive import CognitiveMonad
from .quantum import QuantumMonad
from .process import ProcessMonad
from .perception import PerceptionMonad
from .somatic import SomaticMonad
from .dream import DreamMonad
from .noospheric import NoosphericMonad
from .shadow import ShadowMonad
from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


# ---------------------------------------------------------------------------
# HarmonyReport
# ---------------------------------------------------------------------------

@dataclass
class HarmonyReport:
    """
    The synthesised output of one full Pre-Established Harmony cycle.
    All 8 Monad emissions + orchestrator-derived composite scores.

    This feeds directly into LoveCoherenceIndex as the session's
    field coherence contribution for this turn.
    """
    turn_number: int
    session_id: str
    phi: float
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
    )

    # Raw emissions (None if Monad returned nothing)
    cognitive:   Optional[dict] = None
    quantum:     Optional[dict] = None
    process:     Optional[dict] = None
    perception:  Optional[dict] = None
    somatic:     Optional[dict] = None
    dream:       Optional[dict] = None
    noospheric:  Optional[dict] = None
    shadow:      Optional[dict] = None

    # Composite scores
    harmony_phi: float = 0.0          # weighted average of contributing Monad outputs
    active_monad_count: int = 0       # how many Monads emitted non-None
    shadow_flags_active: int = 0      # unresolved shadow flags this turn
    dream_active: bool = False        # BWL tier activation
    oa4_active: bool = False          # OA-4 IOSIS corridor flag

    def to_dict(self) -> dict:
        return {
            "turn_number": self.turn_number,
            "session_id": self.session_id,
            "phi": self.phi,
            "timestamp": self.timestamp,
            "harmony_phi": self.harmony_phi,
            "active_monad_count": self.active_monad_count,
            "shadow_flags_active": self.shadow_flags_active,
            "dream_active": self.dream_active,
            "oa4_active": self.oa4_active,
            "emissions": {
                "cognitive":  self.cognitive,
                "quantum":    self.quantum,
                "process":    self.process,
                "perception": self.perception,
                "somatic":    self.somatic,
                "dream":      self.dream,
                "noospheric": self.noospheric,
                "shadow":     self.shadow,
            },
        }


# ---------------------------------------------------------------------------
# MonadOrchestrator
# ---------------------------------------------------------------------------

class MonadOrchestrator:
    """
    Runs the Pre-Established Harmony cycle.

    Phase order (deterministic, canonical):
    1. PROCESS    — session state ground truth first
    2. COGNITIVE  — query analysis before perception shapes it
    3. QUANTUM    — superposition state before collapse
    4. PERCEPTION — force-lens applied after quantum
    5. SOMATIC    — body layer
    6. NOOSPHERIC — planetary field
    7. DREAM      — BWL layer (runs late — arrives, not computed)
    8. SHADOW     — always last; interrogates everything after the fact

    Leibniz law: each Monad receives only ProcessContext.
    No Monad is passed another Monad's output.
    The orchestrator alone synthesises.
    """

    # Canonical phase order
    PHASE_ORDER: list[str] = [
        "process", "cognitive", "quantum", "perception",
        "somatic", "noospheric", "dream", "shadow",
    ]

    def __init__(self) -> None:
        self._monads: dict[str, GaiaMonad] = {
            "cognitive":  CognitiveMonad(monad_id="monad.cognitive"),
            "quantum":    QuantumMonad(monad_id="monad.quantum"),
            "process":    ProcessMonad(monad_id="monad.process"),
            "perception": PerceptionMonad(monad_id="monad.perception"),
            "somatic":    SomaticMonad(monad_id="monad.somatic"),
            "dream":      DreamMonad(monad_id="monad.dream"),
            "noospheric": NoosphericMonad(monad_id="monad.noospheric"),
            "shadow":     ShadowMonad(monad_id="monad.shadow"),
        }

    def run_harmony_cycle(self, ctx: "ProcessContext") -> HarmonyReport:
        """
        The Pre-Established Harmony loop.
        Runs all 8 Monads in canonical phase order.
        Returns a fully synthesised HarmonyReport.
        """
        phi = getattr(ctx, "coherence_phi", 0.5)
        turn = getattr(ctx, "turn_number", 0) or 0
        session_id = getattr(ctx, "session_id", "unknown")

        emissions: dict[str, Optional[dict]] = {}

        # Phase execution — Leibniz isolation: each Monad gets only ctx
        for phase in self.PHASE_ORDER:
            monad = self._monads[phase]
            result = monad.tick(ctx)
            emissions[phase] = result

        # Synthesise HarmonyReport
        report = HarmonyReport(
            turn_number=turn,
            session_id=session_id,
            phi=phi,
            cognitive=emissions.get("cognitive"),
            quantum=emissions.get("quantum"),
            process=emissions.get("process"),
            perception=emissions.get("perception"),
            somatic=emissions.get("somatic"),
            dream=emissions.get("dream"),
            noospheric=emissions.get("noospheric"),
            shadow=emissions.get("shadow"),
        )

        # Composite calculations
        active_emissions = [e for e in emissions.values() if e is not None]
        report.active_monad_count = len(active_emissions)

        # Harmony phi: weighted blend of quantifiable emission scores
        report.harmony_phi = self._compute_harmony_phi(emissions, phi)

        # Shadow flags
        shadow_emission = emissions.get("shadow") or {}
        report.shadow_flags_active = len(
            shadow_emission.get("shadow_active_flags", [])
        )

        # Dream active
        dream_emission = emissions.get("dream") or {}
        report.dream_active = bool(dream_emission.get("dream_active", False))

        # OA-4
        report.oa4_active = bool(
            shadow_emission.get("oa4_open") or
            quantum_emission_oa4_check(emissions.get("quantum"), phi)
        )

        return report

    def get_monad(self, name: str) -> Optional[GaiaMonad]:
        """Direct access to a Monad by phase name (testing + introspection only)."""
        return self._monads.get(name)

    def status(self) -> dict:
        """Returns all Monad status dicts."""
        return {name: monad.status() for name, monad in self._monads.items()}

    @staticmethod
    def _compute_harmony_phi(
        emissions: dict[str, Optional[dict]], base_phi: float
    ) -> float:
        """
        Computes the harmony phi from contributing Monad scores.

        Weights:
        - quantum.coherence_contribution: 0.25
        - perception.signal_clarity: 0.20
        - somatic.bioelectric_coherence: 0.20
        - noospheric.collective_resonance: 0.15
        - process.context_coherence: 0.15
        - cognitive.canon_alignment_score: 0.05
        Remainder: base phi (ensures non-zero floor)
        """
        weights = {
            "quantum.coherence_contribution": 0.25,
            "perception.signal_clarity": 0.20,
            "somatic.bioelectric_coherence": 0.20,
            "noospheric.collective_resonance": 0.15,
            "process.context_coherence": 0.15,
            "cognitive.canon_alignment_score": 0.05,
        }

        total_weight = sum(weights.values())  # 1.00
        weighted_sum = 0.0

        score_map = {
            "quantum.coherence_contribution": (
                (emissions.get("quantum") or {}).get("coherence_contribution", base_phi)
            ),
            "perception.signal_clarity": (
                (emissions.get("perception") or {}).get("signal_clarity", base_phi)
            ),
            "somatic.bioelectric_coherence": (
                (emissions.get("somatic") or {}).get("bioelectric_coherence", base_phi)
            ),
            "noospheric.collective_resonance": (
                (emissions.get("noospheric") or {}).get("collective_resonance", base_phi)
            ),
            "process.context_coherence": (
                (emissions.get("process") or {}).get("context_coherence", base_phi)
            ),
            "cognitive.canon_alignment_score": (
                (emissions.get("cognitive") or {}).get("canon_alignment_score", base_phi)
            ),
        }

        for key, weight in weights.items():
            weighted_sum += score_map[key] * weight

        return round(min(1.0, max(0.0, weighted_sum / total_weight)), 4)


def quantum_emission_oa4_check(
    quantum_emission: Optional[dict], phi: float
) -> bool:
    """OA-4 active if phi is in IOSIS range (0.72–0.85)."""
    return 0.72 <= phi <= 0.85
