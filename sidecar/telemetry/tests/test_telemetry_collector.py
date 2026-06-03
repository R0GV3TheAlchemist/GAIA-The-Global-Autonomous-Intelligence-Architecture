"""pytest — TelemetryCollector tests — GAIA-OS Issue #188."""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from sidecar.telemetry.telemetry_collector import TelemetryCollector
from sidecar.telemetry.telemetry_event import TelemetryEvent


@pytest.fixture
def collector(tmp_path):
    return TelemetryCollector(db_path=tmp_path / "telemetry.db")


@pytest.mark.asyncio
async def test_emit_and_session_trace(collector):
    event = TelemetryEvent(
        session_id="session-1",
        source="synergy_orchestrator",
        event_type="job_completed",
        skill_id="research_desk",
        input_summary="load url",
        output_summary="loaded article",
        duration_ms=420,
        dq_score=0.91,
    )
    await collector.emit(event)
    trace = await collector.get_session_trace("session-1")
    assert len(trace) == 1
    assert trace[0].event_type == "job_completed"
    assert trace[0].dq_score == pytest.approx(0.91)


@pytest.mark.asyncio
async def test_skill_health(collector):
    await collector.emit(TelemetryEvent(session_id="s1", source="healing", event_type="fallback_used", skill_id="planetary_hub", input_summary="poll", output_summary="cached", duration_ms=150, degraded=True))
    await collector.emit(TelemetryEvent(session_id="s1", source="planetary", event_type="job_failed", skill_id="planetary_hub", input_summary="poll", output_summary="fail", duration_ms=200))
    report = await collector.get_skill_health("planetary_hub", window_min=60)
    assert report.event_count == 2
    assert report.error_rate == pytest.approx(1.0)
    assert report.circuit_state in {"OPEN", "HALF_OPEN"}


@pytest.mark.asyncio
async def test_dq_history(collector):
    await collector.emit(TelemetryEvent(session_id="s2", source="synergy_orchestrator", event_type="job_completed", skill_id="crystal_graphrag", input_summary="query", output_summary="ok", duration_ms=180, dq_score=0.88))
    history = await collector.get_dq_history(limit=10)
    assert len(history) == 1
    assert history[0].dq_score == pytest.approx(0.88)


@pytest.mark.asyncio
async def test_oe_window(collector):
    await collector.emit(TelemetryEvent(session_id="s3", source="synergy_orchestrator", event_type="job_completed", skill_id="compose", input_summary="compose", output_summary="done", duration_ms=1000, dq_score=0.9, degraded=False))
    await collector.emit(TelemetryEvent(session_id="s3", source="synergy_orchestrator", event_type="job_completed", skill_id="compose", input_summary="compose", output_summary="degraded", duration_ms=2000, dq_score=0.7, degraded=True))
    oe = await collector.get_oe_window("24h")
    assert oe.total_tasks == 2
    assert oe.successful_tasks == 1
    assert oe.avg_task_duration_s == pytest.approx(1.5)
    assert oe.degraded_task_fraction == pytest.approx(0.5)


@pytest.mark.asyncio
async def test_export_and_delete(collector):
    now = datetime.now(timezone.utc)
    event = TelemetryEvent(
        session_id="s4",
        source="skill",
        event_type="skill_invoked",
        skill_id="shell",
        input_summary="run ls",
        output_summary="ok",
        duration_ms=50,
        timestamp=now,
    )
    await collector.emit(event)
    exported = await collector.export_session_trace_json("s4")
    assert "skill_invoked" in exported
    deleted = await collector.delete_range((now - timedelta(seconds=1)).isoformat(), (now + timedelta(seconds=1)).isoformat())
    assert deleted >= 1
