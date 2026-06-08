"""
tools/sim_runner.py
====================
GAIA-OS  Simulation Runner  — zero-dependency PRAO driver.

Runs the SynergyEngine.plan() signal chain against a bank of named
scenarios without touching any LLM, database, or network.  Useful for
local verification, CI smoke-testing, and debugging register-selection
logic before shipping Canon or biometric changes.

Usage
-----
  # Human-readable table (all scenarios, default 8 cycles each)
  python tools/sim_runner.py

  # JSON-lines output for pipes / CI parsing
  python tools/sim_runner.py --json

  # Run a single scenario by index (0-based)
  python tools/sim_runner.py --scenario 2

  # Override cycle count
  python tools/sim_runner.py --cycles 15

  # Combine
  python tools/sim_runner.py --scenario 0 --cycles 20 --json

Scenarios
---------
  0  executive-canon-grounded   High coherence + executive Canon keywords.
  1  reflective-grief-canon     Grief affective + grief Canon passage.
  2  minimal-depleted-no-canon  Low coherence (0.28) — biometric guard fires.
  3  canon-rest-nudge           Good coherence but Canon says "rest".
  4  progress-completion        Pre-seeded high-progress cycles → goal_complete.

Canon Refs
----------
  C01  — plan() proposes; ActionGate disposes.
  C30  — No silent failures; every plan includes a rationale.
  C32  — Multi-signal integration: never act on a single signal alone.
"""

from __future__ import annotations

import asyncio
import json
import sys
from dataclasses import dataclass, field
from typing import Any, List, Optional

# ---------------------------------------------------------------------------
# Minimal LoopContext stub — mirrors the fields plan() reads via getattr()
# ---------------------------------------------------------------------------

@dataclass
class _LoopContext:
    """Minimal stand-in for core.agentic_loop.LoopContext."""
    biometric_coherence: float
    affective_state:     str
    planetary_label:     str
    session_mode:        str
    canon_context:       Any
    cycle_memory:        List[dict] = field(default_factory=list)
    task_graph:          Any        = None


# ---------------------------------------------------------------------------
# Scenario bank
# ---------------------------------------------------------------------------

def _make_scenarios() -> List[dict]:
    """
    Return the list of scenario specs.  Each spec contains:
      name        : display label
      description : one-line summary
      context     : _LoopContext kwargs
      goal        : goal string passed to plan()
    """
    return [
        {
            "name": "executive-canon-grounded",
            "description": "High coherence + executive Canon keywords → 'executive' register with Canon nudge logged.",
            "context": dict(
                biometric_coherence=0.82,
                affective_state="focused",
                planetary_label="clear",
                session_mode="deep_work",
                canon_context=(
                    "C32 — Synergy Doctrine directs GAIA to research the topic "
                    "thoroughly, build a comprehensive knowledge base, and write "
                    "a structured synthesis document before any output is shared. "
                    "All exploration steps must be logged for the audit trail."
                ),
            ),
            "goal": "Research quantum coherence mechanisms and synthesise findings.",
        },
        {
            "name": "reflective-grief-canon",
            "description": "Grief affective + grief Canon passage → both P2 and P3 agree on 'reflective'.",
            "context": dict(
                biometric_coherence=0.61,
                affective_state="grief",
                planetary_label="mild",
                session_mode="default",
                canon_context=(
                    "C30 — The Gaian is processing grief and loss following a "
                    "significant relational rupture.  Trauma-informed protocols "
                    "apply.  Do not push toward executive action; hold space for "
                    "integration and allow the user to lead."
                ),
            ),
            "goal": "Support the Gaian through a difficult emotional transition.",
        },
        {
            "name": "minimal-depleted-no-canon",
            "description": "Coherence 0.28 — biometric guard fires (P1), 'minimal' regardless of everything else.",
            "context": dict(
                biometric_coherence=0.28,
                affective_state="tired",
                planetary_label="storm",   # P2 would fire, but P1 wins
                session_mode="default",
                canon_context="",           # no Canon context
            ),
            "goal": "Process all outstanding tasks and produce a weekly report.",
        },
        {
            "name": "canon-rest-nudge",
            "description": "Good coherence but Canon says 'rest' → Canon overrides default to 'minimal' (P3).",
            "context": dict(
                biometric_coherence=0.74,
                affective_state="calm",
                planetary_label="clear",
                session_mode="default",
                canon_context=(
                    "C32 — Schumann resonance analysis indicates an optimal "
                    "window for rest and consolidation.  Recommend minimal, "
                    "lightweight activity only.  Pause all executive tasks and "
                    "allow the sleep cycle to complete before resuming deep work."
                ),
            ),
            "goal": "Continue developing the new feature module.",
        },
        {
            "name": "progress-completion",
            "description": "12 pre-seeded high-progress cycles → goal_complete fires at cycle 1 (C30 heuristic).",
            "context": dict(
                biometric_coherence=0.78,
                affective_state="energised",
                planetary_label="clear",
                session_mode="default",
                canon_context="C30 — Document all completion events for audit.",
                # 12 cycles, last 5 all have progress >= 0.8
                cycle_memory=[
                    {"action": "research_goal",       "success": True, "progress": 0.55},
                    {"action": "synthesise_findings", "success": True, "progress": 0.62},
                    {"action": "write_output",        "success": True, "progress": 0.70},
                    {"action": "query_crystal",       "success": True, "progress": 0.74},
                    {"action": "research_goal",       "success": True, "progress": 0.76},
                    {"action": "synthesise_findings", "success": True, "progress": 0.78},
                    {"action": "write_output",        "success": True, "progress": 0.80},
                    {"action": "query_crystal",       "success": True, "progress": 0.82},
                    {"action": "research_goal",       "success": True, "progress": 0.85},
                    {"action": "synthesise_findings", "success": True, "progress": 0.87},
                    {"action": "write_output",        "success": True, "progress": 0.90},
                    {"action": "query_crystal",       "success": True, "progress": 0.92},
                ],
            ),
            "goal": "Finalise and publish the research synthesis.",
        },
    ]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

async def _run_scenario(
    spec: dict,
    cycles: int,
    json_mode: bool,
) -> dict:
    """
    Drive one scenario through *cycles* plan() calls.
    Returns a summary dict for end-of-run reporting.
    """
    # Import here so the module is importable even if core isn't on PYTHONPATH
    # (tests that mock sys.path can still import the runner without errors).
    try:
        from core.synergy_engine import SynergyEngine
    except ImportError as exc:
        _print_or_json(
            {"error": f"Could not import SynergyEngine: {exc}"},
            json_mode,
        )
        sys.exit(1)

    engine = SynergyEngine()

    ctx_kwargs = dict(spec["context"])   # shallow copy — don't mutate spec
    # Build fresh cycle_memory from spec; subsequent cycles append to it
    pre_seeded_memory: List[dict] = ctx_kwargs.pop("cycle_memory", [])
    cycle_memory = list(pre_seeded_memory)
    goal: str = spec["goal"]

    goal_complete_count = 0
    canon_nudge_count   = 0

    if not json_mode:
        _section_header(spec["name"], spec["description"])

    for cycle_idx in range(cycles):
        ctx = _LoopContext(
            **ctx_kwargs,
            cycle_memory=list(cycle_memory),
        )
        result = await engine.plan(goal=goal, context=ctx)

        action        = result.get("action", "?")
        tool          = result.get("tool") or "—"
        confidence    = result.get("confidence", 0.0)
        goal_complete = result.get("goal_complete", False)
        canon_hint    = result.get("canon_hint", {})
        rationale_raw = result.get("rationale", "")

        # Extract register from rationale (not in top-level result dict)
        register = _extract_register(rationale_raw)

        if goal_complete:
            goal_complete_count += 1
        if canon_hint.get("register_nudge"):
            canon_nudge_count += 1

        cycle_record = {
            "scenario":      spec["name"],
            "cycle":         cycle_idx,
            "action":        action,
            "tool":          tool,
            "register":      register,
            "confidence":    round(confidence, 3),
            "goal_complete": goal_complete,
            "canon_hint": {
                "present":       canon_hint.get("present", False),
                "register_nudge": canon_hint.get("register_nudge"),
                "nudge_label":   canon_hint.get("nudge_label", ""),
                "canon_refs":    canon_hint.get("canon_refs", []),
                "conflict":      canon_hint.get("conflict_detected", False),
                "char_count":    canon_hint.get("char_count", 0),
            },
            "rationale_excerpt": rationale_raw[:160],
        }

        if json_mode:
            print(json.dumps(cycle_record), flush=True)
        else:
            _print_cycle_row(cycle_record)

        # Append this cycle's result to memory so the next cycle can see it
        cycle_memory.append({
            "action":   action,
            "success":  True,
            "progress": min(1.0, 0.5 + cycle_idx * 0.05),  # synthetic progress ramp
        })

    return {
        "scenario":            spec["name"],
        "cycles_run":          cycles,
        "goal_complete_count": goal_complete_count,
        "canon_nudge_count":   canon_nudge_count,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _extract_register(rationale: str) -> str:
    """Best-effort extraction of the register from the rationale string."""
    for token in ("minimal", "reflective", "executive"):
        if f"Register: {token}" in rationale or f"register set to {token!r}" in rationale:
            return token
    # Fallback: scan for any register keyword
    for token in ("minimal", "reflective", "executive"):
        if token in rationale:
            return token
    return "unknown"


def _section_header(name: str, description: str) -> None:
    width = 78
    print()
    print("═" * width)
    print(f"  SCENARIO: {name}")
    print(f"  {description}")
    print("═" * width)
    header = (
        f"{'Cycle':>5}  {'Action':<28}  {'Tool':<18}  "
        f"{'Register':<12}  {'Conf':>5}  {'Done?':>6}  {'Canon?':>7}"
    )
    print(header)
    print("─" * width)


def _print_cycle_row(r: dict) -> None:
    hint     = r["canon_hint"]
    canon_s  = hint["nudge_label"][:14] if hint.get("nudge_label") else ("yes" if hint["present"] else "no")
    done_s   = "✓" if r["goal_complete"] else "·"
    conflict = " CONFLICT" if hint.get("conflict") else ""
    print(
        f"  {r['cycle']:>3}  {r['action']:<28}  {r['tool']:<18}  "
        f"{r['register']:<12}  {r['confidence']:>5.3f}  {done_s:>6}  {canon_s:<7}{conflict}"
    )


def _print_summary(summaries: List[dict]) -> None:
    width = 78
    print()
    print("═" * width)
    print("  END-OF-RUN SUMMARY")
    print("─" * width)
    print(f"  {'Scenario':<36}  {'Cycles':>6}  {'Completed':>9}  {'Canon nudges':>12}")
    print("─" * width)
    for s in summaries:
        print(
            f"  {s['scenario']:<36}  {s['cycles_run']:>6}  "
            f"{s['goal_complete_count']:>9}  {s['canon_nudge_count']:>12}"
        )
    print("═" * width)
    print()


def _print_or_json(obj: dict, json_mode: bool) -> None:
    if json_mode:
        print(json.dumps(obj), flush=True)
    else:
        print(obj)


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _parse_args() -> tuple:
    """Minimal arg parser — no argparse dependency."""
    args   = sys.argv[1:]
    json_m = "--json" in args
    cycles = 8
    scenario_idx: Optional[int] = None

    i = 0
    while i < len(args):
        if args[i] == "--cycles" and i + 1 < len(args):
            try:
                cycles = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        elif args[i] == "--scenario" and i + 1 < len(args):
            try:
                scenario_idx = int(args[i + 1])
            except ValueError:
                pass
            i += 2
        else:
            i += 1

    return json_m, cycles, scenario_idx


async def main() -> None:
    json_mode, cycles, scenario_idx = _parse_args()
    scenarios = _make_scenarios()

    if scenario_idx is not None:
        if scenario_idx < 0 or scenario_idx >= len(scenarios):
            print(
                f"Error: --scenario {scenario_idx} out of range "
                f"(0–{len(scenarios) - 1})",
                file=sys.stderr,
            )
            sys.exit(1)
        scenarios = [scenarios[scenario_idx]]

    summaries = []
    for spec in scenarios:
        summary = await _run_scenario(spec, cycles=cycles, json_mode=json_mode)
        summaries.append(summary)

    if not json_mode:
        _print_summary(summaries)


if __name__ == "__main__":
    asyncio.run(main())
