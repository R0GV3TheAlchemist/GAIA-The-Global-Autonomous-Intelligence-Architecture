"""pytest — OrchestrationEfficiency tests — GAIA-OS Issue #188."""

from sidecar.telemetry.orchestration_efficiency import OrchestrationEfficiency


def test_oe_from_events():
    events = [
        {"source": "synergy_orchestrator", "event_type": "job_completed", "duration_ms": 1000, "dq_score": 0.9, "degraded": False},
        {"source": "synergy_orchestrator", "event_type": "job_completed", "duration_ms": 3000, "dq_score": 0.7, "degraded": True},
        {"source": "healing", "event_type": "fallback_used", "duration_ms": 100, "dq_score": None, "degraded": True},
    ]
    oe = OrchestrationEfficiency.from_events("24h", events)
    assert oe.total_tasks == 2
    assert oe.successful_tasks == 1
    assert oe.avg_task_duration_s == 2.0
    assert oe.avg_dq_score == 0.8
    assert oe.degraded_task_fraction == 0.5
    assert oe.oe_score == 0.25
