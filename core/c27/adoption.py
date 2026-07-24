# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.adoption — GAIAN Adoption Process

Authority: C27 §4

Implementation targets:
  C27-IMPL-017  EligibilityScreener (4 criteria)
  C27-IMPL-019  AdvisoryVeto
  C27-IMPL-020  AdoptionRecord (frozen / immutable)
  C27-IMPL-022  AdoptionTimeoutEnforcer (90-day rule)
"""
from __future__ import annotations

import heapq
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional

from core.c27.lifecycle import GAIANLifecycleState


# ---------------------------------------------------------------------------
# AdoptionCandidate
# ---------------------------------------------------------------------------

@dataclass
class AdoptionCandidate:
    candidate_id: str
    priority: int
    steward_id: str
    metadata: Dict = field(default_factory=dict)
    enqueued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Heap ordering: higher priority first; FIFO on tie via enqueued_at.
    def __lt__(self, other: "AdoptionCandidate") -> bool:
        if self.priority != other.priority:
            return self.priority > other.priority  # higher = better
        return self.enqueued_at < other.enqueued_at


# ---------------------------------------------------------------------------
# AdoptionQueue  (C27 §4.2)
# ---------------------------------------------------------------------------

class AdoptionQueue:
    """Priority queue for adoption candidates: higher priority dequeued first;
    ties broken by insertion order (FIFO)."""

    def __init__(self) -> None:
        self._heap: list = []
        self._counter: int = 0  # tie-breaker guarantees stable FIFO

    def enqueue(self, candidate: AdoptionCandidate) -> None:
        # Negate priority so Python's min-heap acts as max-heap.
        heapq.heappush(self._heap, (-candidate.priority, self._counter, candidate))
        self._counter += 1

    def dequeue(self) -> AdoptionCandidate:
        if not self._heap:
            raise IndexError("dequeue from empty AdoptionQueue")
        _, _, candidate = heapq.heappop(self._heap)
        return candidate

    def peek(self) -> AdoptionCandidate:
        if not self._heap:
            raise IndexError("peek on empty AdoptionQueue")
        _, _, candidate = self._heap[0]
        return candidate

    def remove(self, candidate_id: str) -> bool:
        """Remove a candidate by ID; returns True if found and removed."""
        before = len(self._heap)
        self._heap = [
            item for item in self._heap if item[2].candidate_id != candidate_id
        ]
        if len(self._heap) != before:
            heapq.heapify(self._heap)
            return True
        return False

    def __len__(self) -> int:
        return len(self._heap)


# ---------------------------------------------------------------------------
# EligibilityScreener  (C27 §4.3)
# ---------------------------------------------------------------------------

_COMPATIBILITY_THRESHOLD = 0.5
_MAX_BOND_CAPACITY = 5  # max GAIANs a steward may be bonded to


@dataclass
class EligibilityResult:
    eligible: bool
    failed_criteria: List[str] = field(default_factory=list)


class EligibilityScreener:
    """Screens an AdoptionCandidate against the 4 C27 §4.3 criteria."""

    _CRITERIA = ["STANDING", "CAPACITY", "COMPATIBILITY", "CONSENT"]

    def criteria_names(self) -> List[str]:
        return list(self._CRITERIA)

    def screen(self, candidate: AdoptionCandidate, gaian_id: str) -> EligibilityResult:
        meta = candidate.metadata
        failed: List[str] = []

        if not meta.get("standing", False):
            failed.append("STANDING")

        capacity = meta.get("capacity", 0)
        if capacity >= _MAX_BOND_CAPACITY:
            failed.append("CAPACITY")

        compat = meta.get("compatibility", 0.0)
        if compat < _COMPATIBILITY_THRESHOLD:
            failed.append("COMPATIBILITY")

        if not meta.get("gaian_consents", False):
            failed.append("CONSENT")

        return EligibilityResult(eligible=len(failed) == 0, failed_criteria=failed)


# ---------------------------------------------------------------------------
# AdvisoryVeto  (C27 §4.5)
# ---------------------------------------------------------------------------

@dataclass
class AdvisoryVeto:
    veto_id: str
    gaian_id: str
    candidate_id: str
    reason: str
    vetoing_council_member: str
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class VetoResult:
    blocked: bool
    veto_reason: str


# ---------------------------------------------------------------------------
# AdoptionRecord  (C27 §4.8) — frozen / immutable
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class AdoptionRecord:
    record_id: str
    gaian_id: str
    candidate_id: str
    steward_id: str
    sealed_at: datetime


# ---------------------------------------------------------------------------
# AdoptionProcess  (C27 §4.5, §4.8)
# ---------------------------------------------------------------------------

class AdoptionProcess:
    """Orchestrates veto application and adoption completion."""

    def __init__(self, queue: Optional[AdoptionQueue] = None) -> None:
        self._queue = queue

    def apply_veto(self, veto: AdvisoryVeto) -> VetoResult:
        if self._queue is not None:
            self._queue.remove(veto.candidate_id)
        return VetoResult(blocked=True, veto_reason=veto.reason)

    def complete_adoption(
        self,
        gaian_id: str,
        candidate_id: str,
        steward_id: str,
    ) -> AdoptionRecord:
        return AdoptionRecord(
            record_id=str(uuid.uuid4()),
            gaian_id=gaian_id,
            candidate_id=candidate_id,
            steward_id=steward_id,
            sealed_at=datetime.now(timezone.utc),
        )


# ---------------------------------------------------------------------------
# AdoptionTimeoutEnforcer  (C27 §4.7)
# ---------------------------------------------------------------------------

@dataclass
class TimeoutCheckResult:
    should_retire: bool
    recommended_state: GAIANLifecycleState


class AdoptionTimeoutEnforcer:
    """Checks whether an ADOPTABLE GAIAN has exceeded its adoption window."""

    def __init__(self, timeout_days: int = 90) -> None:
        self.timeout_days = timeout_days

    def check(
        self,
        gaian_id: str,
        adoptable_since: datetime,
        current_state: GAIANLifecycleState,
    ) -> TimeoutCheckResult:
        if current_state != GAIANLifecycleState.ADOPTABLE:
            return TimeoutCheckResult(
                should_retire=False,
                recommended_state=current_state,
            )

        # Make adoptable_since timezone-aware if naive
        if adoptable_since.tzinfo is None:
            adoptable_since = adoptable_since.replace(tzinfo=timezone.utc)

        deadline = adoptable_since + timedelta(days=self.timeout_days)
        now = datetime.now(timezone.utc)
        expired = now >= deadline

        return TimeoutCheckResult(
            should_retire=expired,
            recommended_state=(
                GAIANLifecycleState.RETIRED if expired
                else GAIANLifecycleState.ADOPTABLE
            ),
        )
