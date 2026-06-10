"""
core/mesh
=========
P2P Mesh layer for GAIA-OS MotherThread coordination.

Public API
----------
from core.mesh import get_p2p_mesh, get_crdt_engine, get_thread_weaver
"""

from core.mesh.p2p_mesh import P2PMesh, PeerRecord, GossipEnvelope, get_p2p_mesh
from core.mesh.crdt_state import CRDTStateEngine, LWWRegister, ORSet, get_crdt_engine
from core.mesh.thread_weaver import ThreadWeaver, WeavingSlot, VectorClock, get_thread_weaver

__all__ = [
    # P2P Mesh
    "P2PMesh",
    "PeerRecord",
    "GossipEnvelope",
    "get_p2p_mesh",
    # CRDT State
    "CRDTStateEngine",
    "LWWRegister",
    "ORSet",
    "get_crdt_engine",
    # Thread Weaver
    "ThreadWeaver",
    "WeavingSlot",
    "VectorClock",
    "get_thread_weaver",
]
