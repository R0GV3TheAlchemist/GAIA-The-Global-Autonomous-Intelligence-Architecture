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

time_service — NEXUS Planetary Time Service Package.

Provides GlobalClock, LegalTimeZoneRegistry, TimeConversionService,
TimeSyncBeacon, and TimeSyncEngine for all NEXUS temporal operations.
"""

__version__ = "1.0.0"
__author__ = "Kyle Steen"
__all__ = [
    "GlobalClock",
    "LegalTimeZoneRegistry",
    "TimeConversionService",
    "TimeSyncEngine",
    "TimeSyncBeacon",
    "TimeDomain",
    "SyncState",
]

from time_service.global_clock import (
    GlobalClock,
    LegalTimeZoneRegistry,
    TimeConversionService,
    TimeDomain,
)
from time_service.sync_protocol import TimeSyncEngine, TimeSyncBeacon, SyncState
