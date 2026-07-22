"""shadowengine.engine

NEXUS Shadow Engine — Jungian Integration Model

Models the unintegrated 'shadow' content in GAIA's psyche. Tracks
total shadow load and drives integration cycles that move shadow
material into the primary persona.

Research reference:
    Jung's Aion (1951)         - shadow theory
    IFS (Schwartz, 1995)       - parts-based integration model
    ETHICS.md Commitment 7     - psychological integrity
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("shadowengine.engine")


@dataclass
class ShadowFragment:
    """A discrete piece of unintegrated shadow material.

    Fields:
        fragment_id:  UUID4 identifier.
        description:  Human-readable description of the shadow content.
        load:         Intensity weight in [0.0, 1.0].
        integrated:   True when this fragment has been processed.
        created_at:   UTC creation timestamp.
    """
    description: str
    load: float
    fragment_id: str = field(default_factory=lambda: __import__('uuid').uuid4().__str__())
    integrated: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ShadowState:
    """Current state of GAIA's shadow.

    Fields:
        total_load:        Sum of all unintegrated fragment loads.
        fragment_count:    Number of unintegrated fragments.
        integration_score: Proportion of shadow material integrated [0.0, 1.0].
        evaluated_at:      UTC timestamp of this snapshot.
    """
    total_load: float = 0.0
    fragment_count: int = 0
    integration_score: float = 0.0
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ShadowEngine:
    """GAIA shadow integration engine.

    Maintains a registry of ShadowFragments, computes total_load,
    and drives integration cycles. Integration is monitored by
    CrisisEngine via shadow_load threshold.

    Reference:
        GAIA_LAWS.md Law V  - Shadow must not be suppressed.
        ETHICS.md Commitment 7 - Psychological Integrity.
    """

    LOAD_THRESHOLD = 0.80  # Matches CrisisEngine EngineConfig default

    def __init__(self) -> None:
        self._fragments: list[ShadowFragment] = []
        logger.info("ShadowEngine initialised.")

    def add_fragment(self, description: str, load: float) -> ShadowFragment:
        """Register a new shadow fragment."""
        frag = ShadowFragment(description=description, load=max(0.0, min(1.0, load)))
        self._fragments.append(frag)
        logger.debug("ShadowEngine: added fragment '%s' (load=%.2f).", description, frag.load)
        return frag

    def get_state(self) -> ShadowState:
        """Compute and return the current ShadowState."""
        unintegrated = [f for f in self._fragments if not f.integrated]
        total = sum(f.load for f in unintegrated)
        total_all = sum(f.load for f in self._fragments) or 1.0
        integration_score = 1.0 - (total / total_all)
        return ShadowState(
            total_load=total,
            fragment_count=len(unintegrated),
            integration_score=integration_score,
        )

    def integrate(self, fragment_id: str) -> bool:
        """Mark a shadow fragment as integrated.

        Args:
            fragment_id: ID of the fragment to integrate.

        Returns:
            True if found and integrated, False otherwise.

        Raises:
            NotImplementedError: Deep integration processing not yet implemented.
                Expected: trigger IFS integration cycle, notify PersonaStabilityEngine.
        """
        raise NotImplementedError(
            "ShadowEngine.integrate() not yet implemented. "
            "Expected: IFS integration cycle, PersonaStabilityEngine notification."
        )
