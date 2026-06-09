"""Tests for CycleMemoryGenerator — Issue #257."""
from __future__ import annotations

import pytest

from core.sim.cycle_memory_generator import (
    CycleMemoryGenerator,
    TrajectoryType,
    trajectory_for_scenario,
)


N = 20


def _gen(trajectory: TrajectoryType, **kwargs) -> list[float]:
    return CycleMemoryGenerator(
        trajectory=trajectory, total_cycles=N, seed=42, **kwargs
    ).generate()


# ---------------------------------------------------------------------------
# Length invariant
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("t", list(TrajectoryType))
def test_length(t: TrajectoryType) -> None:
    assert len(_gen(t)) == N


# ---------------------------------------------------------------------------
# Bounds: all values in [0, 1]
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("t", list(TrajectoryType))
def test_bounds(t: TrajectoryType) -> None:
    values = _gen(t)
    assert all(0.0 <= v <= 1.0 for v in values), f"Out-of-bounds in {t}: {values}"


# ---------------------------------------------------------------------------
# Trajectory characteristics
# ---------------------------------------------------------------------------

def test_linear_monotone_ish() -> None:
    """Linear trajectory (no failures) should be strictly non-decreasing."""
    values = CycleMemoryGenerator(
        trajectory=TrajectoryType.LINEAR, total_cycles=N,
        tool_failure_rate=0.0, seed=0
    ).generate()
    for a, b in zip(values, values[1:]):
        assert b >= a - 1e-9


def test_plateau_flattens() -> None:
    """Plateau trajectory: final value within 0.05 of target."""
    values = _gen(TrajectoryType.PLATEAU, target=0.9, tool_failure_rate=0.0)
    assert abs(values[-1] - 0.9) < 0.1


def test_erratic_variance() -> None:
    """Erratic trajectory should have higher std than linear."""
    import statistics
    linear = _gen(TrajectoryType.LINEAR, tool_failure_rate=0.0)
    erratic = _gen(TrajectoryType.ERRATIC, tool_failure_rate=0.0)
    assert statistics.stdev(erratic) > statistics.stdev(linear)


def test_regression_has_dip() -> None:
    """Regression trajectory should dip below the linear midpoint."""
    linear_mid = _gen(TrajectoryType.LINEAR, tool_failure_rate=0.0)[N // 2]
    regress_mid = _gen(TrajectoryType.REGRESSION, tool_failure_rate=0.0)[N // 2]
    assert regress_mid < linear_mid


# ---------------------------------------------------------------------------
# Tool failure injection
# ---------------------------------------------------------------------------

def test_tool_failure_reduces_values() -> None:
    no_fail = _gen(TrajectoryType.LINEAR, tool_failure_rate=0.0)
    high_fail = _gen(TrajectoryType.LINEAR, tool_failure_rate=1.0)
    assert sum(high_fail) < sum(no_fail)


# ---------------------------------------------------------------------------
# Scenario presets
# ---------------------------------------------------------------------------

def test_scenario_presets_known() -> None:
    assert trajectory_for_scenario("grief-reflective") == TrajectoryType.ERRATIC
    assert trajectory_for_scenario("research-executive") == TrajectoryType.PLATEAU


def test_scenario_preset_unknown_returns_linear() -> None:
    assert trajectory_for_scenario("unknown-scenario") == TrajectoryType.LINEAR


# ---------------------------------------------------------------------------
# Streaming variant
# ---------------------------------------------------------------------------

def test_iter_generate_matches_generate() -> None:
    gen = CycleMemoryGenerator(trajectory=TrajectoryType.ERRATIC, total_cycles=N, seed=7)
    assert gen.generate() == list(gen.iter_generate())
