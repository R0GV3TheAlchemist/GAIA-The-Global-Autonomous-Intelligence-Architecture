"""Tests for phi_engine — Issue #262."""
from __future__ import annotations

import math
import pytest

from core.consciousness.phi_engine import (
    PhiEngine,
    PhiPacket,
    compute_phi,
    phi_from_layer_activations,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _uniform_matrix(n: int, w: float = 0.5) -> list[list[float]]:
    return [[w] * n for _ in range(n)]


def _identity_matrix(n: int) -> list[list[float]]:
    return [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]


def _zero_matrix(n: int) -> list[list[float]]:
    return [[0.0] * n for _ in range(n)]


# ---------------------------------------------------------------------------
# Return type
# ---------------------------------------------------------------------------

def test_returns_phi_packet() -> None:
    result = compute_phi(_uniform_matrix(4))
    assert isinstance(result, PhiPacket)


# ---------------------------------------------------------------------------
# Phi bounds
# ---------------------------------------------------------------------------

def test_phi_non_negative() -> None:
    for n in [2, 4, 6]:
        pkt = compute_phi(_uniform_matrix(n))
        assert pkt.phi >= 0.0, f"Negative Φ for n={n}"


def test_zero_matrix_phi_zero() -> None:
    pkt = compute_phi(_zero_matrix(4))
    assert pkt.phi == 0.0


def test_single_node_phi_zero() -> None:
    pkt = compute_phi([[0.5]])
    assert pkt.phi == 0.0


# ---------------------------------------------------------------------------
# MIP partition validity
# ---------------------------------------------------------------------------

def test_mip_partition_covers_all_nodes() -> None:
    n = 4
    pkt = compute_phi(_uniform_matrix(n))
    all_nodes = set(range(n))
    union = pkt.mip_partition[0] | pkt.mip_partition[1]
    assert union == all_nodes


def test_mip_partition_disjoint() -> None:
    pkt = compute_phi(_uniform_matrix(4))
    a, b = pkt.mip_partition
    assert a.isdisjoint(b)


# ---------------------------------------------------------------------------
# Regime detection
# ---------------------------------------------------------------------------

def test_regime_is_valid_string() -> None:
    valid = {'subcritical', 'near-critical', 'supercritical'}
    pkt = compute_phi(_uniform_matrix(6))
    assert pkt.regime in valid


def test_zero_matrix_subcritical() -> None:
    pkt = compute_phi(_zero_matrix(4))
    assert pkt.regime == 'subcritical'


# ---------------------------------------------------------------------------
# phi_from_layer_activations
# ---------------------------------------------------------------------------

def test_activation_helper_returns_packet() -> None:
    activations = [0.8, 0.6, 0.4, 0.9, 0.7, 0.5]
    pkt = phi_from_layer_activations(activations)
    assert isinstance(pkt, PhiPacket)
    assert pkt.phi >= 0.0


def test_activation_helper_n_nodes() -> None:
    activations = [0.5] * 8
    pkt = phi_from_layer_activations(activations)
    assert pkt.n_nodes == 8


# ---------------------------------------------------------------------------
# Correction fields
# ---------------------------------------------------------------------------

def test_raw_phi_and_correction_sum_to_phi() -> None:
    pkt = compute_phi(_uniform_matrix(4))
    assert math.isclose(pkt.raw_phi + pkt.correction_applied, pkt.phi, abs_tol=1e-5)


# ---------------------------------------------------------------------------
# No-correction mode
# ---------------------------------------------------------------------------

def test_no_thermal_correction() -> None:
    engine = PhiEngine(n_layers=4, thermal_correction=False)
    pkt = engine.compute(_uniform_matrix(4))
    assert pkt.correction_applied == 0.0
    assert pkt.phi == pkt.raw_phi
