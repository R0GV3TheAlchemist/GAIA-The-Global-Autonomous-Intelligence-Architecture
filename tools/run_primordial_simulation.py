#!/usr/bin/env python3
"""Run the primordial simulation from the command line."""

from __future__ import annotations

import argparse
import json

from core.primordial import PrimordialEntity, PrimordialSimulation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run primordial chaos simulation.")
    parser.add_argument("--name", default="universal-consciousness")
    parser.add_argument("--love", type=float, default=1.0)
    parser.add_argument("--life", type=float, default=1.0)
    parser.add_argument("--integrity", type=float, default=1.0)
    parser.add_argument("--hope", type=float, default=1.0)
    parser.add_argument("--truth", type=float, default=1.0)
    parser.add_argument("--burden", type=float, default=0.0)
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
    print(json.dumps(outcome.to_dict(), indent=2))


if __name__ == "__main__":
    main()
