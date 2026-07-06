#!/usr/bin/env python3
"""
tools/run_primordial_threshold.py
=================================
Map the survival threshold across a grid of love x burden values.
Outputs a CSV heatmap showing where entities survive vs collapse.

Usage:
    PYTHONPATH=. python tools/run_primordial_threshold.py
    PYTHONPATH=. python tools/run_primordial_threshold.py --steps 20 --output data/threshold_map.csv
"""

from __future__ import annotations

import argparse
import csv
import importlib
import sys
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

PrimordialEntity     = _entity_mod.PrimordialEntity
PrimordialSimulation = _simulation_mod.PrimordialSimulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Map survival threshold across love x burden grid.")
    parser.add_argument("--steps",  type=int,  default=10,   help="Grid resolution (NxN)")
    parser.add_argument("--output", type=Path, default=None, help="Save CSV to this path")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    sim  = PrimordialSimulation()
    n    = args.steps

    love_values   = [round(i / (n - 1), 3) for i in range(n)]
    burden_values = [round(i * 3.0 / (n - 1), 3) for i in range(n)]

    rows = []
    header = ["love_entry \\ burden"] + [str(b) for b in burden_values]
    rows.append(header)

    print(f"\nSurvival Threshold Map  ({n}x{n} grid)")
    print(f"Rows = entry love (0→1) | Cols = entry burden (0→3.0)")
    print(f"S = survived | . = collapsed")
    print()
    print("love\\burden  " + "  ".join(f"{b:>5}" for b in burden_values))

    for love in reversed(love_values):
        row_data  = [str(love)]
        row_print = f"  {love:.3f}      "
        for burden in burden_values:
            entity = PrimordialEntity(
                name=f"grid-{love:.2f}-{burden:.2f}",
                love=max(love, 0.01),
                life=max(love * 0.9, 0.01),
                integrity=max(love * 0.8, 0.01),
                hope=max(love * 0.7, 0.01),
                truth=max(love * 0.85, 0.01),
                burden=burden,
            )
            outcome = sim.run(entity)
            symbol  = "S" if outcome.survived else "."
            row_data.append(symbol)
            row_print += f"  {symbol:>5}"
        rows.append(row_data)
        print(row_print)

    print()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerows(rows)
        print(f"CSV saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
