"""
shadow_engine/integration.py
Integration progress tracker.

Integration is the measure of how much a user has consciously worked
with an active shadow archetype.  It accrues through journaling,
stage advancement, and reflection sessions.  It decays slowly when
the user is not journaling.  It never resets to zero.
"""

from __future__ import annotations
from dataclasses import dataclass
from datetime    import datetime, timezone
from typing      import Optional

# Accrual constants
JOURNAL_ENTRY_GAIN:   float = 0.02   # per qualifying entry
JOURNAL_DAILY_CAP:    float = 0.10   # max gain per day from journaling
STAGE_ADVANCE_GAIN:   float = 0.15   # one-time on stage advancement
REFLECTION_GAIN:      float = 0.05   # per explicit reflection session
PASSIVE_GAIN_PER_DAY: float = 0.01   # when intensity < 0.25 for 7+ days

# Decay constants
DECAY_PER_DAY:        float = 0.005  # when journaling < 1 entry/week
MIN_PROGRESS:         float = 0.0
MAX_PROGRESS:         float = 1.0


@dataclass
class IntegrationState:
    principal_id:         str
    archetype:            str
    progress:             float      # 0.0 – 1.0
    journal_gain_today:   float      # resets each calendar day
    last_updated:         datetime
    last_journal_date:    Optional[datetime]
    low_intensity_days:   int        # consecutive days intensity < 0.25


class IntegrationTracker:
    """
    Manages integration progress for a single (principal, archetype) pair.

    Designed to be loaded from SovereignMemory on engine init and saved
    back after each tick.  The engine is responsible for persistence;
    IntegrationTracker is pure computation.
    """

    def __init__(self, state: IntegrationState) -> None:
        self._s = state

    @classmethod
    def new(cls, principal_id: str, archetype: str) -> "IntegrationTracker":
        return cls(IntegrationState(
            principal_id=principal_id,
            archetype=archetype,
            progress=0.0,
            journal_gain_today=0.0,
            last_updated=datetime.now(timezone.utc),
            last_journal_date=None,
            low_intensity_days=0,
        ))

    @property
    def progress(self) -> float:
        return self._s.progress

    def _clamp(self, v: float) -> float:
        return max(MIN_PROGRESS, min(MAX_PROGRESS, v))

    def _is_same_day(self, a: datetime, b: datetime) -> bool:
        return a.date() == b.date()

    def accrue_journal_entry(self) -> float:
        """Record one qualifying journal entry.  Returns gain applied."""
        now = datetime.now(timezone.utc)
        if (self._s.last_journal_date is None
                or not self._is_same_day(now, self._s.last_journal_date)):
            self._s.journal_gain_today = 0.0

        remaining_cap = JOURNAL_DAILY_CAP - self._s.journal_gain_today
        if remaining_cap <= 0:
            return 0.0

        gain = min(JOURNAL_ENTRY_GAIN, remaining_cap)
        self._s.progress          = self._clamp(self._s.progress + gain)
        self._s.journal_gain_today += gain
        self._s.last_journal_date = now
        self._s.last_updated      = now
        return gain

    def accrue_stage_advance(self) -> float:
        """Call when the user advances a stage while this archetype is active."""
        self._s.progress     = self._clamp(self._s.progress + STAGE_ADVANCE_GAIN)
        self._s.last_updated = datetime.now(timezone.utc)
        return STAGE_ADVANCE_GAIN

    def accrue_reflection_session(self) -> float:
        """Call when the user completes a shadow reflection session."""
        self._s.progress     = self._clamp(self._s.progress + REFLECTION_GAIN)
        self._s.last_updated = datetime.now(timezone.utc)
        return REFLECTION_GAIN

    def tick_daily(
        self,
        shadow_intensity: float,
        journal_entries_this_week: int,
    ) -> None:
        """
        Called once per day.  Handles:
        - Passive gain when intensity is low for 7+ consecutive days
        - Decay when journaling frequency drops below 1/week
        """
        now = datetime.now(timezone.utc)

        # Track consecutive low-intensity days
        if shadow_intensity < 0.25:
            self._s.low_intensity_days += 1
        else:
            self._s.low_intensity_days = 0

        if self._s.low_intensity_days >= 7:
            self._s.progress = self._clamp(
                self._s.progress + PASSIVE_GAIN_PER_DAY
            )

        # Decay when not journaling
        if journal_entries_this_week < 1:
            self._s.progress = self._clamp(
                self._s.progress - DECAY_PER_DAY
            )

        self._s.last_updated = now

    def state(self) -> IntegrationState:
        return self._s
