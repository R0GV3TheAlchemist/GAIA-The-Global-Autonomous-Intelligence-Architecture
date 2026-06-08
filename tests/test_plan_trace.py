"""
tests/test_plan_trace.py
=========================
Unit tests for GAIATrace integration in SynergyEngine.plan().

Acceptance criteria covered (Issue #258):
  [1] QUERY event emitted at plan() entry:
        goal_excerpt, coherence, affective, planetary, session_mode,
        cycle_count, canon_present, canon_refs
  [2] OUTPUT event emitted with:
        action, tool, register, confidence, goal_complete,
        canon_nudge_label, conflict_detected
  [3] META latency_ms recorded via record_meta()
  [4] Canon refs [C01, C30, C32] forwarded on QUERY, OUTPUT, ERROR events
  [5] All trace calls wrapped in try/except — a broken trace writer
        never silences a plan result
  [6] trace=None is a safe no-op; plan() still returns a valid result
  [7] PLANNING_FAILED path emits an ERROR trace event

Canon refs: C30 (No silent failures), C32 (Synergy Doctrine)
"""

import asyncio
import pytest
from unittest.mock import MagicMock, call, patch

from core.synergy_engine import SynergyEngine


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PLAN_CANON_REFS = ["C01", "C30", "C32"]


def _run(coro):
    """Run an async coroutine in a blocking context.

    Creates a fresh event loop for each call so this helper works
    correctly in Python 3.10+, where asyncio.get_event_loop() raises
    RuntimeError when no loop exists in the current thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _make_context(
    coherence: float = 0.75,
    affective: str = "calm",
    planetary: str = "clear",
    session_mode: str = "default",
    cycle_memory: list | None = None,
    canon_context: str = "",
    task_graph=None,
):
    """Build a minimal LoopContext-like mock for plan()."""
    ctx = MagicMock()
    ctx.biometric_coherence = coherence
    ctx.affective_state = affective
    ctx.planetary_label = planetary
    ctx.session_mode = session_mode
    ctx.cycle_memory = cycle_memory if cycle_memory is not None else []
    ctx.canon_context = canon_context
    ctx.task_graph = task_graph
    return ctx


def _make_trace():
    """Build a mock trace object with record_output and record_meta."""
    trace = MagicMock()
    trace.record_output = MagicMock()
    trace.record_meta = MagicMock()
    return trace


def _events_by_type(trace):
    """
    Return a dict mapping event_type.name (or value) -> list of kwargs
    from all record_output calls.
    """
    events = {}
    for c in trace.record_output.call_args_list:
        kwargs = c.kwargs if c.kwargs else {}
        if not kwargs and c.args:
            # positional call — less likely but guard anyway
            continue
        et = kwargs.get("event_type")
        key = et.name if hasattr(et, "name") else str(et)
        events.setdefault(key, []).append(kwargs)
    return events


# ---------------------------------------------------------------------------
# [6] trace=None is a safe no-op
# ---------------------------------------------------------------------------

class TestTraceNone:

    def test_plan_without_trace_returns_valid_result(self):
        engine = SynergyEngine()
        ctx = _make_context()
        result = _run(engine.plan("Build the new feature.", ctx, trace=None))
        assert isinstance(result, dict)
        assert "action" in result
        assert "confidence" in result
        assert "rationale" in result

    def test_plan_without_trace_no_attribute_error(self):
        """Omitting trace kwarg entirely must also be safe."""
        engine = SynergyEngine()
        ctx = _make_context()
        result = _run(engine.plan("Explore the canon.", ctx))
        assert result["action"] is not None


# ---------------------------------------------------------------------------
# [1] QUERY event
# ---------------------------------------------------------------------------

class TestQueryEvent:

    def test_query_event_emitted(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context(
            coherence=0.8,
            affective="curious",
            planetary="clear",
            session_mode="deep_work",
            cycle_memory=[{"progress": 0.5}] * 3,
            canon_context="Research and explore the new domain.",
        )
        _run(engine.plan("Research the topic.", ctx, trace=trace))
        events = _events_by_type(trace)
        assert "QUERY" in events, "QUERY event must be emitted"

    def test_query_event_contains_goal_excerpt(self):
        engine = SynergyEngine()
        trace = _make_trace()
        goal = "Build the quantum coherence module for GAIA-OS."
        ctx = _make_context()
        _run(engine.plan(goal, ctx, trace=trace))
        events = _events_by_type(trace)
        query_outputs = [e["output"] for e in events.get("QUERY", [])]
        assert any(
            goal[:40] in str(o.get("goal_excerpt", ""))
            for o in query_outputs
        ), "goal_excerpt must contain the goal text"

    def test_query_event_contains_coherence(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context(coherence=0.62)
        _run(engine.plan("Write documentation.", ctx, trace=trace))
        events = _events_by_type(trace)
        query_outputs = [e["output"] for e in events.get("QUERY", [])]
        assert any(
            abs(o.get("coherence", -1) - 0.62) < 0.01
            for o in query_outputs
        ), "coherence must be present in QUERY output"

    def test_query_event_contains_cycle_count(self):
        engine = SynergyEngine()
        trace = _make_trace()
        cycles = [{"progress": 0.5}] * 7
        ctx = _make_context(cycle_memory=cycles)
        _run(engine.plan("Synthesise findings.", ctx, trace=trace))
        events = _events_by_type(trace)
        query_outputs = [e["output"] for e in events.get("QUERY", [])]
        assert any(
            o.get("cycle_count") == 7
            for o in query_outputs
        ), "cycle_count must equal len(cycle_memory)"

    def test_query_event_canon_refs_forwarded(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        _run(engine.plan("Build something.", ctx, trace=trace))
        events = _events_by_type(trace)
        query_calls = events.get("QUERY", [])
        assert query_calls, "QUERY event must exist"
        canon_refs = query_calls[0].get("canon_refs", [])
        for ref in _PLAN_CANON_REFS:
            assert ref in canon_refs, f"{ref} must be in QUERY canon_refs"


# ---------------------------------------------------------------------------
# [2] OUTPUT event
# ---------------------------------------------------------------------------

class TestOutputEvent:

    def test_output_event_emitted(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        _run(engine.plan("Research the domain.", ctx, trace=trace))
        events = _events_by_type(trace)
        assert "OUTPUT" in events, "OUTPUT event must be emitted"

    def test_output_event_contains_action(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        result = _run(engine.plan("Write output.", ctx, trace=trace))
        events = _events_by_type(trace)
        output_payloads = [e["output"] for e in events.get("OUTPUT", [])]
        assert any(
            o.get("action") == result["action"]
            for o in output_payloads
        ), "OUTPUT event action must match plan() return value"

    def test_output_event_contains_confidence(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context(coherence=0.9)
        result = _run(engine.plan("Synthesise.", ctx, trace=trace))
        events = _events_by_type(trace)
        output_payloads = [e["output"] for e in events.get("OUTPUT", [])]
        assert any(
            o.get("confidence") is not None
            for o in output_payloads
        ), "confidence must be present in OUTPUT event"

    def test_output_event_contains_goal_complete(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        _run(engine.plan("Any goal.", ctx, trace=trace))
        events = _events_by_type(trace)
        output_payloads = [e["output"] for e in events.get("OUTPUT", [])]
        assert any(
            "goal_complete" in o
            for o in output_payloads
        ), "goal_complete must be present in OUTPUT event"

    def test_output_event_canon_refs_forwarded(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        _run(engine.plan("Build.", ctx, trace=trace))
        events = _events_by_type(trace)
        output_calls = events.get("OUTPUT", [])
        assert output_calls, "OUTPUT event must exist"
        canon_refs = output_calls[0].get("canon_refs", [])
        for ref in _PLAN_CANON_REFS:
            assert ref in canon_refs, f"{ref} must be in OUTPUT canon_refs"


# ---------------------------------------------------------------------------
# [3] META latency_ms
# ---------------------------------------------------------------------------

class TestMetaLatency:

    def test_record_meta_called_with_latency(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        _run(engine.plan("Write the doc.", ctx, trace=trace))
        calls = trace.record_meta.call_args_list
        assert calls, "record_meta must be called at least once"
        keys = [c.args[0] if c.args else c.kwargs.get("key") for c in calls]
        assert "latency_ms" in keys, "record_meta must be called with 'latency_ms'"

    def test_latency_is_positive_number(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()
        _run(engine.plan("Research.", ctx, trace=trace))
        for c in trace.record_meta.call_args_list:
            key   = c.args[0] if c.args else c.kwargs.get("key")
            value = c.args[1] if len(c.args) > 1 else c.kwargs.get("value")
            if key == "latency_ms":
                assert isinstance(value, (int, float)), "latency_ms must be numeric"
                assert value >= 0, "latency_ms must be non-negative"


# ---------------------------------------------------------------------------
# [5] Broken trace never silences plan result
# ---------------------------------------------------------------------------

class TestBrokenTraceSafety:

    def test_broken_record_output_does_not_raise(self):
        """If trace.record_output raises, plan() must still return a valid dict."""
        engine = SynergyEngine()
        trace = MagicMock()
        trace.record_output.side_effect = RuntimeError("trace writer offline")
        trace.record_meta = MagicMock()
        ctx = _make_context()
        result = _run(engine.plan("Build something.", ctx, trace=trace))
        assert isinstance(result, dict)
        assert "action" in result
        # trace.record_output was called (and raised) but plan still returned
        assert trace.record_output.called

    def test_broken_record_meta_does_not_raise(self):
        engine = SynergyEngine()
        trace = MagicMock()
        trace.record_output = MagicMock()
        trace.record_meta.side_effect = OSError("disk full")
        ctx = _make_context()
        result = _run(engine.plan("Explore.", ctx, trace=trace))
        assert isinstance(result, dict)
        assert "action" in result

    def test_none_trace_attribute_does_not_raise(self):
        """Passing trace=None must never cause AttributeError inside helpers."""
        engine = SynergyEngine()
        ctx = _make_context()
        result = _run(engine.plan("Integrate.", ctx, trace=None))
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# [7] PLANNING_FAILED path emits ERROR event
# ---------------------------------------------------------------------------

class TestPlanningFailedError:

    def test_planning_failed_emits_error_event(self):
        """
        If _plan_internal raises, plan() catches it, emits an ERROR trace
        event, and returns a PLANNING_FAILED dict.
        """
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()

        with patch.object(
            engine, "_plan_internal",
            side_effect=RuntimeError("injected failure"),
        ):
            result = _run(engine.plan("Fail intentionally.", ctx, trace=trace))

        assert result["action"] == "PLANNING_FAILED"
        assert result["confidence"] == 0.0
        events = _events_by_type(trace)
        assert "ERROR" in events, "ERROR event must be emitted on PLANNING_FAILED"

    def test_planning_failed_error_contains_exception_detail(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()

        with patch.object(
            engine, "_plan_internal",
            side_effect=ValueError("bad signal"),
        ):
            result = _run(engine.plan("Fail.", ctx, trace=trace))

        events = _events_by_type(trace)
        error_outputs = [e["output"] for e in events.get("ERROR", [])]
        assert any(
            "ValueError" in str(o.get("error", "")) or "bad signal" in str(o.get("detail", ""))
            for o in error_outputs
        ), "ERROR event must contain exception type and detail"

    def test_planning_failed_error_canon_refs_forwarded(self):
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context()

        with patch.object(
            engine, "_plan_internal",
            side_effect=RuntimeError("injected"),
        ):
            _run(engine.plan("Fail.", ctx, trace=trace))

        events = _events_by_type(trace)
        error_calls = events.get("ERROR", [])
        assert error_calls, "ERROR event must exist"
        canon_refs = error_calls[0].get("canon_refs", [])
        for ref in _PLAN_CANON_REFS:
            assert ref in canon_refs, f"{ref} must be in ERROR canon_refs"


# ---------------------------------------------------------------------------
# Integration: canon nudge appears in OUTPUT event
# ---------------------------------------------------------------------------

class TestCanonNudgeInOutput:

    def test_canon_rest_nudge_reflected_in_output_register(self):
        """When canon says 'rest', OUTPUT event register should be 'minimal'."""
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context(
            coherence=0.8,          # not depleted — canon nudge should win
            affective="calm",
            canon_context="Gaian must rest and pause all activity today.",
        )
        _run(engine.plan("Work on the feature.", ctx, trace=trace))
        events = _events_by_type(trace)
        output_payloads = [e["output"] for e in events.get("OUTPUT", [])]
        assert any(
            o.get("register") == "minimal"
            for o in output_payloads
        ), "Canon rest nudge must set register to 'minimal' in OUTPUT event"

    def test_no_canon_context_defaults_to_executive_in_output(self):
        """With no canon context and healthy coherence, register is 'executive'."""
        engine = SynergyEngine()
        trace = _make_trace()
        ctx = _make_context(coherence=0.85, affective="focused", canon_context="")
        _run(engine.plan("Build the system.", ctx, trace=trace))
        events = _events_by_type(trace)
        output_payloads = [e["output"] for e in events.get("OUTPUT", [])]
        assert any(
            o.get("register") == "executive"
            for o in output_payloads
        ), "Without canon nudge and healthy coherence, register must be 'executive'"
