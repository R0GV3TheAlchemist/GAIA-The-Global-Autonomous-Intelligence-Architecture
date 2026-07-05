# GAIANProfileModel — Python-side dataclass
# Add this to src/gaian/runtimetypes.py
#
# Canon: docs/canon/GAIAN_IDENTITY.md
# Issue: #756
#
# NOTE: This file shows the addition to be merged into runtimetypes.py
# It is kept separate to make the diff reviewable.
# Once reviewed, merge into runtimetypes.py and delete this file.

from dataclasses import dataclass, field
from typing import Literal

LCITrend = Literal['ascending', 'stable', 'descending', 'volatile']


@dataclass
class LCIRecord:
    session_id: str
    phi: float
    force: str
    stage: str
    timestamp: str  # ISO 8601


@dataclass
class SessionCadenceRecord:
    preferred_hours: list[int] = field(default_factory=list)  # 0-23 UTC
    avg_session_duration: float = 0.0   # minutes
    longest_session: float = 0.0        # minutes


@dataclass
class OrbParamOverride:
    color_override: str | None = None
    size_scale: float | None = None     # 0.5-2.0
    pulse_rate: float | None = None     # BPM


@dataclass
class GAIANProfileModel:
    # Identity
    architect_id: str
    display_name: str
    birth_timestamp: str
    birth_force: str
    birth_stage: str

    # LCI
    lci_baseline: float
    lci_history: list[LCIRecord] = field(default_factory=list)
    lci_trend: LCITrend = 'stable'

    # Console
    active_modules: list[str] = field(default_factory=list)
    console_layout: str = 'full'
    theme: str = 'viriditas_default'
    orb_params: OrbParamOverride = field(default_factory=OrbParamOverride)

    # Personalization
    query_patterns: list[str] = field(default_factory=list)
    session_cadence: SessionCadenceRecord = field(default_factory=SessionCadenceRecord)
    preferred_forces: list[str] = field(default_factory=list)
    preferred_stages: list[str] = field(default_factory=list)

    # Session metadata
    total_sessions: int = 0
    last_session_timestamp: str = ''
    last_known_phi: float = 0.0
    last_known_force: str = ''
    last_known_stage: str = ''

    # Akashic
    akashic_loaded: bool = False
    akashic_version: str = ''

    # Schema
    schema_version: int = 1


@dataclass
class PersonalizationSignal:
    """Derived from GAIANProfileModel. Injected into RAGPipeline.query()."""
    architect_id: str
    lci_baseline: float
    lci_trend: LCITrend
    preferred_forces: list[str]
    preferred_stages: list[str]
    query_patterns: list[str]
    console_layout: str
    avg_session_duration: float
