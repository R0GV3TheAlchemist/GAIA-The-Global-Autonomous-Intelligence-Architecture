"""
env_check.py
============
Runtime validation that the Qiskit Nature / Aer / PySCF environment
is correctly installed and meets GAIA-OS minimum version requirements.

Usage
-----
    python -m quantum_chemistry.env_check        # prints report to stdout
    from quantum_chemistry.env_check import check_environment
    report = check_environment()
    assert report.ok, report.summary()
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from packaging.version import Version

# Minimum version requirements (mirrors requirements.txt)
MIN_VERSIONS: Dict[str, Tuple[str, str]] = {
    # (import_name, min_version)
    "qiskit_nature": ("qiskit_nature", "0.7.0"),
    "qiskit_aer": ("qiskit_aer", "0.14.0"),
    "pyscf": ("pyscf", "2.4.0"),
}

# Display names for reporting
DISPLAY_NAMES: Dict[str, str] = {
    "qiskit_nature": "qiskit-nature",
    "qiskit_aer": "qiskit-aer",
    "pyscf": "pyscf",
}


@dataclass
class PackageStatus:
    name: str
    required: str
    installed: str | None
    ok: bool
    message: str


@dataclass
class EnvReport:
    packages: List[PackageStatus] = field(default_factory=list)
    python_version: str = field(default_factory=lambda: sys.version)
    aer_backend_available: bool = False
    pyscf_driver_available: bool = False

    @property
    def ok(self) -> bool:
        return all(p.ok for p in self.packages)

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "GAIA-OS Quantum Chemistry Environment Report",
            f"Python: {self.python_version.split()[0]}",
            "=" * 60,
        ]
        for p in self.packages:
            status = "✓" if p.ok else "✗"
            lines.append(f"  [{status}] {p.name:<20} required>={p.required}  installed={p.installed or 'MISSING'}")
            if not p.ok:
                lines.append(f"       → {p.message}")
        lines.append("-" * 60)
        lines.append(f"  AerSimulator backend : {'available' if self.aer_backend_available else 'NOT AVAILABLE'}")
        lines.append(f"  PySCF driver         : {'available' if self.pyscf_driver_available else 'NOT AVAILABLE'}")
        lines.append("=" * 60)
        overall = "PASS" if self.ok else "FAIL"
        lines.append(f"  Overall: {overall}")
        lines.append("=" * 60)
        return "\n".join(lines)


def _check_package(import_name: str, min_version: str) -> PackageStatus:
    display = DISPLAY_NAMES.get(import_name, import_name)
    try:
        mod = importlib.import_module(import_name)
        installed_str = getattr(mod, "__version__", None)
        if installed_str is None:
            # pyscf exposes version via pyscf.__version__
            installed_str = getattr(mod, "version", None) or "unknown"
        try:
            ok = Version(installed_str) >= Version(min_version)
            msg = "" if ok else f"version {installed_str} < required {min_version}"
        except Exception:
            ok = False
            msg = f"could not parse installed version '{installed_str}'"
        return PackageStatus(
            name=display,
            required=min_version,
            installed=installed_str,
            ok=ok,
            message=msg,
        )
    except ImportError as exc:
        return PackageStatus(
            name=display,
            required=min_version,
            installed=None,
            ok=False,
            message=f"ImportError: {exc}",
        )


def _check_aer_backend() -> bool:
    """Verify AerSimulator can be instantiated (statevector method)."""
    try:
        from qiskit_aer import AerSimulator  # type: ignore
        sim = AerSimulator(method="statevector")
        return sim is not None
    except Exception:
        return False


def _check_pyscf_driver() -> bool:
    """Verify the Qiskit Nature PySCF driver is importable."""
    try:
        from qiskit_nature.second_q.drivers import PySCFDriver  # type: ignore  # noqa: F401
        return True
    except Exception:
        return False


def check_environment() -> EnvReport:
    """Run all environment checks and return an EnvReport."""
    report = EnvReport()
    for import_name, (_, min_ver) in MIN_VERSIONS.items():
        report.packages.append(_check_package(import_name, min_ver))
    report.aer_backend_available = _check_aer_backend()
    report.pyscf_driver_available = _check_pyscf_driver()
    return report


if __name__ == "__main__":
    report = check_environment()
    print(report.summary())
    sys.exit(0 if report.ok else 1)
