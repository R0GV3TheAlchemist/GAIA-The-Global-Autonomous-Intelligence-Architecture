"""
core/lifecycle/adoption_queue.py
C27 §4 — Adoption Queue & Timeout Escalation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional


class AdoptionVisibility(str, Enum):
    STANDARD = "STANDARD"
    ESCALATED = "ESCALATED"
    COUNCIL_REVIEW = "COUNCIL_REVIEW"
    RETIREMENT_REVIEW = "RETIREMENT_REVIEW"


@dataclass
class AdoptionQueueEntry:
    gaian_id: str
    archetype: Optional[str] = None
    elemental_profile: Optional[str] = None
    capability_summary: Optional[str] = None
    lifecycle_history_summary: Optional[dict] = field(default_factory=dict)
    health_status: Optional[str] = None
    known_anomalies: List[str] = field(default_factory=list)
    entered_adoptable_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    visibility: AdoptionVisibility = AdoptionVisibility.STANDARD
    sentinel_notified: bool = False
    council_review_required: bool = False
    retirement_eligible: bool = False
    extended_until: Optional[datetime] = None

    def days_in_queue(self, now: Optional[datetime] = None) -> int:
        now = now or datetime.now(timezone.utc)
        return (now - self.entered_adoptable_at).days


class AdoptionQueue:
    """In-memory Phase 2 implementation of the GAIA Adoption Queue (C27 §4.1–§4.4)."""

    def __init__(self) -> None:
        self._entries: Dict[str, AdoptionQueueEntry] = {}

    def enqueue(
        self,
        gaian_id: str,
        archetype: Optional[str] = None,
        elemental_profile: Optional[str] = None,
        capability_summary: Optional[str] = None,
        lifecycle_history_summary: Optional[dict] = None,
        health_status: Optional[str] = None,
        known_anomalies: Optional[List[str]] = None,
    ) -> AdoptionQueueEntry:
        entry = AdoptionQueueEntry(
            gaian_id=gaian_id,
            archetype=archetype,
            elemental_profile=elemental_profile,
            capability_summary=capability_summary,
            lifecycle_history_summary=lifecycle_history_summary or {},
            health_status=health_status,
            known_anomalies=known_anomalies or [],
        )
        self._entries[gaian_id] = entry
        return entry

    def remove(self, gaian_id: str) -> None:
        self._entries.pop(gaian_id, None)

    def get(self, gaian_id: str) -> Optional[AdoptionQueueEntry]:
        return self._entries.get(gaian_id)

    def list_entries(self) -> List[AdoptionQueueEntry]:
        return list(self._entries.values())

    def evaluate_timeouts(self, now: Optional[datetime] = None) -> List[dict]:
        now = now or datetime.now(timezone.utc)
        actions: List[dict] = []
        for entry in self._entries.values():
            if entry.extended_until and now <= entry.extended_until:
                continue
            days = entry.days_in_queue(now)
            if 31 <= days <= 60 and entry.visibility != AdoptionVisibility.ESCALATED:
                entry.visibility = AdoptionVisibility.ESCALATED
                entry.sentinel_notified = True
                actions.append({"gaian_id": entry.gaian_id, "action": "ESCALATE_VISIBILITY", "days": days})
            elif 61 <= days <= 90 and entry.visibility != AdoptionVisibility.COUNCIL_REVIEW:
                entry.visibility = AdoptionVisibility.COUNCIL_REVIEW
                entry.council_review_required = True
                actions.append({"gaian_id": entry.gaian_id, "action": "COUNCIL_REVIEW", "days": days})
            elif days >= 91 and not entry.retirement_eligible:
                entry.visibility = AdoptionVisibility.RETIREMENT_REVIEW
                entry.retirement_eligible = True
                actions.append({"gaian_id": entry.gaian_id, "action": "RETIREMENT_INITIATE", "days": days})
        return actions

    def extend_entry(self, gaian_id: str, days: int) -> None:
        entry = self._entries[gaian_id]
        entry.extended_until = datetime.now(timezone.utc) + timedelta(days=days)
