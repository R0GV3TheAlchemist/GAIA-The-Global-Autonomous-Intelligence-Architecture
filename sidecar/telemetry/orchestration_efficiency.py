"""OrchestrationEfficiency models and computation — GAIA-OS Issue #188."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean


@dataclass
class OrchestrationEfficiency:
    window: str
    successful_tasks: int
    total_tasks: int
    avg_task_duration_s: float
    avg_dq_score: float
    degraded_task_fraction: float
    oe_score: float

    @classmethod
    def from_events(cls, window: str, events: list[dict]) -> "OrchestrationEfficiency":
        relevant = [e for e in events if e.get("source") == "synergy_orchestrator" and e.get("event_type") == "job_completed"]
        total = len(relevant)
        if total == 0:
            return cls(window, 0, 0, 0.0, 0.0, 0.0, 0.0)

        successful = sum(1 for e in relevant if not e.get("degraded", False))
        durations_s = [max(0, e.get("duration_ms", 0)) / 1000.0 for e in relevant]
        dq_scores = [e["dq_score"] for e in relevant if e.get("dq_score") is not None]
        degraded_fraction = sum(1 for e in relevant if e.get("degraded", False)) / total
        avg_duration = mean(durations_s) if durations_s else 0.0
        avg_dq = mean(dq_scores) if dq_scores else 0.0
        success_rate = successful / total if total else 0.0
        oe_score = 0.0 if avg_duration <= 0 else success_rate / avg_duration
        return cls(
            window=window,
            successful_tasks=successful,
            total_tasks=total,
            avg_task_duration_s=avg_duration,
            avg_dq_score=avg_dq,
            degraded_task_fraction=degraded_fraction,
            oe_score=oe_score,
        )
