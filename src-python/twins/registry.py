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

registry.py — NEXUS Digital Twin Registry.

TwinRegistry is the authoritative index of all live twins.
Supports UUID/name lookup, type-filtered queries, event
subscription, and bulk snapshot export.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4
import time

from twins.entity import DigitalTwin, TwinState, TwinType


class TwinEventType(Enum):
    CREATED          = auto()
    STATE_UPDATED    = auto()
    ANOMALY_DETECTED = auto()
    DECOMMISSIONED   = auto()


@dataclass
class TwinEvent:
    """An event emitted by the TwinRegistry on state changes."""
    event_id:   UUID           = field(default_factory=uuid4)
    event_type: TwinEventType  = TwinEventType.STATE_UPDATED
    twin_id:    UUID           = field(default_factory=uuid4)
    twin_name:  str            = ""
    twin_type:  TwinType       = TwinType.ABSTRACT
    payload:    Dict[str, Any] = field(default_factory=dict)
    timestamp:  float          = field(default_factory=time.time)


class TwinRegistry:
    """
    Authoritative index of all live NEXUS Digital Twins.
    UUID/name lookup, type-filtered queries, event subscription,
    and bulk snapshot export.
    """

    def __init__(self) -> None:
        self._twins:       Dict[UUID, DigitalTwin]             = {}
        self._name_index:  Dict[str, UUID]                     = {}
        self._subscribers: Dict[TwinEventType, List[Callable]] = {
            et: [] for et in TwinEventType
        }
        self._event_log: List[TwinEvent] = []

    def register(self, twin: DigitalTwin) -> None:
        self._twins[twin.twin_id]   = twin
        self._name_index[twin.name] = twin.twin_id
        self._emit(TwinEventType.CREATED, twin, {})

    def decommission(self, twin_id: UUID) -> None:
        twin = self._twins.pop(twin_id, None)
        if twin:
            self._name_index.pop(twin.name, None)
            self._emit(TwinEventType.DECOMMISSIONED, twin, {})

    def get(self, twin_id: UUID) -> Optional[DigitalTwin]:
        return self._twins.get(twin_id)

    def get_by_name(self, name: str) -> Optional[DigitalTwin]:
        uid = self._name_index.get(name)
        return self._twins.get(uid) if uid else None

    def query_by_type(self, twin_type: TwinType) -> List[DigitalTwin]:
        return [t for t in self._twins.values() if t.twin_type == twin_type]

    def all_twins(self) -> List[DigitalTwin]:
        return list(self._twins.values())

    def update(self, twin_id: UUID,
               properties: Dict[str, Any],
               health: Optional[float] = None) -> Optional[TwinState]:
        twin = self._twins.get(twin_id)
        if twin is None:
            return None
        prev_anomalies = set(twin.state.anomaly_flags)
        new_state = twin.update(properties, health)
        self._emit(TwinEventType.STATE_UPDATED, twin,
                   {"version": new_state.version, "properties": properties})
        for anomaly in set(new_state.anomaly_flags) - prev_anomalies:
            self._emit(TwinEventType.ANOMALY_DETECTED, twin, {"anomaly": anomaly})
        return new_state

    def subscribe(self, event_type: TwinEventType,
                  callback: Callable[[TwinEvent], None]) -> None:
        self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: TwinEventType,
                    callback: Callable[[TwinEvent], None]) -> None:
        subs = self._subscribers[event_type]
        if callback in subs:
            subs.remove(callback)

    def snapshot(self) -> List[Dict[str, Any]]:
        return [t.to_dict() for t in self._twins.values()]

    def event_log(self) -> List[TwinEvent]:
        return list(self._event_log)

    def __len__(self) -> int:
        return len(self._twins)

    def _emit(self, event_type: TwinEventType,
              twin: DigitalTwin,
              payload: Dict[str, Any]) -> None:
        event = TwinEvent(
            event_type=event_type, twin_id=twin.twin_id,
            twin_name=twin.name, twin_type=twin.twin_type,
            payload=payload,
        )
        self._event_log.append(event)
        for cb in self._subscribers[event_type]:
            try:
                cb(event)
            except Exception:
                pass
