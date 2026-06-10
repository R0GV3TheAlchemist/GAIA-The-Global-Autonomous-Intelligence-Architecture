"""TelemetryCollector — append-only local telemetry store and query layer.

GAIA-OS Issue #188.
GAIA-OS Issue #281 — StorageBackend mirror added.

Features:
- Append-only SQLite store (primary — all query methods read from here).
- StorageBackend mirror (secondary, fire-and-forget, pluggable).
  Key format: telemetry:<session_id>:<safe_iso_ts>:<event_id>
  Phase 2: swap to CockroachDB via GAIA_STORAGE_BACKEND=cockroachdb.
- Real-time stream hooks for Glass Room.
- High-value event indexing hook for Crystal.
- Session trace, skill health, DQ history, OE windows.
- Local-only export and deletion helpers.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Awaitable, Callable, Optional

from .orchestration_efficiency import OrchestrationEfficiency
from .telemetry_event import TelemetryEvent

try:
    from core.storage import get_backend as _get_storage_backend
    _STORAGE_AVAILABLE = True
except ImportError:
    _STORAGE_AVAILABLE = False
    _get_storage_backend = None  # type: ignore[assignment]

logger = logging.getLogger("gaia.telemetry.collector")

# Backend key prefix for all telemetry mirror entries.
# Format: telemetry:<session_id>:<safe_iso_ts>:<event_id>
# Allows prefix scans:
#   telemetry:<session_id>:            → all events in a session
#   telemetry:<session_id>:2026-06-10  → session events on a given day
_BACKEND_KEY_PREFIX = "telemetry"


@dataclass
class SkillHealthReport:
    skill_id: str
    window_min: int
    event_count: int
    error_rate: float
    avg_latency_ms: float
    circuit_state: str
    degraded_count: int
    last_failure_at: str | None


@dataclass
class DecisionQualityRecord:
    event_id: str
    timestamp: str
    skill_id: str | None
    dq_score: float
    degraded: bool
    fallback_mode: str | None


def _backend_key(session_id: str, iso_ts: str, event_id: str) -> str:
    """
    Build the backend mirror key for a telemetry event.
    ISO timestamp colons replaced with hyphens for URL-safety and
    lexicographic chronological ordering.
    """
    safe_ts = iso_ts.replace(":", "-").replace("+", "Z")
    return f"{_BACKEND_KEY_PREFIX}:{session_id}:{safe_ts}:{event_id}"


def _mirror_event(
    backend: Any,
    key: str,
    payload: bytes,
    ttl: Optional[int] = None,
) -> None:
    """
    Fire-and-forget mirror write to the StorageBackend.
    Runs in a daemon thread so emit() is never delayed.
    Failures are warned but never propagated.
    """
    def _run() -> None:
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(backend.put(key, payload, ttl=ttl))
            loop.close()
        except Exception as exc:
            logger.warning(
                f"[TelemetryCollector] ⚠ Backend mirror write failed (non-fatal): "
                f"key={key!r} err={exc}"
            )
    threading.Thread(target=_run, daemon=True, name="telemetry-mirror").start()


class TelemetryCollector:
    """
    Append-only telemetry store with SQLite primary persistence and an
    optional StorageBackend mirror for mesh-wide telemetry queries.

    Parameters
    ----------
    db_path          : Path to the local SQLite database.
    stream_callback  : Optional async callback fired for every event
                       (Glass Room live feed).
    crystal_index_callback : Optional async callback for high-value
                       events (risk_tier YELLOW/RED or degraded).
    storage_backend  : Optional StorageBackend for mirror writes.
                       Defaults to get_backend() SQLite singleton.
                       Pass None to disable mirroring entirely.
    backend_ttl      : TTL in seconds for backend mirror entries.
                       None = no expiry.  Useful for short-lived
                       session telemetry.  Local SQLite unaffected.
    """

    def __init__(
        self,
        db_path: str | Path = "sidecar/telemetry/telemetry.db",
        stream_callback: Callable[[TelemetryEvent], Awaitable[None]] | None = None,
        crystal_index_callback: Callable[[TelemetryEvent], Awaitable[None]] | None = None,
        storage_backend: Any = ...,   # ... sentinel = use default
        backend_ttl: Optional[int] = None,
    ) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._stream_callback = stream_callback
        self._crystal_index_callback = crystal_index_callback
        self._backend_ttl = backend_ttl
        self._init_db()

        # ── StorageBackend setup (same sentinel pattern as AuditStore) ──
        if storage_backend is ...:
            if _STORAGE_AVAILABLE and _get_storage_backend is not None:
                try:
                    self._backend: Optional[Any] = _get_storage_backend()
                except Exception as exc:
                    logger.warning(
                        f"[TelemetryCollector] Could not initialise default backend: {exc}. "
                        "Mirroring disabled."
                    )
                    self._backend = None
            else:
                self._backend = None
        else:
            self._backend = storage_backend

        if self._backend is not None:
            logger.debug(f"[TelemetryCollector] Backend mirror: {self._backend!r}")

    # ──────────────────────────────────────────
    # DB INIT
    # ──────────────────────────────────────────

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS telemetry_events (
                    id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    skill_id TEXT,
                    trust_tier TEXT,
                    intent_class TEXT,
                    risk_tier TEXT,
                    input_summary TEXT NOT NULL,
                    output_summary TEXT NOT NULL,
                    duration_ms INTEGER NOT NULL,
                    dq_score REAL,
                    degraded INTEGER NOT NULL,
                    fallback_mode TEXT,
                    biometric_context TEXT,
                    planetary_context TEXT,
                    canon_refs TEXT NOT NULL,
                    tags TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_session ON telemetry_events(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_skill ON telemetry_events(skill_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry_events(timestamp)")
            conn.commit()

    # ──────────────────────────────────────────
    # EMIT — hot path
    # ──────────────────────────────────────────

    async def emit(self, event: TelemetryEvent) -> None:
        """
        Persist a telemetry event.

        Execution order (all non-blocking relative to the caller):
          1. SQLite write  — always first, awaited via asyncio.to_thread
          2. stream_callback (Glass Room live feed)  — awaited if set
          3. crystal_index_callback (high-value events)  — awaited if set
          4. Backend mirror  — fire-and-forget daemon thread, never awaited
        """
        # 1. Primary local SQLite write
        await asyncio.to_thread(self._write_to_sqlite, event)

        # 2. Glass Room stream
        if self._stream_callback is not None:
            await self._stream_callback(event)

        # 3. Crystal high-value index
        if self._should_index_to_crystal(event) and self._crystal_index_callback is not None:
            await self._crystal_index_callback(event)

        # 4. Backend mirror — fire-and-forget, never delays emit()
        if self._backend is not None:
            record = event.to_record()
            iso_ts = record["timestamp"]
            bkey = _backend_key(record["session_id"], iso_ts, record["id"])
            payload = json.dumps(record, separators=(",", ":"), default=str).encode("utf-8")
            _mirror_event(self._backend, bkey, payload, self._backend_ttl)

    # ──────────────────────────────────────────
    # LOCAL SQLITE WRITE
    # ──────────────────────────────────────────

    def _write_to_sqlite(self, event: TelemetryEvent) -> None:
        record = event.to_record()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO telemetry_events (
                    id, timestamp, session_id, source, event_type, skill_id,
                    trust_tier, intent_class, risk_tier, input_summary,
                    output_summary, duration_ms, dq_score, degraded,
                    fallback_mode, biometric_context, planetary_context,
                    canon_refs, tags
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["timestamp"],
                    record["session_id"],
                    record["source"],
                    record["event_type"],
                    record["skill_id"],
                    record["trust_tier"],
                    record["intent_class"],
                    record["risk_tier"],
                    record["input_summary"],
                    record["output_summary"],
                    record["duration_ms"],
                    record["dq_score"],
                    1 if record["degraded"] else 0,
                    record["fallback_mode"],
                    record["biometric_context"],
                    record["planetary_context"],
                    json.dumps(record["canon_refs"]),
                    json.dumps(record["tags"]),
                ),
            )
            conn.commit()

    def _should_index_to_crystal(self, event: TelemetryEvent) -> bool:
        return event.risk_tier in ("YELLOW", "RED") or event.degraded is True

    # ──────────────────────────────────────────
    # LOCAL QUERY METHODS (unchanged — all read from SQLite)
    # ──────────────────────────────────────────

    async def get_session_trace(self, session_id: str) -> list[TelemetryEvent]:
        rows = await asyncio.to_thread(self._query_session_trace, session_id)
        return [self._row_to_event(row) for row in rows]

    def _query_session_trace(self, session_id: str) -> list[sqlite3.Row]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM telemetry_events WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,),
            )
            return list(cursor.fetchall())

    async def get_skill_health(self, skill_id: str, window_min: int = 60) -> SkillHealthReport:
        rows = await asyncio.to_thread(self._query_skill_window, skill_id, window_min)
        event_count = len(rows)
        failure_rows = [r for r in rows if r["event_type"] in ("job_failed", "fallback_used", "circuit_broken")]
        degraded_count = sum(1 for r in rows if r["degraded"] == 1)
        durations = [r["duration_ms"] for r in rows if r["duration_ms"] is not None]
        avg_latency = mean(durations) if durations else 0.0
        last_failure = failure_rows[-1]["timestamp"] if failure_rows else None
        circuit_state = "CLOSED"
        if any(r["event_type"] == "circuit_broken" for r in rows):
            circuit_state = "OPEN"
        elif any(r["event_type"] == "fallback_used" for r in rows):
            circuit_state = "HALF_OPEN"
        return SkillHealthReport(
            skill_id=skill_id,
            window_min=window_min,
            event_count=event_count,
            error_rate=(len(failure_rows) / event_count) if event_count else 0.0,
            avg_latency_ms=avg_latency,
            circuit_state=circuit_state,
            degraded_count=degraded_count,
            last_failure_at=last_failure,
        )

    def _query_skill_window(self, skill_id: str, window_min: int) -> list[sqlite3.Row]:
        cutoff = (datetime.now(timezone.utc) - timedelta(minutes=window_min)).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM telemetry_events WHERE skill_id = ? AND timestamp >= ? ORDER BY timestamp ASC",
                (skill_id, cutoff),
            )
            return list(cursor.fetchall())

    async def get_dq_history(self, limit: int = 100) -> list[DecisionQualityRecord]:
        rows = await asyncio.to_thread(self._query_dq_history, limit)
        return [
            DecisionQualityRecord(
                event_id=row["id"],
                timestamp=row["timestamp"],
                skill_id=row["skill_id"],
                dq_score=row["dq_score"],
                degraded=bool(row["degraded"]),
                fallback_mode=row["fallback_mode"],
            )
            for row in rows
        ]

    def _query_dq_history(self, limit: int) -> list[sqlite3.Row]:
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM telemetry_events WHERE dq_score IS NOT NULL ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )
            return list(cursor.fetchall())

    async def get_oe_window(self, window: str) -> OrchestrationEfficiency:
        mapping = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}
        hours = mapping.get(window, 24)
        rows = await asyncio.to_thread(self._query_window_hours, hours)
        return OrchestrationEfficiency.from_events(window, [dict(r) for r in rows])

    def _query_window_hours(self, hours: int) -> list[sqlite3.Row]:
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM telemetry_events WHERE timestamp >= ? ORDER BY timestamp ASC",
                (cutoff,),
            )
            return list(cursor.fetchall())

    async def export_session_trace_json(self, session_id: str) -> str:
        events = await self.get_session_trace(session_id)
        return json.dumps([e.to_record() for e in events], indent=2)

    async def delete_range(self, start_iso: str, end_iso: str) -> int:
        return await asyncio.to_thread(self._delete_range, start_iso, end_iso)

    def _delete_range(self, start_iso: str, end_iso: str) -> int:
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM telemetry_events WHERE timestamp >= ? AND timestamp <= ?",
                (start_iso, end_iso),
            )
            conn.commit()
            return cursor.rowcount

    # ──────────────────────────────────────────
    # HEALTH
    # ──────────────────────────────────────────

    async def backend_ping(self) -> bool:
        """
        Health-check the StorageBackend.
        Returns True if reachable, False if unavailable or not configured.
        Consistent with AuditStore.backend_ping() and
        SovereignMemory.backend_ping() for the mesh health endpoint.
        """
        if self._backend is None:
            return False
        try:
            return await self._backend.ping()
        except Exception:
            return False

    # ──────────────────────────────────────────
    # INTERNAL HELPERS
    # ──────────────────────────────────────────

    def _row_to_event(self, row: sqlite3.Row) -> TelemetryEvent:
        return TelemetryEvent(
            id=row["id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            session_id=row["session_id"],
            source=row["source"],
            event_type=row["event_type"],
            skill_id=row["skill_id"],
            trust_tier=row["trust_tier"],
            intent_class=row["intent_class"],
            risk_tier=row["risk_tier"],
            input_summary=row["input_summary"],
            output_summary=row["output_summary"],
            duration_ms=row["duration_ms"],
            dq_score=row["dq_score"],
            degraded=bool(row["degraded"]),
            fallback_mode=row["fallback_mode"],
            biometric_context=row["biometric_context"],
            planetary_context=row["planetary_context"],
            canon_refs=json.loads(row["canon_refs"]),
            tags=json.loads(row["tags"]),
        )
