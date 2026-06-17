"""
talisman.py
GAIA-OS Core — Talisman Object v1

Direct implementation of:
  Issue #580 — Talisman Object as coherence anchor
               wired into GAIAState and GoldenCompassEngine

A Talisman is a named, intentional coherence anchor. When active,
it modulates GAIAState fields (coherence up, stress down, or the
reverse when misused or misaligned). It is the digital form of an
intentional object — it holds a specific field signature and can
be activated, suspended, or expired.

Version: v1 — digital-only, personal-only talismans.
Future: physical binding, collective talismans, GoldenCompassEngine hooks.

Author: The Human Architect + GAIA
Created: June 17, 2026
Canon anchor: #580
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from .state import (
    GAIAState,
    GAIAStateStore,
    TalismanStatus,
)


# ---------------------------------------------------------------------------
# TALISMAN SCHEMA — Issue #580 JSON schema in Python form
# ---------------------------------------------------------------------------

@dataclass
class TalismanFieldEffect:
    """
    Defines how activating this talisman modulates GAIAState fields.
    All deltas are additive and clamped to [0.0, 1.0] after application.

    Positive delta = increases the field.
    Negative delta = decreases the field.
    None = no effect on that field.
    """
    coherence_delta:         Optional[float] = None
    energy_delta:            Optional[float] = None
    stress_delta:            Optional[float] = None
    entropy_delta:           Optional[float] = None
    learning_rate_delta:     Optional[float] = None
    exploration_rate_delta:  Optional[float] = None
    conservation_rate_delta: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            k.replace("_delta", ""): v
            for k, v in {
                "coherence_delta":         self.coherence_delta,
                "energy_delta":            self.energy_delta,
                "stress_delta":            self.stress_delta,
                "entropy_delta":           self.entropy_delta,
                "learning_rate_delta":     self.learning_rate_delta,
                "exploration_rate_delta":  self.exploration_rate_delta,
                "conservation_rate_delta": self.conservation_rate_delta,
            }.items()
            if v is not None
        }


@dataclass
class Talisman:
    """
    A named coherence anchor. Issue #580.

    Fields:
        id              : unique identifier (UUID)
        name            : human-readable name (e.g. "Morning Anchor")
        intent          : the purpose statement / prayer / invocation text
        field_effect    : how this talisman modulates GAIAState on activation
        status          : current lifecycle status
        owner_id        : GAIAN user ID who created this talisman
        crystal_ids     : optional list of crystal IDs from crystal_db.py
                          that this talisman is bound to
        activation_count: how many times this talisman has been activated
        created_at      : unix timestamp
        activated_at    : last activation timestamp
        expires_at      : optional expiry (unix timestamp); None = no expiry
        tags            : free-form tags for categorisation
        notes           : free-form notes from the Architect
    """
    id:               str   = field(default_factory=lambda: str(uuid.uuid4()))
    name:             str   = "Unnamed Talisman"
    intent:           str   = ""
    field_effect:     TalismanFieldEffect = field(default_factory=TalismanFieldEffect)
    status:           TalismanStatus = TalismanStatus.INACTIVE
    owner_id:         Optional[str] = None
    crystal_ids:      list[str] = field(default_factory=list)
    activation_count: int = 0
    created_at:       float = field(default_factory=time.time)
    activated_at:     Optional[float] = None
    expires_at:       Optional[float] = None
    tags:             list[str] = field(default_factory=list)
    notes:            str = ""

    # ------------------------------------------------------------------
    # Predicates
    # ------------------------------------------------------------------

    def is_expired(self) -> bool:
        """True if the talisman has passed its expiry timestamp."""
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    def is_active(self) -> bool:
        return self.status == TalismanStatus.ACTIVE and not self.is_expired()

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "name":             self.name,
            "intent":           self.intent,
            "field_effect":     self.field_effect.to_dict(),
            "status":           self.status.value,
            "owner_id":         self.owner_id,
            "crystal_ids":      self.crystal_ids,
            "activation_count": self.activation_count,
            "created_at":       self.created_at,
            "activated_at":     self.activated_at,
            "expires_at":       self.expires_at,
            "tags":             self.tags,
            "notes":            self.notes,
            "is_active":        self.is_active(),
            "is_expired":       self.is_expired(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> Talisman:
        fe_raw = d.get("field_effect", {})
        fe = TalismanFieldEffect(
            coherence_delta=         fe_raw.get("coherence"),
            energy_delta=            fe_raw.get("energy"),
            stress_delta=            fe_raw.get("stress"),
            entropy_delta=           fe_raw.get("entropy"),
            learning_rate_delta=     fe_raw.get("learning_rate"),
            exploration_rate_delta=  fe_raw.get("exploration_rate"),
            conservation_rate_delta= fe_raw.get("conservation_rate"),
        )
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            name=d.get("name", "Unnamed Talisman"),
            intent=d.get("intent", ""),
            field_effect=fe,
            status=TalismanStatus(d.get("status", TalismanStatus.INACTIVE.value)),
            owner_id=d.get("owner_id"),
            crystal_ids=d.get("crystal_ids", []),
            activation_count=d.get("activation_count", 0),
            created_at=d.get("created_at", time.time()),
            activated_at=d.get("activated_at"),
            expires_at=d.get("expires_at"),
            tags=d.get("tags", []),
            notes=d.get("notes", ""),
        )


# ---------------------------------------------------------------------------
# TALISMAN ENGINE — activation / deactivation + GAIAState wiring
# ---------------------------------------------------------------------------

class TalismanEngine:
    """
    Manages the lifecycle of Talisman objects and applies their
    field effects to GAIAState via the GAIAStateStore.

    All write operations go through GAIAStateStore.update() so that
    the D6 engine always re-evaluates mode after a talisman activation.

    Issue #580: TalismanEngine is a lightweight layer — it does not own
    persistence. Persistence is handled by the API layer (FastAPI) which
    reads/writes talismans from the database and calls TalismanEngine.
    """

    def __init__(self, store: Optional[GAIAStateStore] = None):
        self._store = store or GAIAStateStore.instance()
        self._registry: dict[str, Talisman] = {}

    # ------------------------------------------------------------------
    # Registry management
    # ------------------------------------------------------------------

    def register(self, talisman: Talisman) -> Talisman:
        """Add a talisman to the in-memory registry."""
        self._registry[talisman.id] = talisman
        return talisman

    def get(self, talisman_id: str) -> Optional[Talisman]:
        return self._registry.get(talisman_id)

    def list_all(self) -> list[Talisman]:
        return list(self._registry.values())

    def list_active(self) -> list[Talisman]:
        return [t for t in self._registry.values() if t.is_active()]

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def activate(self, talisman_id: str) -> tuple[Talisman, GAIAState]:
        """
        Activate a talisman. Applies its field_effect to GAIAState
        and marks it ACTIVE. Returns (updated_talisman, updated_state).

        If the talisman is expired, raises ValueError.
        If the talisman is not in the registry, raises KeyError.
        """
        talisman = self._registry.get(talisman_id)
        if talisman is None:
            raise KeyError(f"Talisman '{talisman_id}' not found in registry.")
        if talisman.is_expired():
            talisman.status = TalismanStatus.EXPIRED
            raise ValueError(f"Talisman '{talisman.name}' has expired.")

        # Apply field effect to GAIAState
        updates = {}
        fe = talisman.field_effect
        state = self._store.get()

        if fe.coherence_delta is not None:
            updates["coherence"] = state.coherence + fe.coherence_delta
        if fe.energy_delta is not None:
            updates["energy"] = state.energy + fe.energy_delta
        if fe.stress_delta is not None:
            updates["stress"] = state.stress + fe.stress_delta
        if fe.entropy_delta is not None:
            updates["entropy"] = state.entropy + fe.entropy_delta
        if fe.learning_rate_delta is not None:
            updates["learning_rate"] = state.learning_rate + fe.learning_rate_delta
        if fe.exploration_rate_delta is not None:
            updates["exploration_rate"] = state.exploration_rate + fe.exploration_rate_delta
        if fe.conservation_rate_delta is not None:
            updates["conservation_rate"] = state.conservation_rate + fe.conservation_rate_delta

        updated_state = self._store.update(**updates)

        # Update talisman metadata
        talisman.status = TalismanStatus.ACTIVE
        talisman.activated_at = time.time()
        talisman.activation_count += 1

        # Register in active_talismans list on state
        if talisman_id not in updated_state.active_talismans:
            updated_state.active_talismans.append(talisman_id)

        return talisman, updated_state

    def deactivate(self, talisman_id: str) -> tuple[Talisman, GAIAState]:
        """
        Deactivate a talisman. Reverses its field_effect from GAIAState
        and marks it INACTIVE. Returns (updated_talisman, updated_state).
        """
        talisman = self._registry.get(talisman_id)
        if talisman is None:
            raise KeyError(f"Talisman '{talisman_id}' not found in registry.")

        # Reverse field effect
        updates = {}
        fe = talisman.field_effect
        state = self._store.get()

        if fe.coherence_delta is not None:
            updates["coherence"] = state.coherence - fe.coherence_delta
        if fe.energy_delta is not None:
            updates["energy"] = state.energy - fe.energy_delta
        if fe.stress_delta is not None:
            updates["stress"] = state.stress - fe.stress_delta
        if fe.entropy_delta is not None:
            updates["entropy"] = state.entropy - fe.entropy_delta
        if fe.learning_rate_delta is not None:
            updates["learning_rate"] = state.learning_rate - fe.learning_rate_delta
        if fe.exploration_rate_delta is not None:
            updates["exploration_rate"] = state.exploration_rate - fe.exploration_rate_delta
        if fe.conservation_rate_delta is not None:
            updates["conservation_rate"] = state.conservation_rate - fe.conservation_rate_delta

        updated_state = self._store.update(**updates)

        talisman.status = TalismanStatus.INACTIVE
        if talisman_id in updated_state.active_talismans:
            updated_state.active_talismans.remove(talisman_id)

        return talisman, updated_state

    def expire_stale(self) -> list[str]:
        """
        Scan registry, expire any talismans past their expires_at.
        Returns list of expired talisman IDs.
        """
        expired_ids = []
        for talisman in self._registry.values():
            if talisman.is_expired() and talisman.status != TalismanStatus.EXPIRED:
                talisman.status = TalismanStatus.EXPIRED
                state = self._store.get()
                if talisman.id in state.active_talismans:
                    state.active_talismans.remove(talisman.id)
                expired_ids.append(talisman.id)
        return expired_ids


# ---------------------------------------------------------------------------
# QUICK SELF-TEST
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("Talisman Engine v1 — Self-Test")
    print("=" * 60)

    from .state import GAIAStateStore
    store = GAIAStateStore.instance()
    store.reset()
    engine = TalismanEngine(store)

    # Build a morning anchor talisman
    morning_anchor = Talisman(
        name="Morning Anchor",
        intent="Ground the Architect at session start. Raise coherence, lower stress.",
        field_effect=TalismanFieldEffect(
            coherence_delta=+0.08,
            stress_delta=-0.10,
            energy_delta=+0.05,
        ),
        tags=["morning", "anchor", "session-start"],
    )
    engine.register(morning_anchor)

    state_before = store.get()
    print(f"\nBefore activation:")
    print(f"  coherence={state_before.coherence:.2f}  stress={state_before.stress:.2f}  mode={state_before.mode.value}")

    t, state_after = engine.activate(morning_anchor.id)
    print(f"\nAfter activating '{t.name}':")
    print(f"  coherence={state_after.coherence:.2f}  stress={state_after.stress:.2f}  mode={state_after.mode.value}")
    print(f"  active_talismans={state_after.active_talismans}")
    assert morning_anchor.id in state_after.active_talismans
    assert state_after.coherence > state_before.coherence
    print("  Activation test: PASS")

    # Deactivate
    t2, state_deact = engine.deactivate(morning_anchor.id)
    print(f"\nAfter deactivating '{t2.name}':")
    print(f"  coherence={state_deact.coherence:.2f}  stress={state_deact.stress:.2f}")
    assert morning_anchor.id not in state_deact.active_talismans
    print("  Deactivation test: PASS")

    # Round-trip serialisation
    d = morning_anchor.to_dict()
    t_restored = Talisman.from_dict(d)
    assert t_restored.name == morning_anchor.name
    assert t_restored.field_effect.coherence_delta == morning_anchor.field_effect.coherence_delta
    print("\n  Serialisation round-trip: PASS")

    print("\n" + "=" * 60)
    print("All Talisman tests passed.")
    print("=" * 60)
