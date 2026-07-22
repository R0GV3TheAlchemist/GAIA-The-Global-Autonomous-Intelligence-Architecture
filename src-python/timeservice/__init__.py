"""timeservice — Time synchronisation and scheduling service

Provides:
  - TimeSync: synchronises NEXUS node clocks against NTP / GPS / mesh
    consensus time sources.
  - ScheduleService: cron-style and deadline-aware task scheduler.
  - TimeServiceConfig: configuration for sync sources and schedule policy.

Phase C — all methods are stubbed.

References
----------
- NTP RFC 5905 for clock synchronisation.
- asyncio event loop + heapq for EDF scheduling (from nexusos.scheduler).
- Delay-Tolerant Networking (RFC 9171): time handling for
  interplanetary nodes where NTP is unavailable.
"""
from __future__ import annotations
from timeservice.service import TimeSync, ScheduleService, TimeServiceConfig

__all__ = ["TimeSync", "ScheduleService", "TimeServiceConfig"]
