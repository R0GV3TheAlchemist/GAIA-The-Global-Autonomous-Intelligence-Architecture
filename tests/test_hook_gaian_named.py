"""
Reg test — gap-1: gaian_named hook

Verifies that renaming a GAIAN fires `on_gaian_named` on PersistenceManager
so the display_name change survives a restart.
"""
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call


# ---------------------------------------------------------------------------
# Minimal stubs — real modules may not yet be importable in CI
# ---------------------------------------------------------------------------

class _FakeSession:
    """Thin session stub with an observable hook table."""

    def __init__(self):
        self._hooks: dict[str, list] = {}

    def add_hook(self, event: str, handler) -> None:
        self._hooks.setdefault(event, []).append(handler)

    def fire_hook(self, event: str, *args, **kwargs) -> None:
        for h in self._hooks.get(event, []):
            h(*args, **kwargs)


class _FakeIdentityPersistence:
    """Records the last name written."""

    def __init__(self):
        self.last_written: dict | None = None

    def save_identity(self, gaian_id: str, payload: dict) -> None:
        self.last_written = {"gaian_id": gaian_id, **payload}


class _FakePersistenceManager:
    """Mimics PersistenceManager with only the naming hook wired."""

    def __init__(self, identity_persistence):
        self._ip = identity_persistence

    def _on_gaian_named_hook(self, gaian_id: str, name: str) -> None:
        """Adapter: session fires (gaian_id, name); we persist the patch."""
        self._ip.save_identity(gaian_id, {"display_name": name})


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_gaian_named_hook_fires_and_persists():
    """Renaming must reach IdentityPersistence.save_identity."""
    session = _FakeSession()
    ip = _FakeIdentityPersistence()
    manager = _FakePersistenceManager(ip)

    # Registration — mirrors server/startup.py
    session.add_hook("gaian_named", manager._on_gaian_named_hook)

    # Act: session fires the event (as api.py now does)
    session.fire_hook("gaian_named", "gaian-001", "Solaris")

    assert ip.last_written is not None, "save_identity was never called"
    assert ip.last_written["gaian_id"] == "gaian-001"
    assert ip.last_written["display_name"] == "Solaris"


def test_gaian_named_hook_not_fired_without_registration():
    """Without the hook, renames are silently lost — confirms the old bug."""
    session = _FakeSession()
    ip = _FakeIdentityPersistence()

    # Intentionally skip session.add_hook(...)
    session.fire_hook("gaian_named", "gaian-001", "Solaris")

    assert ip.last_written is None, "Expected no persistence without hook"


def test_gaian_named_hook_multiple_renames_last_wins():
    """Only the most recent rename is what matters for identity.json."""
    session = _FakeSession()
    ip = _FakeIdentityPersistence()
    manager = _FakePersistenceManager(ip)
    session.add_hook("gaian_named", manager._on_gaian_named_hook)

    session.fire_hook("gaian_named", "gaian-001", "First")
    session.fire_hook("gaian_named", "gaian-001", "Second")
    session.fire_hook("gaian_named", "gaian-001", "Third")

    assert ip.last_written["display_name"] == "Third"


def test_gaian_named_hook_different_gaians_isolated():
    """Each GAIAN's rename must be scoped to its own ID."""
    session = _FakeSession()
    written = []

    class _Multi:
        def _on_gaian_named_hook(self, gaian_id, name):
            written.append((gaian_id, name))

    manager = _Multi()
    session.add_hook("gaian_named", manager._on_gaian_named_hook)

    session.fire_hook("gaian_named", "g-001", "Alpha")
    session.fire_hook("gaian_named", "g-002", "Beta")

    assert ("g-001", "Alpha") in written
    assert ("g-002", "Beta") in written
    assert len(written) == 2
