"""
test_qchem_env.py
=================
Smoke tests for the quantum_chemistry environment check.

These tests verify that:
  1. env_check imports without error.
  2. EnvReport and PackageStatus dataclasses are well-formed.
  3. check_environment() returns an EnvReport with the expected packages.
  4. Each package entry has the required fields populated.
  5. The summary string contains all expected package names.
  6. When all packages are present and version-compliant, report.ok is True.
     (Skipped gracefully when packages are not installed in the test env.)

Run with:
    pytest src-python/tests/test_qchem_env.py -v
"""

import importlib
import sys

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

QPKGS = ["qiskit_nature", "qiskit_aer", "pyscf"]


def _all_installed() -> bool:
    for pkg in QPKGS:
        try:
            importlib.import_module(pkg)
        except ImportError:
            return False
    return True


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_env_check_module_importable():
    """env_check must import without raising."""
    import quantum_chemistry.env_check as ec  # noqa: F401
    assert ec is not None


def test_env_report_dataclass_fields():
    """EnvReport must expose .ok, .packages, .summary()."""
    from quantum_chemistry.env_check import EnvReport, PackageStatus

    ps = PackageStatus(
        name="test-pkg",
        required="1.0.0",
        installed="1.2.0",
        ok=True,
        message="",
    )
    report = EnvReport(packages=[ps])
    assert report.ok is True
    summary = report.summary()
    assert "test-pkg" in summary
    assert "PASS" in summary


def test_env_report_fail_when_package_missing():
    """EnvReport.ok must be False when any package has ok=False."""
    from quantum_chemistry.env_check import EnvReport, PackageStatus

    ps = PackageStatus(
        name="missing-pkg",
        required="0.7.0",
        installed=None,
        ok=False,
        message="ImportError: No module named 'missing-pkg'",
    )
    report = EnvReport(packages=[ps])
    assert report.ok is False
    summary = report.summary()
    assert "FAIL" in summary
    assert "missing-pkg" in summary


def test_check_environment_returns_three_packages():
    """check_environment() must return exactly 3 package statuses."""
    from quantum_chemistry.env_check import check_environment

    report = check_environment()
    assert len(report.packages) == 3


def test_check_environment_package_names():
    """Each of the three required packages must appear in the report."""
    from quantum_chemistry.env_check import check_environment

    report = check_environment()
    names = {p.name for p in report.packages}
    assert "qiskit-nature" in names
    assert "qiskit-aer" in names
    assert "pyscf" in names


def test_check_environment_summary_contains_all_packages():
    """Summary string must mention all three package names."""
    from quantum_chemistry.env_check import check_environment

    report = check_environment()
    summary = report.summary()
    for name in ("qiskit-nature", "qiskit-aer", "pyscf"):
        assert name in summary, f"'{name}' missing from summary"


@pytest.mark.skipif(
    not _all_installed(),
    reason="Quantum chemistry packages not installed in this environment — skipping live check.",
)
def test_full_environment_passes_when_packages_installed():
    """When all packages are installed and version-compliant, report.ok must be True."""
    from quantum_chemistry.env_check import check_environment

    report = check_environment()
    failed = [p for p in report.packages if not p.ok]
    assert not failed, (
        f"Environment check failed for: {[p.name for p in failed]}\n{report.summary()}"
    )


@pytest.mark.skipif(
    not _all_installed(),
    reason="Quantum chemistry packages not installed — skipping AerSimulator check.",
)
def test_aer_backend_available_when_installed():
    """AerSimulator must be available when qiskit-aer is installed."""
    from quantum_chemistry.env_check import check_environment

    report = check_environment()
    assert report.aer_backend_available, "AerSimulator backend not available despite qiskit-aer being installed."


@pytest.mark.skipif(
    not _all_installed(),
    reason="Quantum chemistry packages not installed — skipping PySCF driver check.",
)
def test_pyscf_driver_available_when_installed():
    """PySCFDriver must be importable when qiskit-nature + pyscf are installed."""
    from quantum_chemistry.env_check import check_environment

    report = check_environment()
    assert report.pyscf_driver_available, "PySCFDriver not available despite packages being installed."
