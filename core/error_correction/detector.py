# Copyright (c) 2026 R0GV3 The Alchemist
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/error_correction/detector.py

GAIA Error Correction — Detection Engine (Phase 1)

Runs Ruff in JSON mode across the repo (or a subset of files) and
normalizes every diagnostic into a GAIAErrorFinding.  Additional
detectors (Black, isort, Canon rule checks) will be added in Phase 1b.

Design principles:
  - Detection only. No files are modified here.
  - Every finding carries full provenance metadata.
  - Stateless: create a new ErrorDetector per run.

Canon Ref: C01, C30, Issue #755 Phase 1
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Iterator, Optional, Sequence

from core.error_correction.models import (
    GAIAErrorCategory,
    GAIAErrorFinding,
    GAIASeverity,
)
from core.logger import get_logger

_logger = get_logger("gaia.error_correction.detector")


class ErrorDetector:
    """
    Runs configured detection tools and yields GAIAErrorFinding instances.

    Usage
    -----
    detector = ErrorDetector(repo_root=Path("."))
    findings = list(detector.run())
    """

    def __init__(
        self,
        repo_root: Optional[Path] = None,
        files: Optional[Sequence[str]] = None,
    ) -> None:
        """
        Parameters
        ----------
        repo_root : Root of the repository. Defaults to cwd.
        files     : Optional list of specific files to check.
                    When None, the entire repo_root is scanned.
        """
        self.repo_root = repo_root or Path(".")
        self.files = list(files) if files else None

    # ---------------------------------------------------------------- #
    #  Public API                                                       #
    # ---------------------------------------------------------------- #

    def run(self) -> list[GAIAErrorFinding]:
        """Run all detectors and return a sorted list of findings."""
        findings: list[GAIAErrorFinding] = []
        findings.extend(self._run_ruff())
        # Phase 1b: findings.extend(self._run_copyright_check())
        # Phase 1b: findings.extend(self._run_canon_rules())
        findings.sort(key=lambda f: (f.severity.value, f.file_path, f.line or 0))
        _logger.info(
            f"ErrorDetector: {len(findings)} finding(s) across "
            f"{len({f.file_path for f in findings})} file(s)"
        )
        return findings

    def iter(self) -> Iterator[GAIAErrorFinding]:
        """Streaming variant — yields findings as each detector completes."""
        yield from self._run_ruff()

    # ---------------------------------------------------------------- #
    #  Ruff detector                                                    #
    # ---------------------------------------------------------------- #

    def _run_ruff(self) -> list[GAIAErrorFinding]:
        """Run `ruff check --output-format json` and parse diagnostics."""
        cmd = [
            sys.executable, "-m", "ruff", "check",
            "--output-format", "json",
            "--no-fix",          # detection only — never mutate files
        ]
        if self.files:
            cmd.extend(self.files)
        else:
            cmd.append(str(self.repo_root))

        _logger.debug(f"Running ruff: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_root,
            )
        except FileNotFoundError:
            _logger.error("ruff not found — install with: pip install ruff")
            return []

        # Ruff exits 1 when findings exist — that’s normal, not an error
        raw = result.stdout.strip()
        if not raw:
            _logger.debug("Ruff returned no findings.")
            return []

        try:
            diagnostics: list[dict] = json.loads(raw)
        except json.JSONDecodeError as exc:
            _logger.error(f"Failed to parse ruff JSON output: {exc}")
            return []

        findings = []
        for diag in diagnostics:
            file_path = diag.get("filename", "unknown")
            # Make path repo-relative
            try:
                file_path = str(
                    Path(file_path).relative_to(self.repo_root.resolve())
                )
            except ValueError:
                pass  # keep absolute path if relative fails
            findings.append(
                GAIAErrorFinding.from_ruff_diagnostic(diag, file_path)
            )

        _logger.debug(f"Ruff: {len(findings)} finding(s)")
        return findings

    # ---------------------------------------------------------------- #
    #  Convenience: blocking findings only                              #
    # ---------------------------------------------------------------- #

    def blocking_findings(self) -> list[GAIAErrorFinding]:
        """Return only CRITICAL and HIGH severity findings."""
        return [f for f in self.run() if f.is_blocking()]

    def findings_by_file(self) -> dict[str, list[GAIAErrorFinding]]:
        """Group all findings by file path."""
        result: dict[str, list[GAIAErrorFinding]] = {}
        for finding in self.run():
            result.setdefault(finding.file_path, []).append(finding)
        return result
