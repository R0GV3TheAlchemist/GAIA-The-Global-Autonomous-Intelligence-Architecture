"""
GAIA Node API Router
Claim submission, query, sync trigger, and node info endpoints.
"""

import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from node import sync as sync_module


class ClaimRequest(BaseModel):
    statement: str
    confidence: float = 0.5
    status: Optional[str] = "unknown"
    domain: Optional[str] = None
    sources: Optional[List[str]] = []
    entities: Optional[List[str]] = []


def build_router(state) -> APIRouter:
    router = APIRouter()

    @router.post("/claim")
    def submit_claim(req: ClaimRequest):
        """
        Submit a new claim to this node.
        Stores in local world state and broadcasts to peers.
        """
        claim_id = str(uuid.uuid4())
        entry = {
            "id":         claim_id,
            "statement":  req.statement,
            "confidence": req.confidence,
            "status":     req.status,
            "domain":     req.domain,
            "sources":    req.sources,
            "entities":   req.entities
        }
        state.update(claim_id, entry)

        # Broadcast to peers after every claim submission
        broadcast_result = sync_module.broadcast(state.get_snapshot())

        return {
            "id":        claim_id,
            "status":    "stored",
            "broadcast": broadcast_result
        }

    @router.get("/claims")
    def list_claims(
        keyword: Optional[str] = None,
        min_confidence: float = 0.0
    ):
        """List all claims, optionally filtered by keyword and min confidence."""
        data = state.get()
        results = [
            v for v in data.values()
            if isinstance(v, dict)
            and v.get("confidence", 0) >= min_confidence
            and (not keyword or keyword.lower() in v.get("statement", "").lower())
        ]
        return {
            "count":  len(results),
            "claims": sorted(results, key=lambda x: x.get("confidence", 0), reverse=True)
        }

    @router.post("/sync/trigger")
    def trigger_sync():
        """
        Manually trigger a sync cycle:
        fetch peer states and merge into local state.
        """
        peer_states = sync_module.fetch_peers()
        merge_results = []
        for peer_url, peer_snapshot in peer_states.items():
            result = state.merge(peer_snapshot)
            merge_results.append({"peer": peer_url, **result})
        return {
            "peers_contacted": len(peer_states),
            "merge_results":   merge_results
        }

    @router.get("/peers")
    def get_peers():
        return {"peers": sync_module.PEERS}

    return router
