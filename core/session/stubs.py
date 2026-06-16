"""Stub interfaces for engines not yet implemented.

These stubs allow the SessionBootstrap to be fully wired and testable
right now, while the actual engine implementations are built in:
  #431 — CircadianLightEngine
  #432 — ShadowInterrogatorEngine
  #434 — MagnumOpusStageEngine
  #437 — SpectralForceEngine (QuantumFieldArchitectureEngine)

When those engines land, replace the stub with the real implementation
in SessionBootstrap.__init__() — the interface contracts here define
exactly what is expected.

All stubs return safe, deterministic defaults so tests pass immediately.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Result dataclasses (returned by engines)
# ---------------------------------------------------------------------------

@dataclass
class CircadianPhase:
    """Current phase of the circadian/light cycle — from #431."""
    phase_name: str = "UNKNOWN"            # e.g. DAWN, MORNING, NOON, DUSK, EVENING, NIGHT
    solar_elevation_degrees: float = 0.0
    lunar_phase: str = "UNKNOWN"           # NEW, WAXING_CRESCENT, FULL, etc.
    local_time_utc: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_stub: bool = True


@dataclass
class SpectralForceReport:
    """Current dominant spectral force — from #437."""
    dominant_force: str = "UNKNOWN"        # e.g. FIRE, EARTH, WATER, AIR, AETHER
    force_intensity: float = 0.5           # 0.0–1.0
    phi_basis: Optional[float] = None      # The phi value that produced this detection
    is_stub: bool = True


@dataclass
class MagnumOpusStageReport:
    """Current detected alchemical stage — from #434."""
    stage: str = "NIGREDO"                 # NIGREDO / ALBEDO / CITRINITAS / RUBEDO
    confidence: float = 0.5
    evidence: list[str] = field(default_factory=list)
    is_stub: bool = True


@dataclass
class ShadowInterrogatorReport:
    """Shadow patterns detected at session open — from #432."""
    active_patterns: list[str] = field(default_factory=list)
    risk_level: str = "LOW"                # LOW / MEDIUM / HIGH
    recommended_containment: bool = False
    notes: str = ""
    is_stub: bool = True


# ---------------------------------------------------------------------------
# Abstract interfaces — the contracts real engines must fulfil
# ---------------------------------------------------------------------------

class ICircadianLightEngine(ABC):
    @abstractmethod
    def get_current_phase(
        self, latitude: Optional[float], longitude: Optional[float],
        utc_now: Optional[datetime] = None,
    ) -> CircadianPhase: ...


class ISpectralForceEngine(ABC):
    @abstractmethod
    def detect_current_force(self, last_phi: Optional[float]) -> SpectralForceReport: ...


class IMagnumOpusStageEngine(ABC):
    @abstractmethod
    def detect_stage(self, last_phi: Optional[float], context: dict[str, Any]) -> MagnumOpusStageReport: ...


class IShadowInterrogatorEngine(ABC):
    @abstractmethod
    def interrogate(
        self, context: dict[str, Any], last_harmony_report: Optional[dict]
    ) -> ShadowInterrogatorReport: ...


class ISystemPromptBuilder(ABC):
    @abstractmethod
    def build(
        self,
        spectral: SpectralForceReport,
        stage: MagnumOpusStageReport,
        twin_profile_summary: str,
        circadian: CircadianPhase,
        shadow_report: ShadowInterrogatorReport,
        space_context: Optional[str] = None,
    ) -> str: ...


# ---------------------------------------------------------------------------
# Stub implementations — safe deterministic defaults
# ---------------------------------------------------------------------------

class StubCircadianLightEngine(ICircadianLightEngine):
    def get_current_phase(self, latitude, longitude, utc_now=None) -> CircadianPhase:
        return CircadianPhase(phase_name="UNKNOWN", is_stub=True)


class StubSpectralForceEngine(ISpectralForceEngine):
    def detect_current_force(self, last_phi) -> SpectralForceReport:
        return SpectralForceReport(dominant_force="UNKNOWN", is_stub=True)


class StubMagnumOpusStageEngine(IMagnumOpusStageEngine):
    def detect_stage(self, last_phi, context) -> MagnumOpusStageReport:
        return MagnumOpusStageReport(stage="NIGREDO", is_stub=True)


class StubShadowInterrogatorEngine(IShadowInterrogatorEngine):
    def interrogate(self, context, last_harmony_report) -> ShadowInterrogatorReport:
        return ShadowInterrogatorReport(active_patterns=[], is_stub=True)


class StubSystemPromptBuilder(ISystemPromptBuilder):
    def build(self, spectral, stage, twin_profile_summary, circadian,
              shadow_report, space_context=None) -> str:
        lines = [
            "## GAIA SESSION CONTEXT",
            f"Stage: {stage.stage}",
            f"Spectral Force: {spectral.dominant_force}",
            f"Circadian Phase: {circadian.phase_name}",
            f"Shadow Risk: {shadow_report.risk_level}",
        ]
        if twin_profile_summary:
            lines.append(f"Twin Profile: {twin_profile_summary}")
        if space_context:
            lines.append(f"Space: {space_context}")
        lines.append("[STUB — replace with real SystemPromptBuilder from #464]")
        return "\n".join(lines)
