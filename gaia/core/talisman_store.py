"""
gaia/core/talisman_store.py

In-memory Talisman store for Queue 4.

v1 scope:
  - CRUD-lite (create/list/get)
  - activate/deactivate
  - activation feeds GAIAState through run_d6_cycle()

Future:
  - persist to DB
  - link to GoldenCompassEngine
  - per-user ownership / auth
"""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from gaia.core.state_store import run_d6_cycle
from gaia.core.talisman import Talisman, TalismanEffect, TalismanStatus

_lock = Lock()
_talismans: dict[str, Talisman] = {}


def list_talismans() -> list[Talisman]:
    with _lock:
        return list(_talismans.values())


def get_talisman(talisman_id: str) -> Talisman | None:
    with _lock:
        return _talismans.get(talisman_id)


def create_talisman(
    *,
    name: str,
    purpose: str,
    created_by: str = "Kyle Steen",
    coherence_delta: float = 0.05,
    energy_delta: float = 0.02,
    stress_delta: float = -0.05,
    entropy_delta: float = -0.02,
    notes: str = "",
) -> Talisman:
    talisman = Talisman(
        name=name,
        purpose=purpose,
        created_by=created_by,
        effect=TalismanEffect(
            coherence_delta=coherence_delta,
            energy_delta=energy_delta,
            stress_delta=stress_delta,
            entropy_delta=entropy_delta,
        ),
        notes=notes,
    )
    with _lock:
        _talismans[talisman.id] = talisman
    return talisman


def activate_talisman(talisman_id: str):
    with _lock:
        talisman = _talismans[talisman_id]
        talisman.status = TalismanStatus.ACTIVE
        talisman.last_activated_at = datetime.now(timezone.utc)

    decision = run_d6_cycle(
        coherence=max(0.0, talisman.effect.coherence_delta),
        energy=max(0.0, talisman.effect.energy_delta),
        stress=0.0 if talisman.effect.stress_delta < 0 else talisman.effect.stress_delta,
        entropy=0.0 if talisman.effect.entropy_delta < 0 else talisman.effect.entropy_delta,
    )
    return talisman, decision


def deactivate_talisman(talisman_id: str) -> Talisman:
    with _lock:
        talisman = _talismans[talisman_id]
        talisman.status = TalismanStatus.DORMANT
        return talisman


def seed_default_talismans() -> None:
    with _lock:
        if _talismans:
            return
    create_talisman(
        name="Builder's Flame",
        purpose="Support focused implementation when coherence is stable.",
        coherence_delta=0.08,
        energy_delta=0.05,
        stress_delta=-0.03,
        entropy_delta=-0.01,
        notes="Queue 4 seed talisman.",
    )
    create_talisman(
        name="Mirror of Return",
        purpose="Encourage reflection and stress release before burnout.",
        coherence_delta=0.04,
        energy_delta=0.01,
        stress_delta=-0.08,
        entropy_delta=-0.03,
        notes="Recovery-biased coherence anchor.",
    )
