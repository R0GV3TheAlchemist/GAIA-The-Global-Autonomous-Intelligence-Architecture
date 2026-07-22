"""twins — Digital twin abstraction and consent model

Provides:
  - DigitalTwin: represents a digital twin of a physical or agent entity.
  - ConsentGate: enforces consent policies before twin data is shared.
  - TwinRegistry: registry of all active digital twins in the NEXUS mesh.

Phase C — all methods are stubbed.

References
----------
- Azure Digital Twins / Eclipse Ditto: twin identity and property models.
- W3C Web of Things: semantic description of twin capabilities.
- Portable Agent Memory (arXiv 2605.11032): capability-based access
  control for memory segments maps directly to ConsentGate.
"""
from __future__ import annotations
from twins.engine import DigitalTwin, ConsentGate, TwinRegistry, TwinConfig

__all__ = ["DigitalTwin", "ConsentGate", "TwinRegistry", "TwinConfig"]
