"""
quantum_chemistry
=================
GAIA-OS Quantum Chemistry Simulation layer.

Provides Qiskit Nature / PySCF-based molecular simulation for
Gaianite substrate materials (Canon C65-C67).

Submodules
----------
env_check   -- Runtime validation of Qiskit Nature / Aer / PySCF environment.
targets/    -- Per-material geometry and simulation drivers
               (ysz, bts, alscn_gan).
canon_mapper -- Maps simulation outputs to Gaianite canon schema.
validator    -- Cross-validates results against RRUFF / Mindat references.

Quick start
-----------
>>> from quantum_chemistry.env_check import check_environment
>>> report = check_environment()
>>> print(report.summary())
"""

from importlib.metadata import version, PackageNotFoundError

__all__ = ["env_check", "canon_mapper", "validator"]


def _pkg_version(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "not installed"


__versions__ = {
    "qiskit-nature": _pkg_version("qiskit-nature"),
    "qiskit-aer": _pkg_version("qiskit-aer"),
    "pyscf": _pkg_version("pyscf"),
}
