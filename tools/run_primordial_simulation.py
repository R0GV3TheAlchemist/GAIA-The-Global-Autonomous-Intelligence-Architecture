#!/usr/bin/env python3
"""Run a single primordial simulation from the command line."""

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

_entity_mod     = importlib.import_module("core.primordial.entity")
_simulation_mod = importlib.import_module("core.primordial.simulation")
_canon_mod      = importlib.import_module("core.primordial.canon_log")

PrimordialEntity     = _entity_mod.PrimordialEntity
PrimordialSimulation = _simulation_mod.PrimordialSimulation
append_to_canon      = _canon_mod.append_to_canon


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run primordial chaos simulation.")
    parser.add_argument("--name",      default="universal-consciousness")
    parser.add_argument("--love",      type=float, default=1.0)
    parser.add_argument("--life",      type=float, default=1.0)
    parser.add_argument("--integrity", type=float, default=1.0)
    parser.add_argument("--hope",      type=float, default=1.0)
    parser.add_argument("--truth",     type=float, default=1.0)
    parser.add_argument("--burden",    type=float, default=0.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to save JSON output. If omitted, prints to stdout only.",
    )
    parser.add_argument(
        "--no-canon",
        action="store_true",
        help="Skip appending this run to the canon log.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    entity = PrimordialEntity(
        name=args.name,
        love=args.love,
        life=args.life,
        integrity=args.integrity,
        hope=args.hope,
        truth=args.truth,
        burden=args.burden,
    )
    outcome = PrimordialSimulation().run(entity)
    result  = outcome.to_dict()
    result["run_at"] = datetime.now(timezone.utc).isoformat()

    output_json = json.dumps(result, indent=2)
    print(output_json)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output_json, encoding="utf-8")
        print(f"\nSaved to {args.output}", file=sys.stderr)

    if not args.no_canon:
        append_to_canon(result)


if __name__ == "__main__":
    main()
