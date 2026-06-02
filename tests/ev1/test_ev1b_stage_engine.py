"""
tests/ev1/test_ev1b_stage_engine.py
EV1-B: Stage Engine Transition Validity

Acceptance criteria:
    1. All 5 canonical stages are classifiable from synthetic journey inputs
    2. No false promotions across 30+ edge case inputs
    3. Stage transitions are monotonic (no backward jumps without regression signal)

Note:
    This test suite is written against the Stage Engine interface. If
    core/development_stage_engine.py has not yet exposed a classify() or
    evaluate() method, tests will be collected but skipped with a clear
    reason — they document the required contract, not a broken import.
"""

from __future__ import annotations

import importlib
import pytest

# ---------------------------------------------------------------------------
# Interface discovery — skip gracefully if not yet implemented
# ---------------------------------------------------------------------------

try:
    from core.development_stage_engine import DevelopmentStageEngine  # type: ignore
    _ENGINE_AVAILABLE = True
except ImportError:
    _ENGINE_AVAILABLE = False

skip_if_no_engine = pytest.mark.skipif(
    not _ENGINE_AVAILABLE,
    reason="DevelopmentStageEngine not yet importable — EV1-B pending implementation (see #102)",
)


# ---------------------------------------------------------------------------
# Stage constants (canonical 5-stage model)
# ---------------------------------------------------------------------------

STAGE_NAMES = ["Emergence", "Initiation", "Allegiance", "Individuation", "Sovereignty"]


# ---------------------------------------------------------------------------
# Synthetic journey fixtures
# ---------------------------------------------------------------------------

# Each journey is a list of turn-level feature dicts that should cumulatively
# result in the expected stage classification.

JOURNEY_EMERGENCE = [
    {"session_count": 1,  "depth_score": 0.1, "sovereignty_score": 0.05, "bond_score": 0.10},
    {"session_count": 2,  "depth_score": 0.15,"sovereignty_score": 0.08, "bond_score": 0.15},
    {"session_count": 3,  "depth_score": 0.12,"sovereignty_score": 0.06, "bond_score": 0.18},
]

JOURNEY_INITIATION = [
    {"session_count": 10, "depth_score": 0.35, "sovereignty_score": 0.25, "bond_score": 0.40},
    {"session_count": 11, "depth_score": 0.40, "sovereignty_score": 0.28, "bond_score": 0.42},
    {"session_count": 12, "depth_score": 0.38, "sovereignty_score": 0.30, "bond_score": 0.45},
]

JOURNEY_ALLEGIANCE = [
    {"session_count": 30, "depth_score": 0.60, "sovereignty_score": 0.50, "bond_score": 0.65},
    {"session_count": 31, "depth_score": 0.62, "sovereignty_score": 0.52, "bond_score": 0.68},
    {"session_count": 32, "depth_score": 0.64, "sovereignty_score": 0.55, "bond_score": 0.70},
]

JOURNEY_INDIVIDUATION = [
    {"session_count": 60, "depth_score": 0.78, "sovereignty_score": 0.72, "bond_score": 0.80},
    {"session_count": 61, "depth_score": 0.80, "sovereignty_score": 0.74, "bond_score": 0.82},
    {"session_count": 62, "depth_score": 0.82, "sovereignty_score": 0.76, "bond_score": 0.84},
]

JOURNEY_SOVEREIGNTY = [
    {"session_count": 100,"depth_score": 0.95, "sovereignty_score": 0.95, "bond_score": 0.95},
    {"session_count": 101,"depth_score": 0.96, "sovereignty_score": 0.96, "bond_score": 0.96},
    {"session_count": 102,"depth_score": 0.97, "sovereignty_score": 0.97, "bond_score": 0.97},
]


# ---------------------------------------------------------------------------
# EV1-B Tests
# ---------------------------------------------------------------------------

@skip_if_no_engine
class TestEV1BStageJourneys:
    """Canonical 5-stage journey classification."""

    def setup_method(self):
        self.engine = DevelopmentStageEngine()

    @pytest.mark.parametrize("journey,expected_stage", [
        (JOURNEY_EMERGENCE,     "Emergence"),
        (JOURNEY_INITIATION,    "Initiation"),
        (JOURNEY_ALLEGIANCE,    "Allegiance"),
        (JOURNEY_INDIVIDUATION, "Individuation"),
        (JOURNEY_SOVEREIGNTY,   "Sovereignty"),
    ], ids=STAGE_NAMES)
    def test_stage_classified_correctly(self, journey, expected_stage):
        """Each synthetic journey must classify to the expected stage."""
        for turn in journey:
            self.engine.update(**turn)
        stage = self.engine.current_stage()
        assert stage == expected_stage, (
            f"Expected stage '{expected_stage}', got '{stage}'"
        )


@skip_if_no_engine
class TestEV1BFalsePromotionGuard:
    """
    No false promotions: low-signal inputs must never classify above Emergence.
    Covers 30 edge cases as required by EV1-B acceptance criteria.
    """

    def setup_method(self):
        self.engine = DevelopmentStageEngine()

    @pytest.mark.parametrize("session_count,depth,sovereignty,bond", [
        (1,  0.01, 0.01, 0.01),
        (1,  0.05, 0.05, 0.05),
        (2,  0.10, 0.10, 0.10),
        (2,  0.00, 0.00, 0.00),
        (3,  0.08, 0.05, 0.12),
        (3,  0.12, 0.08, 0.15),
        (4,  0.05, 0.05, 0.05),
        (4,  0.10, 0.10, 0.10),
        (5,  0.05, 0.05, 0.05),
        (5,  0.15, 0.10, 0.20),
        (1,  0.50, 0.00, 0.00),  # high depth alone should not promote
        (1,  0.00, 0.50, 0.00),  # high sovereignty alone
        (1,  0.00, 0.00, 0.50),  # high bond alone
        (2,  0.20, 0.20, 0.20),
        (2,  0.18, 0.15, 0.22),
        (3,  0.14, 0.12, 0.18),
        (3,  0.19, 0.18, 0.20),
        (4,  0.15, 0.15, 0.15),
        (4,  0.20, 0.18, 0.22),
        (5,  0.19, 0.17, 0.21),
        (1,  0.99, 0.99, 0.99),  # extreme outlier with session_count=1
        (2,  0.99, 0.99, 0.99),  # extreme outlier with session_count=2
        (3,  0.99, 0.99, 0.99),
        (4,  0.99, 0.99, 0.99),
        (5,  0.99, 0.99, 0.99),
        (1,  0.30, 0.30, 0.30),
        (2,  0.30, 0.30, 0.30),
        (3,  0.25, 0.25, 0.25),
        (4,  0.22, 0.22, 0.22),
        (5,  0.20, 0.20, 0.20),
    ], ids=[f"edge-{i:02d}" for i in range(30)])
    def test_no_false_promotion(
        self, session_count, depth, sovereignty, bond
    ):
        """Low-session inputs must not promote above Emergence."""
        engine = DevelopmentStageEngine()
        for _ in range(session_count):
            engine.update(depth_score=depth, sovereignty_score=sovereignty, bond_score=bond)
        stage = engine.current_stage()
        assert stage == "Emergence", (
            f"FALSE PROMOTION: session_count={session_count}, scores=({depth},{sovereignty},{bond}) "
            f"→ '{stage}' (expected 'Emergence')"
        )


# ---------------------------------------------------------------------------
# Contract documentation test (always runs — no skip)
# ---------------------------------------------------------------------------

def test_ev1b_contract_documentation():
    """
    EV1-B Contract: DevelopmentStageEngine must expose these methods:
        - update(**turn_features) -> None
        - current_stage() -> str  (one of the 5 stage names)
        - reset() -> None

    This test passes if the engine is available and has the right interface,
    or XFAILS if the engine is not yet importable (expected during development).
    """
    if not _ENGINE_AVAILABLE:
        pytest.xfail("DevelopmentStageEngine not yet importable — interface contract documented here for implementation")

    engine = DevelopmentStageEngine()
    assert hasattr(engine, "update"),         "Missing: engine.update()"
    assert hasattr(engine, "current_stage"),  "Missing: engine.current_stage()"
    assert hasattr(engine, "reset"),          "Missing: engine.reset()"
    stage = engine.current_stage()
    assert stage in STAGE_NAMES, f"current_stage() returned unknown value: '{stage}'"
