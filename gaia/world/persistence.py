"""
GAIA World Persistence
JSON-based persistence for the world state.
Every save is a versioned truth commit.
Upgrade path: swap JSON for Neo4j / Redis in v0.3.
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

DEFAULT_STATE_FILE = Path("world_state.json")


class WorldPersistence:

    def save(self, state: Dict[str, Any], path: Path = DEFAULT_STATE_FILE) -> None:
        """Persist the world state snapshot to JSON."""
        payload = {
            "saved_at":    datetime.utcnow().isoformat(),
            "gaia_version": "0.2.0",
            **state
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2, default=str)

    def load(self, path: Path = DEFAULT_STATE_FILE) -> Dict[str, Any]:
        """Load world state from JSON. Returns empty state if file not found."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
            print(f"  Loaded world state from {path} "
                  f"(saved_at={data.get('saved_at', 'unknown')})")
            return data
        except FileNotFoundError:
            print(f"  No prior world state at {path}. Starting fresh.")
            return {"state": {}, "update_count": 0}
