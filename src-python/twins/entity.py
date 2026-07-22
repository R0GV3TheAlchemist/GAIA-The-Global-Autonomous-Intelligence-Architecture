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

entity.py — NEXUS Digital Twin Entity.

DigitalTwin class, TwinState versioned snapshots, and TwinType taxonomy.
Supports state history, rollback, anomaly flagging, and property diffing.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import copy, time


class TwinType(Enum):
    DEVICE   = auto()
    AGENT    = auto()
    FACILITY = auto()
    REGION   = auto()
    PROCESS  = auto()
    ABSTRACT = auto()


@dataclass
class TwinState:
    """
    Versioned, timestamped snapshot of a DigitalTwin's observable properties.
    Every update increments version and appends to the owner's history buffer.
    """
    state_id:      UUID           = field(default_factory=uuid4)
    version:       int            = 0
    timestamp:     float          = field(default_factory=time.time)
    properties:    Dict[str, Any] = field(default_factory=dict)
    health:        float          = 1.0
    anomaly_flags: List[str]      = field(default_factory=list)

    def flag_anomaly(self, label: str) -> None:
        if label not in self.anomaly_flags:
            self.anomaly_flags.append(label)

    def clear_anomaly(self, label: str) -> None:
        self.anomaly_flags = [f for f in self.anomaly_flags if f != label]

    def diff(self, other: TwinState) -> Dict[str, Any]:
        all_keys = set(self.properties) | set(other.properties)
        return {
            k: {"from": self.properties.get(k), "to": other.properties.get(k)}
            for k in all_keys
            if self.properties.get(k) != other.properties.get(k)
        }


class DigitalTwin:
    """
    NEXUS Digital Twin — live, versioned, bidirectionally synchronized
    virtual representation of any physical or logical entity.
    """

    def __init__(self, name: str, twin_type: TwinType,
                 physical_id: Optional[UUID] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        self.twin_id:     UUID           = uuid4()
        self.name:        str            = name
        self.twin_type:   TwinType       = twin_type
        self.physical_id: Optional[UUID] = physical_id
        self.metadata:    Dict[str, Any] = metadata or {}
        self._state:      TwinState      = TwinState(version=0)
        self._history:    List[TwinState] = []

    def update(self, properties: Dict[str, Any],
               health: Optional[float] = None) -> TwinState:
        self._history.append(copy.deepcopy(self._state))
        self._state = TwinState(
            version=self._state.version + 1,
            timestamp=time.time(),
            properties={**self._state.properties, **properties},
            health=health if health is not None else self._state.health,
            anomaly_flags=list(self._state.anomaly_flags),
        )
        return self._state

    def rollback(self, version: int) -> Optional[TwinState]:
        for state in reversed(self._history):
            if state.version == version:
                self._history.append(copy.deepcopy(self._state))
                self._state = copy.deepcopy(state)
                self._state.version   = self._history[-1].version + 1
                self._state.timestamp = time.time()
                return self._state
        return None

    def flag_anomaly(self, label: str) -> None:
        self._state.flag_anomaly(label)

    def clear_anomaly(self, label: str) -> None:
        self._state.clear_anomaly(label)

    def get_property(self, key: str, default: Any = None) -> Any:
        return self._state.properties.get(key, default)

    def history_depth(self) -> int:
        return len(self._history)

    @property
    def state(self) -> TwinState:
        return self._state

    @property
    def version(self) -> int:
        return self._state.version

    @property
    def health(self) -> float:
        return self._state.health

    def to_dict(self) -> Dict[str, Any]:
        return {
            "twin_id":       str(self.twin_id),
            "name":          self.name,
            "twin_type":     self.twin_type.name,
            "physical_id":   str(self.physical_id) if self.physical_id else None,
            "version":       self.version,
            "health":        self.health,
            "properties":    self._state.properties,
            "anomaly_flags": self._state.anomaly_flags,
            "metadata":      self.metadata,
        }
