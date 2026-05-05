"""GAIA-OS Stage Engine — Transition Rules

Contains the threshold tables and evaluation logic for forward transitions
and regression detection per the Stage Engine spec (Issue #63).
"""

from __future__ import annotations

from .types import (
    MarkerScores,
    TRANSITION_WINDOWS,
    FORWARD_MARKERS_REQUIRED,
    REGRESSION_MARKERS_REQUIRED,
)

# ─────────────────────────────────────────────
# FORWARD TRANSITION THRESHOLDS
# Keyed by (from_stage, to_stage): {marker_name: min_score}
# ─────────────────────────────────────────────

FORWARD_THRESHOLDS: dict[tuple[int, int], dict[str, float]] = {
    (1, 2): {
        "journaling_depth": 35.0,
        "hrv_coherence": 40.0,
        "goal_completion_rate": 25.0,
        "emotional_arc_stability": 30.0,
        "decision_entropy": 30.0,
        "focus_session_length_min": 35.0,
    },
    (2, 3): {
        "journaling_depth": 50.0,
        "goal_completion_rate": 40.0,
        "hrv_coherence": 45.0,
        "emotional_arc_stability": 40.0,
        "decision_entropy": 40.0,
        "focus_session_length_min": 45.0,
    },
    (3, 4): {
        "goal_completion_rate": 60.0,
        "hrv_coherence": 55.0,
        "journaling_depth": 60.0,
        "emotional_arc_stability": 55.0,
        "decision_entropy": 55.0,
        "focus_session_length_min": 55.0,
    },
    (4, 5): {
        "goal_completion_rate": 70.0,
        "hrv_coherence": 60.0,
        "emotional_arc_stability": 65.0,
        "decision_entropy": 60.0,
        "journaling_depth": 65.0,
        "focus_session_length_min": 60.0,
    },
}


def markers_met_for_transition(
    scores: MarkerScores,
    from_stage: int,
    to_stage: int,
) -> list[str]:
    """
    Returns a list of marker names that meet the forward transition thresholds.
    An empty list means no marker qualifies for this transition pair.
    """
    thresholds = FORWARD_THRESHOLDS.get((from_stage, to_stage), {})
    scores_dict = scores.to_dict()
    met = [
        marker
        for marker, threshold in thresholds.items()
        if scores_dict.get(marker, 0.0) >= threshold
    ]
    return met


def check_forward_transition(
    scores: MarkerScores,
    from_stage: int,
    days_window_met: int,
) -> tuple[bool, list[str]]:
    """
    Evaluate whether a forward transition (from_stage → from_stage+1) should fire.

    Args:
        scores:          Current marker scores.
        from_stage:      Current stage number.
        days_window_met: Number of consecutive days the marker set has been
                         sustained at or above threshold.

    Returns:
        (should_transition, markers_met)
    """
    to_stage = from_stage + 1
    if to_stage > 5:
        return False, []
    required_window = TRANSITION_WINDOWS.get((from_stage, to_stage), 999)
    if days_window_met < required_window:
        return False, []
    met = markers_met_for_transition(scores, from_stage, to_stage)
    return len(met) >= FORWARD_MARKERS_REQUIRED, met


def check_regression(
    scores: MarkerScores,
    current_stage: int,
    days_regression_window: int,
) -> tuple[bool, list[str]]:
    """
    Evaluate whether a regression (current_stage → current_stage-1) should fire.

    Regression fires when 5 of 6 prior-stage markers are met for 14+ days.
    Prior-stage = the stage the user was in before the current one.

    Args:
        scores:                Current marker scores.
        current_stage:         Current stage number.
        days_regression_window: Consecutive days prior-stage pattern has held.

    Returns:
        (should_regress, prior_stage_markers_met)
    """
    prior_stage = current_stage - 1
    if prior_stage < 1:
        return False, []
    if days_regression_window < 14:
        return False, []
    # Use the prior → current thresholds inverted: check which markers have
    # dropped BACK to the prior-stage threshold range.
    prior_thresholds = FORWARD_THRESHOLDS.get((prior_stage, current_stage), {})
    scores_dict = scores.to_dict()
    # A marker is "regression-active" if it falls BELOW the forward threshold
    # that was required to enter the current stage.
    regressed_markers = [
        marker
        for marker, threshold in prior_thresholds.items()
        if scores_dict.get(marker, 0.0) < threshold
    ]
    return len(regressed_markers) >= REGRESSION_MARKERS_REQUIRED, regressed_markers
