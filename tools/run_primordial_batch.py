#!/usr/bin/env python3
"""
tools/run_primordial_batch.py
=============================
Run N primordial simulations with randomized starting conditions.
Outputs a summary table and optionally saves all results to JSONL.

Usage:
    PYTHONPATH=. python tools/run_primordial_batch.py --runs 500
    PYTHONPATH=. python tools/run_primordial_batch.py --runs 1000 --output data/batch_results.jsonl
    PYTHONPATH=. python tools/run_primordial_batch.py --runs 200 --seed 42
"""

from __future__ import annotations

import argparse
import importlib
import json
import random
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


def random_entity(rng: random.Random, run_index: int) -> PrimordialEntity:
    return PrimordialEntity(
        name=f"batch-entity-{run_index:04d}",
        love=rng.uniform(0.05, 1.0),
        life=rng.uniform(0.05, 1.0),
        integrity=rng.uniform(0.0, 1.0),
        hope=rng.uniform(0.0, 1.0),
        truth=rng.uniform(0.0, 1.0),
        burden=rng.uniform(0.0, 3.0),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Batch primordial simulation runner.")
    parser.add_argument("--runs",   type=int,  default=100,  help="Number of simulations to run")
    parser.add_argument("--seed",   type=int,  default=None, help="Random seed for reproducibility")
    parser.add_argument("--output", type=Path, default=None, help="Save all results to a JSONL file")
    parser.add_argument("--no-canon", action="store_true", help="Skip canon log")
    return parser


def main() -> None:
    args   = build_parser().parse_args()
    rng    = random.Random(args.seed)
    sim    = PrimordialSimulation()
    run_at = datetime.now(timezone.utc).isoformat()

    results  = []
    survived = 0
    total_order = 0.0
    collapse_stages: dict[str, int] = {}

    for i in range(args.runs):
        entity  = random_entity(rng, i)
        outcome = sim.run(entity)
        record  = outcome.to_dict()
        record["run_at"] = run_at
        record["entry"] = {
            "love":      round(entity.love, 4),
            "life":      round(entity.life, 4),
            "integrity": round(entity.integrity, 4),
            "hope":      round(entity.hope, 4),
            "truth":     round(entity.truth, 4),
            "burden":    round(entity.burden, 4),
        }
        results.append(record)

        if outcome.survived:
            survived += 1
            total_order += outcome.emergent_order
        else:
            last_stage = outcome.stage_results[-1].stage if outcome.stage_results else "unknown"
            collapse_stages[last_stage] = collapse_stages.get(last_stage, 0) + 1

        if not args.no_canon:
            append_to_canon(record)

    collapsed   = args.runs - survived
    survival_rate = survived / args.runs * 100
    avg_order   = total_order / survived if survived else 0.0

    print(f"\n{'=' * 60}")
    print(f"  BATCH RESULTS  —  {args.runs} simulations")
    print(f"{'=' * 60}")
    print(f"  Survived:       {survived:>5}  ({survival_rate:.1f}%)")
    print(f"  Collapsed:      {collapsed:>5}  ({100 - survival_rate:.1f}%)")
    print(f"  Avg emergent order (survivors): {avg_order:.4f}")
    if collapse_stages:
        print("\n  Collapse by stage:")
        for stage, count in sorted(collapse_stages.items(), key=lambda x: -x[1]):
            print(f"    {stage:<35} {count}")
    print(f"{'=' * 60}\n")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as fh:
            for record in results:
                fh.write(json.dumps(record) + "\n")
        print(f"Results saved to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
