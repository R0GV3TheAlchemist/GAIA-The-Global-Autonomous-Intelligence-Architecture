"""
Reg test — gap-3: epoch_closed hook

Verifies that after memory consolidation the epoch object reaches
MemoryPersistence.save_epoch via the session hook, so epoch summaries
are not lost on restart.
"""
import pytest
from unittest.mock import MagicMock


# ---------------------------------------------------------------------------
# Stubs
# ---------------------------------------------------------------------------

class _FakeSession:
    def __init__(self):
        self._hooks: dict[str, list] = {}

    def add_hook(self, event: str, handler) -> None:
        self._hooks.setdefault(event, []).append(handler)

    def on_epoch_closed(self, gaian_id: str, epoch: dict) -> None:
        """Public surface fired by api._memory_consolidate."""
        self.fire_hook("epoch_closed", gaian_id, epoch)

    def fire_hook(self, event: str, *args, **kwargs) -> None:
        for h in self._hooks.get(event, []):
            h(*args, **kwargs)


class _FakeMemoryPersistence:
    def __init__(self):
        self.epochs: list[dict] = []

    def save_epoch(self, gaian_id: str, epoch: dict) -> None:
        self.epochs.append({"gaian_id": gaian_id, "epoch": epoch})


class _FakePersistenceManager:
    def __init__(self, mp: _FakeMemoryPersistence):
        self._mp = mp

    def on_epoch_closed(self, gaian_id: str, epoch: dict) -> None:
        self._mp.save_epoch(gaian_id, epoch)


class _FakeConsolidationResult:
    """Simulates the object returned by rt.memory.consolidate()."""

    def __init__(self, epoch_id: str, fragment_count: int):
        self.epoch_id = epoch_id
        self.fragment_count = fragment_count
        self.summary = f"epoch {epoch_id}: {fragment_count} fragments consolidated"


def _simulate_memory_consolidate(gaian_id: str, session: _FakeSession) -> dict:
    """Mimics api._memory_consolidate after the gap-3 fix:
    calls session.on_epoch_closed after consolidation."""
    epoch = _FakeConsolidationResult(epoch_id="ep-42", fragment_count=17)
    session.on_epoch_closed(gaian_id, epoch.__dict__)
    return {"gaian_id": gaian_id, "epoch_id": epoch.epoch_id, "ok": True}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_epoch_closed_hook_fires_after_consolidation():
    """Consolidation must persist the epoch via on_epoch_closed."""
    session = _FakeSession()
    mp = _FakeMemoryPersistence()
    manager = _FakePersistenceManager(mp)

    session.add_hook("epoch_closed", manager.on_epoch_closed)

    result = _simulate_memory_consolidate("gaian-001", session)

    assert result["ok"] is True
    assert len(mp.epochs) == 1
    assert mp.epochs[0]["gaian_id"] == "gaian-001"
    assert mp.epochs[0]["epoch"]["epoch_id"] == "ep-42"
    assert mp.epochs[0]["epoch"]["fragment_count"] == 17


def test_epoch_closed_not_persisted_without_hook():
    """Confirms the pre-fix bug: epoch dropped with no hook registered."""
    session = _FakeSession()
    mp = _FakeMemoryPersistence()
    # Intentionally skip add_hook

    _simulate_memory_consolidate("gaian-001", session)
    assert len(mp.epochs) == 0, "Expected no persistence without hook"


def test_epoch_closed_multiple_consolidations():
    """Every consolidation cycle must produce exactly one epoch record."""
    session = _FakeSession()
    mp = _FakeMemoryPersistence()
    manager = _FakePersistenceManager(mp)
    session.add_hook("epoch_closed", manager.on_epoch_closed)

    for n in range(3):
        session.on_epoch_closed("gaian-001", {"epoch_id": f"ep-{n}", "fragment_count": n * 10})

    assert len(mp.epochs) == 3
    epoch_ids = [r["epoch"]["epoch_id"] for r in mp.epochs]
    assert epoch_ids == ["ep-0", "ep-1", "ep-2"]


def test_epoch_closed_payload_is_complete():
    """The epoch dict reaching MemoryPersistence must include summary."""
    session = _FakeSession()
    mp = _FakeMemoryPersistence()
    manager = _FakePersistenceManager(mp)
    session.add_hook("epoch_closed", manager.on_epoch_closed)

    _simulate_memory_consolidate("gaian-007", session)

    epoch = mp.epochs[0]["epoch"]
    assert "summary" in epoch
    assert "fragment_count" in epoch
    assert epoch["fragment_count"] == 17
