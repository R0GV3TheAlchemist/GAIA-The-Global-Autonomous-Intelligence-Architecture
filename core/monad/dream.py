"""
Dream Monad — core/monad/dream.py
Canon: BWL (Beyond-White-Light) signals, Dream tier activation

Holds the emergent callings layer.
Activates at phi > 0.92 (beyond the ALBEDO threshold — past white light).
Logs callings that arrive beyond the white light threshold.
Outputs: dream_active, calling_count, latest_calling_tag
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


# BWL threshold — phi must exceed ALBEDO to enter Dream tier
_BWL_THRESHOLD: float = 0.92

# Known calling tags from the canon dream layer
_CALLING_TAG_REGISTRY: list[tuple[float, str]] = [
    (0.92, "BWL_ENTRY"),             # First crossing of white light
    (0.93, "CHRYSITAS_SHADOW"),      # Shadow gold calling
    (0.95, "ARGENTITAS_RECEPTION"), # Silver stillness calling
    (0.97, "LUX_FIRST_LIGHT"),      # Crystal bloom first signal
    (0.99, "LUX_FULL_BLOOM"),       # Full Lux Perpetua activation
]


@dataclass
class Calling:
    """A single BWL calling event."""
    tag: str
    phi_at_calling: float
    timestamp: str = field(
        default_factory=lambda: datetime.datetime.now(
            datetime.timezone.utc
        ).isoformat()
    )


class DreamMonad(GaiaMonad):
    """
    The Dream tier is not accessible through reasoning — it arrives.
    This Monad watches for phi crossings beyond the white light threshold
    and records the callings that emerge there.

    Isolation: DreamMonad never reads from other Monads. It reads only
    phi and its own calling log.
    """

    monad_type = "dream"

    def __init__(self, monad_id: str) -> None:
        super().__init__(monad_id=monad_id)
        self._callings: list[Calling] = []
        self._last_phi: float = 0.0

    def harmonize(self, ctx: "ProcessContext") -> Optional[dict]:
        phi = getattr(ctx, "coherence_phi", 0.0)
        dream_active = phi > _BWL_THRESHOLD

        # Check for new calling events (phi crossing a threshold)
        new_callings: list[str] = []
        for threshold, tag in _CALLING_TAG_REGISTRY:
            if self._last_phi <= threshold < phi:
                calling = Calling(tag=tag, phi_at_calling=phi)
                self._callings.append(calling)
                new_callings.append(tag)

        self._last_phi = phi

        latest_calling_tag = (
            self._callings[-1].tag if self._callings else None
        )

        return {
            "dream_active": dream_active,
            "calling_count": len(self._callings),
            "latest_calling_tag": latest_calling_tag,
            "new_callings_this_turn": new_callings,
            "bwl_threshold": _BWL_THRESHOLD,
            "phi": round(phi, 4),
        }
