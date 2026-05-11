"""
tests/test_shadow_intensity.py
Unit tests for the intensity ramp formula.
"""

import pytest
from shadow_engine.intensity import compute_intensity_modifier, compute_shadow_intensity


class TestIntensityModifier:
    def test_day_zero_is_floor(self):
        assert compute_intensity_modifier(0) == pytest.approx(0.6)

    def test_day_14_is_ceiling(self):
        assert compute_intensity_modifier(14) == pytest.approx(1.0)

    def test_day_7_is_midpoint(self):
        result = compute_intensity_modifier(7)
        assert pytest.approx(0.8, abs=0.01) == result

    def test_beyond_14_stays_at_1(self):
        assert compute_intensity_modifier(100) == pytest.approx(1.0)

    def test_never_exceeds_1(self):
        for days in range(0, 100):
            assert compute_intensity_modifier(days) <= 1.0

    def test_never_below_floor(self):
        for days in range(0, 100):
            assert compute_intensity_modifier(days) >= 0.6


class TestShadowIntensity:
    def test_zero_score_gives_zero_intensity(self):
        assert compute_shadow_intensity(0.0, 14) == pytest.approx(0.0)

    def test_full_score_day_0_gives_floor_intensity(self):
        result = compute_shadow_intensity(1.0, 0)
        assert result == pytest.approx(0.6)

    def test_full_score_day_14_gives_full_intensity(self):
        result = compute_shadow_intensity(1.0, 14)
        assert result == pytest.approx(1.0)

    def test_intensity_bounded_0_to_1(self):
        for days in [0, 7, 14, 30]:
            for score in [0.0, 0.5, 1.0]:
                result = compute_shadow_intensity(score, days)
                assert 0.0 <= result <= 1.0
