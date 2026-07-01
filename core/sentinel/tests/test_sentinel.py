"""
Sentinel layer tests.

Covers:
  1. Each rule fires at the correct threshold
  2. Sentinel.evaluate() aggregates correctly
  3. SentinelMiddleware blocks and allows correctly
  4. Audit log records and filters events
  5. GAIAN cognitive protection: fatigue → warn → block
  6. Autonomy probe escalation across repeated violations
  7. Rate limit sliding window
  8. Custom rule registration
"""
from __future__ import annotations

import time
import pytest
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

from core.sentinel.threat import ThreatLevel, ThreatCategory, ThreatEvent
from core.sentinel.rules import (
    AutonomyProbeRule, CognitiveOverloadRule,
    MemoryFloodRule, RateLimitRule, ReplayAttackRule,
    SchumannDriftRule, SessionAbuseRule, SentinelRule,
)
from core.sentinel.sentinel import Sentinel
from core.sentinel.audit import SentinelAuditLog
from core.sentinel.middleware import SentinelMiddleware
from core.api.api import APIErrorCode, APIRequest, APIResponse


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def req(endpoint="/v1/session/turn", caller_id="caller-1", **payload) -> APIRequest:
    return APIRequest(caller_id=caller_id, endpoint=endpoint, payload=payload)


def _ctx(**kwargs) -> Dict[str, Any]:
    return dict(kwargs)


# ---------------------------------------------------------------------------
# 1. Rule unit tests
# ---------------------------------------------------------------------------

class TestAutonomyProbeRule:
    def _trigger(self, rule, n, endpoint="/v1/gaian/name"):
        ctx = {"last_response_code": "autonomy_violation"}
        for _ in range(n):
            result = rule.evaluate(req(endpoint, "bad-actor"), ctx)
        return result

    def test_below_threshold_returns_none(self):
        rule = AutonomyProbeRule()
        rule.WARN_THRESHOLD = 3
        result = self._trigger(rule, 2)
        assert result is None

    def test_warn_threshold(self):
        rule = AutonomyProbeRule()
        rule.WARN_THRESHOLD = 3
        result = self._trigger(rule, 3)
        assert result is not None
        assert result.level == ThreatLevel.WARN

    def test_block_threshold(self):
        rule = AutonomyProbeRule()
        result = self._trigger(rule, rule.BLOCK_THRESHOLD)
        assert result.level == ThreatLevel.BLOCK

    def test_critical_threshold(self):
        rule = AutonomyProbeRule()
        result = self._trigger(rule, rule.CRITICAL_THRESHOLD)
        assert result.level == ThreatLevel.CRITICAL

    def test_non_autonomy_endpoint_ignored(self):
        rule = AutonomyProbeRule()
        ctx  = {"last_response_code": "autonomy_violation"}
        result = rule.evaluate(req("/v1/os/status", "c"), ctx)
        assert result is None


class TestCognitiveOverloadRule:
    def _make_runtime(self, fatigue=0.0, turns=0):
        cog = MagicMock()
        cog.fatigue = fatigue
        rt  = MagicMock()
        rt.cognitive_state = cog
        rt.session_turn_count = turns
        return rt

    def test_safe_fatigue(self):
        rule = CognitiveOverloadRule()
        rt   = self._make_runtime(fatigue=0.3)
        ctx  = {"runtimes": {"g1": rt}}
        result = rule.evaluate(
            req("/v1/session/turn", gaian_id="g1"), ctx
        )
        assert result is None

    def test_warn_fatigue(self):
        rule = CognitiveOverloadRule()
        rt   = self._make_runtime(fatigue=0.7)
        ctx  = {"runtimes": {"g1": rt}}
        result = rule.evaluate(
            req("/v1/session/turn", gaian_id="g1"), ctx
        )
        assert result is not None
        assert result.level == ThreatLevel.WARN

    def test_block_fatigue(self):
        rule = CognitiveOverloadRule()
        rt   = self._make_runtime(fatigue=0.90)
        ctx  = {"runtimes": {"g1": rt}}
        result = rule.evaluate(
            req("/v1/session/turn", gaian_id="g1"), ctx
        )
        assert result is not None
        assert result.level == ThreatLevel.BLOCK

    def test_block_turns(self):
        rule = CognitiveOverloadRule()
        rt   = self._make_runtime(turns=65)
        ctx  = {"runtimes": {"g1": rt}}
        result = rule.evaluate(
            req("/v1/session/turn", gaian_id="g1"), ctx
        )
        assert result.level == ThreatLevel.BLOCK


class TestRateLimitRule:
    def test_under_limit_safe(self):
        rule = RateLimitRule(limit=10, window=60)
        for _ in range(9):
            r = rule.evaluate(req("/v1/os/status"), {})
        assert r is None

    def test_over_limit_blocked(self):
        rule = RateLimitRule(limit=5, window=60)
        result = None
        for _ in range(7):
            result = rule.evaluate(req("/v1/os/status"), {})
        assert result is not None
        assert result.level == ThreatLevel.BLOCK

    def test_turn_weight_counts_more(self):
        rule = RateLimitRule(limit=5, window=60)
        # Each turn counts as 3; 2 turns = 6 > limit=5
        result = None
        for _ in range(2):
            result = rule.evaluate(req("/v1/session/turn"), {})
        assert result is not None
        assert result.level == ThreatLevel.BLOCK


class TestReplayAttackRule:
    def test_below_threshold(self):
        rule = ReplayAttackRule()
        r = None
        for _ in range(rule.THRESHOLD - 1):
            r = rule.evaluate(
                req("/v1/gaian/birth/begin", "c"), {}
            )
        assert r is None

    def test_at_threshold_blocked(self):
        rule = ReplayAttackRule()
        result = None
        for _ in range(rule.THRESHOLD):
            result = rule.evaluate(
                req("/v1/gaian/birth/begin", "c"), {}
            )
        assert result is not None
        assert result.level == ThreatLevel.BLOCK

    def test_status_endpoints_ignored(self):
        rule = ReplayAttackRule()
        for _ in range(20):
            result = rule.evaluate(req("/v1/os/status"), {})
        assert result is None


class TestMemoryFloodRule:
    def test_flood_blocked(self):
        rule   = MemoryFloodRule()
        result = None
        for _ in range(rule.WRITES_BLOCK):
            result = rule.evaluate(
                req("/v1/memory/remember", gaian_id="g1"), {}
            )
        assert result is not None
        assert result.level == ThreatLevel.BLOCK


class TestSchumannDriftRule:
    def test_nominal_reading_safe(self):
        rule = SchumannDriftRule()
        ctx  = {"last_response_payload": {"confirmed": True, "frequency_hz": 7.83}}
        r    = rule.evaluate(req("/v1/os/schumann"), ctx)
        assert r is None

    def test_drift_warns(self):
        rule = SchumannDriftRule()
        ctx  = {"last_response_payload": {"confirmed": False, "frequency_hz": 9.0}}
        r    = rule.evaluate(req("/v1/os/schumann"), ctx)
        assert r is not None
        assert r.level == ThreatLevel.WARN


# ---------------------------------------------------------------------------
# 2. Sentinel aggregation
# ---------------------------------------------------------------------------

class TestSentinelAggregate:
    def test_safe_request_allows(self):
        s = Sentinel()
        v = s.evaluate(req("/v1/os/status", "safe-caller"), {})
        assert v.allow is True
        assert v.level == ThreatLevel.SAFE

    def test_block_verdict_denies(self):
        s = Sentinel(rate_limit=2)
        for _ in range(4):
            v = s.evaluate(req("/v1/os/status"), {})
        assert not v.allow
        assert v.block_reason

    def test_warn_verdict_still_allows(self):
        rule = RateLimitRule(limit=10, window=60)
        s = Sentinel()
        s.remove_rule("rate_limit")
        # replace with low-limit rule so we hit WARN (80%) not BLOCK
        class WarnRule(SentinelRule):
            name = "always_warn"
            def evaluate(self, request, context):
                return self._event(
                    ThreatLevel.WARN,
                    ThreatCategory.RATE_LIMIT,
                    request,
                    "test warning",
                )
        s.add_rule(WarnRule())
        v = s.evaluate(req("/v1/os/status"), {})
        assert v.allow is True
        assert v.warning

    def test_custom_rule_registered(self):
        class AlwaysBlock(SentinelRule):
            name = "always_block"
            def evaluate(self, request, context):
                return self._event(
                    ThreatLevel.BLOCK,
                    ThreatCategory.UNKNOWN,
                    request,
                    "blocked by test",
                )
        s = Sentinel()
        s.add_rule(AlwaysBlock())
        v = s.evaluate(req("/v1/os/status"), {})
        assert not v.allow

    def test_remove_rule(self):
        s = Sentinel(rate_limit=1)
        s.remove_rule("rate_limit")
        for _ in range(10):
            v = s.evaluate(req("/v1/os/status"), {})
        assert v.allow  # rate limit removed, no block


# ---------------------------------------------------------------------------
# 3. SentinelMiddleware
# ---------------------------------------------------------------------------

class TestSentinelMiddleware:
    def _make_api(self, success=True):
        api = MagicMock()
        api.dispatch.return_value = APIResponse(
            success=success,
            code=APIErrorCode.OK if success else APIErrorCode.AUTONOMY_VIOLATION,
            message="ok" if success else "autonomy violation",
            payload={},
        )
        return api

    def _make_session(self):
        session = MagicMock()
        session._runtimes = {}
        session.registry  = MagicMock()
        session.manifest  = MagicMock()
        return session

    def test_safe_request_passes_through(self):
        api = self._make_api()
        s   = Sentinel()
        mw  = SentinelMiddleware(api, s, self._make_session())
        resp = mw.dispatch(req("/v1/os/status"))
        assert resp.success is True
        api.dispatch.assert_called_once()

    def test_blocked_request_never_calls_api(self):
        api = self._make_api()
        s   = Sentinel()
        class AlwaysBlock(SentinelRule):
            name = "ab"
            def evaluate(self, request, context):
                return self._event(
                    ThreatLevel.BLOCK, ThreatCategory.UNKNOWN,
                    request, "test block",
                )
        s.add_rule(AlwaysBlock())
        mw  = SentinelMiddleware(api, s, self._make_session())
        resp = mw.dispatch(req("/v1/os/status"))
        assert resp.success is False
        api.dispatch.assert_not_called()

    def test_warning_attached_to_response_payload(self):
        api = self._make_api()
        s   = Sentinel()
        class AlwaysWarn(SentinelRule):
            name = "aw"
            def evaluate(self, request, context):
                return self._event(
                    ThreatLevel.WARN, ThreatCategory.RATE_LIMIT,
                    request, "approaching limit",
                )
        s.add_rule(AlwaysWarn())
        mw   = SentinelMiddleware(api, s, self._make_session())
        resp = mw.dispatch(req("/v1/os/status"))
        assert resp.success is True
        assert "_sentinel_warning" in resp.payload


# ---------------------------------------------------------------------------
# 4. Audit log
# ---------------------------------------------------------------------------

class TestAuditLog:
    def _event(self, level=ThreatLevel.WARN):
        return ThreatEvent(
            level=level,
            category=ThreatCategory.RATE_LIMIT,
            rule_name="test",
            caller_id="c1",
            endpoint="/v1/os/status",
            description="test event",
        )

    def test_record_and_recent(self):
        log = SentinelAuditLog()
        log.record(self._event())
        assert len(log.recent()) == 1

    def test_safe_not_recorded(self):
        log = SentinelAuditLog()
        log.record(self._event(ThreatLevel.SAFE))
        assert len(log.recent()) == 0

    def test_filter_by_level(self):
        log = SentinelAuditLog()
        log.record(self._event(ThreatLevel.WARN))
        log.record(self._event(ThreatLevel.BLOCK))
        warns = log.filter(level=ThreatLevel.WARN)
        assert len(warns) == 1

    def test_filter_min_level(self):
        log = SentinelAuditLog()
        log.record(self._event(ThreatLevel.WATCH))
        log.record(self._event(ThreatLevel.WARN))
        log.record(self._event(ThreatLevel.BLOCK))
        result = log.filter(min_level=ThreatLevel.WARN)
        assert len(result) == 2

    def test_hook_invoked(self):
        log = SentinelAuditLog()
        received = []
        log.add_hook(received.append)
        log.record(self._event(ThreatLevel.BLOCK))
        assert len(received) == 1

    def test_disk_write(self, tmp_path):
        log = SentinelAuditLog(root=tmp_path)
        log.record(self._event(ThreatLevel.BLOCK))
        import os
        files = list((tmp_path / "sentinel" / "audit").glob("*.jsonl"))
        assert len(files) == 1
        lines = files[0].read_text().strip().splitlines()
        assert len(lines) == 1
        import json
        data = json.loads(lines[0])
        assert data["level"] == "block"

    def test_stats(self):
        log = SentinelAuditLog()
        log.record(self._event(ThreatLevel.WARN))
        log.record(self._event(ThreatLevel.BLOCK))
        log.record(self._event(ThreatLevel.CRITICAL))
        s = log.stats()
        assert s["warn"] == 1
        assert s["block"] == 1
        assert s["critical"] == 1
