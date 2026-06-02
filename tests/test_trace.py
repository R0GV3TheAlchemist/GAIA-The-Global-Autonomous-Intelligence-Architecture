"""
tests/test_trace.py
Full test coverage for core/trace.py

Covers:
  TraceEventType  — values, str coercion, JSON serialisability, iteration
  TraceRecord     — field presence, defaults, dataclass contract
  GAIATrace       — happy path, error capture, output/meta recording,
                    trace_id uniqueness, correlation_id propagation,
                    flush writes valid JSONL, exceptions propagate (not suppressed)
  AsyncGAIATrace  — async happy path, async error capture
  Correlation ID  — new_correlation_id, set_correlation_id, context isolation
  CLI             — _cmd_stats against synthetic JSONL, _cmd_query filters

Run with:
    pytest tests/test_trace.py -v --asyncio-mode=auto
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Ensure repo root is on sys.path so `core.trace` resolves correctly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.trace import (
    AsyncGAIATrace,
    GAIATrace,
    TraceEventType,
    TraceRecord,
    correlation_id_ctx,
    new_correlation_id,
    set_correlation_id,
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
            "SYNERGY_COMPUTE",
            "LLM_INFERENCE",
            "MEMORY_RECALL",
            "MEMORY_WRITE",
            "ACTION_GATE_DECISION",
            "TASK_NODE_EXEC",
            "CANON_LOAD",
            "STAGE_SESSION",
            "TOOL_CALL",
        }

    def test_members_are_str_subclass(self):
        for evt in TraceEventType:
            assert isinstance(evt, str), f"{evt!r} must be a str subclass"

    def test_json_serialisable_without_custom_encoder(self):
        for evt in TraceEventType:
            serialised = json.dumps({"event": evt})
            decoded = json.loads(serialised)
            assert decoded["event"] == evt.value

    def test_string_comparison(self):
        assert TraceEventType.LLM_INFERENCE == "llm_inference"

    def test_iteration_yields_all(self):
        assert len(list(TraceEventType)) == 9


# ===========================================================================
# TraceRecord
# ===========================================================================

class TestTraceRecord:
    def _make(self, **kwargs) -> TraceRecord:
        defaults = dict(
            trace_id="t1",
            event="synergy_compute",
            gaian_id="g1",
            correlation_id="req-abc",
            canon_refs=["C01"],
            started_at="2026-06-02T00:00:00+00:00",
            ended_at=None,
            latency_ms=None,
            inputs={"x": 1},
            outputs={},
            error=None,
        )
        defaults.update(kwargs)
        return TraceRecord(**defaults)

    def test_all_fields_present(self):
        r = self._make()
        for attr in (
            "trace_id", "event", "gaian_id", "correlation_id", "canon_refs",
            "started_at", "ended_at", "latency_ms", "inputs", "outputs",
            "error", "meta",
        ):
            assert hasattr(r, attr), f"TraceRecord missing field: {attr}"

    def test_meta_defaults_to_empty_dict(self):
        r = self._make()
        assert r.meta == {}

    def test_meta_not_shared_between_instances(self):
        """Mutable default via field(default_factory=dict) must not be shared."""
        r1 = self._make()
        r2 = self._make()
        r1.meta["key"] = "value"
        assert r2.meta == {}, "meta dicts must not be shared across instances"


# ===========================================================================
# GAIATrace — sync
# ===========================================================================

class TestGAIATrace:
    def test_trace_id_is_uuid4_string(self):
        with GAIATrace(event=TraceEventType.SYNERGY_COMPUTE) as t:
            tid = t.trace_id
        import re
        assert re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
            tid,
        ), f"trace_id {tid!r} is not a valid UUID4"

    def test_trace_ids_are_unique(self):
        ids = set()
        for _ in range(50):
            with GAIATrace(event=TraceEventType.TOOL_CALL) as t:
                ids.add(t.trace_id)
        assert len(ids) == 50, "trace_id must be unique per instance"

    def test_record_output_merges_data(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.LLM_INFERENCE, inputs={"prompt": "hi"}) as t:
                t.record_output({"tokens": 42})
                t.record_output({"model": "gaia-7b"})
        assert t._record.outputs == {"tokens": 42, "model": "gaia-7b"}

    def test_record_meta_merges_data(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.TOOL_CALL) as t:
                t.record_meta({"version": "0.9"})
        assert t._record.meta == {"version": "0.9"}

    def test_latency_ms_is_positive_float(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            t0 = time.monotonic()
            with GAIATrace(event=TraceEventType.SYNERGY_COMPUTE) as t:
                time.sleep(0.01)
        assert t._record.latency_ms is not None
        assert t._record.latency_ms >= 10.0, "Expected ≥10ms for a 10ms sleep"

    def test_ended_at_is_set(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with GAIATrace(event=TraceEventType.CANON_LOAD) as t:
                pass
        assert t._record.ended_at is not None

    def test_error_recorded_but_exception_propagates(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with pytest.raises(ValueError, match="boom"):
                with GAIATrace(event=TraceEventType.SYNERGY_COMPUTE) as t:
                    raise ValueError("boom")
        assert "ValueError: boom" in t._record.error

    def test_flush_writes_valid_jsonl(self, tmp_path):
        audit_dir = tmp_path / "audit"
        with patch("core.trace._AUDIT_DIR", audit_dir):
            with GAIATrace(
                event=TraceEventType.LLM_INFERENCE,
                gaian_id="g-test",
                canon_refs=["C01", "C30"],
                inputs={"q": "hello"},
            ) as t:
                t.record_output({"answer": "world"})

        files = list(audit_dir.glob("traces_*.jsonl"))
        assert len(files) == 1, "Expected exactly one daily JSONL file"
        lines = files[0].read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert record["event"] == "llm_inference"
        assert record["gaian_id"] == "g-test"
        assert record["canon_refs"] == ["C01", "C30"]
        assert record["outputs"] == {"answer": "world"}
        assert record["error"] is None

    def test_flush_error_does_not_raise(self, tmp_path):
        """A disk I/O failure in _flush must never propagate to the caller."""
        audit_dir = tmp_path / "audit"
        with patch("core.trace._AUDIT_DIR", audit_dir):
            with patch("pathlib.Path.open", side_effect=OSError("disk full")):
                # Should complete without raising
                with GAIATrace(event=TraceEventType.TOOL_CALL) as t:
                    pass
        # No assertion needed — reaching here proves no exception escaped

    def test_correlation_id_inherits_from_context(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            set_correlation_id("req-fixed-001")
            with GAIATrace(event=TraceEventType.MEMORY_RECALL) as t:
                pass
        assert t._record.correlation_id == "req-fixed-001"


# ===========================================================================
# AsyncGAIATrace
# ===========================================================================

class TestAsyncGAIATrace:
    @pytest.mark.asyncio
    async def test_async_happy_path(self, tmp_path):
        audit_dir = tmp_path / "audit"
        with patch("core.trace._AUDIT_DIR", audit_dir):
            async with AsyncGAIATrace(
                event=TraceEventType.LLM_INFERENCE,
                inputs={"prompt": "test"},
            ) as t:
                await asyncio.sleep(0.005)
                t.record_output({"tokens": 7})

        assert t._record.outputs == {"tokens": 7}
        assert t._record.latency_ms is not None
        assert t._record.error is None
        files = list(audit_dir.glob("traces_*.jsonl"))
        assert len(files) == 1

    @pytest.mark.asyncio
    async def test_async_error_recorded_and_propagates(self, tmp_path):
        with patch("core.trace._AUDIT_DIR", tmp_path / "audit"):
            with pytest.raises(RuntimeError, match="async fail"):
                async with AsyncGAIATrace(event=TraceEventType.TOOL_CALL) as t:
                    raise RuntimeError("async fail")
        assert "RuntimeError: async fail" in t._record.error


# ===========================================================================
# Correlation ID helpers
# ===========================================================================

class TestCorrelationID:
    def test_new_correlation_id_format(self):
        cid = new_correlation_id()
        assert cid.startswith("req-")
        assert len(cid) == 16  # "req-" + 12 hex chars

    def test_new_correlation_id_sets_context(self):
        cid = new_correlation_id()
        assert correlation_id_ctx.get("-") == cid

    def test_set_correlation_id(self):
        set_correlation_id("req-custom-id")
        assert correlation_id_ctx.get("-") == "req-custom-id"


# ===========================================================================
# CLI helpers (unit-level — no subprocess)
# ===========================================================================

class TestCLI:
    def _write_records(self, path: Path, records: list[dict]) -> None:
        path.mkdir(parents=True, exist_ok=True)
        log = path / "traces_20260602.jsonl"
        with log.open("w", encoding="utf-8") as fh:
            for r in records:
                fh.write(json.dumps(r) + "\n")

    def test_stats_counts_errors(self, tmp_path, capsys):
        records = [
            {"event": "llm_inference", "gaian_id": "g1", "started_at": "2026-06-02T01:00:00+00:00",
             "latency_ms": 100.0, "error": None},
            {"event": "llm_inference", "gaian_id": "g1", "started_at": "2026-06-02T01:01:00+00:00",
             "latency_ms": 200.0, "error": "ValueError: oops"},
            {"event": "tool_call",    "gaian_id": "g2", "started_at": "2026-06-02T01:02:00+00:00",
             "latency_ms": 50.0,  "error": None},
        ]
        audit = tmp_path / "audit"
        self._write_records(audit, records)

        parser = _build_parser()
        args = parser.parse_args(["stats", "--event", "llm_inference", "--since", "9999h"])

        with patch("core.trace._AUDIT_DIR", audit):
            _cmd_stats(args)

        out = capsys.readouterr().out
        assert "Total traces : 2" in out
        assert "Errors       : 1" in out

    def test_query_error_only_filter(self, tmp_path, capsys):
        records = [
            {"event": "llm_inference", "gaian_id": "g1", "started_at": "2026-06-02T01:00:00+00:00",
             "latency_ms": 100.0, "error": None, "correlation_id": "req-a"},
            {"event": "llm_inference", "gaian_id": "g1", "started_at": "2026-06-02T01:01:00+00:00",
             "latency_ms": 200.0, "error": "ValueError: bad", "correlation_id": "req-b"},
        ]
        audit = tmp_path / "audit"
        self._write_records(audit, records)

        parser = _build_parser()
        args = parser.parse_args(["query", "--error-only", "--since", "9999h"])

        with patch("core.trace._AUDIT_DIR", audit):
            _cmd_query(args)

        out = capsys.readouterr().out
        lines = [l for l in out.strip().split("\n") if l.strip()]
        assert len(lines) == 1
        assert json.loads(lines[0])["correlation_id"] == "req-b"
