"""
stage_engine.window_tracker
===========================
WindowTracker — temporal sliding-window context manager for StageEngine.

Maintains a bounded ring-buffer of recent signal snapshots used by
StageEngine.evaluate to compute temporal trends.

Architecture reference : NEXUS_UNIVERSAL_OS.md  Domain 2.3
"""
from __future__ import annotations

import logging
from collections import deque
from typing import Any, Deque, Dict, List

logger = logging.getLogger("stage_engine.window_tracker")

_DEFAULT_WINDOW = 20


class WindowTracker:
    """
    Sliding-window buffer of signal snapshots for the StageEngine.

    Maintains up to ``max_size`` entries.  When the buffer is full,
    the oldest entry is evicted automatically (FIFO).

    Reference: NEXUS_UNIVERSAL_OS.md Domain 2.3
    """

    def __init__(self, max_size: int = _DEFAULT_WINDOW) -> None:
        self.max_size = max_size
        self._buffer: Deque[Dict[str, Any]] = deque(maxlen=max_size)
        logger.info("WindowTracker created (max_size=%d).", max_size)

    def push(self, snapshot: Dict[str, Any]) -> None:
        """Add a snapshot to the window."""
        self._buffer.append(snapshot)

    def window(self) -> List[Dict[str, Any]]:
        """Return a list copy of the current window (oldest first)."""
        return list(self._buffer)

    def clear(self) -> None:
        """Clear the window buffer."""
        self._buffer.clear()
        logger.info("WindowTracker cleared.")

    def __len__(self) -> int:
        return len(self._buffer)
