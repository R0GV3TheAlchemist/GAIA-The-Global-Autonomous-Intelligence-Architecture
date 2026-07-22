"""core.obs.audit_store

AuditStore — Tamper-evident, append-only audit log.

Design intent
-------------
Every governance-relevant action in NEXUS (capability grants, consent
decisions, agent overrides, mesh topology changes, crisis escalations)
should produce an ``AuditRecord`` and pass it to ``AuditStore.record()``.

The store:
1. Appends records to an in-memory ledger.
2. Chains each record to its predecessor via a SHA-256 hash link,
   forming a lightweight append-only Merkle chain — any tampering
   invalidates all subsequent records.
3. Exposes ``query()`` for filtered retrieval and ``export()`` for
   JSON / NDJSON serialisation (useful for compliance reporting).

Phase B scope
-------------
- ``record()`` is fully functional (in-memory ledger + hash chain).
- ``query()`` supports filtering by source, event_type, and time range.
- ``export()`` is stubbed and raises ``NotImplementedError``.

Future backends (Phase D)
--------------------------
- SQLite / PostgreSQL for persistence.
- IPFS / Filecoin for planetary-scale immutable storage.
- Integration with ``sidecar.telemetry.TelemetryCollector`` so every
  AuditRecord is also emitted as a telemetry event.

References
----------
- Portable Agent Memory (arXiv 2605.11032): Merkle-DAG provenance graph
  for tamper-evidence and capability-based access control.
- NEXUS GOVERNANCE.md: governance event taxonomy.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterator, Mapping, Sequence


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------

@dataclass
class AuditRecord:
    """A single immutable governance audit record.

    Parameters
    ----------
    source:
        Module or component that generated the record
        (e.g. ``"crisisengine"``, ``"sovereignmemory"``).
    event_type:
        Short, dot-namespaced event type
        (e.g. ``"capability.granted"``, ``"consent.denied"``,
        ``"crisis.escalated"``).
    payload:
        Structured data describing the event.  Must be
        JSON-serialisable.
    actor:
        Identity of the agent / user initiating the action.
        ``None`` if the event is system-generated.
    record_id:
        Auto-generated UUID.
    timestamp:
        UTC timestamp assigned at construction time.
    prev_hash:
        SHA-256 hash of the previous record's canonical representation.
        ``"GENESIS"`` for the first record in the chain.
    record_hash:
        SHA-256 hash of *this* record's canonical representation
        (populated by ``AuditStore.record()``).
    """
    source: str
    event_type: str
    payload: Mapping[str, Any] = field(default_factory=dict)
    actor: str | None = None
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(tz=timezone.utc)
    )
    prev_hash: str = "GENESIS"
    record_hash: str = ""

    def canonical(self) -> str:
        """Return the canonical JSON string used for hashing.

        The canonical form excludes ``record_hash`` (which is computed
        from all other fields) and sorts keys deterministically.
        """
        data = {
            "record_id": self.record_id,
            "source": self.source,
            "event_type": self.event_type,
            "actor": self.actor,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "prev_hash": self.prev_hash,
        }
        return json.dumps(data, sort_keys=True)


@dataclass
class AuditQuery:
    """Filter parameters for ``AuditStore.query()``.

    All filters are ANDed together.  Omit (leave as ``None``) any
    dimension you do not wish to filter on.

    Parameters
    ----------
    source:
        Match records whose ``source`` equals this value.
    event_type_prefix:
        Match records whose ``event_type`` starts with this prefix
        (e.g. ``"capability"`` matches ``"capability.granted"``).
    actor:
        Match records with this actor value.
    since:
        Include only records at or after this UTC datetime.
    until:
        Include only records before or at this UTC datetime.
    limit:
        Maximum number of records to return (most recent first).
        ``None`` means no limit.
    """
    source: str | None = None
    event_type_prefix: str | None = None
    actor: str | None = None
    since: datetime | None = None
    until: datetime | None = None
    limit: int | None = None


# ---------------------------------------------------------------------------
# AuditStore
# ---------------------------------------------------------------------------

class AuditStore:
    """Tamper-evident, append-only audit log for NEXUS governance events.

    Usage
    -----
    .. code-block:: python

        from core.obs.audit_store import AuditStore

        store = AuditStore()
        record = store.record(
            source="crisisengine",
            event_type="crisis.escalated",
            payload={"severity": "CRITICAL", "modules_affected": ["mesh"]},
            actor="nexus-kernel",
        )
        print(record.record_hash)  # SHA-256 chain link

    Integrity verification
    ----------------------
    Call ``verify_chain()`` at any time to assert that the hash chain
    is unbroken.  Returns ``True`` if intact, raises
    ``IntegrityError`` otherwise.
    """

    class IntegrityError(Exception):
        """Raised when the audit chain hash verification fails."""

    def __init__(self) -> None:
        self._ledger: list[AuditRecord] = []
        self._head_hash: str = "GENESIS"

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def record(
        self,
        source: str,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
        actor: str | None = None,
    ) -> AuditRecord:
        """Append a new ``AuditRecord`` to the ledger.

        Computes the SHA-256 hash of the canonical record representation
        and chains it to the previous record's hash.

        Args:
            source:     Emitting module identifier.
            event_type: Dot-namespaced event type string.
            payload:    Structured event data (must be JSON-serialisable).
            actor:      Identity of the agent / user initiating the action.

        Returns:
            The appended ``AuditRecord`` with ``prev_hash`` and
            ``record_hash`` populated.
        """
        rec = AuditRecord(
            source=source,
            event_type=event_type,
            payload=payload or {},
            actor=actor,
            prev_hash=self._head_hash,
        )
        canonical = rec.canonical()
        rec.record_hash = hashlib.sha256(canonical.encode()).hexdigest()
        self._head_hash = rec.record_hash
        self._ledger.append(rec)
        return rec

    def query(self, q: AuditQuery | None = None) -> list[AuditRecord]:
        """Return records matching the given ``AuditQuery``.

        Records are returned in chronological order (oldest first) unless
        ``q.limit`` is set, in which case the *most recent* ``limit``
        records matching the filter are returned.

        Args:
            q: ``AuditQuery`` filter.  Pass ``None`` to return all records.

        Returns:
            Filtered list of ``AuditRecord`` instances.
        """
        q = q or AuditQuery()
        results: list[AuditRecord] = []

        for rec in self._ledger:
            if q.source is not None and rec.source != q.source:
                continue
            if (
                q.event_type_prefix is not None
                and not rec.event_type.startswith(q.event_type_prefix)
            ):
                continue
            if q.actor is not None and rec.actor != q.actor:
                continue
            if q.since is not None and rec.timestamp < q.since:
                continue
            if q.until is not None and rec.timestamp > q.until:
                continue
            results.append(rec)

        if q.limit is not None:
            results = results[-q.limit:]

        return results

    def verify_chain(self) -> bool:
        """Verify the integrity of the entire hash chain.

        Recomputes each record's hash and checks that it matches the
        stored ``record_hash`` and that ``prev_hash`` equals the previous
        record's hash.

        Returns:
            ``True`` if the chain is intact.

        Raises:
            AuditStore.IntegrityError: If any record's hash is invalid
                or the chain linkage is broken.
        """
        prev = "GENESIS"
        for i, rec in enumerate(self._ledger):
            if rec.prev_hash != prev:
                raise AuditStore.IntegrityError(
                    f"Chain broken at index {i}: "
                    f"prev_hash mismatch (expected {prev!r}, "
                    f"got {rec.prev_hash!r})."
                )
            expected = hashlib.sha256(rec.canonical().encode()).hexdigest()
            if rec.record_hash != expected:
                raise AuditStore.IntegrityError(
                    f"Hash mismatch at index {i} (record_id={rec.record_id!r}): "
                    f"expected {expected!r}, stored {rec.record_hash!r}."
                )
            prev = rec.record_hash
        return True

    # ------------------------------------------------------------------
    # Export stub (Phase D)
    # ------------------------------------------------------------------

    def export(
        self,
        fmt: str = "ndjson",
        q: AuditQuery | None = None,
    ) -> str:
        """Serialise matching records to the requested format.

        Intended implementation
        -----------------------
        - ``"ndjson"``: one JSON object per line (Newline-Delimited JSON),
          ideal for log ingestion pipelines.
        - ``"json"``: a JSON array.
        - ``"csv"``: comma-separated with a header row.

        Args:
            fmt: Output format — ``"ndjson"`` (default), ``"json"``,
                 or ``"csv"``.
            q:   Optional ``AuditQuery`` filter.

        Returns:
            Serialised string in the requested format.

        Raises:
            NotImplementedError: Always in Phase B.
        """
        raise NotImplementedError(
            f"AuditStore.export(fmt={fmt!r}) is not yet implemented. "
            "Expected: serialise self.query(q) to the requested format."
        )

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        """Return the number of records in the ledger."""
        return len(self._ledger)

    def head_hash(self) -> str:
        """Return the hash of the most recently appended record."""
        return self._head_hash

    def __iter__(self) -> Iterator[AuditRecord]:
        """Iterate over all records in chronological order."""
        return iter(self._ledger)
