"""
tests/test_shadow_integration.py
Unit tests for IntegrationTracker accrual, decay, and milestones.
"""

import pytest
from shadow_engine.integration import (
    IntegrationTracker,
    JOURNAL_ENTRY_GAIN,
    JOURNAL_DAILY_CAP,
    STAGE_ADVANCE_GAIN,
    REFLECTION_GAIN,
    PASSIVE_GAIN_PER_DAY,
    DECAY_PER_DAY,
)


def fresh_tracker(archetype: str = "Orphan") -> IntegrationTracker:
    return IntegrationTracker.new("test-user", archetype)


class TestJournalAccrual:
    def test_single_entry_gain(self):
        t = fresh_tracker()
        gain = t.accrue_journal_entry()
        assert gain == pytest.approx(JOURNAL_ENTRY_GAIN)
        assert t.progress == pytest.approx(JOURNAL_ENTRY_GAIN)

    def test_daily_cap_enforced(self):
        t = fresh_tracker()
        total = 0.0
        for _ in range(20):          # 20 × 0.02 = 0.40, but cap is 0.10
            total += t.accrue_journal_entry()
        assert total == pytest.approx(JOURNAL_DAILY_CAP)
        assert t.progress == pytest.approx(JOURNAL_DAILY_CAP)

    def test_progress_never_exceeds_1(self):
        t = fresh_tracker()
        # Force progress near ceiling
        t._s.progress = 0.99
        t._s.journal_gain_today = 0.0  # reset daily cap
        t.accrue_journal_entry()
        assert t.progress <= 1.0


class TestStageAdvance:
    def test_stage_advance_adds_correct_gain(self):
        t = fresh_tracker()
        gain = t.accrue_stage_advance()
        assert gain == pytest.approx(STAGE_ADVANCE_GAIN)
        assert t.progress == pytest.approx(STAGE_ADVANCE_GAIN)


class TestReflectionSession:
    def test_reflection_adds_correct_gain(self):
        t = fresh_tracker()
        gain = t.accrue_reflection_session()
        assert gain == pytest.approx(REFLECTION_GAIN)


class TestDecay:
    def test_decay_when_no_journaling(self):
        t = fresh_tracker()
        t._s.progress = 0.5
        t.tick_daily(shadow_intensity=0.5, journal_entries_this_week=0)
        assert t.progress == pytest.approx(0.5 - DECAY_PER_DAY)

    def test_no_decay_when_journaling(self):
        t = fresh_tracker()
        t._s.progress = 0.5
        t.tick_daily(shadow_intensity=0.5, journal_entries_this_week=2)
        assert t.progress == pytest.approx(0.5)

    def test_never_below_zero(self):
        t = fresh_tracker()
        t._s.progress = 0.001
        for _ in range(10):
            t.tick_daily(shadow_intensity=0.5, journal_entries_this_week=0)
        assert t.progress >= 0.0


class TestPassiveGain:
    def test_passive_gain_after_7_low_intensity_days(self):
        t = fresh_tracker()
        t._s.progress = 0.2
        # Simulate 7 days of low intensity
        for _ in range(7):
            t.tick_daily(shadow_intensity=0.1, journal_entries_this_week=1)
        # Day 7 triggers passive gain
        assert t.progress > 0.2

    def test_no_passive_gain_before_7_days(self):
        t = fresh_tracker()
        t._s.progress = 0.2
        for _ in range(6):
            t.tick_daily(shadow_intensity=0.1, journal_entries_this_week=1)
        assert t.progress == pytest.approx(0.2)
