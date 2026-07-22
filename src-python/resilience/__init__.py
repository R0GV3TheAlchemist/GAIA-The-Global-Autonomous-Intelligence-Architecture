"""resilience — Health monitoring and auto-restart engine

Provides:
  - HealthMonitor: watches module health signals and triggers recovery.
  - AutoRestart: policy engine for automatic module restart on failure.
  - ResilienceConfig: configuration for thresholds and policies.

Phase B — all engine methods are stubbed.
Inspired by MINIX 3's reincarnation server pattern (auto-restart on crash)
and the EmrysEngine resilience layer designed in Phase B.
"""
from __future__ import annotations
from resilience.engine import HealthMonitor, AutoRestart, ResilienceConfig

__all__ = ["HealthMonitor", "AutoRestart", "ResilienceConfig"]
