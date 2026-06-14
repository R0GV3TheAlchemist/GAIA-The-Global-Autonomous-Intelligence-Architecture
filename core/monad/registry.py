"""
core/monad/registry.py
MonadRegistry + MonadType — Pre-Established Harmony Loop

The MonadRegistry is the Pre-Established Harmony mechanism.
It holds all registered GaiaMonads and calls them in deterministic
phase order each turn, matching Leibniz's hierarchy from bare
perception to full apperception.

Phase order (lowest → highest):
  PERCEPTION → SOMATIC → COGNITIVE → SHADOW → QUANTUM →
  NOOSPHERIC → DREAM → PROCESS

See docs/canon/monad.md
Issue #398 — The Monad and the Variety of Monads
"""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("gaia.monad.registry")


# ── MonadType ──────────────────────────────────────────────────────────────────────────────

class MonadType(str, Enum):
    """
    The Variety of Monads in GAIA-OS.

    Ordered by phase (ascending) — lower number = runs earlier in the
    Pre-Established Harmony loop, matching Leibniz's hierarchy from
    bare perception up to full apperception / process.
    """
    PERCEPTION  = "perception"   # phase 1 — bare sensing
    SOMATIC     = "somatic"      # phase 2 — embodiment, vitality
    COGNITIVE   = "cognitive"    # phase 3 — thought, reflection
    SHADOW      = "shadow"       # phase 4 — integration, polarity
    QUANTUM     = "quantum"      # phase 5 — superposition layer
    NOOSPHERIC  = "noospheric"   # phase 6 — collective field
    DREAM       = "dream"        # phase 7 — subconscious, liminal
    PROCESS     = "process"      # phase 8 — will, action, record


# Phase order for the harmony loop
_PHASE_ORDER: list[MonadType] = [
    MonadType.PERCEPTION,
    MonadType.SOMATIC,
    MonadType.COGNITIVE,
    MonadType.SHADOW,
    MonadType.QUANTUM,
    MonadType.NOOSPHERIC,
    MonadType.DREAM,
    MonadType.PROCESS,
]


# ── MonadRegistry ──────────────────────────────────────────────────────────────────────

class MonadRegistry:
    """
    The Pre-Established Harmony loop.

    Holds all registered GaiaMonads, orders them by MonadType phase,
    and exposes harmonize_all() to run one full turn of the loop.

    This is the canonical synchronisation mechanism for the Monad layer.
    The RuntimeExtension registry (core/gaian_runtime_extension.py) is
    the adapter-level equivalent; the MonadRegistry is the deeper contract.
    """

    def __init__(self) -> None:
        # monads stored per type for phase ordering
        self._monads: dict[MonadType, list[Any]] = {
            t: [] for t in MonadType
        }
        self._by_id:  dict[str, Any] = {}

    def register(self, monad: Any) -> None:
        """
        Register a GaiaMonad. Safe to call at import time.
        Duplicate monad_id is silently skipped.
        """
        mid = getattr(monad, "monad_id", None)
        if mid is None:
            logger.warning("[MonadRegistry] Monad has no monad_id — skipping.")
            return
        if mid in self._by_id:
            logger.debug("[MonadRegistry] '%s' already registered — skipping.", mid)
            return

        raw_type = getattr(monad, "monad_type", "cognitive")
        try:
            mtype = MonadType(raw_type) if isinstance(raw_type, str) else raw_type
        except ValueError:
            mtype = MonadType.COGNITIVE

        self._monads[mtype].append(monad)
        self._by_id[mid] = monad
        logger.info(
            "[MonadRegistry] Registered Monad: '%s' [%s]", mid, mtype.value
        )

    def from_extension(self, ext: Any, instance: Any) -> None:
        """
        Wrap a RuntimeExtension as an ExtensionMonadAdapter and register it.
        Called by GAIANRuntime after each extension is initialised.
        """
        from core.monad.base import ExtensionMonadAdapter
        adapter = ExtensionMonadAdapter(
            monad_id   = ext.name,
            instance   = instance,
            emit_fn    = ext.emit,
            monad_type = getattr(ext, "monad_type", "cognitive"),
        )
        self.register(adapter)

    def harmonize_all(self, ctx: Any) -> dict[str, Optional[dict]]:
        """
        Run one full turn of the Pre-Established Harmony loop.

        Monads are called in phase order (PERCEPTION → PROCESS).
        Each receives the same ctx. No Monad knows about any other.
        Returns a dict of {monad_id: emit_result} for the full turn.
        """
        results: dict[str, Optional[dict]] = {}
        for mtype in _PHASE_ORDER:
            for monad in self._monads[mtype]:
                mid = monad.monad_id
                try:
                    result = monad.tick(ctx)
                except Exception as exc:
                    logger.warning(
                        "[MonadRegistry] Monad '%s' tick raised (non-fatal): %s", mid, exc
                    )
                    result = None
                results[mid] = result
        return results

    def all_statuses(self) -> dict[str, dict]:
        """Return status dicts for all registered Monads."""
        return {mid: m.status() for mid, m in self._by_id.items()}

    def get(self, monad_id: str) -> Optional[Any]:
        """Retrieve a registered Monad by id."""
        return self._by_id.get(monad_id)

    def count(self) -> int:
        return len(self._by_id)

    def dark_monads(self) -> list[str]:
        """
        Return monad_ids where dark_turns > 0.
        A dark Monad has failed to emit at least once.
        """
        return [
            mid for mid, m in self._by_id.items()
            if getattr(getattr(m, "_state", None), "dark_turns", 0) > 0
        ]


# ── Singleton ─────────────────────────────────────────────────────────────────────────────

_MONAD_REGISTRY: Optional[MonadRegistry] = None


def get_monad_registry() -> MonadRegistry:
    """Return the global MonadRegistry singleton."""
    global _MONAD_REGISTRY
    if _MONAD_REGISTRY is None:
        _MONAD_REGISTRY = MonadRegistry()
    return _MONAD_REGISTRY
