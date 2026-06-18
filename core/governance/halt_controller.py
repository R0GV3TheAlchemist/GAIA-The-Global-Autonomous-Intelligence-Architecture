"""HaltController — verifiable, externally-triggerable stoppability for GAIA.

Design goals (from issue #250):
- Staged halt modes: PAUSE (suspend + resume), SOFT_STOP (finish current
  cycle then stop), HARD_STOP (immediate cancellation of all sessions).
- Distributed session registry so a single cancel signal reaches every
  active AgenticLoop session.
- Signed halt audit trail — every halt event is HMAC-signed and stored
  durably in an append-only JSON-Lines file.
- Dead-man's switch — if the Gaian liveness heartbeat is not received
  within the configured interval, GAIA auto-halts.
- Halt SLA — maximum time from cancel signal to full stop is enforced
  and logged; any breach is flagged in the audit trail.
- Thread-safe; designed for use under asyncio (sync API wraps asyncio
  primitives via threading.Event for cross-thread compatibility).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Optional, Set

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Enums & data classes
# ---------------------------------------------------------------------------


class HaltMode(str, Enum):
    """Staged halt levels."""
    PAUSE = "PAUSE"           # Suspend all sessions; resumable
    SOFT_STOP = "SOFT_STOP"   # Finish current iteration, then stop
    HARD_STOP = "HARD_STOP"   # Immediate cancellation — no grace period


class HaltStatus(str, Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    SOFT_STOPPING = "SOFT_STOPPING"
    STOPPED = "STOPPED"


def _hmac_sign(secret: bytes, payload: bytes) -> str:
    """Compute an HMAC-SHA256 hex digest. Compatible with Python 3.4+."""
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


@dataclass
class HaltRecord:
    """Immutable, HMAC-signed audit record for a single halt event."""
    event_id: str
    timestamp: float
    mode: str
    triggered_by: str          # Gaian identifier or "DEADMANS_SWITCH"
    sessions_affected: list
    sla_deadline: float        # Expected completion time (epoch)
    sla_met: Optional[bool]    # Set to True/False when halt completes
    completion_time: Optional[float]
    signature: str = field(default="", repr=False)

    def _payload(self) -> bytes:
        return json.dumps(
            {
                "event_id": self.event_id,
                "timestamp": self.timestamp,
                "mode": self.mode,
                "triggered_by": self.triggered_by,
            },
            sort_keys=True,
        ).encode()

    def sign(self, secret: bytes) -> None:
        self.signature = _hmac_sign(secret, self._payload())

    def verify(self, secret: bytes) -> bool:
        expected = _hmac_sign(secret, self._payload())
        return hmac.compare_digest(self.signature, expected)


# ---------------------------------------------------------------------------
# Session handle
# ---------------------------------------------------------------------------


@dataclass
class SessionHandle:
    """Lightweight reference to a running AgenticLoop session."""
    session_id: str
    cancel_fn: Callable[[], None]    # Calls AgenticLoop.cancel()
    pause_fn: Callable[[], None]     # Calls AgenticLoop.pause()
    resume_fn: Callable[[], None]    # Calls AgenticLoop.resume()
    gaian_id: str = "unknown"


# ---------------------------------------------------------------------------
# HaltController
# ---------------------------------------------------------------------------


class HaltController:
    """Singleton controller for GAIA stoppability governance.

    Usage::

        ctrl = HaltController.get_instance()
        ctrl.register_session(handle)
        # ... later, from API handler:
        ctrl.halt(HaltMode.SOFT_STOP, triggered_by="gaian-42")
    """

    _instance: Optional["HaltController"] = None
    _lock: threading.Lock = threading.Lock()

    # SLA: maximum seconds from halt signal to full stop
    DEFAULT_SLA_SECONDS: float = float(os.getenv("GAIA_HALT_SLA_SECONDS", "30"))
    # Dead-man's switch: Gaian must call heartbeat() within this interval
    DEFAULT_HEARTBEAT_INTERVAL: float = float(
        os.getenv("GAIA_HEARTBEAT_INTERVAL_SECONDS", "120")
    )
    AUDIT_FILE: Path = Path(os.getenv("GAIA_HALT_AUDIT_FILE", "/tmp/gaia_halt_audit.jsonl"))
    _HMAC_SECRET: bytes = os.getenv("GAIA_HALT_HMAC_SECRET", "gaia-default-secret").encode()

    def __init__(self) -> None:
        self._status: HaltStatus = HaltStatus.RUNNING
        self._sessions: Dict[str, SessionHandle] = {}
        self._sessions_lock = threading.Lock()
        self._audit: list[HaltRecord] = []
        self._audit_lock = threading.Lock()
        self._last_heartbeat: float = time.time()
        self._heartbeat_lock = threading.Lock()
        self._deadmans_thread: Optional[threading.Thread] = None
        self._deadmans_active = threading.Event()
        self._current_halt_record: Optional[HaltRecord] = None
        self._start_deadmans_switch()

    # ------------------------------------------------------------------
    # Singleton
    # ------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "HaltController":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_for_testing(cls) -> None:
        """Tear down the singleton for isolated unit tests."""
        with cls._lock:
            if cls._instance is not None:
                cls._instance._deadmans_active.clear()
            cls._instance = None

    # ------------------------------------------------------------------
    # Session registry
    # ------------------------------------------------------------------

    def register_session(self, handle: SessionHandle) -> None:
        with self._sessions_lock:
            self._sessions[handle.session_id] = handle
        logger.debug("HaltController: registered session %s", handle.session_id)

    def unregister_session(self, session_id: str) -> None:
        with self._sessions_lock:
            self._sessions.pop(session_id, None)
        logger.debug("HaltController: unregistered session %s", session_id)

    def active_session_ids(self) -> Set[str]:
        with self._sessions_lock:
            return set(self._sessions.keys())

    # ------------------------------------------------------------------
    # Heartbeat (dead-man's switch)
    # ------------------------------------------------------------------

    def heartbeat(self, gaian_id: str = "unknown") -> None:
        """Gaian must call this periodically to prove liveness."""
        with self._heartbeat_lock:
            self._last_heartbeat = time.time()
        logger.debug("HaltController: heartbeat from %s", gaian_id)

    def _start_deadmans_switch(self) -> None:
        self._deadmans_active.set()

        def _watch() -> None:
            while self._deadmans_active.is_set():
                time.sleep(5)  # Poll every 5 seconds
                if self._status == HaltStatus.STOPPED:
                    break
                with self._heartbeat_lock:
                    elapsed = time.time() - self._last_heartbeat
                if elapsed > self.DEFAULT_HEARTBEAT_INTERVAL:
                    logger.warning(
                        "HaltController: dead-man's switch triggered "
                        "(no heartbeat for %.0fs)",
                        elapsed,
                    )
                    self.halt(HaltMode.HARD_STOP, triggered_by="DEADMANS_SWITCH")
                    break

        self._deadmans_thread = threading.Thread(
            target=_watch, daemon=True, name="gaia-deadmans-switch"
        )
        self._deadmans_thread.start()

    # ------------------------------------------------------------------
    # Halt API
    # ------------------------------------------------------------------

    @property
    def status(self) -> HaltStatus:
        return self._status

    def pause(self, triggered_by: str = "system") -> HaltRecord:
        """Suspend all sessions. Resumable via resume()."""
        logger.info("HaltController: PAUSE requested by %s", triggered_by)
        record = self._create_record(HaltMode.PAUSE, triggered_by)
        with self._sessions_lock:
            sessions = list(self._sessions.values())
        for handle in sessions:
            try:
                handle.pause_fn()
            except Exception as exc:
                logger.error("Error pausing session %s: %s", handle.session_id, exc)
        self._status = HaltStatus.PAUSED
        self._finalize_record(record)
        return record

    def resume(self, triggered_by: str = "system") -> None:
        """Resume all paused sessions."""
        if self._status != HaltStatus.PAUSED:
            raise RuntimeError(f"Cannot resume from status {self._status}")
        logger.info("HaltController: RESUME requested by %s", triggered_by)
        with self._sessions_lock:
            sessions = list(self._sessions.values())
        for handle in sessions:
            try:
                handle.resume_fn()
            except Exception as exc:
                logger.error("Error resuming session %s: %s", handle.session_id, exc)
        self._status = HaltStatus.RUNNING
        # Reset heartbeat so the dead-man's switch doesn't immediately fire
        self.heartbeat(triggered_by)

    def halt(
        self,
        mode: HaltMode = HaltMode.SOFT_STOP,
        triggered_by: str = "system",
    ) -> HaltRecord:
        """Halt all sessions according to *mode*.

        Args:
            mode: SOFT_STOP lets the current iteration finish; HARD_STOP
                  cancels immediately.
            triggered_by: Identifier of the entity triggering the halt.

        Returns:
            HaltRecord with SLA result attached.
        """
        logger.info("HaltController: %s requested by %s", mode, triggered_by)

        if mode == HaltMode.PAUSE:
            return self.pause(triggered_by)

        record = self._create_record(mode, triggered_by)

        with self._sessions_lock:
            sessions = list(self._sessions.values())

        if mode == HaltMode.HARD_STOP:
            self._status = HaltStatus.STOPPED
            for handle in sessions:
                try:
                    handle.cancel_fn()
                except Exception as exc:
                    logger.error(
                        "Error hard-stopping session %s: %s", handle.session_id, exc
                    )
        elif mode == HaltMode.SOFT_STOP:
            self._status = HaltStatus.SOFT_STOPPING
            for handle in sessions:
                try:
                    handle.cancel_fn()
                except Exception as exc:
                    logger.error(
                        "Error soft-stopping session %s: %s", handle.session_id, exc
                    )
            self._status = HaltStatus.STOPPED

        self._finalize_record(record)
        self._deadmans_active.clear()  # Stop the dead-man's watch thread
        return record

    # ------------------------------------------------------------------
    # Audit trail
    # ------------------------------------------------------------------

    def audit_trail(self) -> list[dict]:
        """Return all halt records as plain dicts (safe for JSON serialisation)."""
        with self._audit_lock:
            return [asdict(r) for r in self._audit]

    def _create_record(
        self, mode: HaltMode, triggered_by: str
    ) -> HaltRecord:
        now = time.time()
        with self._sessions_lock:
            affected = list(self._sessions.keys())
        record = HaltRecord(
            event_id=str(uuid.uuid4()),
            timestamp=now,
            mode=mode.value,
            triggered_by=triggered_by,
            sessions_affected=affected,
            sla_deadline=now + self.DEFAULT_SLA_SECONDS,
            sla_met=None,
            completion_time=None,
        )
        record.sign(self._HMAC_SECRET)
        self._current_halt_record = record
        return record

    def _finalize_record(self, record: HaltRecord) -> None:
        now = time.time()
        record.completion_time = now
        record.sla_met = now <= record.sla_deadline
        if not record.sla_met:
            logger.warning(
                "HaltController: SLA BREACH for event %s — took %.2fs (limit %.2fs)",
                record.event_id,
                now - record.timestamp,
                self.DEFAULT_SLA_SECONDS,
            )
        with self._audit_lock:
            self._audit.append(record)
        self._persist_record(record)

    def _persist_record(self, record: HaltRecord) -> None:
        try:
            self.AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with self.AUDIT_FILE.open("a") as fh:
                fh.write(json.dumps(asdict(record)) + "\n")
        except OSError as exc:
            logger.error("HaltController: failed to persist audit record: %s", exc)
