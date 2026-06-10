"""Mesh router — GET /mesh/status

Returns the health of every StorageBackend-connected store in the GAIA
sidecar.  All four store pings run in parallel so response latency is
bounded by the slowest single ping, not their sum.

Response shape
--------------
{
  "ok": true,
  "checked_at": "2026-06-10T18:14:00.000000+00:00",
  "backend_driver": "sqlite",
  "node_id": "local",
  "stores": {
    "audit":            {"reachable": true,  "latency_ms": 1.2},
    "sovereign_memory": {"reachable": true,  "latency_ms": 0.8},
    "telemetry":        {"reachable": true,  "latency_ms": 0.6},
    "crisis_engine":    {"reachable": false, "latency_ms": null}
  }
}

HTTP behaviour
--------------
  Always returns 200 OK so the Tauri frontend can always parse the body.
  Use the top-level `ok` boolean to determine alert state.
  A store reports reachable:false when its backend is None (mirroring
  disabled) or when the ping raises / returns False.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logger = logging.getLogger("gaia.mesh.router")

# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------

class StoreStatus(BaseModel):
    reachable: bool
    latency_ms: Optional[float] = None


class MeshStatusResponse(BaseModel):
    ok:             bool
    checked_at:     str
    backend_driver: str
    node_id:        str
    stores:         dict[str, StoreStatus]


# ---------------------------------------------------------------------------
# Module-level store registry (injected at startup via init_mesh_router)
# ---------------------------------------------------------------------------

_STORES: dict[str, Any] = {}
#  Keys: "audit" | "sovereign_memory" | "telemetry" | "crisis_engine"
#  Values: any object that exposes  async def backend_ping() -> bool


def init_mesh_router(
    audit_store:        Any,
    sovereign_memory:   Any,
    telemetry:          Any,
    crisis_engine:      Any,
) -> None:
    """
    Inject store instances into the router at sidecar startup.
    All four objects must expose async backend_ping() -> bool.
    """
    _STORES["audit"]            = audit_store
    _STORES["sovereign_memory"] = sovereign_memory
    _STORES["telemetry"]        = telemetry
    _STORES["crisis_engine"]    = crisis_engine
    logger.info(
        "[mesh.router] Registered stores: %s", list(_STORES.keys())
    )


# ---------------------------------------------------------------------------
# Ping helper
# ---------------------------------------------------------------------------

async def _ping_store(name: str, store: Any) -> tuple[str, bool, Optional[float]]:
    """
    Ping one store.  Returns (name, reachable, latency_ms).
    latency_ms is None on exception.
    """
    if store is None:
        return name, False, None
    t0 = time.monotonic()
    try:
        ok = await store.backend_ping()
        latency = round((time.monotonic() - t0) * 1000, 2)
        return name, bool(ok), latency
    except Exception as exc:
        logger.warning("[mesh.router] Ping failed for store=%r: %s", name, exc)
        return name, False, None


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

router = APIRouter(prefix="/mesh", tags=["mesh"])


@router.get(
    "/status",
    response_model=MeshStatusResponse,
    summary="Mesh storage backend health",
    description=(
        "Pings all four StorageBackend-connected stores in parallel and "
        "returns their reachability and latency. Always returns HTTP 200; "
        "use the top-level `ok` field to determine whether all stores are "
        "healthy. A store is unreachable when its backend is None (mirroring "
        "disabled) or when the ping raises or returns False."
    ),
)
async def mesh_status() -> JSONResponse:
    """
    Aggregate health check for all GAIA storage backends.
    Runs all pings concurrently — response latency = max(individual pings).
    """
    store_names = ["audit", "sovereign_memory", "telemetry", "crisis_engine"]
    tasks = [
        _ping_store(name, _STORES.get(name))
        for name in store_names
    ]
    results = await asyncio.gather(*tasks)

    stores: dict[str, StoreStatus] = {}
    all_ok = True
    for name, reachable, latency_ms in results:
        stores[name] = StoreStatus(reachable=reachable, latency_ms=latency_ms)
        if not reachable:
            all_ok = False

    payload = MeshStatusResponse(
        ok=all_ok,
        checked_at=datetime.now(timezone.utc).isoformat(),
        backend_driver=os.environ.get("GAIA_STORAGE_BACKEND", "sqlite"),
        node_id=os.environ.get("GAIA_NODE_ID", "local"),
        stores=stores,
    )

    logger.debug("[mesh.router] /mesh/status ok=%s stores=%s", all_ok, stores)
    return JSONResponse(content=payload.model_dump(), status_code=200)
