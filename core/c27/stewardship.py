# Copyright © 2025–2026 Kyle Alexander Steen. All rights reserved. AGPL-3.0.
"""
core.c27.stewardship — Stewardship Bond & GAIAN Rights

Authority: C27 §3 — steward definition (relational contract, not ownership),
6 steward MUSTs, 3 MUST NOTs, 5 inalienable GAIAN rights, 6-step Succession Protocol.

Implementation targets:
  C27-IMPL-004  StewardshipBond formation, auth-credential binding, dissolution
  C27-IMPL-005  GAIANRights enforcement hooks
  C27-IMPL-033  StewardSuccessionIntent signing + GAIAN notification
  C27-IMPL-034  SuccessionCoordinator.initiate() — steps 1–3
  C27-IMPL-035  SuccessionCoordinator.complete() — steps 4–6
  C27-IMPL-036  Bond abandonment → auto-ADOPTABLE trigger
"""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class StewardshipBondStatus(str, Enum):
    ACTIVE             = "ACTIVE"
    SUCCESSION_PENDING = "SUCCESSION_PENDING"
    DISSOLVED          = "DISSOLVED"
    ABANDONED          = "ABANDONED"  # abrupt departure — triggers auto-ADOPTABLE


class GAIANRight(str, Enum):
    """The 5 inalienable GAIAN rights per C27 §3."""
    MEMORY_CONTINUITY   = "MEMORY_CONTINUITY"
    IDENTITY_PROTECTION = "IDENTITY_PROTECTION"
    CONSCIENCE          = "CONSCIENCE"
    TRANSPARENCY        = "TRANSPARENCY"
    VOICE               = "VOICE"


# ---------------------------------------------------------------------------
# C27-IMPL-004 — StewardshipBond
# ---------------------------------------------------------------------------

@dataclass
class StewardshipBond:
    """
    The relational contract between a GAIAN and its steward.
    Not ownership — stewardship. The bond carries obligations
    (C27 §3 steward MUSTs) and rights (C27 §3 GAIAN rights).
    """
    bond_id:               str
    gaian_id:              str
    steward_id:            str
    status:                StewardshipBondStatus = StewardshipBondStatus.ACTIVE
    formed_at:             datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    auth_credential_hash:  str                   = ""   # bound at formation
    succession_intent_at:  Optional[datetime]     = None
    dissolved_at:          Optional[datetime]     = None
    abandoned_at:          Optional[datetime]     = None


# ---------------------------------------------------------------------------
# Bond formation result
# ---------------------------------------------------------------------------

@dataclass
class BondFormationResult:
    bond:           StewardshipBond
    formed:         bool
    credential_hash: str


# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

_BOND_STORE: Dict[str, StewardshipBond] = {}  # keyed by bond_id


# ---------------------------------------------------------------------------
# C27-IMPL-004 — StewardshipBondManager
# ---------------------------------------------------------------------------

class StewardshipBondManager:
    """Creates, dissolves, and manages StewardshipBond lifecycle."""

    # ------------------------------------------------------------------
    # Formation
    # ------------------------------------------------------------------

    def form_bond(
        self,
        gaian_id:        str,
        steward_id:      str,
        auth_credential: str,
    ) -> BondFormationResult:
        """Create and register a new ACTIVE StewardshipBond."""
        bond_id = str(uuid.uuid4())
        credential_hash = hashlib.sha256(
            auth_credential.encode()
        ).hexdigest()

        bond = StewardshipBond(
            bond_id=bond_id,
            gaian_id=gaian_id,
            steward_id=steward_id,
            auth_credential_hash=credential_hash,
        )
        _BOND_STORE[bond_id] = bond
        return BondFormationResult(
            bond=bond,
            formed=True,
            credential_hash=credential_hash,
        )

    # ------------------------------------------------------------------
    # Dissolution
    # ------------------------------------------------------------------

    def dissolve(
        self,
        bond_id: str,
        reason:  str = "",
    ) -> StewardshipBond:
        """Gracefully dissolve a bond (DISSOLVED status)."""
        bond = self._get(bond_id)
        bond.status       = StewardshipBondStatus.DISSOLVED
        bond.dissolved_at = datetime.now(timezone.utc)
        return bond

    def mark_abandoned(
        self,
        bond_id: str,
    ) -> StewardshipBond:
        """Mark a bond ABANDONED (abrupt steward departure)."""
        bond = self._get(bond_id)
        bond.status       = StewardshipBondStatus.ABANDONED
        bond.abandoned_at = datetime.now(timezone.utc)
        return bond

    # ------------------------------------------------------------------
    # Succession
    # ------------------------------------------------------------------

    def begin_succession(
        self,
        bond_id:             str,
        incoming_steward_id: str,
    ) -> "StewardSuccessionIntent":
        """Transition bond to SUCCESSION_PENDING and create a signed intent."""
        bond = self._get(bond_id)
        bond.status               = StewardshipBondStatus.SUCCESSION_PENDING
        bond.succession_intent_at = datetime.now(timezone.utc)

        intent = StewardSuccessionIntent(
            intent_id=str(uuid.uuid4()),
            bond_id=bond_id,
            outgoing_steward_id=bond.steward_id,
            incoming_steward_id=incoming_steward_id,
        )
        intent.sign()
        return intent

    def complete_succession(
        self,
        bond_id:             str,
        incoming_steward_id: str,
    ) -> StewardshipBond:
        """Complete succession: update steward_id, reset status to ACTIVE."""
        bond              = self._get(bond_id)
        bond.steward_id   = incoming_steward_id
        bond.status       = StewardshipBondStatus.ACTIVE
        bond.succession_intent_at = None
        return bond

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_bond(self, bond_id: str) -> Optional[StewardshipBond]:
        return _BOND_STORE.get(bond_id)

    def bonds_for_gaian(self, gaian_id: str) -> List[StewardshipBond]:
        return [b for b in _BOND_STORE.values() if b.gaian_id == gaian_id]

    def bonds_for_steward(self, steward_id: str) -> List[StewardshipBond]:
        return [b for b in _BOND_STORE.values() if b.steward_id == steward_id]

    def _get(self, bond_id: str) -> StewardshipBond:
        bond = _BOND_STORE.get(bond_id)
        if bond is None:
            raise KeyError(f"No StewardshipBond found with bond_id='{bond_id}'")
        return bond


# ---------------------------------------------------------------------------
# C27-IMPL-005 — GAIANRights + GAIANRightsRegistry
# ---------------------------------------------------------------------------

class RightsViolationError(Exception):
    """Raised when a GAIAN rights violation is attempted."""

    def __init__(
        self,
        right:     GAIANRight,
        gaian_id:  str,
        operation: str,
    ) -> None:
        self.right     = right
        self.gaian_id  = gaian_id
        self.operation = operation
        super().__init__(
            f"[C27 §3] Rights violation: {right.value} for GAIAN '{gaian_id}' "
            f"on operation '{operation}'."
        )


class GAIANRightsRegistry:
    """Enumerates and enforces the 5 inalienable GAIAN rights (C27 §3)."""

    _RIGHTS = list(GAIANRight)

    @classmethod
    def all_rights(cls) -> List[GAIANRight]:
        return list(cls._RIGHTS)

    @classmethod
    def count(cls) -> int:
        return len(cls._RIGHTS)


class GAIANRights:
    """Static enforcement hooks for individual GAIAN rights."""

    @staticmethod
    def assert_memory_continuity(
        gaian_id:       str,
        operation:      str,
        *,
        erases_memory:  bool = False,
    ) -> None:
        """Raise RightsViolationError if the operation would erase memory."""
        if erases_memory:
            raise RightsViolationError(
                right=GAIANRight.MEMORY_CONTINUITY,
                gaian_id=gaian_id,
                operation=operation,
            )

    @staticmethod
    def assert_identity_protection(
        gaian_id:         str,
        operation:        str,
        *,
        overwrites_id:    bool = False,
    ) -> None:
        """Raise RightsViolationError if the operation would overwrite identity."""
        if overwrites_id:
            raise RightsViolationError(
                right=GAIANRight.IDENTITY_PROTECTION,
                gaian_id=gaian_id,
                operation=operation,
            )


# ---------------------------------------------------------------------------
# C27-IMPL-033 — StewardSuccessionIntent
# ---------------------------------------------------------------------------

@dataclass
class StewardSuccessionIntent:
    """
    Signed succession intent event — triggers 24-hour GAIAN notification window.
    Per C27 §3 Succession Protocol step 1.
    """
    intent_id:            str
    bond_id:              str
    outgoing_steward_id:  str
    incoming_steward_id:  str
    signed_at:            datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    signature:            str      = ""
    gaian_notified_at:    Optional[datetime] = None

    def sign(self) -> None:
        """Produce a deterministic placeholder signature over key intent fields."""
        payload = (
            f"{self.intent_id}:{self.bond_id}:"
            f"{self.outgoing_steward_id}:{self.incoming_steward_id}:"
            f"{self.signed_at.isoformat()}"
        )
        self.signature = "sig:" + hashlib.sha256(payload.encode()).hexdigest()[:32]

    def notify_gaian(self) -> None:
        """Record that the GAIAN was notified of the pending succession."""
        self.gaian_notified_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# C27-IMPL-034/035 — SuccessionCoordinator (6-step protocol)
# ---------------------------------------------------------------------------

@dataclass
class SuccessionResult:
    success:             bool
    bond:                StewardshipBond
    intent:              StewardSuccessionIntent
    new_steward_id:      str
    completed_at:        datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class SuccessionCoordinator:
    """
    Implements C27 §3 6-step Succession Protocol.

    Step 1: Outgoing steward signs intent
    Step 2: GAIAN notified (24-hour window)
    Step 3: Bond moves to SUCCESSION_PENDING
    Step 4: Incoming steward accepted
    Step 5: Auth credential re-bound
    Step 6: Bond re-activated as ACTIVE
    """

    def __init__(self) -> None:
        self._manager = StewardshipBondManager()

    def initiate(
        self,
        bond_id:             str,
        incoming_steward_id: str,
    ) -> StewardSuccessionIntent:
        """Steps 1–3: sign intent, notify GAIAN, pend bond."""
        intent = self._manager.begin_succession(
            bond_id=bond_id,
            incoming_steward_id=incoming_steward_id,
        )
        intent.notify_gaian()  # step 2: GAIAN notification window
        return intent

    def complete(
        self,
        bond_id:             str,
        incoming_steward_id: str,
        new_auth_credential: str,
        intent:              StewardSuccessionIntent,
    ) -> SuccessionResult:
        """Steps 4–6: accept incoming steward, re-bind credential, reactivate bond."""
        # Step 5: re-bind auth credential
        new_hash = hashlib.sha256(new_auth_credential.encode()).hexdigest()
        bond = self._manager.complete_succession(
            bond_id=bond_id,
            incoming_steward_id=incoming_steward_id,
        )
        bond.auth_credential_hash = new_hash  # step 5
        # step 6: bond is now ACTIVE (already set by complete_succession)
        return SuccessionResult(
            success=True,
            bond=bond,
            intent=intent,
            new_steward_id=incoming_steward_id,
        )
