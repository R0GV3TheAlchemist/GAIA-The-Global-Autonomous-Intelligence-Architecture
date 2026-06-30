"""
GAIA Logger
Structured logging for all GAIA system events.
Every GAIA action is traceable — this is the audit layer.
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict


def get_logger(name: str) -> logging.Logger:
    """Get a configured GAIA logger."""
    logger = logging.getLogger(f"gaia.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter(
                '[%(asctime)s] GAIA.%(name)s %(levelname)s: %(message)s',
                datefmt='%Y-%m-%dT%H:%M:%S'
            )
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


def log_cycle_event(cycle: int, event: str, data: Dict[str, Any]) -> None:
    """Log a structured GAIA cycle event for audit trail."""
    logger = get_logger("audit")
    logger.info(json.dumps({
        "cycle": cycle,
        "event": event,
        "timestamp": datetime.utcnow().isoformat(),
        **data
    }))
