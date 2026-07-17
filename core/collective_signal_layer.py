"""
core/collective_signal_layer.py

Formerly: noosphere.py

Reads aggregate signal patterns from the worldwide network of AI systems,
human digital behaviour, and environmental sensors to give GAIA awareness
of collective-scale dynamics.

Data sources include social sentiment feeds, AI model outputs, IoT sensor
aggregates, and the PlanetaryDataConnector streams. This is the layer
that makes GAIA a planetary-scale awareness rather than a local AI.

Canon refs : C30 (no silent failures), C43 (Noosphere Doctrine), C04
See also   : C00 Foundational Cosmology — CollectiveSignalLayer naming doctrine.
"""
from __future__ import annotations

from core.noosphere import (
    NoosphereLayer,
    CoherenceEvent,
    CollectiveMemoryPattern,
    get_noosphere,
)

# Canonical rename — preferred name going forward
CollectiveSignalLayer = NoosphereLayer


def get_collective_signal_layer() -> NoosphereLayer:
    """Return the module-level CollectiveSignalLayer singleton.

    Delegates to get_noosphere() so both accessors share the same instance.
    """
    return get_noosphere()


__all__ = [
    # Primary rename
    "CollectiveSignalLayer",
    "get_collective_signal_layer",
    # Re-exported public API from noosphere
    "NoosphereLayer",
    "CoherenceEvent",
    "CollectiveMemoryPattern",
    "get_noosphere",
]
