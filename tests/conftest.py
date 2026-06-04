"""
tests/conftest.py
Pytest fixtures for the root-level GAIA-OS test suite.

Covers: test_synergy_engine.py, test_sovereign_memory.py, and any
future tests that live in tests/ (repo root).

All fixture kwargs are built against the REAL SynergyEngine.compute()
signature from core/synergy_engine.py — verified June 4 2026.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# ── Path guard ──────────────────────────────────────────────────────────────────
_TESTS_DIR  = Path(__file__).parent.resolve()
_REPO_ROOT  = _TESTS_DIR.parent
_SRC_PYTHON = _REPO_ROOT / "src-python"

for _p in (str(_REPO_ROOT), str(_SRC_PYTHON)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# Suppress sentence-transformers blob-path warnings in CI.
# vec_search gracefully falls back to time-order when embeddings are off.
if not os.environ.get("GAIA_EMBED_MODEL"):
    os.environ["GAIA_EMBED_MODEL"] = "none"


# ── SynergyEngine fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def engine():
    """Fresh SynergyEngine instance for each test."""
    from core.synergy_engine import SynergyEngine
    return SynergyEngine()


@pytest.fixture
def blank_state():
    """Clean SynergyState via the canonical factory."""
    from core.synergy_engine import blank_synergy_state
    return blank_synergy_state()


@pytest.fixture
def nascent_kwargs():
    """
    Full kwargs for SynergyEngine.compute() producing a LOW-synergy
    (nascent) reading.  Every parameter name matches the real signature.

    Target scores per dimension:
      body: dominant_hz=174 (score 0.0) + schumann=False + low phi    -> ~0.15
      mind: low layer_phi, high conflict_density, high shadow         -> ~0.15
      soul: unconscious (0.15) + fire + high fluidity (disorder)      -> ~0.20
      arc:  divergence (0.15) + mc1 (0.0) + nascent att (0.30)       -> ~0.12
      bond: bond_depth=5, gentle_boundary (0.20), unsettled (0.20)    -> ~0.13
    Expected synergy_factor ≈ 0.15 — well below 0.35 threshold.
    """
    return {
        # Body
        "dominant_hz":        174.0,
        "schumann_aligned":   False,
        "noosphere_health":   0.10,
        "coherence_phi":      0.10,
        # Mind
        "layer_phi":          0.10,
        "phi_rolling_avg":    0.10,
        "conflict_density":   0.90,
        "shadow_activations": 5,
        "codex_stage":        0,
        # Soul
        "individuation_phase": "unconscious",
        "element":             "fire",
        "fluidity_score":      0.90,
        # Arc
        "love_arc_stage":     "divergence",
        "arc_output_vector":  0.0,
        "mc_stage":           "mc1",
        "attachment_phase":   "nascent",
        # Bond
        "bond_depth":         5.0,
        "dependency_signal":  "gentle_boundary",
        "settling_phase":     "unsettled",
        "crystallisation_pct": 0.0,
    }


@pytest.fixture
def integrated_kwargs():
    """
    Full kwargs for SynergyEngine.compute() producing a HIGH-synergy
    (integrated) reading.  Every parameter name matches the real signature.

    Target scores per dimension:
      body: dominant_hz=963 (score 1.0) + schumann=True + high phi    -> ~0.95
      mind: high layer_phi, low conflict, no shadow, high codex       -> ~0.90
      soul: self (0.85) + light + low fluidity (coherent)             -> ~0.85
      arc:  transcendence (0.95) + mc7 (1.0) + integrated att (0.90) -> ~0.95
      bond: bond_depth=95, healthy (1.0), settled (0.90)             -> ~0.93
    Expected synergy_factor ≈ 0.92 — well above 0.70 threshold.
    """
    return {
        # Body
        "dominant_hz":        963.0,
        "schumann_aligned":   True,
        "noosphere_health":   0.95,
        "coherence_phi":      0.95,
        # Mind
        "layer_phi":          0.90,
        "phi_rolling_avg":    0.90,
        "conflict_density":   0.05,
        "shadow_activations": 0,
        "codex_stage":        12,
        # Soul
        "individuation_phase": "self",
        "element":             "light",
        "fluidity_score":      0.05,
        # Arc
        "love_arc_stage":     "transcendence",
        "arc_output_vector":  1.0,
        "mc_stage":           "mc7",
        "attachment_phase":   "integrated",
        # Bond
        "bond_depth":         95.0,
        "dependency_signal":  "healthy",
        "settling_phase":     "settled",
        "crystallisation_pct": 100.0,
    }
