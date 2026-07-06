#!/usr/bin/env python3
"""
tools/run_primordial_archetypes.py
===================================
Run all five primordial entity archetypes and display their outcomes.

Usage:
    PYTHONPATH=. python tools/run_primordial_archetypes.py
    PYTHONPATH=. python tools/run_primordial_archetypes.py --output data/archetypes.json
    PYTHONPATH=. python tools/run_primordial_archetypes.py --archetype the_witness
"""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import types as _types
if "core" not in sys.modules:
    _core_pkg = _types.ModuleType("core")
    _core_pkg.__path__ = [str(_ROOT / "core")]  # type: ignore[attr-defined]
    _core_pkg.__package__ = "core"
    sys.modules["core"] = _core_pkg

_archetypes_mod = importlib.import_module("core.primordial.archetypes")
_canon_mod      = importlib.import_module("core.primordial.canon_log")

ARCHETYPES        = _archetypes_mod.ARCHETYPES
run_all_archetypes = _archetypes_mod.run_all_archetypes
append_to_canon   = _canon_mod.append_to_canon


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run all primordial entity archetypes.")
    parser.add_argument(
        "--archetype",
        choices=list(ARCHETYPES.keys()),
        default=None,
        help="Run a single archetype instead of all five.",
    )
    parser.add_argument("--output",   type=Path, default=None)
    parser.add_argument("--no-canon", action="store_true")
    return parser


def main() -> None:
    args    = build_parser().parse_args()
    results = run_all_archetypes()

    if args.archetype:
        results = [r for r in results if r.archetype.name == ARCHETYPES[args.archetype].name]

    output: list[dict] = []
    for r in results:
        d = r.to_dict()
        d["run_at"] = datetime.now(timezone.utc).isoformat()
        output.append(d)

        if not args.no_canon:
            append_to_canon({"type": "archetype", **d})

    print(json.dumps(output, indent=2))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(f"\nSaved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
