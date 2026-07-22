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

sync_protocol.py — NEXUS Time Synchronization Protocol.

TimeSyncBeacon pulses, TimeSyncEngine grandmaster election,
offset/drift computation, and monotonic clock adjustment.
Based on IEEE 1588 PTP profile.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import time


class SyncState(Enum):
    UNSYNCHRONIZED = auto()
    ACQUIRING      = auto()
    SYNCHRONIZED   = auto()
    HOLDOVER       = auto()
    LOST           = auto()


@dataclass
class TimeSyncBeacon:
    """
    A precision time beacon broadcast by a node.
    Carries the sender's current physical time and stratum level.
    """
    beacon_id:      UUID  = field(default_factory=uuid4)
    sender_id:      UUID  = field(default_factory=uuid4)
    stratum:        int   = 2
    physical_time:  float = field(default_factory=time.time)
    precision_ns:   float = 1000.0
    leap_indicator: int   = 0
    sequence:       int   = 0


@dataclass
class SyncSample:
    """A single offset measurement between local and reference clocks."""
    sample_id:      UUID  = field(default_factory=uuid4)
    reference_id:   UUID  = field(default_factory=uuid4)
    local_time:     float = 0.0
    reference_time: float = 0.0
    roundtrip_ns:   float = 0.0
    offset_seconds: float = 0.0
    timestamp:      float = field(default_factory=time.time)

    def compute_offset(self) -> float:
        return self.reference_time - self.local_time


class TimeSyncEngine:
    """
    NEXUS distributed precision time synchronization engine.
    IEEE 1588 PTP profile:
    - Collects TimeSyncBeacon pulses from peer nodes
    - Elects grandmaster (lowest stratum, best precision)
    - Computes clock offset via median-filtered sample history
    - Never steps the clock backward (monotonic guarantee)
    """

    PRECISION_TARGETS = {
        "datacenter":    100e-9,
        "regional":      1e-3,
        "continental":   10e-3,
        "interplanetary": None,
    }

    def __init__(self, node_id: Optional[UUID] = None,
                 stratum: int = 2,
                 max_samples: int = 64) -> None:
        self.node_id     = node_id or uuid4()
        self.stratum     = stratum
        self.max_samples = max_samples
        self._state:        SyncState                  = SyncState.UNSYNCHRONIZED
        self._peers:        Dict[UUID, TimeSyncBeacon] = {}
        self._samples:      List[SyncSample]           = []
        self._grandmaster:  Optional[UUID]             = None
        self._clock_offset: float                      = 0.0
        self._last_sync:    float                      = 0.0

    def receive_beacon(self, beacon: TimeSyncBeacon) -> None:
        self._peers[beacon.sender_id] = beacon
        self._elect_grandmaster()
        if self._state == SyncState.UNSYNCHRONIZED:
            self._state = SyncState.ACQUIRING

    def _elect_grandmaster(self) -> None:
        if not self._peers:
            return
        best = min(self._peers.values(),
                   key=lambda b: (b.stratum, b.precision_ns))
        self._grandmaster = best.sender_id

    def record_sample(self, sample: SyncSample) -> None:
        self._samples.append(sample)
        if len(self._samples) > self.max_samples:
            self._samples = self._samples[-self.max_samples:]
        self._compute_offset()
        self._last_sync = time.time()
        self._state = SyncState.SYNCHRONIZED

    def _compute_offset(self) -> None:
        if not self._samples:
            return
        offsets = sorted(s.compute_offset() for s in self._samples)
        median  = offsets[len(offsets) // 2]
        if median > self._clock_offset:
            self._clock_offset = median
        else:
            self._clock_offset = max(median, self._clock_offset - 0.0005)

    def clock_offset_seconds(self) -> float:
        return self._clock_offset

    def enter_holdover(self) -> None:
        self._state = SyncState.HOLDOVER

    def lose_sync(self) -> None:
        self._state = SyncState.LOST

    def status(self) -> dict:
        return {
            "node_id":        str(self.node_id),
            "state":          self._state.name,
            "grandmaster":    str(self._grandmaster),
            "clock_offset_s": self._clock_offset,
            "peer_count":     len(self._peers),
            "sample_count":   len(self._samples),
            "last_sync":      self._last_sync,
        }

    @property
    def state(self) -> SyncState:
        return self._state

    @property
    def grandmaster_id(self) -> Optional[UUID]:
        return self._grandmaster
