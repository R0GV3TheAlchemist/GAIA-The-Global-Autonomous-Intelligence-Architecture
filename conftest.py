"""
conftest.py  (repo root)

Self-healing sys.path guard.

Ensures src-python/ is always on sys.path before pytest attempts to import
any test module — regardless of whether pytest.ini, pyproject.toml, or
neither is supplying a pythonpath setting.  This makes the test suite
robust to the pytest.ini-vs-pyproject.toml precedence trap that previously
caused 9 ModuleNotFoundError failures during CI collection.

Safe to leave in place permanently.  The insert is a no-op if src-python/
is already on sys.path (e.g. because PYTHONPATH is set in CI or because
pyproject.toml pythonpath is active).
"""

from __future__ import annotations

import sys
from pathlib import Path

# ── Self-healing path injection ───────────────────────────────────────────────
_REPO_ROOT = Path(__file__).parent.resolve()
_SRC_PYTHON = _REPO_ROOT / "src-python"
_REPO_ROOT_STR = str(_REPO_ROOT)
_SRC_PYTHON_STR = str(_SRC_PYTHON)

if _SRC_PYTHON_STR not in sys.path:
    sys.path.insert(0, _SRC_PYTHON_STR)

if _REPO_ROOT_STR not in sys.path:
    sys.path.insert(0, _REPO_ROOT_STR)


# ── Debug hook — printed once per CI run ─────────────────────────────────────
def pytest_configure(config):
    """Emit active pythonpath at the start of every pytest session."""
    print(
        f"\n[conftest] sys.path includes:"
        f"\n  repo root  : {_REPO_ROOT_STR}"
        f"\n  src-python : {_SRC_PYTHON_STR}"
        f"\n  already present: {_SRC_PYTHON_STR in sys.path}"
    )
