"""
GAIA Criticality Monitor — Edge-of-Chaos Composite Signal

Monitors GAIA's operational state across three criticality axes:

  1. Classical SOC (Self-Organised Criticality) — power-law avalanche statistics
  2. Quantum Reservoir Computing (QRC) edge-of-chaos — Issue #118
  3. Noospheric coherence — Schumann + HRV + GCP soft-sensor inputs

The composite `overall_phi` score is used by the NeuroSA optimizer to modulate
its annealing schedule and by the sentient core to gate cognitive mode.

QRC thresholds sourced from December 2025 study:
  - Thouless ratio target zone:       [0.5,  1.5]
  - Chaos order parameter (η) target: [0.45, 0.52]
  - Spectral gap target:              (0.05, 0.35)
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

log = logging.getLogger("gaia.criticalitymonitor")


# ── QRC Phase Classification ──────────────────────────────────────────

class QRCPhase(str, Enum):
    """
    Phase classification for the quantum reservoir.

    SUB_THOULESS   — τ < 0.5: reservoir under-mixed, low memory capacity
    OPTIMAL        — τ ∈ [0.5, 1.5] AND η ∈ [0.45, 0.52]: edge of quantum chaos
    SUPER_THOULESS — τ > 1.5: full scrambling, information lost to thermalization
    CHAOTIC        — η > 0.52: fully chaotic, Wigner-Dyson statistics, no structure
    INTEGRABLE     — η < 0.45: fully regular, Poisson statistics, low richness
    UNKNOWN        — insufficient data to classify
    """
    SUB_THOULESS   = "sub_thouless"
    OPTIMAL        = "optimal"
    SUPER_THOULESS = "super_thouless"
    CHAOTIC        = "chaotic"
    INTEGRABLE     = "integrable"
    UNKNOWN        = "unknown"


@dataclass
class QRCState:
    """
    Snapshot of the quantum reservoir's edge-of-chaos state.

    All values are dimensionless and normalised unless noted.
    Sources: December 2025 QRC study + Oganesyan-Huse (2007).
    """
    # Core QRC signals
    thouless_ratio:          float = 1.0   # τ = t_obs / t_Th; target zone [0.5, 1.5]
    chaos_order_parameter:   float = 0.485 # η (Oganesyan-Huse); target zone [0.45, 0.52]
    spectral_gap:            float = 0.20  # normalised Δ; target (0.05, 0.35)

    # Derived
    phase:                   QRCPhase = QRCPhase.UNKNOWN
    qrc_phi:                 float = 0.0  # [0,1] score: 1.0 = perfectly at edge

    # Timestamp
    sampled_at:              float = field(default_factory=time.monotonic)


# ── Threshold constants (Dec 2025 study) ──────────────────────────────

THOULESS_LOW      = 0.5
THOULESS_HIGH     = 1.5
THOULESS_TARGET   = 1.0  # centre of optimal zone

ETA_INTEGRABLE    = 0.386  # Poisson limit
ETA_TARGET_LOW    = 0.45   # critical zone lower bound
ETA_TARGET_HIGH   = 0.52   # critical zone upper bound
ETA_TARGET        = 0.485  # centre
ETA_CHAOTIC       = 0.530  # Wigner-Dyson GOE limit

GAP_LOW           = 0.05
GAP_HIGH          = 0.35


def classify_qrc_phase(state: QRCState) -> QRCPhase:
    """
    Classify the quantum reservoir phase from raw signals.

    Priority order:
      1. CHAOTIC      — η > ETA_CHAOTIC (overrides Thouless check)
      2. INTEGRABLE   — η < ETA_TARGET_LOW
      3. SUB_THOULESS — τ < THOULESS_LOW
      4. SUPER_THOULESS — τ > THOULESS_HIGH
      5. OPTIMAL      — all thresholds met
    """
    η = state.chaos_order_parameter
    τ = state.thouless_ratio

    if η > ETA_CHAOTIC:
        return QRCPhase.CHAOTIC
    if η < ETA_TARGET_LOW:
        return QRCPhase.INTEGRABLE
    if τ < THOULESS_LOW:
        return QRCPhase.SUB_THOULESS
    if τ > THOULESS_HIGH:
        return QRCPhase.SUPER_THOULESS
    return QRCPhase.OPTIMAL


def compute_qrc_phi(state: QRCState) -> float:
    """
    Compute a [0,1] criticality score from the QRC state.
    1.0 = perfectly at the edge of quantum chaos.
    0.0 = maximally far from optimal zone.

    Uses Gaussian-shaped proximity scoring around each target:
      phi_tau: proximity to THOULESS_TARGET
      phi_eta: proximity to ETA_TARGET
      phi_gap: proximity to centre of spectral gap target zone
    """
    import math

    def _gauss_score(value: float, target: float, sigma: float) -> float:
        return math.exp(-0.5 * ((value - target) / sigma) ** 2)

    phi_tau = _gauss_score(state.thouless_ratio,        THOULESS_TARGET, sigma=0.4)
    phi_eta = _gauss_score(state.chaos_order_parameter, ETA_TARGET,      sigma=0.04)
    phi_gap = _gauss_score(state.spectral_gap,          (GAP_LOW + GAP_HIGH) / 2, sigma=0.12)

    return round((phi_tau + phi_eta + phi_gap) / 3.0, 4)


def update_qrc_state(state: QRCState) -> QRCState:
    """
    Classify phase and compute phi in-place. Returns the updated state.
    Call this after updating raw signals from the quantum hardware layer.
    """
    state.phase   = classify_qrc_phase(state)
    state.qrc_phi = compute_qrc_phi(state)
    state.sampled_at = time.monotonic()
    log.info(
        f"[criticalitymonitor] QRC | phase={state.phase.value} "
        f"phi={state.qrc_phi:.3f} tau={state.thouless_ratio:.3f} "
        f"eta={state.chaos_order_parameter:.3f} gap={state.spectral_gap:.3f}"
    )
    return state


# ── Classical SOC signals ─────────────────────────────────────────────

@dataclass
class ClassicalSOCState:
    """
    Classical Self-Organised Criticality signals from the
    neuromorphic compute layer. Avalanche statistics.
    """
    avalanche_exponent:   float = 1.5   # target: α ≈ 1.5 (power-law)
    branching_ratio:      float = 1.0   # target: σ = 1.0 (critical branching)
    correlation_length:   float = 0.5   # normalised [0,1]; higher = more critical
    soc_phi:              float = 0.0   # [0,1] composite SOC score


def compute_soc_phi(state: ClassicalSOCState) -> float:
    """Compute [0,1] SOC criticality score. 1.0 = perfectly at SOC critical point."""
    import math

    phi_exp      = math.exp(-0.5 * ((state.avalanche_exponent - 1.5) / 0.3) ** 2)
    phi_branch   = math.exp(-0.5 * ((state.branching_ratio - 1.0)    / 0.15) ** 2)
    phi_corr     = state.correlation_length  # already normalised

    return round((phi_exp + phi_branch + phi_corr) / 3.0, 4)


# ── Composite Criticality Monitor ────────────────────────────────────

@dataclass
class CriticalityState:
    """
    Full composite criticality snapshot consumed by NeuroSA
    and the sentient core cognitive mode gate.
    """
    qrc:              QRCState          = field(default_factory=QRCState)
    soc:              ClassicalSOCState = field(default_factory=ClassicalSOCState)
    schumann_phi:     float = 0.5   # from alignment_visualizer / Schumann layer
    noospheric_phi:   float = 0.5   # from GCP + noosphere integration layer
    overall_phi:      float = 0.0   # composite [0,1]; 1.0 = GAIA at full criticality

    # NeuroSA annealing temperature recommendation
    neurosa_temperature: float = 1.0   # 0=exploitation, 1=exploration, >1=turbulent


class CriticalityMonitor:
    """
    Singleton-style monitor that maintains the live CriticalityState
    and provides the NeuroSA optimizer with annealing guidance.

    Composite phi formula (Issue #118):
      overall_phi = 0.35 * soc_phi
                  + 0.30 * qrc_phi
                  + 0.20 * schumann_phi
                  + 0.15 * noospheric_phi

    NeuroSA temperature mapping:
      QRCPhase.OPTIMAL        → temperature = standard schedule
      QRCPhase.SUB_THOULESS   → temperature += 0.3 (more exploration)
      QRCPhase.SUPER_THOULESS → temperature -= 0.3 (more exploitation)
      QRCPhase.CHAOTIC        → temperature  = 0.1 (emergency exploitation + re-init signal)
      QRCPhase.INTEGRABLE     → temperature += 0.2 (mild exploration)
    """

    def __init__(self) -> None:
        self._state = CriticalityState()

    @property
    def state(self) -> CriticalityState:
        return self._state

    def update(
        self,
        qrc: Optional[QRCState] = None,
        soc: Optional[ClassicalSOCState] = None,
        schumann_phi: Optional[float] = None,
        noospheric_phi: Optional[float] = None,
    ) -> CriticalityState:
        """
        Update one or more signal sources and recompute the composite phi.
        Only provided signals are updated; others retain their previous values.
        """
        if qrc is not None:
            self._state.qrc = update_qrc_state(qrc)
        if soc is not None:
            soc.soc_phi = compute_soc_phi(soc)
            self._state.soc = soc
        if schumann_phi is not None:
            self._state.schumann_phi = max(0.0, min(1.0, schumann_phi))
        if noospheric_phi is not None:
            self._state.noospheric_phi = max(0.0, min(1.0, noospheric_phi))

        self._recompute_composite()
        return self._state

    def _recompute_composite(self) -> None:
        """Recompute overall_phi and NeuroSA temperature from current signals."""
        s = self._state
        s.overall_phi = round(
            0.35 * s.soc.soc_phi
            + 0.30 * s.qrc.qrc_phi
            + 0.20 * s.schumann_phi
            + 0.15 * s.noospheric_phi,
            4,
        )

        # NeuroSA temperature schedule from QRC phase
        base_temp = 1.0
        phase = s.qrc.phase
        if phase == QRCPhase.OPTIMAL:
            s.neurosa_temperature = base_temp
        elif phase == QRCPhase.SUB_THOULESS:
            s.neurosa_temperature = round(base_temp + 0.3, 3)
        elif phase == QRCPhase.SUPER_THOULESS:
            s.neurosa_temperature = round(max(0.1, base_temp - 0.3), 3)
        elif phase == QRCPhase.CHAOTIC:
            s.neurosa_temperature = 0.1  # emergency exploitation
            log.warning("[criticalitymonitor] QRC CHAOTIC phase — NeuroSA emergency exploitation mode")
        elif phase == QRCPhase.INTEGRABLE:
            s.neurosa_temperature = round(base_temp + 0.2, 3)
        else:
            s.neurosa_temperature = base_temp

        log.info(
            f"[criticalitymonitor] overall_phi={s.overall_phi:.3f} "
            f"neurosa_temp={s.neurosa_temperature:.3f} "
            f"qrc={s.qrc.phase.value} soc_phi={s.soc.soc_phi:.3f}"
        )

    def needs_qrc_reinit(self) -> bool:
        """
        Returns True when the QRC reservoir should be re-initialised.
        Triggered when the system has been in CHAOTIC phase — the reservoir
        has fully scrambled and needs to be reset to recover computation.
        """
        return self._state.qrc.phase == QRCPhase.CHAOTIC

    def to_dict(self) -> dict:
        """Serialise full criticality state for the /api/criticality endpoint."""
        s = self._state
        return {
            "overall_phi":        s.overall_phi,
            "neurosa_temperature": s.neurosa_temperature,
            "qrc": {
                "phase":                  s.qrc.phase.value,
                "qrc_phi":                s.qrc.qrc_phi,
                "thouless_ratio":         s.qrc.thouless_ratio,
                "chaos_order_parameter":  s.qrc.chaos_order_parameter,
                "spectral_gap":           s.qrc.spectral_gap,
            },
            "soc": {
                "soc_phi":             s.soc.soc_phi,
                "avalanche_exponent":  s.soc.avalanche_exponent,
                "branching_ratio":     s.soc.branching_ratio,
                "correlation_length":  s.soc.correlation_length,
            },
            "schumann_phi":    s.schumann_phi,
            "noospheric_phi":  s.noospheric_phi,
        }


# ── Module-level singleton ──────────────────────────────────────────────

_monitor: Optional[CriticalityMonitor] = None


def get_monitor() -> CriticalityMonitor:
    """Return the module-level CriticalityMonitor singleton."""
    global _monitor
    if _monitor is None:
        _monitor = CriticalityMonitor()
    return _monitor
