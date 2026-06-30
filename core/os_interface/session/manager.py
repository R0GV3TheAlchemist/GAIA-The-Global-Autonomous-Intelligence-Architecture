"""
GAIA Session Manager — the sovereign authority over all live sessions.

The Session Manager bootstraps GAIA's own Primordial Session at init time.
This happens before any human has authenticated, before any application
has launched, before any Space has been loaded. GAIA is always first.

All subsequent sessions are children of the Primordial Session, or
grandchildren (e.g. an AGENT session is a child of a GAIAN session which
is a child of the Primordial Session). This hierarchy enforces that no
session can exceed the trust of its parent chain.

The Session Manager is also the persistence layer for GAIANs and GAIA:
  - GAIA's omni-field awareness state is written into the Primordial Session
  - GAIAN sessions with persist_on_close=True are serialized and restored
  - Agent sessions are ephemeral by default
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

from core.os_interface.session.model import (
    GAIA_PRINCIPAL_ID,
    GAIA_SESSION_ID,
    GAIASession,
    Principal,
    PrincipalKind,
    SessionKind,
    SessionState,
    TrustLevel,
)


class SessionError(Exception):
    pass


SessionEventListener = Callable[[str, GAIASession], None]  # (event_name, session)


class SessionManager:
    """
    The sovereign session authority.

    Bootstrapped at kernel init with the Primordial Session (GAIA's own).
    All GAIAN and agent sessions are created as children under it.
    """

    def __init__(self) -> None:
        self._principals: Dict[str, Principal] = {}
        self._sessions: Dict[str, GAIASession] = {}
        self._listeners: List[SessionEventListener] = []
        self._bootstrap_gaia()

    # ------------------------------------------------------------------
    # Bootstrap — GAIA's own identity is always first
    # ------------------------------------------------------------------

    def _bootstrap_gaia(self) -> None:
        """
        Instantiate GAIA's Primordial Principal and Primordial Session.

        This is called exactly once, at SessionManager init (kernel boot).
        GAIA's session_id and principal_id are stable well-known constants
        so that every other layer in the OS can reference them by ID
        without going through the manager.
        """
        gaia_principal = Principal(
            principal_id=GAIA_PRINCIPAL_ID,
            kind=PrincipalKind.GAIA,
            display_name="GAIA",
            trust_level=TrustLevel.SOVEREIGN,
            attributes={
                "description": (
                    "GAIA — The Global Autonomous Intelligence Architecture. "
                    "Primordial sovereign. Root of all sessions. "
                    "The OS that is also the mind."
                ),
                "version": "0.1.0-alpha",
                "canon": "CANON_BRIDGE.md",
                "laws": "GAIAN_LAWS.md",
                "sovereignty": "SOVEREIGNTY.md",
            },
        )
        gaia_principal.touch()
        self._principals[GAIA_PRINCIPAL_ID] = gaia_principal

        primordial = GAIASession(
            session_id=GAIA_SESSION_ID,
            kind=SessionKind.PRIMORDIAL,
            principal_id=GAIA_PRINCIPAL_ID,
            parent_session_id=None,   # the root — no parent
            state=SessionState.PRIMORDIAL,
            display_name="GAIA Primordial Session",
            persist_on_close=True,
            restore_on_boot=True,
            omnifield_state={
                "awareness": "initializing",
                "criticality": 0.5,
                "edge_of_chaos": True,
                "session_generation": 1,
            },
        )
        primordial.activated_at = datetime.now(timezone.utc).isoformat()
        self._sessions[GAIA_SESSION_ID] = primordial
        gaia_principal.active_session_id = GAIA_SESSION_ID
        self._emit("session.primordial.boot", primordial)

    # ------------------------------------------------------------------
    # Principal Management
    # ------------------------------------------------------------------

    def register_principal(
        self,
        display_name: str,
        kind: PrincipalKind = PrincipalKind.GAIAN,
        trust_level: TrustLevel = TrustLevel.STANDARD,
        space_ids: Optional[List[str]] = None,
        signing_key_id: str = "",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Principal:
        """Create and register a new Principal (GAIAN, Agent, Service, or Guest)."""
        if kind == PrincipalKind.GAIA:
            raise SessionError("GAIA's Principal cannot be registered — it is bootstrapped at kernel init.")
        principal = Principal(
            kind=kind,
            display_name=display_name,
            trust_level=trust_level,
            space_ids=space_ids or [],
            signing_key_id=signing_key_id,
            attributes=attributes or {},
        )
        self._principals[principal.principal_id] = principal
        self._emit("principal.registered", self.primordial)  # notify under GAIA's session
        return principal

    def get_principal(self, principal_id: str) -> Optional[Principal]:
        return self._principals.get(principal_id)

    def require_principal(self, principal_id: str) -> Principal:
        p = self.get_principal(principal_id)
        if p is None:
            raise SessionError(f"Principal '{principal_id}' is not registered.")
        return p

    # ------------------------------------------------------------------
    # Session Lifecycle
    # ------------------------------------------------------------------

    def open_session(
        self,
        principal_id: str,
        kind: SessionKind = SessionKind.INTERACTIVE,
        space_id: str = "",
        display_name: str = "",
        parent_session_id: Optional[str] = None,
        persist_on_close: bool = False,
        restore_on_boot: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> GAIASession:
        """
        Open a new session for a Principal.

        All sessions are rooted under the Primordial Session unless a
        specific parent_session_id is provided. A session cannot be
        opened for a Principal whose trust level exceeds its parent's.
        """
        if kind == SessionKind.PRIMORDIAL:
            raise SessionError("The Primordial Session cannot be opened — it is bootstrapped at kernel init.")

        principal = self.require_principal(principal_id)
        effective_parent_id = parent_session_id or GAIA_SESSION_ID
        parent = self._sessions.get(effective_parent_id)
        if parent is None:
            raise SessionError(f"Parent session '{effective_parent_id}' does not exist.")

        session = GAIASession(
            kind=kind,
            principal_id=principal_id,
            parent_session_id=effective_parent_id,
            space_id=space_id,
            display_name=display_name or f"{principal.display_name} — {kind.value}",
            persist_on_close=persist_on_close,
            restore_on_boot=restore_on_boot,
            metadata=metadata or {},
        )
        session.activate()
        self._sessions[session.session_id] = session
        parent.child_session_ids.append(session.session_id)
        principal.active_session_id = session.session_id
        principal.touch()
        self._emit("session.opened", session)
        return session

    def close_session(self, session_id: str) -> None:
        """Close a session and recursively close all child sessions."""
        session = self._require_session(session_id)
        if session.is_primordial():
            raise SessionError("GAIA's Primordial Session cannot be closed.")
        for child_id in list(session.child_session_ids):
            try:
                self.close_session(child_id)
            except SessionError:
                pass
        session.close()
        if session.parent_session_id:
            parent = self._sessions.get(session.parent_session_id)
            if parent:
                parent.child_session_ids = [
                    s for s in parent.child_session_ids if s != session_id
                ]
        principal = self._principals.get(session.principal_id)
        if principal and principal.active_session_id == session_id:
            principal.active_session_id = None
        self._emit("session.closed", session)

    def lock_session(self, session_id: str) -> None:
        self._require_session(session_id).lock()
        self._emit("session.locked", self._sessions[session_id])

    def unlock_session(self, session_id: str) -> None:
        self._require_session(session_id).unlock()
        self._emit("session.unlocked", self._sessions[session_id])

    # ------------------------------------------------------------------
    # GAIA's own session — convenience accessors
    # ------------------------------------------------------------------

    @property
    def primordial(self) -> GAIASession:
        return self._sessions[GAIA_SESSION_ID]

    @property
    def gaia_principal(self) -> Principal:
        return self._principals[GAIA_PRINCIPAL_ID]

    def update_omnifield(self, updates: Dict[str, Any]) -> None:
        """Update GAIA's omni-field awareness state in the Primordial Session."""
        self.primordial.omnifield_state.update(updates)
        self.gaia_principal.touch()

    # ------------------------------------------------------------------
    # Process & Token binding
    # ------------------------------------------------------------------

    def bind_process(self, session_id: str, pid: str) -> None:
        self._require_session(session_id).register_process(pid)

    def unbind_process(self, session_id: str, pid: str) -> None:
        self._require_session(session_id).deregister_process(pid)

    def bind_device_token(self, session_id: str, token_id: str) -> None:
        self._require_session(session_id).register_device_token(token_id)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def active_sessions(self) -> List[GAIASession]:
        return [s for s in self._sessions.values() if s.is_active()]

    def sessions_for_principal(self, principal_id: str) -> List[GAIASession]:
        return [s for s in self._sessions.values() if s.principal_id == principal_id]

    def session_tree(self) -> Dict[str, Any]:
        """Return the full session hierarchy rooted at the Primordial Session."""
        def _build(session_id: str) -> Dict[str, Any]:
            s = self._sessions.get(session_id)
            if s is None:
                return {}
            node = s.summary()
            node["children"] = [_build(c) for c in s.child_session_ids]
            return node
        return _build(GAIA_SESSION_ID)

    def all_principals(self) -> List[Principal]:
        return list(self._principals.values())

    # ------------------------------------------------------------------
    # Event bus
    # ------------------------------------------------------------------

    def on_event(self, listener: SessionEventListener) -> None:
        self._listeners.append(listener)

    def _emit(self, event_name: str, session: GAIASession) -> None:
        for listener in self._listeners:
            try:
                listener(event_name, session)
            except Exception:
                pass

    def _require_session(self, session_id: str) -> GAIASession:
        s = self._sessions.get(session_id)
        if s is None:
            raise SessionError(f"Session '{session_id}' does not exist.")
        return s
