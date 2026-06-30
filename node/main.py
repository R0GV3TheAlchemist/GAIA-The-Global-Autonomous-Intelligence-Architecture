"""
GAIA Node — FastAPI Server
Each instance of this is one epistemic node in the GAIA network.
Nodes communicate over HTTP, sync state, and converge on shared truth.

Run standalone:
  uvicorn node.main:app --port 8000

Run as network (recommended):
  docker-compose up
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from node.state import NodeState
from node.api import build_router
from node import sync as sync_module

NODE_ID = os.getenv("NODE_ID", "local")
NODE_DOMAIN = os.getenv("NODE_DOMAIN", None)
NODE_TRUST = float(os.getenv("NODE_TRUST", "1.0"))

# Shared state instance — single source of truth for this node process
state = NodeState(node_id=NODE_ID, domain=NODE_DOMAIN, trust=NODE_TRUST)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n  GAIA Node [{NODE_ID}] starting up")
    print(f"  Domain:  {NODE_DOMAIN or 'general'}")
    print(f"  Trust:   {NODE_TRUST}")
    print(f"  Peers:   {sync_module.PEERS}\n")
    yield
    print(f"\n  GAIA Node [{NODE_ID}] shutting down — saving state...")
    state.save()


app = FastAPI(
    title=f"GAIA Node [{NODE_ID}]",
    description="Epistemic world model node — GAIA distributed network",
    version="0.5.0",
    lifespan=lifespan
)

app.include_router(build_router(state))


@app.get("/")
def root():
    return {
        "system": "GAIA",
        "node_id": NODE_ID,
        "version": "0.5.0",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "ok", "node_id": NODE_ID}


@app.get("/state")
def get_state():
    """Return this node's full current world state."""
    return state.get_snapshot()


@app.post("/sync")
def receive_sync(payload: dict):
    """
    Receive a state push from a peer node.
    Merge incoming claims using confidence-priority resolution.
    """
    result = state.merge(payload)
    return result


@app.get("/stats")
def get_stats():
    return state.stats()
