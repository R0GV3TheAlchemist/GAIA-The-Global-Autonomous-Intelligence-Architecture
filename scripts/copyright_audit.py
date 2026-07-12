#!/usr/bin/env python3
"""
copyright_audit.py
------------------
GAIA Copyright & License Header Audit Tool

Scans every source file in the repository for the presence of a
copyright/license header and writes a detailed report to:
  - stdout (summary table)
  - reports/copyright_audit_report.txt  (full list)
  - reports/copyright_audit_missing.txt (missing-header files only)

Copyright (c) 2026 R0GV3 The Alchemist — GAIA Project
Licensed under the GAIA Sovereign License (see LICENSE.md)
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone
from typing import NamedTuple

# ─── Configuration ────────────────────────────────────────────────────────────

# File extensions to audit
AUDITED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".sol", ".yaml", ".yml", ".toml",
    ".md", ".rst", ".txt",
    ".sh", ".bash",
    ".json",
    ".html", ".css", ".scss",
}

# Directories to skip entirely
SKIP_DIRS = {
    ".git", "__pycache__", "node_modules", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "dist", "build", "eggs",
    ".eggs", "*.egg-info", ".tox", ".nox",
}

# Patterns that constitute a valid copyright notice (case-insensitive)
COPYRIGHT_PATTERNS = [
    r"copyright",
    r"©",
    r"\(c\)\s+\d{4}",
    r"spdx-license-identifier",
    r"licensed under",
    r"all rights reserved",
    r"gaia sovereign license",
    r"r0gv3",
    r"the alchemist",
]

COPYRIGHT_RE = re.compile(
    "|".join(COPYRIGHT_PATTERNS),
    re.IGNORECASE,
)

# How many lines from the top of a file to check
HEADER_SCAN_LINES = 30

# ─── Data types ───────────────────────────────────────────────────────────────

class FileAudit(NamedTuple):
    path: str
    extension: str
    size_bytes: int
    has_header: bool
    header_snippet: str   # first matching line (or empty)
    skip_reason: str      # non-empty if file was skipped


# ─── Core logic ───────────────────────────────────────────────────────────────

def should_skip_dir(dirname: str) -> bool:
    return dirname in SKIP_DIRS or dirname.endswith(".egg-info")


def audit_file(filepath: Path) -> FileAudit:
    ext = filepath.suffix.lower()
    size = filepath.stat().st_size

    if size == 0:
        return FileAudit(
            path=str(filepath),
            extension=ext,
            size_bytes=0,
            has_header=False,
            header_snippet="",
            skip_reason="empty file",
        )

    # Binary-sniff: try reading as UTF-8; skip if it fails
    try:
        with filepath.open("r", encoding="utf-8", errors="strict") as fh:
            lines = []
            for i, line in enumerate(fh):
                if i >= HEADER_SCAN_LINES:
                    break
                lines.append(line)
    except (UnicodeDecodeError, PermissionError) as exc:
        return FileAudit(
            path=str(filepath),
            extension=ext,
            size_bytes=size,
            has_header=False,
            header_snippet="",
            skip_reason=f"unreadable ({exc.__class__.__name__})",
        )

    header_text = "".join(lines)
    match = COPYRIGHT_RE.search(header_text)
    snippet = ""
    if match:
        # Grab the full line that matched
        start = header_text.rfind("\n", 0, match.start()) + 1
        end = header_text.find("\n", match.end())
        snippet = header_text[start: end if end != -1 else None].strip()[:120]

    return FileAudit(
        path=str(filepath),
        extension=ext,
        size_bytes=size,
        has_header=bool(match),
        header_snippet=snippet,
        skip_reason="",
    )


def walk_repo(root: Path) -> list[FileAudit]:
    results: list[FileAudit] = []

    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in-place so os.walk doesn't descend into them
        dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

        for filename in filenames:
            filepath = Path(dirpath) / filename
            ext = filepath.suffix.lower()
            if ext not in AUDITED_EXTENSIONS:
                continue
            results.append(audit_file(filepath))

    return results


# ─── Reporting ────────────────────────────────────────────────────────────────

def write_report(results: list[FileAudit], root: Path, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)

    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    audited   = [r for r in results if not r.skip_reason]
    skipped   = [r for r in results if r.skip_reason]
    has_hdr   = [r for r in audited if r.has_header]
    missing   = [r for r in audited if not r.has_header]

    total = len(audited)
    pct   = (len(has_hdr) / total * 100) if total else 0.0

    # ── Stats by extension ───────────────────────────────────────────────────
    ext_stats: dict[str, dict] = {}
    for r in audited:
        s = ext_stats.setdefault(r.extension, {"total": 0, "ok": 0})
        s["total"] += 1
        if r.has_header:
            s["ok"] += 1

    # ── Full report ──────────────────────────────────────────────────────────
    full_path = report_dir / "copyright_audit_report.txt"
    with full_path.open("w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("  GAIA COPYRIGHT AUDIT REPORT\n")
        f.write(f"  Generated : {now_utc}\n")
        f.write(f"  Root      : {root.resolve()}\n")
        f.write("=" * 80 + "\n\n")

        f.write(f"Files audited  : {total}\n")
        f.write(f"Files skipped  : {len(skipped)}\n")
        f.write(f"With header    : {len(has_hdr)}  ({pct:.1f}%)\n")
        f.write(f"Missing header : {len(missing)}\n\n")

        f.write("─" * 60 + "\n")
        f.write("COVERAGE BY FILE TYPE\n")
        f.write("─" * 60 + "\n")
        for ext, s in sorted(ext_stats.items()):
            p = s["ok"] / s["total"] * 100 if s["total"] else 0
            f.write(f"  {ext or '(no ext)':<12}  {s['ok']:>4}/{s['total']:<4}  {p:5.1f}%\n")

        f.write("\n" + "─" * 60 + "\n")
        f.write("FILES WITH COPYRIGHT HEADER\n")
        f.write("─" * 60 + "\n")
        for r in sorted(has_hdr, key=lambda x: x.path):
            rel = os.path.relpath(r.path, root)
            f.write(f"  ✓  {rel}\n")
            if r.header_snippet:
                f.write(f"       → {r.header_snippet}\n")

        f.write("\n" + "─" * 60 + "\n")
        f.write("FILES MISSING COPYRIGHT HEADER\n")
        f.write("─" * 60 + "\n")
        for r in sorted(missing, key=lambda x: x.path):
            rel = os.path.relpath(r.path, root)
            f.write(f"  ✗  {rel}  ({r.size_bytes} bytes)\n")

        if skipped:
            f.write("\n" + "─" * 60 + "\n")
            f.write("SKIPPED FILES\n")
            f.write("─" * 60 + "\n")
            for r in sorted(skipped, key=lambda x: x.path):
                rel = os.path.relpath(r.path, root)
                f.write(f"  –  {rel}  [{r.skip_reason}]\n")

    # ── Missing-only report ──────────────────────────────────────────────────
    missing_path = report_dir / "copyright_audit_missing.txt"
    with missing_path.open("w", encoding="utf-8") as f:
        f.write(f"# GAIA Missing-Copyright Report — {now_utc}\n")
        f.write(f"# {len(missing)} file(s) need a copyright header\n\n")
        for r in sorted(missing, key=lambda x: x.path):
            rel = os.path.relpath(r.path, root)
            f.write(f"{rel}\n")

    # ── JSON machine-readable output ─────────────────────────────────────────
    json_path = report_dir / "copyright_audit.json"
    payload = {
        "generated_utc": now_utc,
        "root": str(root.resolve()),
        "summary": {
            "audited": total,
            "skipped": len(skipped),
            "with_header": len(has_hdr),
            "missing_header": len(missing),
            "coverage_pct": round(pct, 2),
        },
        "by_extension": {
            ext: {"total": s["total"], "ok": s["ok"],
                  "coverage_pct": round(s["ok"] / s["total"] * 100, 2)}
            for ext, s in sorted(ext_stats.items())
        },
        "missing": [
            {"path": os.path.relpath(r.path, root), "size_bytes": r.size_bytes}
            for r in sorted(missing, key=lambda x: x.path)
        ],
    }
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    return full_path, missing_path, json_path, payload


def print_summary(payload: dict) -> None:
    s = payload["summary"]
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║       GAIA COPYRIGHT AUDIT — SUMMARY             ║")
    print("╠══════════════════════════════════════════════════╣")
    print(f"║  Files audited  : {s['audited']:<31}║")
    print(f"║  With header    : {s['with_header']:<31}║")
    print(f"║  Missing header : {s['missing_header']:<31}║")
    print(f"║  Coverage       : {s['coverage_pct']:.1f}%{'':<26}║")
    print("╠══════════════════════════════════════════════════╣")
    print("║  Coverage by type:                               ║")
    for ext, data in payload["by_extension"].items():
        bar_len = int(data["coverage_pct"] / 5)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"║  {ext or '(none)':<9} {bar} {data['coverage_pct']:5.1f}%  ║")
    print("╚══════════════════════════════════════════════════╝")
    print()

    if payload["missing"]:
        print(f"⚠  {len(payload['missing'])} file(s) are missing a copyright header.")
        print("   See reports/copyright_audit_missing.txt for the full list.")
    else:
        print("✅  All audited files have a copyright header. Well done!")
    print()


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="GAIA Copyright Audit — scan source files for license headers.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository root to scan (default: current directory)",
    )
    parser.add_argument(
        "--report-dir",
        default="reports",
        help="Directory to write report files into (default: reports/)",
    )
    parser.add_argument(
        "--fail-on-missing",
        action="store_true",
        help="Exit with code 1 if any files are missing headers (useful for CI)",
    )
    parser.add_argument(
        "--extensions",
        nargs="*",
        help="Override audited extensions (e.g. .py .js .ts)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: {root} is not a directory.", file=sys.stderr)
        return 2

    report_dir = root / args.report_dir

    if args.extensions:
        global AUDITED_EXTENSIONS
        AUDITED_EXTENSIONS = {e if e.startswith(".") else f".{e}" for e in args.extensions}

    print(f"🔍  Scanning {root} …")
    results = walk_repo(root)

    full_path, missing_path, json_path, payload = write_report(results, root, report_dir)

    print_summary(payload)
    print(f"📄  Full report   → {full_path}")
    print(f"📄  Missing list  → {missing_path}")
    print(f"📄  JSON output   → {json_path}")
    print()

    if args.fail_on_missing and payload["summary"]["missing_header"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
