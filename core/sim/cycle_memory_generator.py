"""CycleMemoryGenerator — realistic cycle_memory trajectories for simulate_canon_comparison.

Canon refs: C30 (No silent failures)
Issue: #257
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Iterator


class TrajectoryType(str, Enum):
    LINEAR = "linear"        # Steady ramp — best-case baseline
    PLATEAU = "plateau"      # Fast rise then flat (research-executive)
    REGRESSION = "regression" # Dip mid-journey then recovery
    ERRATIC = "erratic"      # High variance — grief-reflective, trauma


@dataclass
class CycleMemoryGenerator:
    """Generate per-cycle memory values reflecting plausible human trajectories.

    Args:
        trajectory: One of LINEAR / PLATEAU / REGRESSION / ERRATIC.
        start: Initial memory value (0.0–1.0).
        target: Asymptotic ceiling memory value (0.0–1.0).
        total_cycles: Total number of cycles the simulation will run.
        tool_failure_rate: Probability [0.0, 1.0] that a cycle injects a
            tool-failure penalty (−0.05 to −0.15) regardless of trajectory.
        seed: Optional random seed for reproducibility.
    """

    trajectory: TrajectoryType = TrajectoryType.LINEAR
    start: float = 0.10
    target: float = 0.90
    total_cycles: int = 20
    tool_failure_rate: float = 0.05
    seed: int | None = None

    _rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(self) -> list[float]:
        """Return a list of `total_cycles` memory values."""
        values = list(self._base_trajectory())
        return [self._apply_tool_failure(v) for v in values]

    def iter_generate(self) -> Iterator[float]:
        """Yield memory values one cycle at a time (streaming variant)."""
        for v in self._base_trajectory():
            yield self._apply_tool_failure(v)

    # ------------------------------------------------------------------
    # Trajectory implementations
    # ------------------------------------------------------------------

    def _base_trajectory(self) -> Iterator[float]:
        n = self.total_cycles
        s, t = self.start, self.target
        rng = self._rng

        if self.trajectory == TrajectoryType.LINEAR:
            for i in range(n):
                yield s + (t - s) * (i / max(n - 1, 1))

        elif self.trajectory == TrajectoryType.PLATEAU:
            # Fast rise in first 40 % of cycles, then flat
            rise_cycles = max(1, int(n * 0.4))
            for i in range(n):
                if i < rise_cycles:
                    yield s + (t - s) * (i / rise_cycles)
                else:
                    yield t + rng.uniform(-0.02, 0.02)

        elif self.trajectory == TrajectoryType.REGRESSION:
            # Ramp up → dip at 50 % → recovery
            mid = n // 2
            dip_depth = 0.15
            for i in range(n):
                linear = s + (t - s) * (i / max(n - 1, 1))
                dip = dip_depth * _triangle_wave(i / n, peak=0.5)
                yield max(0.0, min(1.0, linear - dip))

        elif self.trajectory == TrajectoryType.ERRATIC:
            # Brownian-ish walk biased upward but with high noise
            current = s
            step_bias = (t - s) / n
            for _ in range(n):
                noise = rng.uniform(-0.12, 0.14)
                current = max(0.0, min(1.0, current + step_bias + noise))
                yield current

        else:
            raise ValueError(f"Unknown trajectory type: {self.trajectory}")

    def _apply_tool_failure(self, value: float) -> float:
        if self._rng.random() < self.tool_failure_rate:
            penalty = self._rng.uniform(0.05, 0.15)
            return max(0.0, value - penalty)
        return value


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _triangle_wave(x: float, peak: float = 0.5) -> float:
    """Return a triangle pulse centred at `peak` with amplitude 1.0."""
    if x < peak:
        return x / peak
    return max(0.0, 1.0 - (x - peak) / (1.0 - peak))


# ---------------------------------------------------------------------------
# Scenario presets — maps scenario tag → recommended trajectory
# ---------------------------------------------------------------------------

SCENARIO_PRESETS: dict[str, TrajectoryType] = {
    "grief-reflective": TrajectoryType.ERRATIC,
    "research-executive": TrajectoryType.PLATEAU,
    "creative-flow": TrajectoryType.LINEAR,
    "recovery-journey": TrajectoryType.REGRESSION,
    "baseline": TrajectoryType.LINEAR,
}


def trajectory_for_scenario(scenario: str) -> TrajectoryType:
    """Return the recommended TrajectoryType for a named scenario."""
    return SCENARIO_PRESETS.get(scenario, TrajectoryType.LINEAR)
