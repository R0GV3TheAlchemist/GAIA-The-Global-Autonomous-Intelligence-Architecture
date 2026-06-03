"""Tests for Schumann alignment tolerance computation.

Bug: is_aligned() used strict > causing boundary values to return False.
Fix: Changed to >= (inclusive) in schumann/alignment.py.
"""
import pytest
from schumann.alignment import is_aligned, DEFAULT_TOLERANCE


class TestSchumannAlignment:

    def test_computed_aligned_within_tolerance(self):
        """A score exactly equal to tolerance must return True (>= not >)."""
        score     = DEFAULT_TOLERANCE  # 0.50
        tolerance = DEFAULT_TOLERANCE  # 0.50
        result    = is_aligned(score, tolerance)
        assert result is True, (
            f"is_aligned({score}, {tolerance}) returned False — expected True. "
            "Boundary value must be considered aligned."
        )

    def test_above_tolerance_is_aligned(self):
        """Score above tolerance is always aligned."""
        assert is_aligned(0.75, 0.50) is True
        assert is_aligned(1.00, 0.50) is True

    def test_below_tolerance_is_not_aligned(self):
        """Score below tolerance is never aligned."""
        assert is_aligned(0.49, 0.50) is False
        assert is_aligned(0.00, 0.50) is False

    def test_default_tolerance_is_fifty_percent(self):
        """DEFAULT_TOLERANCE must be 0.50."""
        assert DEFAULT_TOLERANCE == 0.50

    def test_custom_tolerance_respected(self):
        """Custom tolerance argument overrides the default."""
        assert is_aligned(0.30, tolerance=0.30) is True   # boundary
        assert is_aligned(0.29, tolerance=0.30) is False  # just below
        assert is_aligned(0.31, tolerance=0.30) is True   # just above
