"""
gaia.session
============
Wire 4 — Session tracking layer.

Exposes:
  SessionClock        — wall-clock session tracker singleton
  SleepQualityStore   — sleep score store singleton
  SessionToD6Bridge   — Wire 4 translation layer
  create_wire4        — convenience factory
"""

from .session_clock import SessionClock, SleepQualityStore, get_session_clock, get_sleep_store
from .session_d6_bridge import SessionProbeResult, SessionToD6Bridge, create_wire4

__all__ = [
    "SessionClock",
    "SleepQualityStore",
    "get_session_clock",
    "get_sleep_store",
    "SessionProbeResult",
    "SessionToD6Bridge",
    "create_wire4",
]
