"""
core/obs/audit_store.py
~~~~~~~~~~~~~~~~~~~~~~~
Immutable, signed, hash-chained audit persistence for GAIA-OS.

Design
------
* NDJSON file  — one JSON object per line, appended on every record().
  Append-only at the filesystem level; no line is ever overwritten.
* HMAC-SHA256  — every entry is signed with a key derived from a
  Gaian-supplied passphrase (PBKDF2) or an auto-generated key stored
  at <store_dir>/audit.key.  Signature covers the canonical JSON of
  the entry body (sorted keys, no whitespace).
* Hash chain   — each entry carries prev_hash (SHA-256 of the previous
  raw NDJSON line).  verify() walks the chain and reports every broken
  link so tampering is immediately locatable.
* JSON-LD      — export_jsonld() wraps entries in a minimal @context
  that maps GAIA vocabulary to prov-o / schema.org terms.
* Retention    — max_days prunes entries older than the policy.
* Purge        — Gaian-controlled right-to-erasure; logs a PURGE event
  before modifying the file.
* AuditReader  — read-only interface for third-party auditors.

Usage
-----
    from core.obs.audit_store import AuditStore, AuditReader

    store = AuditStore(store_dir=Path(".gaia/audit"), passphrase="secret")
    store.record(event_type="agent.action", actor="planner",
                 action="call_tool", outcome="ok")

    reader = AuditReader(store_dir=Path(".gaia/audit"), passphrase="secret")
    ok, errors = reader.verify()
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .tracer import get_current_trace_id
except ImportError:  # standalone / test usage
    def get_current_trace_id() -> Optional[str]:  # type: ignore[misc]
        return None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NDJSON_FILENAME  = "audit.ndjson"
KEY_FILENAME     = "audit.key"
SALT_FILENAME    = "audit.salt"

PBKDF2_ITERATIONS = 260_000   # OWASP 2023 recommendation for HMAC-SHA256
KEY_BYTES         = 32

JSONLD_CONTEXT = {
    "@vocab": "https://gaia-os.dev/audit#",
    "prov":   "http://www.w3.org/ns/prov#",
    "schema": "https://schema.org/",
    "xsd":    "http://www.w3.org/2001/XMLSchema#",
    # field mappings
    "ts":         {"@id": "prov:generatedAtTime",  "@type": "xsd:dateTime"},
    "actor":      {"@id": "prov:wasAttributedTo"},
    "action":     {"@id": "prov:used"},
    "outcome":    {"@id": "schema:result"},
    "event_type": {"@id": "schema:actionStatus"},
    "trace_id":   {"@id": "prov:wasInfluencedBy"},
    "resource":   {"@id": "schema:object"},
}


# ---------------------------------------------------------------------------
# Stored entry dataclass (entry body + envelope)
# ---------------------------------------------------------------------------

@dataclass
class StoredAuditEntry:
    """One persisted audit record — body + tamper-evidence envelope."""
    # --- body (same fields as AuditEvent) ---
    event_type: str
    actor:      str
    action:     str
    outcome:    str
    ts:         str
    trace_id:   Optional[str]         = None
    resource:   Optional[str]         = None
    meta:       Dict[str, Any]        = field(default_factory=dict)
    # --- envelope ---
    seq:        int                   = 0       # monotonic sequence number
    prev_hash:  Optional[str]         = None    # SHA-256 of previous raw line
    signature:  Optional[str]         = None    # HMAC-SHA256 of canonical body JSON

    def body_dict(self) -> Dict[str, Any]:
        """Return the signable body — all fields except envelope fields."""
        return {
            "event_type": self.event_type,
            "actor":      self.actor,
            "action":     self.action,
            "outcome":    self.outcome,
            "ts":         self.ts,
            "trace_id":   self.trace_id,
            "resource":   self.resource,
            "meta":       self.meta,
            "seq":        self.seq,
            "prev_hash":  self.prev_hash,
        }

    def canonical_json(self) -> bytes:
        """Deterministic JSON for signing — sorted keys, no whitespace."""
        return json.dumps(self.body_dict(), sort_keys=True,
                          separators=(",", ":"), default=str).encode()

    def to_line(self) -> str:
        """Serialise to a single NDJSON line (no trailing newline)."""
        return json.dumps(asdict(self), sort_keys=True,
                          separators=(",", ":"), default=str)

    @staticmethod
    def from_line(line: str) -> "StoredAuditEntry":
        d = json.loads(line)
        return StoredAuditEntry(**{k: d.get(k) for k in StoredAuditEntry.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Key management helpers
# ---------------------------------------------------------------------------

def _derive_key(passphrase: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac(
        "sha256", passphrase.encode(), salt,
        PBKDF2_ITERATIONS, dklen=KEY_BYTES,
    )


def _load_or_create_key(store_dir: Path,
                        passphrase: Optional[str]) -> bytes:
    """
    Return a 32-byte HMAC key.
    - If passphrase given  → derive via PBKDF2 with a stored salt.
    - If no passphrase     → load or generate a random key file.
    """
    if passphrase:
        salt_path = store_dir / SALT_FILENAME
        if salt_path.exists():
            salt = salt_path.read_bytes()
        else:
            salt = secrets.token_bytes(32)
            salt_path.write_bytes(salt)
        return _derive_key(passphrase, salt)

    key_path = store_dir / KEY_FILENAME
    if key_path.exists():
        return key_path.read_bytes()
    key = secrets.token_bytes(KEY_BYTES)
    key_path.write_bytes(key)
    key_path.chmod(0o600)
    return key


def _sign(body_bytes: bytes, key: bytes) -> str:
    return hmac.new(key, body_bytes, hashlib.sha256).hexdigest()


def _verify_sig(entry: StoredAuditEntry, key: bytes) -> bool:
    expected = _sign(entry.canonical_json(), key)
    return hmac.compare_digest(expected, entry.signature or "")


# ---------------------------------------------------------------------------
# AuditStore — write + read
# ---------------------------------------------------------------------------

class AuditStore:
    """
    Append-only, signed, hash-chained audit log backed by an NDJSON file.

    Parameters
    ----------
    store_dir  : directory where audit.ndjson (and key/salt) are stored.
    passphrase : optional Gaian passphrase for key derivation.  If omitted,
                 an auto-generated key is used.
    max_days   : retention policy in days.  Entries older than this are
                 pruned on open and when apply_retention() is called.
                 0 = no retention limit.
    """

    def __init__(
        self,
        store_dir:  Path,
        passphrase: Optional[str] = None,
        max_days:   int           = 0,
    ) -> None:
        self._dir      = Path(store_dir)
        self._path     = self._dir / NDJSON_FILENAME
        self._max_days = max_days
        self._lock     = threading.Lock()
        self._seq      = 0
        self._prev_hash: Optional[str] = None

        self._dir.mkdir(parents=True, exist_ok=True)
        self._key = _load_or_create_key(self._dir, passphrase)

        # Hydrate seq and prev_hash from existing file
        self._hydrate()

        if max_days > 0:
            self._apply_retention()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _hydrate(self) -> None:
        """Read the last line of an existing store to restore seq + prev_hash."""
        if not self._path.exists():
            return
        last_line: Optional[str] = None
        with open(self._path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line:
                    last_line = line
                    self._seq += 1
        if last_line:
            self._prev_hash = hashlib.sha256(last_line.encode()).hexdigest()

    def _append_line(self, line: str) -> None:
        with open(self._path, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
            fh.flush()
            os.fsync(fh.fileno())

    def _read_all_entries(self) -> List[Tuple[str, StoredAuditEntry]]:
        """Return (raw_line, entry) pairs for every non-empty line."""
        if not self._path.exists():
            return []
        pairs: List[Tuple[str, StoredAuditEntry]] = []
        with open(self._path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if line:
                    try:
                        pairs.append((line, StoredAuditEntry.from_line(line)))
                    except Exception:  # noqa: BLE001
                        pass
        return pairs

    def _rewrite(self, entries: List[StoredAuditEntry]) -> None:
        """Atomically rewrite the store with a new set of entries."""
        tmp = self._path.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as fh:
            for e in entries:
                fh.write(e.to_line() + "\n")
        tmp.replace(self._path)
        # Re-hydrate seq + prev_hash
        self._seq = 0
        self._prev_hash = None
        self._hydrate()

    def _apply_retention(self) -> None:
        if self._max_days <= 0:
            return
        cutoff = (datetime.now(timezone.utc)
                  - timedelta(days=self._max_days)).isoformat()
        pairs   = self._read_all_entries()
        kept    = [e for _, e in pairs if e.ts >= cutoff]
        pruned  = len(pairs) - len(kept)
        if pruned:
            self._rewrite(kept)

    # ------------------------------------------------------------------
    # Public write API
    # ------------------------------------------------------------------

    def record(
        self,
        event_type: str,
        actor:      str,
        action:     str,
        outcome:    str                  = "ok",
        resource:   Optional[str]        = None,
        meta:       Optional[Dict[str, Any]] = None,
        trace_id:   Optional[str]        = None,
    ) -> StoredAuditEntry:
        """
        Append a signed, hash-chained audit entry to the NDJSON store.
        Thread-safe.  Returns the created entry.
        """
        with self._lock:
            entry = StoredAuditEntry(
                event_type = event_type,
                actor      = actor,
                action     = action,
                outcome    = outcome,
                ts         = datetime.now(timezone.utc).isoformat(),
                trace_id   = trace_id or get_current_trace_id(),
                resource   = resource,
                meta       = meta or {},
                seq        = self._seq,
                prev_hash  = self._prev_hash,
            )
            entry.signature = _sign(entry.canonical_json(), self._key)
            line = entry.to_line()
            self._append_line(line)
            self._prev_hash = hashlib.sha256(line.encode()).hexdigest()
            self._seq += 1
        return entry

    # ------------------------------------------------------------------
    # Retention & Gaian-controlled deletion
    # ------------------------------------------------------------------

    def apply_retention(self) -> int:
        """Prune entries older than max_days.  Returns number of entries pruned."""
        if self._max_days <= 0:
            return 0
        with self._lock:
            before = self._seq
            self._apply_retention()
            return before - self._seq

    def purge(self, before_ts: str) -> int:
        """
        Gaian right-to-erasure: delete all entries with ts < before_ts.
        Logs a PURGE record BEFORE modifying the file.
        Returns number of entries deleted.
        """
        # Record the purge intent first (cannot be erased by the purge itself)
        self.record(
            event_type = "audit.purge",
            actor      = "gaian",
            action     = "purge",
            outcome    = "initiated",
            meta       = {"before_ts": before_ts},
        )
        with self._lock:
            pairs  = self._read_all_entries()
            kept   = [e for _, e in pairs if e.ts >= before_ts]
            pruned = len(pairs) - len(kept)
            if pruned:
                self._rewrite(kept)
        return pruned

    def delete_store(self) -> None:
        """Gaian full wipe — delete the NDJSON file entirely."""
        with self._lock:
            if self._path.exists():
                self._path.unlink()
            self._seq       = 0
            self._prev_hash = None

    # ------------------------------------------------------------------
    # Read API (also exposed on AuditReader)
    # ------------------------------------------------------------------

    def query(
        self,
        event_type: Optional[str] = None,
        actor:      Optional[str] = None,
        outcome:    Optional[str] = None,
        since:      Optional[str] = None,
    ) -> List[StoredAuditEntry]:
        """Filter entries by optional criteria.  Returns a copy."""
        results = [e for _, e in self._read_all_entries()]
        if event_type:
            results = [e for e in results if e.event_type == event_type]
        if actor:
            results = [e for e in results if e.actor == actor]
        if outcome:
            results = [e for e in results if e.outcome == outcome]
        if since:
            results = [e for e in results if e.ts >= since]
        return results

    def export_json(self) -> str:
        """Export all entries as a pretty-printed JSON array."""
        return json.dumps(
            [asdict(e) for _, e in self._read_all_entries()],
            indent=2, default=str,
        )

    def export_jsonld(self) -> str:
        """
        Export entries as a JSON-LD document.
        Maps GAIA audit vocabulary to prov-o / schema.org for
        regulatory / external reviewer consumption.
        """
        entries = [asdict(e) for _, e in self._read_all_entries()]
        doc = {
            "@context": JSONLD_CONTEXT,
            "@type":    "prov:Collection",
            "@id":      "gaia:audit-log",
            "prov:generatedBy": "GAIA-OS AuditStore",
            "prov:generatedAtTime": datetime.now(timezone.utc).isoformat(),
            "entries": entries,
        }
        return json.dumps(doc, indent=2, default=str)

    def verify(self) -> Tuple[bool, List[str]]:
        """
        Walk the full entry list and verify:
          1. Each entry's HMAC signature is valid.
          2. Each entry's prev_hash matches SHA-256 of the previous raw line.

        Returns (all_ok: bool, errors: List[str]).
        """
        errors: List[str] = []
        pairs = self._read_all_entries()

        prev_raw: Optional[str] = None
        for raw, entry in pairs:
            # Signature check
            if not _verify_sig(entry, self._key):
                errors.append(
                    f"seq={entry.seq} ts={entry.ts}: invalid signature"
                )
            # Hash-chain check
            expected_prev = (
                hashlib.sha256(prev_raw.encode()).hexdigest()
                if prev_raw else None
            )
            if entry.prev_hash != expected_prev:
                errors.append(
                    f"seq={entry.seq} ts={entry.ts}: broken hash chain "
                    f"(expected {expected_prev!r}, got {entry.prev_hash!r})"
                )
            prev_raw = raw

        return (len(errors) == 0, errors)

    def count(self) -> int:
        return len(self._read_all_entries())


# ---------------------------------------------------------------------------
# AuditReader — read-only scoped interface for third-party auditors
# ---------------------------------------------------------------------------

class AuditReader:
    """
    Read-only view of an AuditStore.  Hand this to external auditors.
    Exposes: query, export_json, export_jsonld, verify, count.
    Does NOT expose: record, purge, delete_store, apply_retention.
    """

    def __init__(
        self,
        store_dir:  Path,
        passphrase: Optional[str] = None,
    ) -> None:
        # Internally uses AuditStore but we only surface read methods
        self._store = AuditStore(store_dir=store_dir, passphrase=passphrase)

    def query(self, **kwargs) -> List[StoredAuditEntry]:
        return self._store.query(**kwargs)

    def export_json(self) -> str:
        return self._store.export_json()

    def export_jsonld(self) -> str:
        return self._store.export_jsonld()

    def verify(self) -> Tuple[bool, List[str]]:
        return self._store.verify()

    def count(self) -> int:
        return self._store.count()
