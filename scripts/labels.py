#!/usr/bin/env python3
"""
scripts/labels.py
=================
Bootstrap all GAIA project labels on GitHub.

Usage:
    export GITHUB_TOKEN=ghp_...
    python scripts/labels.py

Requires a PAT with `repo` scope (or a fine-grained token with
"Issues" read/write permission on this repository).

Safe to re-run — existing labels are updated (PATCH), new ones are
created (POST).  Labels not in this list are left untouched.
"""

from __future__ import annotations

import os
import sys
import json
import urllib.request
import urllib.error

OWNER = "R0GV3TheAlchemist"
REPO  = "GAIA-The-Global-Autonomous-Intelligence-Architecture"

LABELS = [
    # ── Type ─────────────────────────────────────────────────────────────
    {"name": "type: bug",         "color": "d73a4a", "description": "Something isn't working"},
    {"name": "type: feature",     "color": "0075ca", "description": "New feature or request"},
    {"name": "type: chore",       "color": "e4e669", "description": "Build, tooling, or maintenance task"},
    {"name": "type: docs",        "color": "0052cc", "description": "Documentation only"},
    {"name": "type: test",        "color": "bfd4f2", "description": "Test coverage or test infrastructure"},
    {"name": "type: security",    "color": "b60205", "description": "Security vulnerability or hardening"},
    {"name": "type: performance", "color": "f9d0c4", "description": "Performance improvement"},

    # ── Priority ─────────────────────────────────────────────────────────
    {"name": "priority: critical", "color": "b60205", "description": "Must fix immediately — blocks release"},
    {"name": "priority: high",     "color": "e11d48", "description": "High urgency — address this sprint"},
    {"name": "priority: medium",   "color": "f97316", "description": "Normal priority"},
    {"name": "priority: low",      "color": "fde68a", "description": "Nice to have — address when capacity allows"},

    # ── Component ────────────────────────────────────────────────────────
    {"name": "comp: core",       "color": "5b21b6", "description": "core/ — epistemic engine, criticality, models"},
    {"name": "comp: api",        "color": "6d28d9", "description": "api/ — FastAPI routers and routes"},
    {"name": "comp: cli",        "color": "7c3aed", "description": "cli/ — command-line interface"},
    {"name": "comp: crypto",     "color": "8b5cf6", "description": "api/crypto.py — encryption layer"},
    {"name": "comp: memory",     "color": "a78bfa", "description": "Memory store, elemental memory, retrieval"},
    {"name": "comp: alignment",  "color": "c4b5fd", "description": "api/routers/alignment.py — alignment engine"},
    {"name": "comp: gaian",      "color": "ddd6fe", "description": "api/routers/gaian.py — GAIAN runtime"},
    {"name": "comp: ui",         "color": "0ea5e9", "description": "src/ ui/ client/ — frontend"},
    {"name": "comp: infra",      "color": "0369a1", "description": "Docker, k8s, CI/CD, Makefile"},

    # ── Status ───────────────────────────────────────────────────────────
    {"name": "status: needs-triage",     "color": "ededed", "description": "Newly opened — not yet assessed"},
    {"name": "status: in-progress",      "color": "fbca04", "description": "Actively being worked on"},
    {"name": "status: blocked",          "color": "e11d48", "description": "Cannot proceed — waiting on something"},
    {"name": "status: ready-for-review", "color": "0e8a16", "description": "Work done — awaiting review / merge"},
    {"name": "status: wont-fix",         "color": "ffffff", "description": "Acknowledged but will not be addressed"},

    # ── Special ──────────────────────────────────────────────────────────
    {"name": "good first issue", "color": "7057ff", "description": "Good for newcomers"},
    {"name": "help wanted",      "color": "008672", "description": "Extra attention is needed"},
    {"name": "breaking change",  "color": "b60205", "description": "Introduces a breaking API or behaviour change"},
    {"name": "ruff / lint",      "color": "e4e669", "description": "Code style or linting issue"},
    {"name": "epic",             "color": "3b0764", "description": "Large multi-issue initiative"},
]


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _request(method: str, url: str, token: str, body: dict | None = None):
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(url, data=data, headers=_headers(token), method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read())


def _existing_labels(token: str) -> dict[str, str]:
    """Return {name: node_id} for all existing labels (handles pagination)."""
    result = {}
    page   = 1
    base   = f"https://api.github.com/repos/{OWNER}/{REPO}/labels"
    while True:
        status, data = _request("GET", f"{base}?per_page=100&page={page}", token)
        if status != 200 or not data:
            break
        for label in data:
            result[label["name"]] = label["name"]  # key by name
        if len(data) < 100:
            break
        page += 1
    return result


def main() -> None:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN environment variable not set.", file=sys.stderr)
        sys.exit(1)

    base     = f"https://api.github.com/repos/{OWNER}/{REPO}/labels"
    existing = _existing_labels(token)

    created = updated = failed = 0

    for label in LABELS:
        name = label["name"]
        if name in existing:
            # PATCH to update color/description in case they drifted
            encoded = urllib.parse.quote(name, safe="")
            status, _ = _request("PATCH", f"{base}/{encoded}", token, label)
            if status in (200, 201):
                print(f"  UPDATED  {name}")
                updated += 1
            else:
                print(f"  FAILED   {name}  (HTTP {status})")
                failed += 1
        else:
            status, _ = _request("POST", base, token, label)
            if status in (200, 201):
                print(f"  CREATED  {name}")
                created += 1
            else:
                print(f"  FAILED   {name}  (HTTP {status})")
                failed += 1

    print(f"\nDone. created={created}  updated={updated}  failed={failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    import urllib.parse  # noqa: PLC0415
    main()
