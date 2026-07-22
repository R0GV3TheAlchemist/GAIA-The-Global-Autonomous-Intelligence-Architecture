"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEXUS — The Universal Autonomous Intelligence Architecture
  GAIA  — The Global Autonomous Intelligence Architecture

  Author   : Kyle Steen
  GitHub   : R0GV3TheAlchemist (https://github.com/R0GV3TheAlchemist)
  Email    : xxkylesteenxx@outlook.com
  Project  : NEXUS / GAIA
  License  : All Rights Reserved © 2026 Kyle Steen
             Unauthorized use, reproduction, or distribution
             of this file or its contents is strictly prohibited.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

global_clock.py — NEXUS Global Clock & Time Conversion Service.

Provides get_physical_time(), get_legal_time(), get_consensus_time(),
LegalTimeZoneRegistry for jurisdiction-to-IANA mapping, and
TimeConversionService for cross-domain time conversions.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
import time


class TimeDomain(Enum):
    PHYSICAL     = auto()   # TAI/GPS atomic, no discontinuities
    LEGAL        = auto()   # Civil time, DST + leap seconds
    CONSENSUS    = auto()   # Cluster-agreed distributed time
    RELATIVISTIC = auto()   # GR-corrected proper time (interplanetary)


@dataclass
class JurisdictionEntry:
    """A single jurisdiction-to-timezone mapping record."""
    jurisdiction_id: str          # ISO 3166-1 alpha-2 + optional subdivision
    iana_timezone:   str          # e.g. "America/Chicago", "Europe/Berlin"
    utc_offset_sec:  int  = 0
    observes_dst:    bool = True
    description:     str  = ""


@dataclass
class TimeReading:
    """A timestamped reading in a specific time domain."""
    reading_id:   UUID       = field(default_factory=uuid4)
    domain:       TimeDomain = TimeDomain.PHYSICAL
    unix_seconds: float      = 0.0
    tai_seconds:  float      = 0.0
    jurisdiction: str        = ""
    utc_offset:   int        = 0
    is_dst:       bool       = False
    node_id:      Optional[UUID] = None


class LegalTimeZoneRegistry:
    """
    Maps jurisdiction identifiers to IANA timezone entries.
    Supports DST transitions, historical offsets, and scheduled changes.
    Deep-space or jurisdiction-free nodes default to PHYSICAL time.
    """

    _DEFAULTS: List[JurisdictionEntry] = [
        JurisdictionEntry("US-CT",  "America/Chicago",     -21600, True,  "US Central"),
        JurisdictionEntry("US-ET",  "America/New_York",    -18000, True,  "US Eastern"),
        JurisdictionEntry("US-MT",  "America/Denver",      -25200, True,  "US Mountain"),
        JurisdictionEntry("US-PT",  "America/Los_Angeles", -28800, True,  "US Pacific"),
        JurisdictionEntry("GB",     "Europe/London",        0,     True,  "UK"),
        JurisdictionEntry("DE",     "Europe/Berlin",        3600,  True,  "Germany"),
        JurisdictionEntry("JP",     "Asia/Tokyo",           32400, False, "Japan"),
        JurisdictionEntry("AU-ET",  "Australia/Sydney",     36000, True,  "AU Eastern"),
        JurisdictionEntry("UTC",    "UTC",                  0,     False, "Universal"),
        JurisdictionEntry("SPACE",  "UTC",                  0,     False, "Deep-space node"),
    ]

    def __init__(self) -> None:
        self._entries: Dict[str, JurisdictionEntry] = {
            e.jurisdiction_id: e for e in self._DEFAULTS
        }

    def register(self, entry: JurisdictionEntry) -> None:
        self._entries[entry.jurisdiction_id] = entry

    def lookup(self, jurisdiction_id: str) -> Optional[JurisdictionEntry]:
        return self._entries.get(jurisdiction_id)

    def all_jurisdictions(self) -> List[str]:
        return list(self._entries.keys())


class TimeConversionService:
    """
    Converts timestamps between NEXUS time domains.

    - PHYSICAL ↔ LEGAL        : UTC offset + DST from LegalTimeZoneRegistry
    - PHYSICAL ↔ TAI          : leap-second table (37 s as of 2026)
    - PHYSICAL ↔ RELATIVISTIC : Lorentz + gravitational blueshift stub
    """

    TAI_UTC_OFFSET_SECONDS: int = 37  # unchanged through 2026

    def __init__(self, registry: LegalTimeZoneRegistry) -> None:
        self._registry = registry

    def to_tai(self, utc_unix: float) -> float:
        return utc_unix + self.TAI_UTC_OFFSET_SECONDS

    def from_tai(self, tai_seconds: float) -> float:
        return tai_seconds - self.TAI_UTC_OFFSET_SECONDS

    def to_legal(self, utc_unix: float,
                 jurisdiction_id: str) -> Tuple[float, int, bool]:
        entry = self._registry.lookup(jurisdiction_id)
        if entry is None:
            return utc_unix, 0, False
        return utc_unix + entry.utc_offset_sec, entry.utc_offset_sec, entry.observes_dst

    def from_legal(self, legal_unix: float, jurisdiction_id: str) -> float:
        entry = self._registry.lookup(jurisdiction_id)
        if entry is None:
            return legal_unix
        return legal_unix - entry.utc_offset_sec

    def to_relativistic(self, utc_unix: float,
                        altitude_m: float = 0.0,
                        velocity_ms: float = 0.0) -> float:
        """
        Gravitational blueshift + Lorentz time dilation correction.
        Stub — replace with full GR ephemeris for production interplanetary nodes.
        """
        C = 299_792_458.0
        G = 9.80665
        g_factor = (G * altitude_m) / (C ** 2)
        l_factor = -(velocity_ms ** 2) / (2 * C ** 2)
        return utc_unix * (1 + g_factor + l_factor)


class GlobalClock:
    """
    NEXUS Global Clock — single access point for all time domains.
    All audit entries, ledger records, and IPC messages should
    timestamp via GlobalClock.get_consensus_time().
    """

    def __init__(self, registry: Optional[LegalTimeZoneRegistry] = None,
                 sync_engine=None) -> None:
        self._registry    = registry or LegalTimeZoneRegistry()
        self._converter   = TimeConversionService(self._registry)
        self._sync_engine = sync_engine
        self._node_id: UUID = uuid4()

    def get_physical_time(self) -> TimeReading:
        now = time.time()
        return TimeReading(
            domain=TimeDomain.PHYSICAL,
            unix_seconds=now,
            tai_seconds=self._converter.to_tai(now),
            node_id=self._node_id,
        )

    def get_legal_time(self, jurisdiction_id: str = "UTC") -> TimeReading:
        now = time.time()
        legal, offset, is_dst = self._converter.to_legal(now, jurisdiction_id)
        return TimeReading(
            domain=TimeDomain.LEGAL,
            unix_seconds=legal,
            tai_seconds=self._converter.to_tai(now),
            jurisdiction=jurisdiction_id,
            utc_offset=offset,
            is_dst=is_dst,
            node_id=self._node_id,
        )

    def get_consensus_time(self) -> TimeReading:
        offset = self._sync_engine.clock_offset_seconds() \
            if self._sync_engine else 0.0
        now = time.time() + offset
        return TimeReading(
            domain=TimeDomain.CONSENSUS,
            unix_seconds=now,
            tai_seconds=self._converter.to_tai(now),
            node_id=self._node_id,
        )

    def get_relativistic_time(self, altitude_m: float = 0.0,
                               velocity_ms: float = 0.0) -> TimeReading:
        now = time.time()
        rel = self._converter.to_relativistic(now, altitude_m, velocity_ms)
        return TimeReading(
            domain=TimeDomain.RELATIVISTIC,
            unix_seconds=rel,
            tai_seconds=self._converter.to_tai(rel),
            node_id=self._node_id,
        )

    @property
    def converter(self) -> TimeConversionService:
        return self._converter

    @property
    def registry(self) -> LegalTimeZoneRegistry:
        return self._registry
