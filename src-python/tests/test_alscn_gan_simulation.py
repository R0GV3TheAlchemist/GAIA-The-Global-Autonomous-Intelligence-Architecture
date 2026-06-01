"""
test_alscn_gan_simulation.py
============================
Tests for the AlScN/GaN heterostructure interface simulation driver.

Same skipif strategy as YSZ and BTS tests:
  - Structural / schema / physics-constant tests run unconditionally.
  - Live simulation tests skipped when quantum packages absent.

Run with:
    pytest src-python/tests/test_alscn_gan_simulation.py -v
"""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _qpkgs_installed() -> bool:
    for pkg in ("pyscf", "qiskit_nature", "qiskit_aer"):
        try:
            importlib.import_module(pkg)
        except ImportError:
            return False
    return True


QPKGS_MARK = pytest.mark.skipif(
    not _qpkgs_installed(),
    reason="Quantum chemistry packages not installed — skipping live AlScN/GaN tests.",
)


# ---------------------------------------------------------------------------
# Structural / schema / physics tests (no packages required)
# ---------------------------------------------------------------------------

def test_alscn_gan_module_importable():
    """alscn_gan module must import without error."""
    import quantum_chemistry.targets.alscn_gan as m  # noqa: F401
    assert m is not None


def test_interface_atoms_structure():
    """INTERFACE_ATOMS must have 9 entries, each (symbol, (x,y,z))."""
    from quantum_chemistry.targets.alscn_gan import INTERFACE_ATOMS
    assert len(INTERFACE_ATOMS) == 9
    for sym, coords in INTERFACE_ATOMS:
        assert isinstance(sym, str)
        assert len(coords) == 3


def test_interface_atoms_species():
    """Interface cluster must contain Al, Sc, N, and Ga atoms."""
    from quantum_chemistry.targets.alscn_gan import INTERFACE_ATOMS
    symbols = {sym for sym, _ in INTERFACE_ATOMS}
    assert "Al" in symbols
    assert "Sc" in symbols
    assert "N" in symbols
    assert "Ga" in symbols


def test_active_space_12e_12o():
    """Active space must be exactly 12 electrons in 12 orbitals."""
    from quantum_chemistry.targets.alscn_gan import ACTIVE_ELECTRONS, ACTIVE_ORBITALS
    assert ACTIVE_ELECTRONS == 12
    assert ACTIVE_ORBITALS == 12


def test_vqe_max_iter_500():
    """VQE iteration cap must be 500 (acceptance criteria requirement)."""
    from quantum_chemistry.targets.alscn_gan import VQE_MAX_ITER
    assert VQE_MAX_ITER == 500


def test_2deg_reference_range():
    """2DEG reference range must be 1e13 – 3e13 cm⁻² (HEMT literature)."""
    from quantum_chemistry.targets.alscn_gan import (
        SIGMA_2DEG_MIN_CM2, SIGMA_2DEG_MAX_CM2
    )
    assert SIGMA_2DEG_MIN_CM2 == pytest.approx(1e13, rel=1e-6)
    assert SIGMA_2DEG_MAX_CM2 == pytest.approx(3e13, rel=1e-6)


def test_2deg_density_calculation():
    """compute_2deg_density must produce a value in the expected HEMT range."""
    from quantum_chemistry.targets.alscn_gan import (
        compute_2deg_density, DELTA_P_TOTAL_C_M2,
        SIGMA_2DEG_MIN_CM2, SIGMA_2DEG_MAX_CM2,
    )
    sigma = compute_2deg_density(DELTA_P_TOTAL_C_M2)
    assert SIGMA_2DEG_MIN_CM2 <= sigma <= SIGMA_2DEG_MAX_CM2, (
        f"2DEG density {sigma:.2e} outside expected range "
        f"{SIGMA_2DEG_MIN_CM2:.1e}–{SIGMA_2DEG_MAX_CM2:.1e} cm⁻²"
    )


def test_band_offset_reference_positive():
    """Delta_Ec reference must be positive (type-II staggered alignment)."""
    from quantum_chemistry.targets.alscn_gan import DELTA_EC_REFERENCE_EV
    assert DELTA_EC_REFERENCE_EV > 0


def test_alscn_gan_result_defaults():
    """AlScNGaNSimulationResult must instantiate with correct identity defaults."""
    from quantum_chemistry.targets.alscn_gan import AlScNGaNSimulationResult
    r = AlScNGaNSimulationResult()
    assert r.material == "AlScN/GaN"
    assert r.formula == "Al0.7Sc0.3N/GaN"
    assert r.canon_ref == "C67"
    assert r.active_electrons == 12
    assert r.active_orbitals == 12
    assert r.vqe_ansatz == "UCCSD"
    assert len(r.known_limitations) >= 6


def test_alscn_gan_to_canon_c67_dict_keys():
    """to_canon_c67_dict() must include all required Canon C67 keys."""
    from quantum_chemistry.targets.alscn_gan import AlScNGaNSimulationResult
    r = AlScNGaNSimulationResult()
    d = r.to_canon_c67_dict()
    required_keys = {
        "material", "formula", "canon_ref",
        "ground_state_energy_hartree", "ground_state_energy_ev",
        "vqe_converged", "vqe_ansatz", "vqe_optimizer",
        "band_alignment", "polarisation_discontinuity",
        "sigma_2deg_cm2", "sigma_2deg_within_range",
        "within_tolerance", "delta_kcal_mol",
        "simulator_backend", "known_limitations",
    }
    missing = required_keys - d.keys()
    assert not missing, f"Missing Canon C67 keys: {missing}"


def test_alscn_gan_results_json_schema_stub_valid():
    """results/alscn_gan_interface.json must be valid JSON with expected keys."""
    json_path = Path("results/alscn_gan_interface.json")
    assert json_path.exists(), "results/alscn_gan_interface.json not found"
    with json_path.open() as fh:
        data = json.load(fh)
    assert data["material"] == "AlScN/GaN"
    assert data["canon_ref"] == "C67"
    assert data["active_electrons"] == 12
    assert data["active_orbitals"] == 12
    assert "band_alignment" in data
    assert "polarisation_discontinuity" in data
    pd = data["polarisation_discontinuity"]
    assert pd["delta_p_total_c_m2"] == pytest.approx(0.136, abs=0.01)


# ---------------------------------------------------------------------------
# Live simulation tests (skipped when packages absent)
# ---------------------------------------------------------------------------

@QPKGS_MARK
def test_build_alscn_gan_mole():
    """build_alscn_gan_mole() must return a valid 9-atom Mole."""
    from quantum_chemistry.targets.alscn_gan import build_alscn_gan_mole
    mol = build_alscn_gan_mole()
    assert mol.natm == 9
    assert mol.nao_nr() > 0


@QPKGS_MARK
def test_full_alscn_gan_simulation_runs(tmp_path):
    """
    Full AlScN/GaN pipeline must complete and produce Canon C67 JSON.
    Band alignment skipped for CI speed.
    """
    from quantum_chemistry.targets.alscn_gan import run_alscn_gan_simulation
    out = str(tmp_path / "alscn_gan_test.json")
    result = run_alscn_gan_simulation(
        output_path=out,
        skip_band_alignment=True,
    )
    assert result.ground_state_energy_ev < 0
    assert result.sigma_2deg_cm2 > 0
    assert result.vqe_iterations <= 500  # must respect the cap
    with open(out) as fh:
        data = json.load(fh)
    assert data["canon_ref"] == "C67"
