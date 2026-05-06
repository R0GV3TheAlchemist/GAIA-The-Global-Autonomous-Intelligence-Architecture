"""
core.runtime.session
====================
Lightweight per-user session tracker.

A SessionInfo records when a session started, the last active time,
and an exchange counter.  The SessionRegistry maps user_id → session_id
and keeps the most recent SessionInfo for each.

This is intentionally minimal — it is NOT a full auth/session system.
It provides the context needed for the orchestrator to:
  - Scope quantum kernels per session
  - Tag memory items with session_id
  - Filter audit events by session
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class SessionInfo:
    session_id:   str
    user_id:      str
    started_at:   float = field(default_factory=time.time)
    last_active:  float = field(default_factory=time.time)
    exchange_count: int = 0

    def touch(self) -> None:
        self.last_active = time.time()
        self.exchange_count += 1

    @property
    def duration_seconds(self) -> float:
        return time.time() - self.started_at

    def to_dict(self) -> dict:
        return {
            "session_id":     self.session_id,
            "user_id":        self.user_id,
            "started_at":     self.started_at,
            "last_active":    self.last_active,
            "exchange_count": self.exchange_count,
            "duration_s":     round(self.duration_seconds, 1),
        }


class SessionRegistry:
    """
    Maps user_id → current SessionInfo.

    When a user sends a message without an explicit session_id,
    get_or_create() either returns their existing active session or
    creates a new one.

    Sessions are stored in memory only; they do not survive a restart.
    Persisting session metadata is the responsibility of the caller
    (e.g. write to MemoryStore with kind=MemoryKind.REFLECTION).
    """

    # Idle cutoff: if last_active > SESSION_IDLE_SECS ago, start a new session.
    SESSION_IDLE_SECS: float = 3600.0  # 1 hour

    def __init__(self) -> None:
        self._sessions: Dict[str, SessionInfo] = {}  # user_id → SessionInfo

    def get_or_create(self, user_id: str, session_id: Optional[str] = None) -> SessionInfo:
        existing = self._sessions.get(user_id)
        if existing and (time.time() - existing.last_active) < self.SESSION_IDLE_SECS:
            existing.touch()
            return existing
        # New session
        sid = session_id or str(uuid.uuid4())
        info = SessionInfo(session_id=sid, user_id=user_id)
        self._sessions[user_id] = info
        return info

    def get(self, user_id: str) -> Optional[SessionInfo]:
        return self._sessions.get(user_id)

    def invalidate(self, user_id: str) -> bool:
        return self._sessions.pop(user_id, None) is not None

    def active_sessions(self) -> list:
        cutoff = time.time() - self.SESSION_IDLE_SECS
        return [s for s in self._sessions.values() if s.last_active >= cutoff]

    def __len__(self) -> int:
        return len(self._sessions)
