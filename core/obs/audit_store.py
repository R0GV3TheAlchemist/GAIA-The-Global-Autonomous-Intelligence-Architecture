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

StorageBackend mirror (Issue #281)
----------------------------------
The NDJSON file is the canonical ledger — its hash-chain, HMAC, and
fsync guarantees cannot be replicated by a generic KV store.  The
StorageBackend is a *secondary mirror* that enables:

  • Mesh-wide audit queries across nodes
    (key prefix: audit:<gaian_id>:<iso_ts>:<seq>)
  • Pluggable backend swap via GAIA_STORAGE_BACKEND env var
    (SQLite by default → CockroachDB in Phase 2)
  • Health check via AuditStore.backend_ping()

Dual-write strategy: NDJSON write always happens first.  Backend mirror
failures are caught and logged but never propagate — the local ledger
is always the source of truth.

Usage
-----
    from core.obs.audit_store import AuditStore, AuditReader

    # Existing usage — unchanged, backend auto-configured from env
    store = AuditStore(store_dir=Path(".gaia/audit"), passphrase="secret")
    store.record(event_type="agent.action", actor="planner",
                 action="call_tool", outcome="ok")

    # Inject a specific backend (e.g. MemoryBackend for tests)
    from core.storage import MemoryBackend
    store = AuditStore(store_dir=Path(".gaia/audit"), backend=MemoryBackend())

    # Cross-node mesh audit query (async)
    entries = await store.query_backend(prefix="audit:luna:")

    reader = AuditReader(store_dir=Path(".gaia/audit"), passphrase="secret")
    ok, errors = reader.verify()
"""
from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
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

try:
    from core.storage import StorageBackend, get_backend
    _STORAGE_AVAILABLE = True
except ImportError:
    _STORAGE_AVAILABLE = False
    StorageBackend = object  # type: ignore[misc,assignment]

logger = logging.getLogger("gaia.obs.audit_store")


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NDJSON_FILENAME   = "audit.ndjson"
KEY_FILENAME      = "audit.key"
SALT_FILENAME     = "audit.salt"

PBKDF2_ITERATIONS = 260_000   # OWASP 2023 recommendation for HMAC-SHA256
KEY_BYTES         = 32

# Key prefix for all audit entries in the StorageBackend
# Format: audit:<gaian_id>:<iso_ts>:<seq>
# Allows mesh-wide prefix scan: query_backend(prefix="audit:luna:")
BACKEND_KEY_PREFIX = "audit"

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

    def to_bytes(self) -> bytes:
        """Serialise to bytes for StorageBackend.put()."""
        return self.to_line().encode("utf-8")

    @staticmethod
    def from_line(line: str) -> "StoredAuditEntry":
        d = json.loads(line)
        return StoredAuditEntry(**{k: d.get(k) for k in StoredAuditEntry.__dataclass_fields__})

    @staticmethod
    def from_bytes(data: bytes) -> "StoredAuditEntry":
        """Deserialise from StorageBackend.get() bytes."""
        return StoredAuditEntry.from_line(data.decode("utf-8"))


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
# StorageBackend mirror helpers
# ---------------------------------------------------------------------------

def _backend_key(gaian_id: str, entry: StoredAuditEntry) -> str:
    """
    Build the backend key for a single audit entry.
    Format: audit:<gaian_id>:<iso_ts>:<seq>

    ISO timestamp is URL-safe (colons replaced with hyphens) so the key
    sorts chronologically and is safe as a prefix in query().
    """
    safe_ts = entry.ts.replace(":", "-").replace("+", "Z")
    return f"{BACKEND_KEY_PREFIX}:{gaian_id}:{safe_ts}:{entry.seq:010d}"


def _mirror_sync(backend: Any, key: str, value: bytes, ttl: Optional[int]) -> None:
    """
    Fire-and-forget mirror write.  Runs `backend.put()` in a background
    thread so the synchronous record() call is never delayed by async I/O.
    The NDJSON write has already succeeded before this is called.
    """
    def _run() -> None:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(backend.put(key, value, ttl=ttl))
            loop.close()
        except Exception as exc:
            logger.warning(
                f"[AuditStore] ⚠ Backend mirror write failed (non-fatal): "
                f"key={key!r} err={exc}"
            )
    t = threading.Thread(target=_run, daemon=True, name="audit-mirror")
    t.start()


# ---------------------------------------------------------------------------
# AuditStore — write + read
# ---------------------------------------------------------------------------

class AuditStore:
    """
    Append-only, signed, hash-chained audit log backed by an NDJSON file,
    with an optional StorageBackend mirror for mesh-wide queries.

    Parameters
    ----------
    store_dir  : directory where audit.ndjson (and key/salt) are stored.
    passphrase : optional Gaian passphrase for key derivation.  If omitted,
                 an auto-generated key is used.
    max_days   : retention policy in days.  Entries older than this are
                 pruned on open and when apply_retention() is called.
                 0 = no retention limit.
    backend    : optional StorageBackend for secondary mirror persistence.
                 Defaults to get_backend() (SQLite) when core.storage is
                 available.  Pass None to disable mirroring entirely.
    gaian_id   : identifier used as the namespace in backend keys.
                 Defaults to 'unknown'.  Set to the Gaian's name/slug.
    backend_ttl: TTL in seconds for backend mirror entries.  None = no expiry.
                 Useful for telemetry-style audit entries that don't need
                 indefinite backend retention.  The NDJSON file is unaffected.
    """

    def __init__(
        self,
        store_dir:   Path,
        passphrase:  Optional[str]     = None,
        max_days:    int               = 0,
        backend:     Optional[Any]     = ...,   # ... sentinel = "use default"
        gaian_id:    str               = "unknown",
        backend_ttl: Optional[int]     = None,
    ) -> None:
        self._dir      = Path(store_dir)
        self._path     = self._dir / NDJSON_FILENAME
        self._max_days = max_days
        self._lock     = threading.RLock()
        self._seq      = 0
        self._prev_hash: Optional[str] = None
        self._gaian_id  = gaian_id
        self._backend_ttl = backend_ttl

        self._dir.mkdir(parents=True, exist_ok=True)
        self._key = _load_or_create_key(self._dir, passphrase)

        # ── StorageBackend setup ───────────────────────────────────────
        # Three cases:
        #   backend=...  (sentinel) → use module default (SQLite)
        #   backend=None            → mirroring disabled
        #   backend=<instance>      → use the supplied backend
        if backend is ...:
            if _STORAGE_AVAILABLE:
                try:
                    self._backend: Optional[Any] = get_backend()
                except Exception as exc:
                    logger.warning(
                        f"[AuditStore] Could not initialise default backend: {exc}. "
                        "Mirroring disabled."
                    )
                    self._backend = None
            else:
                self._backend = None
        else:
            self._backend = backend

        if self._backend is not None:
            logger.debug(
                f"[AuditStore] Backend mirror: {self._backend!r} "
                f"(gaian_id={gaian_id!r})"
            )

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
        outcome:    str                      = "ok",
        resource:   Optional[str]            = None,
        meta:       Optional[Dict[str, Any]] = None,
        trace_id:   Optional[str]            = None,
    ) -> StoredAuditEntry:
        """
        Append a signed, hash-chained audit entry to the NDJSON store,
        then mirror it to the StorageBackend (non-blocking, non-fatal).
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

            # 1. NDJSON write — always first, always fsync’d, always wins.
            self._append_line(line)
            self._prev_hash = hashlib.sha256(line.encode()).hexdigest()
            self._seq += 1

        # 2. Backend mirror — fire-and-forget, never blocks record().
        #    Runs outside the lock so it cannot cause a deadlock.
        if self._backend is not None:
            bkey = _backend_key(self._gaian_id, entry)
            _mirror_sync(self._backend, bkey, entry.to_bytes(), self._backend_ttl)

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
        Logs a PURGE record BEFORE modifying the file so the intent is
        always durable and cannot be erased by the purge itself.
        Returns number of entries deleted.
        """
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
            removed_count = len(pairs) - len(kept)
            if removed_count:
                self._rewrite(kept)
        self.record(
            event_type = "audit.purge",
            actor      = "gaian",
            action     = "purge",
            outcome    = "ok",
            meta       = {"before_ts": before_ts, "removed_count": removed_count},
        )
        return removed_count

    def delete_store(self) -> None:
        """Gaian full wipe — delete the NDJSON file entirely."""
        with self._lock:
            if self._path.exists():
                self._path.unlink()
            self._seq       = 0
            self._prev_hash = None

    # ------------------------------------------------------------------
    # Local read API (sync, from NDJSON file)
    # ------------------------------------------------------------------

    def query(
        self,
        event_type: Optional[str] = None,
        actor:      Optional[str] = None,
        outcome:    Optional[str] = None,
        since:      Optional[str] = None,
    ) -> List[StoredAuditEntry]:
        """Filter entries by optional criteria from the local NDJSON file."""
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
          1. Each entry’s HMAC signature is valid.
          2. Each entry’s prev_hash matches SHA-256 of the previous raw line.

        Returns (all_ok: bool, errors: List[str]).
        """
        errors: List[str] = []
        pairs = self._read_all_entries()

        prev_raw: Optional[str] = None
        for raw, entry in pairs:
            if not _verify_sig(entry, self._key):
                errors.append(
                    f"seq={entry.seq} ts={entry.ts}: invalid signature"
                )
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

    # ------------------------------------------------------------------
    # Distributed backend API (async — for mesh-wide audit queries)
    # ------------------------------------------------------------------

    async def query_backend(
        self,
        prefix:    Optional[str] = None,
        limit:     int           = 200,
    ) -> List[StoredAuditEntry]:
        """
        Query the StorageBackend for audit entries matching a key prefix.

        This enables mesh-wide audit queries: entries from all nodes that
        share the same backend (e.g. CockroachDB) are visible here.

        Args:
            prefix: Key prefix to scan.  Defaults to
                    f"{BACKEND_KEY_PREFIX}:{self._gaian_id}:"
                    to return all entries for this Gaian.
                    Use "audit:" to scan across all Gaians on the mesh.
            limit:  Maximum entries to return.

        Returns:
            List of StoredAuditEntry, sorted by backend key (chronological).
            Returns [] if the backend is unavailable.

        Example::

            # All entries for this Gaian:
            entries = await store.query_backend()

            # All entries for 'luna' since today (ISO prefix scan):
            entries = await store.query_backend(prefix="audit:luna:2026-06-10")

            # All entries across the entire mesh:
            entries = await store.query_backend(prefix="audit:")
        """
        if self._backend is None:
            logger.debug("[AuditStore] query_backend called but no backend configured.")
            return []

        scan_prefix = prefix or f"{BACKEND_KEY_PREFIX}:{self._gaian_id}:"
        try:
            rows = await self._backend.query(scan_prefix, limit=limit)
        except Exception as exc:
            logger.warning(f"[AuditStore] ⚠ query_backend failed: {exc}")
            return []

        entries: List[StoredAuditEntry] = []
        for _key, raw_bytes in rows:
            try:
                entries.append(StoredAuditEntry.from_bytes(raw_bytes))
            except Exception as exc:
                logger.debug(f"[AuditStore] Skipping undecodable backend entry: {exc}")
        return entries

    async def backend_ping(self) -> bool:
        """
        Health-check the StorageBackend.
        Returns True if reachable, False if unavailable or not configured.
        Used by the mesh server health endpoint.
        """
        if self._backend is None:
            return False
        try:
            return await self._backend.ping()
        except Exception:
            return False


# ---------------------------------------------------------------------------
# AuditReader — read-only scoped interface for third-party auditors
# ---------------------------------------------------------------------------

class AuditReader:
    """
    Read-only view of an AuditStore.  Hand this to external auditors.
    Exposes: query, export_json, export_jsonld, verify, count,
             query_backend (async), backend_ping (async).
    Does NOT expose: record, purge, delete_store, apply_retention.
    """

    def __init__(
        self,
        store_dir:  Path,
        passphrase: Optional[str] = None,
        gaian_id:   str           = "unknown",
        backend:    Optional[Any] = ...,
    ) -> None:
        self._store = AuditStore(
            store_dir=store_dir,
            passphrase=passphrase,
            gaian_id=gaian_id,
            backend=backend,
        )

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

    async def query_backend(
        self,
        prefix: Optional[str] = None,
        limit:  int           = 200,
    ) -> List[StoredAuditEntry]:
        """Async mesh-wide audit query — passes through to AuditStore."""
        return await self._store.query_backend(prefix=prefix, limit=limit)

    async def backend_ping(self) -> bool:
        return await self._store.backend_ping()
