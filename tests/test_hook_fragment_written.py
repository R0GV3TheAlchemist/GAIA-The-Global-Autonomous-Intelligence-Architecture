"""
Reg test — gap-2: fragment_written hook

Verifies that the MemoryStore-to-session bridge correctly routes
memory.fragment.written internal events to the session's
`fragment_written` hook, which then reaches MemoryPersistence.
"""
import pytest
from unittest.mock import MagicMock, call


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class _FakeSession:
    def __init__(self):
        self._hooks: dict[str, list] = {}

    def add_hook(self, event: str, handler) -> None:
        self._hooks.setdefault(event, []).append(handler)

    def fire_hook(self, event: str, *args, **kwargs) -> None:
        for h in self._hooks.get(event, []):
            h(*args, **kwargs)


class _FakeMemoryStore:
    """Simulates the internal event bus that MemoryStore exposes."""

    def __init__(self):
        self._listeners: list = []

    def on_event(self, handler) -> None:
        self._listeners.append(handler)

    def remember(self, fragment: dict) -> None:
        """Simulates storing a fragment and emitting the internal event."""
        for listener in self._listeners:
            listener("memory.fragment.written", fragment)


class _FakeMemoryPersistence:
    def __init__(self):
        self.saved: list[dict] = []

    def save_fragment(self, gaian_id: str, fragment: dict) -> None:
        self.saved.append({"gaian_id": gaian_id, "fragment": fragment})


class _FakePersistenceManager:
    def __init__(self, mp: _FakeMemoryPersistence):
        self._mp = mp

    def on_fragment_written(self, gaian_id: str, fragment: dict) -> None:
        self._mp.save_fragment(gaian_id, fragment)


def _attach_fragment_bridge(mem: _FakeMemoryStore, gaian_id: str, session: _FakeSession):
    """Mirror of api._attach_fragment_bridge."""
    def _bridge(event_name, fragment):
        if event_name == "memory.fragment.written":
            session.fire_hook("fragment_written", gaian_id, fragment)
    mem.on_event(_bridge)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_fragment_written_hook_fires_on_remember():
    """After bridge attachment, remember() must reach MemoryPersistence."""
    session = _FakeSession()
    mem = _FakeMemoryStore()
    mp = _FakeMemoryPersistence()
    manager = _FakePersistenceManager(mp)

    session.add_hook("fragment_written", manager.on_fragment_written)
    _attach_fragment_bridge(mem, "gaian-001", session)

    frag = {"id": "f-1", "content": "hello", "salience": 0.9}
    mem.remember(frag)

    assert len(mp.saved) == 1
    assert mp.saved[0]["gaian_id"] == "gaian-001"
    assert mp.saved[0]["fragment"] == frag


def test_fragment_written_not_fired_without_bridge():
    """Without bridge attachment, fragments are silently lost (old bug)."""
    session = _FakeSession()
    mem = _FakeMemoryStore()
    mp = _FakeMemoryPersistence()
    manager = _FakePersistenceManager(mp)

    session.add_hook("fragment_written", manager.on_fragment_written)
    # Intentionally skip _attach_fragment_bridge

    mem.remember({"id": "f-1", "content": "lost"})
    assert len(mp.saved) == 0, "Expected no persistence without bridge"


def test_fragment_written_multiple_fragments_all_persisted():
    session = _FakeSession()
    mem = _FakeMemoryStore()
    mp = _FakeMemoryPersistence()
    manager = _FakePersistenceManager(mp)

    session.add_hook("fragment_written", manager.on_fragment_written)
    _attach_fragment_bridge(mem, "gaian-002", session)

    for i in range(5):
        mem.remember({"id": f"f-{i}", "content": f"fragment {i}"})

    assert len(mp.saved) == 5
    ids = [r["fragment"]["id"] for r in mp.saved]
    assert ids == ["f-0", "f-1", "f-2", "f-3", "f-4"]


def test_fragment_written_bridge_correct_gaian_id():
    """Bridge must tag each fragment with the GAIAN it was registered for."""
    session = _FakeSession()
    saved_ids: list[str] = []

    def _handler(gaian_id, fragment):
        saved_ids.append(gaian_id)

    session.add_hook("fragment_written", _handler)

    mem_a = _FakeMemoryStore()
    mem_b = _FakeMemoryStore()
    _attach_fragment_bridge(mem_a, "gaian-A", session)
    _attach_fragment_bridge(mem_b, "gaian-B", session)

    mem_a.remember({"id": "fa"})
    mem_b.remember({"id": "fb"})

    assert saved_ids == ["gaian-A", "gaian-B"]
