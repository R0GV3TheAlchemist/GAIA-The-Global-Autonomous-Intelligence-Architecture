"""Tests for the EV1A affect inference decision tree.

Verifies priority-ordered signal resolution:
  CD checked before T, T-uncertainty checked before T-care.

Failing cases from the bug report:
  Case 13: T=0.50 > 0.45 should NOT trigger care (0.50 is not > 0.50)
  Case 18: CD=0.30 should fire DISSONANCE before CARE
  Case 34: CD=0.30 < 0.50, T=0.44 should return DISSONANCE (CD wins)
"""
import pytest
from affect_engine.ev1a_inference import AffectState, infer_affect


class TestEV1AAffectInference:

    # --- Case 13: boundary T=0.50, no CD ---------------------------------

    def test_case_13_T050_no_CD_returns_neutral(self):
        """T=0.50 is NOT > care_threshold(0.50) → NEUTRAL, not CARE."""
        result = infer_affect(cognitive_dissonance=0.00, temperature=0.50)
        assert result == AffectState.NEUTRAL, (
            f"Case 13: expected NEUTRAL, got {result}"
        )

    # --- Case 18: CD=0.30 with moderate T → DISSONANCE wins --------------

    def test_case_18_CD030_fires_dissonance_before_care(self):
        """CD=0.30 must fire DISSONANCE even when T would suggest CARE."""
        result = infer_affect(cognitive_dissonance=0.30, temperature=0.60)
        assert result == AffectState.DISSONANCE, (
            f"Case 18: expected DISSONANCE, got {result}"
        )

    # --- Case 34: CD=0.30, T=0.44 → DISSONANCE (CD before uncertainty) --

    def test_case_34_CD030_T044_returns_dissonance(self):
        """CD=0.30 fires DISSONANCE before T=0.44 uncertainty check."""
        result = infer_affect(cognitive_dissonance=0.30, temperature=0.44)
        assert result == AffectState.DISSONANCE, (
            f"Case 34: expected DISSONANCE, got {result}"
        )

    # --- Additional regression cases -------------------------------------

    def test_uncertainty_fires_when_no_cd(self):
        """No CD, low T → UNCERTAINTY."""
        result = infer_affect(cognitive_dissonance=0.00, temperature=0.30)
        assert result == AffectState.UNCERTAINTY

    def test_care_fires_when_no_cd_high_T(self):
        """No CD, high T → CARE."""
        result = infer_affect(cognitive_dissonance=0.00, temperature=0.80)
        assert result == AffectState.CARE

    def test_neutral_when_all_mid(self):
        """No CD, mid T (between uncertainty and care thresholds) → NEUTRAL."""
        result = infer_affect(cognitive_dissonance=0.00, temperature=0.47)
        assert result == AffectState.NEUTRAL

    def test_dissonance_threshold_is_inclusive(self):
        """CD exactly at threshold must fire DISSONANCE (>= not >)."""
        result = infer_affect(cognitive_dissonance=0.30, temperature=0.47)
        assert result == AffectState.DISSONANCE

    def test_uncertainty_threshold_is_exclusive_at_boundary(self):
        """T exactly at uncertainty_threshold (0.45) should NOT fire uncertainty."""
        result = infer_affect(cognitive_dissonance=0.00, temperature=0.45)
        # T=0.45 is NOT < 0.45, and NOT > 0.50 → NEUTRAL
        assert result == AffectState.NEUTRAL
