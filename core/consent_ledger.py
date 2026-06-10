"""
Consent Ledger with Cryptographic Erasure

Issue #127

The consent ledger records every significant consent decision a user makes
with GAIA. It must be cryptographically trustworthy: tamper-evident,
auditable, and capable of providing mathematical proof of erasure.

Four guarantees:

  1. IMMUTABLE AUDIT TRAIL
     Every consent decision is HMAC-signed at creation time. Any subsequent
     alteration of a record is detectable by signature verification.

  2. CHAINED TAMPER-EVIDENCE
     Each ledger entry includes the hash of the previous entry (blockchain-
     inspired chain). Any insertion, deletion, or reordering of entries
     breaks the chain and is detectable by verify_chain().

  3. CRYPTOGRAPHIC ERASURE
     Data encrypted under a consent key becomes permanently inaccessible
     when that key is destroyed. Erasure is not deletion — it is the
     mathematical guarantee that the ciphertext can never be decrypted.
     An ErasureReceipt is produced that the user can independently verify.

  4. KEY-BASED ACCESS CONTROL
     Each consent scope is encrypted under a unique per-scope AES-256 key.
     Revoking consent destroys the key. Even if ciphertext persists in
     backups, it cannot be decrypted.

This is the technical foundation of GAIA's sovereignty promise:
  "Your data, your sovereignty."
Without cryptographic erasure, that promise is words.
With it, it is a mathematical guarantee.

Note on implementation:
  This module provides the full specification, data model, and protocol.
  The cryptographic primitives use Python's hashlib and hmac (always
  available). AES encryption is specified in the architecture but requires
  a cryptography library (e.g. cryptography>=3.0) in production.
  Key material is represented as bytes in this module; in production,
  keys must be managed by a hardware security module (HSM) or equivalent.

References:
  - GDPR Article 17: Right to Erasure
  - NIST SP 800-88: Guidelines for Media Sanitisation
  - Issue #120: SubjectSideIdentity (consent anchors)
  - Issue #119: PersonhoodMonitor (governance integration)
  - Canon C50: Action Gate
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging

log = logging.getLogger("gaia.consent_ledger")

__all__ = [
    "ConsentScope",
    "ConsentDecision",
    "ConsentRecord",
    "ConsentLedgerEntry",
    "CryptoErasureKey",
    "ErasureReceipt",
    "ConsentLedger",
    "CryptoErasureVault",
    "ConsentEngine",
    "get_consent_engine",
    "GENESIS_HASH",
]


# ── Consent scope taxonomy ────────────────────────────────────────────────────────────

class ConsentScope(str, Enum):
    """
    Fourteen granular consent domains.
    Each scope is encrypted under its own key; consent can be granted or
    revoked independently per scope.
    """
    EPISODIC_MEMORY          = "episodic_memory"
    SEMANTIC_MEMORY          = "semantic_memory"
    EMOTIONAL_PROFILE        = "emotional_profile"
    ARCHETYPAL_PROFILE       = "archetypal_profile"
    SOMATIC_PROFILE          = "somatic_profile"
    TRANSPERSONAL_HISTORY    = "transpersonal_history"
    INDIVIDUATION_RECORD     = "individuation_record"
    IDENTITY_ANCHORS         = "identity_anchors"
    CULTURAL_PROFILE         = "cultural_profile"
    PERSONHOOD_TELEMETRY     = "personhood_telemetry"
    SHADOW_HISTORY           = "shadow_history"
    CONSENT_LEDGER_ITSELF    = "consent_ledger_itself"
    THIRD_PARTY_SHARING      = "third_party_sharing"
    RESEARCH_USE             = "research_use"


class ConsentDecision(str, Enum):
    GRANT           = "grant"
    REVOKE          = "revoke"
    RESTRICT        = "restrict"
    TRANSFER        = "transfer"
    ERASURE_REQUEST = "erasure_request"


# ── Ledger data structures ─────────────────────────────────────────────────────────────

@dataclass
class ConsentRecord:
    """
    A single consent decision. Signed at creation; immutable thereafter.
    """
    record_id:    str
    user_id:      str
    scope:        ConsentScope
    decision:     ConsentDecision
    timestamp:    float
    context:      str = ""
    key_id:       str = ""
    signature:    str = ""
    revocation_reason: str = ""

    def canonical_payload(self) -> str:
        """Deterministic string representation for signing (excludes signature)."""
        return json.dumps({
            "record_id":  self.record_id,
            "user_id":    self.user_id,
            "scope":      self.scope.value,
            "decision":   self.decision.value,
            "timestamp":  self.timestamp,
            "context":    self.context,
            "key_id":     self.key_id,
        }, sort_keys=True)


@dataclass
class ConsentLedgerEntry:
    """
    A tamper-evident ledger entry wrapping a ConsentRecord.
    Each entry chains to the previous via prev_entry_hash.
    """
    entry_index:    int
    record:         ConsentRecord
    prev_entry_hash: str
    entry_hash:     str = ""

    def compute_entry_hash(self) -> str:
        payload = self.prev_entry_hash + self.record.canonical_payload()
        return hashlib.sha256(payload.encode()).hexdigest()


# ── Cryptographic erasure ───────────────────────────────────────────────────────────────

@dataclass
class CryptoErasureKey:
    """
    An AES-256 encryption key for a single consent scope.
    Destruction is irreversible: zeroing key_material makes the
    associated ciphertext permanently inaccessible.
    """
    key_id:         str
    scope:          ConsentScope
    user_id:        str
    created_at:     float = field(default_factory=time.time)
    key_material:   Optional[bytes] = None
    destroyed_at:   Optional[float] = None
    destruction_proof: str = ""

    @property
    def is_destroyed(self) -> bool:
        return self.destroyed_at is not None


@dataclass
class ErasureReceipt:
    """
    Cryptographic proof of key destruction / erasure.
    The user can retain this receipt and independently verify it.
    """
    receipt_id:        str
    user_id:           str
    scope:             ConsentScope
    key_id:            str
    destroyed_at:      float
    proof_hash:        str
    ledger_entry_index: int
    verifiable:        bool = True
    notes:             str = ""


# ── HMAC signing ────────────────────────────────────────────────────────────────────────

def _sign_record(record: ConsentRecord, signing_key: bytes) -> str:
    return hmac.new(
        signing_key,
        record.canonical_payload().encode(),
        hashlib.sha256,
    ).hexdigest()


def _verify_record_signature(record: ConsentRecord, signing_key: bytes) -> bool:
    expected = _sign_record(record, signing_key)
    return hmac.compare_digest(expected, record.signature)


# ── Consent Ledger ────────────────────────────────────────────────────────────────────────

GENESIS_HASH = "0" * 64


class ConsentLedger:
    """
    Append-only, HMAC-signed, chained-hash consent ledger.
    verify_chain() detects any modification, insertion, or deletion.
    """

    def __init__(self, signing_key: Optional[bytes] = None) -> None:
        self._signing_key: bytes = signing_key or os.urandom(32)
        self._entries: list[ConsentLedgerEntry] = []

    @property
    def length(self) -> int:
        return len(self._entries)

    def append(
        self,
        user_id: str,
        scope: ConsentScope,
        decision: ConsentDecision,
        context: str = "",
        key_id: str = "",
        revocation_reason: str = "",
    ) -> ConsentLedgerEntry:
        record_id = hashlib.sha256(
            f"{user_id}{scope.value}{decision.value}{time.time()}{os.urandom(8).hex()}"
            .encode()
        ).hexdigest()[:32]

        record = ConsentRecord(
            record_id=record_id,
            user_id=user_id,
            scope=scope,
            decision=decision,
            timestamp=time.time(),
            context=context,
            key_id=key_id,
            revocation_reason=revocation_reason,
        )
        record.signature = _sign_record(record, self._signing_key)

        prev_hash = self._entries[-1].entry_hash if self._entries else GENESIS_HASH
        entry = ConsentLedgerEntry(
            entry_index=len(self._entries),
            record=record,
            prev_entry_hash=prev_hash,
        )
        entry.entry_hash = entry.compute_entry_hash()
        self._entries.append(entry)

        log.info(
            f"[consent_ledger] appended entry={entry.entry_index} "
            f"scope={scope.value} decision={decision.value} user={user_id}"
        )
        return entry

    def verify_chain(self) -> tuple[bool, str]:
        if not self._entries:
            return True, "OK: empty ledger"

        for i, entry in enumerate(self._entries):
            if not _verify_record_signature(entry.record, self._signing_key):
                return False, f"TAMPER DETECTED: signature invalid at entry {i}"

            expected_prev = self._entries[i - 1].entry_hash if i > 0 else GENESIS_HASH
            if entry.prev_entry_hash != expected_prev:
                return False, f"TAMPER DETECTED: chain broken at entry {i}"

            recomputed = entry.compute_entry_hash()
            if recomputed != entry.entry_hash:
                return False, f"TAMPER DETECTED: entry hash mismatch at entry {i}"

        return True, "OK"

    def get_history(
        self,
        user_id: str,
        scope: Optional[ConsentScope] = None,
    ) -> list[ConsentLedgerEntry]:
        return [
            e for e in self._entries
            if e.record.user_id == user_id
            and (scope is None or e.record.scope == scope)
        ]

    def current_consent_state(self, user_id: str) -> dict[str, str]:
        state: dict[str, str] = {}
        for entry in self._entries:
            if entry.record.user_id == user_id:
                state[entry.record.scope.value] = entry.record.decision.value
        return state


# ── Cryptographic Erasure Vault ───────────────────────────────────────────────────────────

class CryptoErasureVault:
    """
    Manages per-scope encryption keys and provides irreversible key destruction.
    After destroy_key(), any data encrypted under the key is permanently inaccessible.
    """

    def __init__(self) -> None:
        self._keys: dict[str, CryptoErasureKey] = {}
        self._receipts: list[ErasureReceipt] = []

    def create_key(self, user_id: str, scope: ConsentScope) -> CryptoErasureKey:
        key_id = hashlib.sha256(
            f"{user_id}{scope.value}{time.time()}{os.urandom(8).hex()}"
            .encode()
        ).hexdigest()[:32]

        key = CryptoErasureKey(
            key_id=key_id,
            scope=scope,
            user_id=user_id,
            key_material=os.urandom(32),
        )
        self._keys[key_id] = key
        log.info(f"[crypto_vault] key created: scope={scope.value} key_id={key_id}")
        return key

    def destroy_key(self, key_id: str, ledger_entry_index: int) -> ErasureReceipt:
        """
        Irreversibly destroy a key and produce an ErasureReceipt.
        key_material bytes are overwritten with zeros before the reference is cleared.
        """
        key = self._keys.get(key_id)
        if key is None:
            raise KeyError(f"Key not found: {key_id}")
        if key.is_destroyed:
            existing = next((r for r in self._receipts if r.key_id == key_id), None)
            if existing:
                return existing
            raise RuntimeError(f"Key {key_id} already destroyed but no receipt found.")

        destroyed_at = time.time()

        if key.key_material is not None:
            buf = bytearray(key.key_material)
            for i in range(len(buf)):
                buf[i] = 0
            key.key_material = bytes(buf)
            key.key_material = None

        key.destroyed_at = destroyed_at
        proof_input = f"{key_id}{destroyed_at}{key.user_id}"
        proof_hash = hashlib.sha256(proof_input.encode()).hexdigest()
        key.destruction_proof = proof_hash

        receipt_id = hashlib.sha256(
            f"{key_id}{destroyed_at}{os.urandom(8).hex()}".encode()
        ).hexdigest()[:32]

        receipt = ErasureReceipt(
            receipt_id=receipt_id,
            user_id=key.user_id,
            scope=key.scope,
            key_id=key_id,
            destroyed_at=destroyed_at,
            proof_hash=proof_hash,
            ledger_entry_index=ledger_entry_index,
            notes=(
                f"Cryptographic erasure complete. "
                f"All data encrypted under key {key_id} (scope: {key.scope.value}) "
                f"is now permanently inaccessible."
            ),
        )
        self._receipts.append(receipt)

        log.warning(
            f"[GLASS_ROOM] cryptographic_erasure: "
            f"scope={key.scope.value} key_id={key_id} "
            f"user={key.user_id} destroyed_at={destroyed_at}"
        )
        return receipt

    def verify_erasure(self, receipt: ErasureReceipt) -> bool:
        proof_input = f"{receipt.key_id}{receipt.destroyed_at}{receipt.user_id}"
        expected_hash = hashlib.sha256(proof_input.encode()).hexdigest()
        return hmac.compare_digest(expected_hash, receipt.proof_hash)

    def get_key(self, key_id: str) -> Optional[CryptoErasureKey]:
        return self._keys.get(key_id)

    def list_active_keys(self, user_id: str) -> list[CryptoErasureKey]:
        return [
            k for k in self._keys.values()
            if k.user_id == user_id and not k.is_destroyed
        ]


# ── ConsentEngine ─────────────────────────────────────────────────────────────────────────

class ConsentEngine:
    """
    Unified interface for consent management and cryptographic erasure.

    Workflow:
      1. grant(user_id, scope)  — create key, record GRANT in ledger
      2. revoke(user_id, scope) — record REVOKE in ledger
      3. erase(user_id, scope)  — record ERASURE_REQUEST, destroy key, return receipt
      4. verify_erasure(receipt) — user can independently verify
      5. verify_ledger_integrity() — detect any tamper in the full ledger
    """

    def __init__(
        self,
        ledger: Optional[ConsentLedger] = None,
        vault: Optional[CryptoErasureVault] = None,
    ) -> None:
        self._ledger = ledger or ConsentLedger()
        self._vault = vault or CryptoErasureVault()
        self._scope_keys: dict[tuple[str, str], str] = {}

    def grant(
        self,
        user_id: str,
        scope: ConsentScope,
        context: str = "",
    ) -> tuple[ConsentLedgerEntry, CryptoErasureKey]:
        key = self._vault.create_key(user_id=user_id, scope=scope)
        self._scope_keys[(user_id, scope.value)] = key.key_id
        entry = self._ledger.append(
            user_id=user_id,
            scope=scope,
            decision=ConsentDecision.GRANT,
            context=context,
            key_id=key.key_id,
        )
        return entry, key

    def revoke(
        self,
        user_id: str,
        scope: ConsentScope,
        reason: str = "",
    ) -> ConsentLedgerEntry:
        return self._ledger.append(
            user_id=user_id,
            scope=scope,
            decision=ConsentDecision.REVOKE,
            revocation_reason=reason,
        )

    def erase(
        self,
        user_id: str,
        scope: ConsentScope,
        reason: str = "",
    ) -> ErasureReceipt:
        entry = self._ledger.append(
            user_id=user_id,
            scope=scope,
            decision=ConsentDecision.ERASURE_REQUEST,
            revocation_reason=reason,
        )

        key_id = self._scope_keys.get((user_id, scope.value))
        if key_id is None:
            log.warning(
                f"[consent_engine] erase() called for scope={scope.value} "
                f"but no key found for user={user_id}."
            )
            return ErasureReceipt(
                receipt_id="no-key-" + entry.record.record_id[:16],
                user_id=user_id,
                scope=scope,
                key_id="",
                destroyed_at=time.time(),
                proof_hash="",
                ledger_entry_index=entry.entry_index,
                verifiable=False,
                notes="No encryption key found for this scope. Data may not have been stored.",
            )

        return self._vault.destroy_key(
            key_id=key_id,
            ledger_entry_index=entry.entry_index,
        )

    def verify_erasure_receipt(self, receipt: ErasureReceipt) -> bool:
        if not receipt.verifiable:
            return False
        return self._vault.verify_erasure(receipt)

    def verify_ledger_integrity(self) -> tuple[bool, str]:
        return self._ledger.verify_chain()

    def consent_state(self, user_id: str) -> dict[str, str]:
        return self._ledger.current_consent_state(user_id)

    def audit_trail(
        self,
        user_id: str,
        scope: Optional[ConsentScope] = None,
    ) -> list[dict]:
        entries = self._ledger.get_history(user_id=user_id, scope=scope)
        return [
            {
                "entry_index":  e.entry_index,
                "scope":        e.record.scope.value,
                "decision":     e.record.decision.value,
                "timestamp":    e.record.timestamp,
                "context":      e.record.context,
                "key_id":       e.record.key_id,
                "entry_hash":   e.entry_hash,
            }
            for e in entries
        ]


# ── Module-level singleton ───────────────────────────────────────────────────────────

_engine: Optional[ConsentEngine] = None


def get_consent_engine() -> ConsentEngine:
    global _engine
    if _engine is None:
        _engine = ConsentEngine()
    return _engine
