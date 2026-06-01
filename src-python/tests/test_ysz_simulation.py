"""
test_ysz_simulation.py
======================
Tests for the YSZ quantum chemistry simulation driver.

Strategy
--------
- Tests that do NOT require quantum chemistry packages run unconditionally.
  They validate data structures, schema correctness, and constant values.
- Tests that require pyscf / qiskit-nature / qiskit-aer are skipped
  gracefully when those packages are absent (same pattern as test_qchem_env).

Run with:
    pytest src-python/tests/test_ysz_simulation.py -v
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
    reason="Quantum chemistry packages not installed — skipping live simulation tests.",
)


# ---------------------------------------------------------------------------
# Structural / schema tests (no packages required)
# ---------------------------------------------------------------------------


def test_ysz_module_importable():
    """ysz module must import without error."""
    import quantum_chemistry.targets.ysz as ysz  # noqa: F401
    assert ysz is not None


def test_ysz_atom_list_correct_structure():
    """YSZ_ATOMS must contain 5 entries, each (symbol, (x,y,z))."""
    from quantum_chemistry.targets.ysz import YSZ_ATOMS
    assert len(YSZ_ATOMS) == 5
    for sym, coords in YSZ_ATOMS:
        assert isinstance(sym, str)
        assert len(coords) == 3


def test_ysz_atom_list_contains_correct_elements():
    """YSZ cluster must contain Zr, Y, and O atoms."""
    from quantum_chemistry.targets.ysz import YSZ_ATOMS
    symbols = {sym for sym, _ in YSZ_ATOMS}
    assert "Zr" in symbols
    assert "Y" in symbols
    assert "O" in symbols


def test_ysz_lattice_parameters():
    """Cubic YSZ lattice parameter must be 5.1225 Å (RRUFF #R060718)."""
    from quantum_chemistry.targets.ysz import YSZ_LATTICE_A, YSZ_LATTICE_B, YSZ_LATTICE_C
    assert YSZ_LATTICE_A == pytest.approx(5.1225, abs=1e-4)
    assert YSZ_LATTICE_B == pytest.approx(5.1225, abs=1e-4)
    assert YSZ_LATTICE_C == pytest.approx(5.1225, abs=1e-4)


def test_ysz_active_space_constants():
    """Active space must be 6 electrons in 6 orbitals."""
    from quantum_chemistry.targets.ysz import ACTIVE_ELECTRONS, ACTIVE_ORBITALS
    assert ACTIVE_ELECTRONS == 6
    assert ACTIVE_ORBITALS == 6


def test_ysz_physical_constants_sane():
    """Physical constants must be within 1 ppm of CODATA 2018 values."""
    from quantum_chemistry.targets.ysz import HARTREE_TO_EV, HARTREE_TO_KCAL_MOL
    assert HARTREE_TO_EV == pytest.approx(27.211386245988, rel=1e-6)
    assert HARTREE_TO_KCAL_MOL == pytest.approx(627.5094740631, rel=1e-6)


def test_ysz_simulation_result_dataclass_defaults():
    """YSZSimulationResult must instantiate with correct defaults."""
    from quantum_chemistry.targets.ysz import YSZSimulationResult
    r = YSZSimulationResult()
    assert r.material == "YSZ"
    assert r.formula == "Zr3Y2O8"
    assert r.canon_ref == "C65"
    assert r.rruff_ref == "R060718"
    assert r.vqe_ansatz == "UCCSD"
    assert r.vqe_optimizer == "SLSQP"
    assert len(r.known_limitations) >= 4


def test_ysz_to_canon_c65_dict_keys():
    """to_canon_c65_dict() must include all required Canon C65 keys."""
    from quantum_chemistry.targets.ysz import YSZSimulationResult
    r = YSZSimulationResult()
    d = r.to_canon_c65_dict()
    required_keys = {
        "material", "formula", "canon_ref", "rruff_ref",
        "ground_state_energy_hartree", "ground_state_energy_ev",
        "ground_state_energy_kcal_mol", "vqe_converged",
        "vqe_ansatz", "vqe_optimizer",
        "phonon_modes", "n_imaginary_modes",
        "epsilon_inf", "epsilon_0",
        "dft_reference_ev", "tolerance_kcal_mol",
        "within_tolerance", "delta_kcal_mol",
        "simulation_time_s", "simulator_backend", "known_limitations",
    }
    missing = required_keys - d.keys()
    assert not missing, f"Missing Canon C65 keys: {missing}"


def test_results_json_schema_stub_valid():
    """results/ysz_ground_state.json must be valid JSON with expected top-level keys."""
    json_path = Path("results/ysz_ground_state.json")
    assert json_path.exists(), "results/ysz_ground_state.json not found"
    with json_path.open() as fh:
        data = json.load(fh)
    assert data["material"] == "YSZ"
    assert data["canon_ref"] == "C65"
    assert data["rruff_ref"] == "R060718"
    assert "ground_state_energy_ev" in data
    assert "phonon_modes" in data


# ---------------------------------------------------------------------------
# Live simulation tests (skipped when packages absent)
# ---------------------------------------------------------------------------

@QPKGS_MARK
def test_build_ysz_mole_succeeds():
    """build_ysz_mole() must return a valid PySCF Mole with 5 atoms."""
    from quantum_chemistry.targets.ysz import build_ysz_mole
    mol = build_ysz_mole()
    assert mol.natm == 5
    assert mol.nao_nr() > 0


@QPKGS_MARK
def test_full_simulation_runs_end_to_end(tmp_path):
    """
    Full simulation pipeline must run without error and produce a valid
    JSON output. Phonons and dielectric skipped for CI speed.
    """
    from quantum_chemistry.targets.ysz import run_ysz_simulation
    out = str(tmp_path / "ysz_test.json")
    result = run_ysz_simulation(
        output_path=out,
        skip_phonons=True,
        skip_dielectric=True,
    )
    assert result.vqe_converged
    assert result.ground_state_energy_ev < 0  # bound state must be negative
    assert Path(out).exists()
    with open(out) as fh:
        data = json.load(fh)
    assert data["canon_ref"] == "C65"
    assert data["vqe_converged"] is True
