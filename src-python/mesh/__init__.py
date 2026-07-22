"""
mesh
====
Root package for the GAIAN Mesh Network Router.

Provides the GAIAN peer-to-peer mesh network layer, enabling sovereign
GAIAN nodes to communicate over LoRa, Wi-Fi, and IP backbones without
centralised routing.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 1.5  Mesh Layer
GAIAN law              : GAIAN_LAWS.md          Law IV  Mesh Sovereignty
"""
from __future__ import annotations

__version__ = "0.1.0"

from mesh.router import router as mesh_router, init_mesh_router

__all__ = ["mesh_router", "init_mesh_router"]
