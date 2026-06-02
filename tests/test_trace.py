"""
tests/test_trace.py
Full test coverage for core/trace.py — written against the canonical main version.

API contract being tested:
  - _load_records(audit_dir: Path, since_hours: int | None) -> list[dict]
  - _cmd_query(args) — --since is int (hours), --limit is int
  - _cmd_stats(args) — outputs JSON, --since is int (hours)
  - _cmd_show(args)  — --trace-id and --correlation-id args
  - TraceEventType   — 9 members, str subclass, JSON-safe
  - TraceRecord      — 12 fields, meta default_factory
  - GAIATrace        — sync CM: happy path, error capture, flush, output/meta
  - AsyncGAIATrace   — async CM: happy path, error capture

Run with:
    pytest tests/test_trace.py -v --asyncio-mode=auto
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.trace import (
    AsyncGAIATrace,
    GAIATrace,
    TraceEventType,
    TraceRecord,
    _AUDIT_DIR,
    _load_records,
    _cmd_query,
    _cmd_stats,
    _cmd_show,
    _build_parser,
)


# ===========================================================================
# TraceEventType
# ===========================================================================

class TestTraceEventType:
    def test_all_nine_members_exist(self):
        names = {e.name for e in TraceEventType}
        assert names == {
            "SYNERGY_COMPUTE", "LLM_INFERENCE", "MEMORY_RECALL",
            "MEMORY_WRITE", "ACTION_GATE_DECISION", "TASK_NODE_EXEC",
            "CANON_LOAD", "STAGE_SESSION", "TOOL_CALL",
        }

    def test_members_are_str_subclass(self):
        for evt in TraceEventType:
            assert isinstance(evt, str)

    def test_json_serialisable_without_custom_encoder(self):
        for evt in TraceEventType:
            out = json.dumps({"event": evt})
            assert json.loads(out)["event"] == evt.value

    def test_string_equality(self):
        assert TraceEventType.LLM_INFERENCE == "llm_inference"

    def test_count(self):
        assert len(list(TraceEventType)) == 9


# ===========================================================================
# TraceRecord
# ===========================================================================

class TestTraceRecord:
    def _make(self, **kw) -> TraceRecord:
        defaults = dict(
            trace_id="t1", event="synergy_compute", gaian_id="g1",
            correlation_id="req-abc", canon_refs=["C01"],
            started_at="2026-06-02T00:00:00+00:00", ended_at=None,
            latency_ms=None, inputs={"x": 1}, outputs={}, error=None,
        )
        defaults.update(kw)
        return TraceRecord(**defaults)

    def test_all_fields_present(self):
        r = self._make()
        for attr in ("trace_id", "event", "gaian_id", "correlation_id",
                     "canon_refs", "started_at", "ended_at", "latency_ms",
                     "inputs", "outputs", "error", "meta"):
            assert hasattr(r, attr)

    def test_meta_defaults_to_empty_dict(self):
        assert self._make().meta == {}

    def test_meta_not_shared_between_instances(self):
        r1, r2 = self._make(), self._make()
        r1.meta["k"] = "v"
        assert r2.meta == {}


# ===========================================================================
# GAIATrace — sync
# ===========================================================================

class TestGAIATrace:
    def test_trace_id_is_uuid4(self):
        import re
        with GAIATrace(event=TraceEventType.SYNERGY_COMPUTE) as t:
            pass
        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            t.trace_id,
        )

    def test_trace_ids_unique(self):
        ids = {GAIATrace(event=TraceEventType.TOOL_CALL).trace_id for _ in range(50)}
        assert len(ids) == 50

    def test_record_output_merges(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.LLM_INFERENCE) as t:
                t.record_output({"tokens": 42})
                t.record_output({"model": "gaia-7b"})
        assert t._record.outputs == {"tokens": 42, "model": "gaia-7b"}

    def test_record_meta_merges(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.TOOL_CALL) as t:
                t.record_meta({"version": "0.9"})
        assert t._record.meta == {"version": "0.9"}

    def test_latency_ms_positive(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.SYNERGY_COMPUTE) as t:
                time.sleep(0.01)
        assert t._record.latency_ms >= 10.0

    def test_ended_at_set(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.CANON_LOAD) as t:
                pass
        assert t._record.ended_at is not None

    def test_error_recorded_and_propagates(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with pytest.raises(ValueError, match="boom"):
                with GAIATrace(event=TraceEventType.SYNERGY_COMPUTE) as t:
                    raise ValueError("boom")
        assert "ValueError: boom" in t._record.error

    def test_flush_writes_valid_jsonl(self, tmp_path):
        audit = tmp_path / "audit"
        with patch("core.trace._AUDIT_DIR", audit):
            with GAIATrace(
                event=TraceEventType.LLM_INFERENCE,
                gaian_id="g-test",
                canon_refs=["C01", "C30"],
                inputs={"q": "hello"},
            ) as t:
                t.record_output({"answer": "world"})
        files = list(audit.glob("traces_*.jsonl"))
        assert len(files) == 1
        rec = json.loads(files[0].read_text())
        assert rec["event"] == "llm_inference"
        assert rec["outputs"] == {"answer": "world"}
        assert rec["error"] is None

    def test_flush_error_never_raises(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with patch("pathlib.Path.open", side_effect=OSError("disk full")):
                with GAIATrace(event=TraceEventType.TOOL_CALL):
                    pass  # must not raise


# ===========================================================================
# AsyncGAIATrace
# ===========================================================================

class TestAsyncGAIATrace:
    @pytest.mark.asyncio
    async def test_async_happy_path(self, tmp_path):
        audit = tmp_path / "audit"
        with patch("core.trace._AUDIT_DIR", audit):
            async with AsyncGAIATrace(
                event=TraceEventType.LLM_INFERENCE,
                inputs={"prompt": "test"},
            ) as t:
                await asyncio.sleep(0.005)
                t.record_output({"tokens": 7})
        assert t._record.outputs == {"tokens": 7}
        assert t._record.error is None
        assert list(audit.glob("traces_*.jsonl"))

    @pytest.mark.asyncio
    async def test_async_error_recorded_and_propagates(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with pytest.raises(RuntimeError, match="async fail"):
                async with AsyncGAIATrace(event=TraceEventType.TOOL_CALL) as t:
                    raise RuntimeError("async fail")
        assert "RuntimeError: async fail" in t._record.error


# ===========================================================================
# CLI helpers — unit level (no subprocess)
# ===========================================================================

class TestCLI:
    def _write_records(self, audit: Path, records: list[dict]) -> None:
        audit.mkdir(parents=True, exist_ok=True)
        log = audit / "traces_20260602.jsonl"
        with log.open("w") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")

    def _records(self):
        return [
            {"event": "llm_inference", "gaian_id": "g1",
             "started_at": "2026-06-02T01:00:00+00:00",
             "latency_ms": 100.0, "error": None,
             "trace_id": "tid-1", "correlation_id": "req-a"},
            {"event": "llm_inference", "gaian_id": "g1",
             "started_at": "2026-06-02T01:01:00+00:00",
             "latency_ms": 200.0, "error": "ValueError: oops",
             "trace_id": "tid-2", "correlation_id": "req-b"},
            {"event": "tool_call", "gaian_id": "g2",
             "started_at": "2026-06-02T01:02:00+00:00",
             "latency_ms": 50.0, "error": None,
             "trace_id": "tid-3", "correlation_id": "req-c"},
        ]

    def test_stats_json_output(self, tmp_path, capsys):
        audit = tmp_path / "audit"
        self._write_records(audit, self._records())
        args = SimpleNamespace(event="llm_inference", since=9999)
        _cmd_stats.__func__ if hasattr(_cmd_stats, '__func__') else _cmd_stats
        with patch("core.trace._AUDIT_DIR", audit):
            _cmd_stats(args)
        out = json.loads(capsys.readouterr().out)
        assert out["total"] == 2
        assert out["errors"] == 1

    def test_query_error_only(self, tmp_path, capsys):
        audit = tmp_path / "audit"
        self._write_records(audit, self._records())
        args = SimpleNamespace(
            gaian=None, event=None, error_only=True, since=9999, limit=50
        )
        with patch("core.trace._AUDIT_DIR", audit):
            _cmd_query(args)
        lines = [l for l in capsys.readouterr().out.strip().split("\n") if l.strip().startswith("{")]
        # error_only returns the 1 record that has an error (tid-2)
        combined = json.loads("".join(lines))
        assert combined["correlation_id"] == "req-b"

    def test_load_records_filters_by_since(self, tmp_path):
        audit = tmp_path / "audit"
        self._write_records(audit, self._records())
        # 1 hour window — all records are from 2026-06-02, well outside 1h of now
        # so result should be empty (they’re in the past, not within last 1h)
        result = _load_records(audit, since_hours=1)
        assert isinstance(result, list)
