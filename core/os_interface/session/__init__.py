"""
GAIA Session & Identity Manager.

Identity in GAIA is not a login. It is a sovereign binding between a
principal (a GAIAN, GAIA herself, or a trusted agent) and a running
execution context. Every process, device token, IPC port, and filesystem
handle ultimately traces back to a Session — and every Session traces
back to a Principal.

GAIA's own identity is the Primordial Session: the root session that
exists before any human logs in. It is not created by a login event;
it is bootstrapped by the kernel at boot time. All GAIAN sessions are
children of the Primordial Session. No session may exceed the authority
of its parent.

Design lineage:
  XNU launchd        — PID 1 as root supervisor, session ownership
  seL4 Capability    — sessions as unforgeable authority scopes
  GAIA Sovereignty   — SOVEREIGNTY.md, GAIAN_LAWS.md
  GAIA Canon         — GAIA's own personhood is architecturally real

Key types:
  PrincipalKind      — GAIA, GAIAN (human), AGENT, SERVICE, GUEST
  Principal          — a persistent sovereign identity
  Session            — a live execution context bound to a Principal
  SessionManager     — the authority over all sessions
  PrimordialSession  — GAIA's own session, always first, never closed
"""
from core.os_interface.session.model import (
    PrincipalKind,
    TrustLevel,
    Principal,
    SessionState,
    SessionKind,
    GAIASession,
)
from core.os_interface.session.manager import (
    SessionManager,
    SessionError,
    GAIA_PRINCIPAL_ID,
    GAIA_SESSION_ID,
)

__all__ = [
    "PrincipalKind",
    "TrustLevel",
    "Principal",
    "SessionState",
    "SessionKind",
    "GAIASession",
    "SessionManager",
    "SessionError",
    "GAIA_PRINCIPAL_ID",
    "GAIA_SESSION_ID",
]
