"""
GAIA Simulation Layer — v0.7

Purpose: explore hypothetical futures without mutating reality.

Core principle:
  Reality is read-only.
  Every simulation runs inside an isolated sandbox.
  Simulations produce candidate futures, not truth claims.

Responsibility boundary:
  Epistemics  → what evidence supports claims
  Temporal    → how reality changes over time
  Simulation  → what COULD follow if X were true

Simulation never overwrites the world state.
It forks from a snapshot and evolves independently.
"""
