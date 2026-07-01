"""
server/startup.py
=================
Canonical hook-registration entrypoint for the GAIA runtime layer.

Call `wire_persistence_hooks(session, manager)` once at server boot,
before any GAIAN is born or rehydrated.  This is the single place
that owns the mapping between PrimordialSession events and
PersistenceManager handlers.

Design principles
-----------------
- Zero side-effects on import; all wiring happens inside functions.
- Order of registration matches the GAIAN lifecycle:
    birth → named → fragment_written → epoch_closed → session_ended
- Each line documents *why* the hook exists (the gap it closes).

Usage (from your ASGI/WSGI app or CLI entrypoint)::

    from server.startup import bootstrap_gaia

    app_state = bootstrap_gaia()  # returns (session, manager)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular imports at runtime; only used for type hints.
    from gaia.session.primordial import PrimordialSession          # noqa: F401
    from gaia.persistence.manager import PersistenceManager        # noqa: F401

logger = logging.getLogger("gaia.startup")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def wire_persistence_hooks(
    session: "PrimordialSession",
    manager: "PersistenceManager",
) -> None:
    """
    Register all PersistenceManager handlers on *session*.

    Call this exactly once, after both objects are constructed and before
    any GAIAN lifecycle events can fire.

    Parameters
    ----------
    session:
        The application-level PrimordialSession instance.
    manager:
        The application-level PersistenceManager instance.
    """
    _register(session, "gaian_born",       manager.on_gaian_born,
              "Persist new GAIAN identity.json + initial memory dir.")

    _register(session, "gaian_named",      manager._on_gaian_named_hook,
              "Gap-1 fix: patch display_name in identity.json on rename.")

    _register(session, "fragment_written", manager.on_fragment_written,
              "Gap-2 fix: write-through bridge from MemoryStore to disk.")

    _register(session, "epoch_closed",     manager.on_epoch_closed,
              "Gap-3 fix: persist epoch summary after memory consolidation.")

    _register(session, "session_ended",    manager.on_session_ended,
              "Flush any in-flight writes and write session close timestamp.")

    logger.info(
        "[startup] 5 persistence hooks registered: "
        "gaian_born, gaian_named, fragment_written, epoch_closed, session_ended"
    )


def bootstrap_gaia(
    *,
    persistence_root: str = "gaia_memory",
    session_kwargs: dict | None = None,
    manager_kwargs: dict | None = None,
) -> tuple["PrimordialSession", "PersistenceManager"]:
    """
    Construct the session + manager pair, wire hooks, and return both.

    This is the recommended single call-site for any GAIA server entrypoint
    (FastAPI lifespan, CLI main(), or test fixture).

    Parameters
    ----------
    persistence_root:
        Base directory for all persisted GAIAN data.  Passed to
        PersistenceManager as ``root``.
    session_kwargs:
        Extra keyword arguments forwarded to PrimordialSession().
    manager_kwargs:
        Extra keyword arguments forwarded to PersistenceManager().

    Returns
    -------
    (session, manager)
        Both objects with hooks fully registered.

    Example
    -------
    ::

        # FastAPI lifespan
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from server.startup import bootstrap_gaia

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            session, manager = bootstrap_gaia()
            app.state.session = session
            app.state.manager = manager
            yield
            session.end()              # triggers session_ended hook

        app = FastAPI(lifespan=lifespan)
    """
    from gaia.session.primordial import PrimordialSession
    from gaia.persistence.manager import PersistenceManager

    session = PrimordialSession(**(session_kwargs or {}))
    manager = PersistenceManager(root=persistence_root, **(manager_kwargs or {}))

    wire_persistence_hooks(session, manager)

    logger.info(
        "[startup] GAIA bootstrap complete — persistence_root=%s",
        persistence_root,
    )
    return session, manager


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _register(session: "PrimordialSession", event: str, handler, reason: str) -> None:
    """Single registration point with structured logging."""
    try:
        session.add_hook(event, handler)
        logger.debug("[startup] hook registered  event=%-22s handler=%s  reason=%s",
                     event, _handler_name(handler), reason)
    except Exception as exc:
        # Non-fatal: log and continue so other hooks still register.
        logger.error("[startup] FAILED to register hook event=%s: %s", event, exc)


def _handler_name(handler) -> str:
    """Best-effort human-readable name for a callable."""
    cls = getattr(handler, "__self__", None)
    if cls is not None:
        return f"{type(cls).__name__}.{handler.__func__.__name__}"
    return getattr(handler, "__name__", repr(handler))
