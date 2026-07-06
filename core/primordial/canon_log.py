"""
core/primordial/canon_log.py
============================
Persistent JSONL canon log for all primordial simulation runs.

Every simulation result is appended as a single JSON line to
data/primordial_canon.jsonl, creating a living record of every
passage attempted through the simulation engine.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

CANON_LOG_PATH = Path(__file__).resolve().parents[2] / "data" / "primordial_canon.jsonl"


def append_to_canon(result: dict[str, Any]) -> None:
    """Append a simulation result to the persistent canon log."""
    CANON_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "logged_at": datetime.now(timezone.utc).isoformat(),
        **result,
    }
    with CANON_LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")


def read_canon(limit: int | None = None) -> list[dict[str, Any]]:
    """Read entries from the canon log, most recent last."""
    if not CANON_LOG_PATH.exists():
        return []
    lines = CANON_LOG_PATH.read_text(encoding="utf-8").strip().splitlines()
    if limit:
        lines = lines[-limit:]
    return [json.loads(line) for line in lines if line.strip()]


def canon_summary() -> dict[str, Any]:
    """Return aggregate statistics across all canon entries."""
    entries = read_canon()
    if not entries:
        return {"total": 0}

    total     = len(entries)
    survived  = sum(1 for e in entries if e.get("survived"))
    orders    = [e["emergent_order"] for e in entries if e.get("survived")]
    avg_order = sum(orders) / len(orders) if orders else 0.0

    all_insights: list[str] = []
    for entry in entries:
        for stage in entry.get("stage_results", []):
            snapshot = stage.get("snapshot", {})
            all_insights.extend(snapshot.get("insights", []))

    insight_freq: dict[str, int] = {}
    for insight in all_insights:
        insight_freq[insight] = insight_freq.get(insight, 0) + 1

    top_insights = sorted(insight_freq.items(), key=lambda x: -x[1])[:5]

    return {
        "total":           total,
        "survived":        survived,
        "collapsed":       total - survived,
        "survival_rate":   round(survived / total, 4),
        "avg_emergent_order": round(avg_order, 4),
        "top_insights":    [i for i, _ in top_insights],
    }
