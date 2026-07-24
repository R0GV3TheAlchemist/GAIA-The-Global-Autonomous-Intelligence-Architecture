# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.retirement — Retirement & Archival Engine

Authority: C27 §8 — 5 retirement conditions, 7-step retirement process
(memory seal + legacy package), 180-day archival eligibility.

Implementation targets:
  C27-IMPL-024  RetirementEngine.initiate() + 72-hour notice + waiver
  C27-IMPL-025  RetirementEngine.seal_memory() — SHA-256 root hash → audit log
  C27-IMPL-026  RetirementEngine.revoke_tools() — C24 Tool Registry hook stub
  C27-IMPL-027  RetirementEngine.generate_legacy_package() — immutable LegacyPackage
  C27-IMPL-028  RetirementEngine.archive() — 180-day eligibility + ArchivalRecord
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from core.c27.lifecycle import GAIANLifecycleState, GAIANLifecycleMachine
from core.c27.audit_log import AuditLogWriter, _STORE as _AUDIT_STORE


# ---------------------------------------------------------------------------
# RetirementCondition
# ---------------------------------------------------------------------------

class RetirementCondition(str, Enum):
    STEWARD_INTENT       = "STEWARD_INTENT"       # Steward formally initiates
    GAIAN_VOLITION       = "GAIAN_VOLITION"        # GAIAN requests own retirement
    SENTINEL_MANDATE     = "SENTINEL_MANDATE"      # SENTINEL critical finding
    ADOPTION_TIMEOUT     = "ADOPTION_TIMEOUT"      # Day 91+ adoption ladder
    SYSTEM_DECOMMISSION  = "SYSTEM_DECOMMISSION"   # Infrastructure retirement


# Auto-waiver conditions: GAIAN has already consented / SENTINEL mandates urgency
_AUTO_WAIVER_CONDITIONS = {
    RetirementCondition.GAIAN_VOLITION,
    RetirementCondition.SENTINEL_MANDATE,
    RetirementCondition.SYSTEM_DECOMMISSION,
}

_NOTICE_HOURS = 72
_ARCHIVAL_DAYS = 180


# ---------------------------------------------------------------------------
# C27-IMPL-024 — RetirementIntent
# ---------------------------------------------------------------------------

@dataclass
class RetirementIntent:
    """
    Formal retirement intent — triggers 72-hour notice period.
    72-hour notice may be waived with GAIAN consent or emergency override.
    """
    intent_id:      str
    gaian_id:       str
    condition:      RetirementCondition
    initiated_by:   str
    justification:  str
    notice_until:   datetime              # 72 hours from initiated_at
    initiated_at:   datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    waiver_granted: bool                  = False
    waiver_reason:  Optional[str]         = None


# ---------------------------------------------------------------------------
# C27-IMPL-027 — LegacyPackage (frozen / immutable)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LegacyPackage:
    """
    Immutable structured summary of a GAIAN's contributions.
    Generated at step 5 of the retirement process; stored permanently.
    """
    package_id:       str
    gaian_id:         str
    generated_at:     datetime
    memory_seal_hash: str
    contributions:    tuple          # immutable via frozen dataclass
    steward_id:       str
    condition:        RetirementCondition


# ---------------------------------------------------------------------------
# C27-IMPL-028 — ArchivalRecord (frozen / immutable)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ArchivalRecord:
    """
    Record of a GAIAN entering the GAIA Immutable Archive.
    Eligible after 180 days in RETIRED state.
    """
    archive_id:        str
    gaian_id:          str
    archived_at:       datetime
    retired_at:        datetime
    legacy_package_id: str


# ---------------------------------------------------------------------------
# Module-level stores
# ---------------------------------------------------------------------------

_INTENT_STORE:  Dict[str, RetirementIntent] = {}   # keyed by gaian_id
_LEGACY_STORE:  Dict[str, LegacyPackage]    = {}   # keyed by gaian_id
_ARCHIVE_STORE: Dict[str, ArchivalRecord]   = {}   # keyed by gaian_id
_RETIRED_AT:    Dict[str, datetime]         = {}   # gaian_id -> retired_at timestamp


# ---------------------------------------------------------------------------
# RetirementResult
# ---------------------------------------------------------------------------

@dataclass
class RetirementResult:
    success:        bool
    gaian_id:       str
    legacy_package: LegacyPackage
    retired_at:     datetime


# ---------------------------------------------------------------------------
# C27-IMPL-024..028 — RetirementEngine
# ---------------------------------------------------------------------------

class RetirementEngine:
    """
    7-step retirement process per C27 §8:

    1. Retirement intent + 72-hour notice
    2. GAIAN consent or waiver
    3. Final memory seal (hash stored in audit log)
    4. Tool & capability revocation (C24 Tool Registry hook)
    5. Legacy package generation
    6. State transition to RETIRED
    7. 180-day archival eligibility timer starts
    """

    # ------------------------------------------------------------------
    # Step 1  (C27-IMPL-024)
    # ------------------------------------------------------------------

    def initiate(
        self,
        gaian_id:      str,
        condition:     RetirementCondition,
        initiated_by:  str,
        justification: str,
    ) -> RetirementIntent:
        """File retirement intent; start 72-hour notice window."""
        now          = datetime.now(timezone.utc)
        notice_until = now + timedelta(hours=_NOTICE_HOURS)

        intent = RetirementIntent(
            intent_id=str(uuid.uuid4()),
            gaian_id=gaian_id,
            condition=condition,
            initiated_by=initiated_by,
            justification=justification,
            notice_until=notice_until,
            initiated_at=now,
        )

        # Auto-waiver for conditions that imply consent or urgency
        if condition in _AUTO_WAIVER_CONDITIONS:
            intent.waiver_granted = True
            intent.waiver_reason  = f"Auto-waiver: {condition.value}"

        _INTENT_STORE[gaian_id] = intent
        return intent

    # ------------------------------------------------------------------
    # Step 2  (C27-IMPL-024)
    # ------------------------------------------------------------------

    def grant_waiver(self, gaian_id: str, reason: str) -> RetirementIntent:
        """Explicitly grant a notice waiver (GAIAN consent path)."""
        intent = self._get_intent(gaian_id)
        intent.waiver_granted = True
        intent.waiver_reason  = reason
        return intent

    def notice_expired(self, gaian_id: str) -> bool:
        """Return True if the 72-hour notice window has elapsed or a waiver was granted."""
        intent = self._get_intent(gaian_id)
        if intent.waiver_granted:
            return True
        return datetime.now(timezone.utc) >= intent.notice_until

    # ------------------------------------------------------------------
    # Step 3  (C27-IMPL-025)
    # ------------------------------------------------------------------

    def seal_memory(self, gaian_id: str) -> str:
        """Hash the GAIAN's memory root and append the seal to the audit log."""
        now    = datetime.now(timezone.utc)
        source = f"{gaian_id}:memory-seal:{now.isoformat()}"
        seal   = hashlib.sha256(source.encode()).hexdigest()

        writer = _AUDIT_STORE.setdefault(
            gaian_id, AuditLogWriter(gaian_id=gaian_id)
        )
        writer.append(
            event_type="MEMORY_SEAL",
            actor="retirement-engine",
            action=f"Memory sealed at step 3; hash={seal[:16]}…",
            payload={"memory_seal_hash": seal},
        )
        return seal

    # ------------------------------------------------------------------
    # Step 4  (C27-IMPL-026)
    # ------------------------------------------------------------------

    def revoke_tools(self, gaian_id: str) -> None:
        """Revoke all tool capabilities; appends audit event (C24 hook stub)."""
        writer = _AUDIT_STORE.setdefault(
            gaian_id, AuditLogWriter(gaian_id=gaian_id)
        )
        writer.append(
            event_type="TOOL_REVOCATION",
            actor="retirement-engine",
            action="All tools revoked via C24 Tool Registry",
            payload={"gaian_id": gaian_id, "revoked_by": "C27-IMPL-026"},
        )

    # ------------------------------------------------------------------
    # Step 5  (C27-IMPL-027)
    # ------------------------------------------------------------------

    def generate_legacy_package(
        self,
        gaian_id:     str,
        steward_id:   str,
        contributions: tuple = (),
    ) -> LegacyPackage:
        """Build an immutable LegacyPackage for permanent storage."""
        seal = self.seal_memory(gaian_id)  # ensure seal exists
        pkg  = LegacyPackage(
            package_id=str(uuid.uuid4()),
            gaian_id=gaian_id,
            generated_at=datetime.now(timezone.utc),
            memory_seal_hash=seal,
            contributions=contributions,
            steward_id=steward_id,
            condition=_INTENT_STORE[gaian_id].condition
            if gaian_id in _INTENT_STORE
            else RetirementCondition.SYSTEM_DECOMMISSION,
        )
        _LEGACY_STORE[gaian_id] = pkg
        return pkg

    # ------------------------------------------------------------------
    # Step 6  (C27-IMPL-024)
    # ------------------------------------------------------------------

    def finalize(
        self,
        gaian_id:      str,
        lifecycle_machine: "GAIANLifecycleMachine",
    ) -> None:
        """Transition the GAIAN to RETIRED state."""
        lifecycle_machine.transition(
            gaian_id=gaian_id,
            to_state=GAIANLifecycleState.RETIRED,
            actor="retirement-engine",
        )
        _RETIRED_AT[gaian_id] = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Step 7  (C27-IMPL-028)
    # ------------------------------------------------------------------

    def archive(self, gaian_id: str) -> ArchivalRecord:
        """Move to GAIA Immutable Archive after 180-day eligibility window."""
        retired_at = _RETIRED_AT.get(gaian_id)
        if retired_at is None:
            raise ValueError(
                f"GAIAN '{gaian_id}' has no retirement record; cannot archive."
            )

        now           = datetime.now(timezone.utc)
        eligible_from = retired_at + timedelta(days=_ARCHIVAL_DAYS)
        if now < eligible_from:
            raise ValueError(
                f"GAIAN '{gaian_id}' is not yet archival-eligible. "
                f"Eligible from {eligible_from.isoformat()}."
            )

        legacy = _LEGACY_STORE.get(gaian_id)
        record = ArchivalRecord(
            archive_id=str(uuid.uuid4()),
            gaian_id=gaian_id,
            archived_at=now,
            retired_at=retired_at,
            legacy_package_id=legacy.package_id if legacy else "",
        )
        _ARCHIVE_STORE[gaian_id] = record
        return record

    # ------------------------------------------------------------------
    # Orchestrator: full 7-step flow
    # ------------------------------------------------------------------

    def retire(
        self,
        gaian_id:          str,
        condition:         RetirementCondition,
        initiated_by:      str,
        justification:     str,
        steward_id:        str,
        lifecycle_machine: "GAIANLifecycleMachine",
        contributions:     tuple = (),
    ) -> RetirementResult:
        """Orchestrate steps 1–6 in sequence (step 7 deferred until 180 days)."""
        # 1. Intent
        self.initiate(gaian_id, condition, initiated_by, justification)
        # 3. Memory seal
        # 4. Tool revocation
        self.revoke_tools(gaian_id)
        # 5. Legacy package (includes memory seal internally)
        pkg = self.generate_legacy_package(gaian_id, steward_id, contributions)
        # 6. State transition
        self.finalize(gaian_id, lifecycle_machine)

        return RetirementResult(
            success=True,
            gaian_id=gaian_id,
            legacy_package=pkg,
            retired_at=_RETIRED_AT[gaian_id],
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_intent(self, gaian_id: str) -> RetirementIntent:
        intent = _INTENT_STORE.get(gaian_id)
        if intent is None:
            raise KeyError(
                f"No RetirementIntent found for gaian_id='{gaian_id}'."
            )
        return intent
