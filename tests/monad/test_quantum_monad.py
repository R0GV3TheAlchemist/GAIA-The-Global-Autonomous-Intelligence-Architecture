"""
Tests — QuantumMonad
Canon: quantum_substrate.md — Proton/Electron/Neutron traversal.
"""
import pytest
from unittest.mock import MagicMock
from core.monad.quantum import QuantumMonad


def make_ctx(phi=0.5, turn=0):
    ctx = MagicMock()
    ctx.coherence_phi = phi
    ctx.turn_number = turn
    ctx.session_id = "test-session"
    ctx.spectral = {}
    return ctx


class TestQuantumMonad:
    def setup_method(self):
        self.monad = QuantumMonad(monad_id="test.quantum")

    def test_electron_pole_at_low_phi(self):
        result = self.monad.harmonize(make_ctx(phi=0.10))
        assert result["traversal_pole"] == "electron"

    def test_proton_pole_at_high_phi(self):
        result = self.monad.harmonize(make_ctx(phi=0.80))
        assert result["traversal_pole"] == "proton"

    def test_neutron_pole_at_mid_phi(self):
        result = self.monad.harmonize(make_ctx(phi=0.50))
        assert result["traversal_pole"] == "neutron"

    def test_superposition_at_turn_0(self):
        result = self.monad.harmonize(make_ctx(phi=0.5, turn=0))
        assert result["collapse_state"] == "superposition"

    def test_collapsed_at_turn_6(self):
        result = self.monad.harmonize(make_ctx(phi=0.5, turn=6))
        assert result["collapse_state"] == "collapsed"

    def test_coherence_contribution_peaks_at_mid_phi(self):
        mid = self.monad.harmonize(make_ctx(phi=0.50))["coherence_contribution"]
        low = self.monad.harmonize(make_ctx(phi=0.10))["coherence_contribution"]
        high = self.monad.harmonize(make_ctx(phi=0.90))["coherence_contribution"]
        assert mid > low
        assert mid > high

    def test_never_returns_none(self):
        for phi in [0.0, 0.5, 1.0]:
            assert self.monad.harmonize(make_ctx(phi=phi)) is not None
