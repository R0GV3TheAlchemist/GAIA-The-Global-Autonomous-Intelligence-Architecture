"""stageengine.windowtracker

Temporal Window Tracker for Stage Engine

Records the start time, cumulative active time, and milestone timestamps
for each GAIA developmental stage. Used by StageEngine to track how
long GAIA has been in each stage and when key criteria were met.

Architecture reference:
    NEXUS_UNIVERSAL_OS.md Domain 2.7
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("stageengine.windowtracker")


@dataclass
class StageWindow:
    """Time window record for a single GAIA stage.

    Fields:
        stage_name:    String name of the stage.
        entered_at:    UTC datetime when GAIA entered this stage.
        exited_at:     UTC datetime when GAIA left this stage (None if current).
        milestones:    Dict mapping milestone names to UTC timestamps.
    """
    stage_name: str
    entered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    exited_at: Optional[datetime] = None
    milestones: dict[str, datetime] = field(default_factory=dict)

    def duration_seconds(self) -> Optional[float]:
        """Return duration in seconds (None if stage not yet exited)."""
        if self.exited_at is None:
            return None
        return (self.exited_at - self.entered_at).total_seconds()


class WindowTracker:
    """Tracks temporal windows across GAIA developmental stages."""

    def __init__(self) -> None:
        self._windows: list[StageWindow] = []
        logger.info("WindowTracker initialised.")

    def open_window(self, stage_name: str) -> StageWindow:
        """Open a new time window for a stage entry."""
        window = StageWindow(stage_name=stage_name)
        self._windows.append(window)
        logger.info("WindowTracker: opened window for stage '%s'.", stage_name)
        return window

    def close_window(self, stage_name: str) -> None:
        """Close the most recent open window for the given stage."""
        for w in reversed(self._windows):
            if w.stage_name == stage_name and w.exited_at is None:
                w.exited_at = datetime.now(timezone.utc)
                logger.info("WindowTracker: closed window for stage '%s'.", stage_name)
                return
        logger.warning("WindowTracker: no open window found for stage '%s'.", stage_name)

    def record_milestone(self, stage_name: str, milestone: str) -> None:
        """Record a named milestone timestamp for the current window."""
        for w in reversed(self._windows):
            if w.stage_name == stage_name and w.exited_at is None:
                w.milestones[milestone] = datetime.now(timezone.utc)
                logger.debug("WindowTracker: milestone '%s' recorded for stage '%s'.", milestone, stage_name)
                return

    def all_windows(self) -> list[StageWindow]:
        """Return all stage windows in chronological order."""
        return list(self._windows)
