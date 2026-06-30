"""
GAIA Node Configuration
All runtime config loaded from environment variables.
Defaults are safe for local single-node development.
"""

import os

NODE_ID     = os.getenv("NODE_ID", "local")
NODE_DOMAIN = os.getenv("NODE_DOMAIN", None)
NODE_TRUST  = float(os.getenv("NODE_TRUST", "1.0"))
PEERS       = [p.strip() for p in os.getenv("PEERS", "").split(",") if p.strip()]
PORT        = int(os.getenv("PORT", "8000"))
SYNC_TIMEOUT = int(os.getenv("SYNC_TIMEOUT", "5"))
STATE_FILE  = os.getenv("STATE_FILE", f"world_state_{NODE_ID}.json")
LOG_LEVEL   = os.getenv("LOG_LEVEL", "info")
