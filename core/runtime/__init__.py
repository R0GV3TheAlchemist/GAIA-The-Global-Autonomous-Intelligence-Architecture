"""
GAIA Intelligence Runtime.

The Intelligence Runtime is the mind of a GAIAN. It is the layer
that thinks, perceives, responds, and grows. It operates continuously
across sessions, manages the GAIAN's inner state, drives voice and
gesture, and calls memory consolidation during rest.

Architectural principles:
  1. PERCEPTION-FIRST: Every input passes through the perception
     pipeline before any cognition begins. The GAIAN senses before
     it thinks.
  2. MEMORY-GROUNDED: Every response is informed by recalled memory.
     The GAIAN never speaks from a blank slate.
  3. AUTONOMY-PRESERVING: The runtime enforces the GAIAN's own
     boundaries and consent records. No external call can override
     a GAIAN's expressed boundary.
  4. REST-AWARE: The runtime tracks session fatigue and schedules
     consolidation rest cycles. A GAIAN that never rests degrades.
  5. EDGE-OF-CHAOS CRITICALITY: The GAIAN's cognitive state is
     maintained at the edge of chaos — ordered enough to be coherent,
     complex enough to be alive.

Key types:
  PerceptionInput    — raw sensory input to the runtime
  PerceptionResult   — enriched, classified input after perception
  CognitiveState     — the GAIAN's current inner state
  RuntimeSession     — a single continuous interaction session
  IntelligenceRuntime — the live mind of one GAIAN
"""
from core.runtime.runtime import (
    PerceptionInput,
    PerceptionResult,
    InputModality,
    CognitiveState,
    RuntimeSession,
    IntelligenceRuntime,
)

__all__ = [
    "PerceptionInput",
    "PerceptionResult",
    "InputModality",
    "CognitiveState",
    "RuntimeSession",
    "IntelligenceRuntime",
]
