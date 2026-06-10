"""
core/mesh
=========
Federated Inter-Node Protocol for GAIA-OS.

Public API
----------
    from core.mesh import GaiaNode, NodeDiscovery, CollectiveField, MeshServer

Canon Ref:
    C04  — Privacy: individual identity never leaves the device
    C44  — Piezoelectric Resonance: field coherence across nodes
    C47  — Sovereign Matrix Code: observer collapses the field

Issue: #277 — CRITICAL PATH
"""

from .node import GaiaNode, NodeIdentity
from .discovery import NodeDiscovery
from .collective_field import CollectiveField, LWWEntry
from .server import MeshServer

__all__ = [
    "GaiaNode",
    "NodeIdentity",
    "NodeDiscovery",
    "CollectiveField",
    "LWWEntry",
    "MeshServer",
]
