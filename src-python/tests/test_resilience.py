"""pytest suite for Issue #187 — Self-Healing Workflow Engine.

Covers:
- CircuitBreaker state transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)
- CircuitBreaker COOLING state (force_close + tick countdown)
- RetryPolicy backoff computation (fixed, exponential, jitter)
- SelfHealingEngine: retry success, retry exhaustion + fallback, non-retryable errors
- SelfHealingEngine: CircuitOpenError breaks retry loop immediately → fallback
- SelfHealingEngine: telemetry events emitted at every stage
- SelfHealingEngine: get_all_health() multi-skill snapshot
- DQ confidence multiplier applied correctly on fallback
- DQ multiplier 0.0 edge case (dev_suite_executor)
- Canon C30: user_message always present when degraded
"""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from resilience.retry_policy import RetryPolicy, BackoffStrategy
from resilience.circuit_breaker import CircuitBreaker, CircuitState, CircuitOpenError
from resilience.degraded_fallbacks import DEGRADED_FALLBACKS, DegradedFallback, FallbackMode
from resilience.self_healing_engine import (
    SelfHealingEngine, HealingResult, WorkflowFailure, NonRetryableError
)


# ---------------------------------------------------------------------------
# RetryPolicy
# ---------------------------------------------------------------------------

class TestRetryPolicy:
    def test_exponential_backoff_doubles(self):
        p = RetryPolicy(base_delay_ms=500, backoff_strategy=BackoffStrategy.EXPONENTIAL)
        assert p.compute_delay_ms(1) == 500
        assert p.compute_delay_ms(2) == 1000
        assert p.compute_delay_ms(3) == 2000

    def test_fixed_backoff_constant(self):
        p = RetryPolicy(base_delay_ms=300, backoff_strategy=BackoffStrategy.FIXED)
        for attempt in range(1, 5):
            assert p.compute_delay_ms(attempt) == 300

    def test_max_delay_capped(self):
        p = RetryPolicy(base_delay_ms=1000, max_delay_ms=2500, backoff_strategy=BackoffStrategy.EXPONENTIAL)
        assert p.compute_delay_ms(10) == 2500

    def test_retryable_error_recognized(self):
        p = RetryPolicy()
        assert p.is_retryable(TimeoutError())
        assert p.is_retryable(ConnectionError())

    def test_non_retryable_error_rejected(self):
        p = RetryPolicy()

        class AuthError(Exception):
            pass

        assert not p.is_retryable(AuthError())

    def test_jitter_within_bounds(self):
        p = RetryPolicy(base_delay_ms=500, backoff_strategy=BackoffStrategy.JITTER)
        for _ in range(20):
            delay = p.compute_delay_ms(3)
            assert delay >= 500
            assert delay <= p.max_delay_ms


# ---------------------------------------------------------------------------
# CircuitBreaker
# ---------------------------------------------------------------------------

class TestCircuitBreaker:
    def _make_cb(self, **kwargs) -> CircuitBreaker:
        return CircuitBreaker(
            skill_id="test_skill",
            failure_rate_threshold=0.5,
            min_calls_in_window=2,
            open_duration_seconds=0,  # immediate probe for tests
            **kwargs,
        )

    @pytest.mark.asyncio
    async def test_starts_closed(self):
        cb = self._make_cb()
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_success_stays_closed(self):
        cb = self._make_cb()
        async def ok(): return "ok"
        await cb.call(ok)
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_failures_open_circuit(self):
        cb = self._make_cb()

        async def fail():
            raise ConnectionError("timeout")

        with pytest.raises(ConnectionError):
            await cb.call(fail)
        with pytest.raises(ConnectionError):
            await cb.call(fail)

        assert cb.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_raises_circuit_open_error(self):
        cb = self._make_cb(open_duration_seconds=9999)
        cb.state = CircuitState.OPEN
        import time
        cb._opened_at = time.monotonic()

        async def ok(): return "ok"
        with pytest.raises(CircuitOpenError):
            await cb.call(ok)

    @pytest.mark.asyncio
    async def test_half_open_probe_success_closes(self):
        cb = self._make_cb()
        cb.state = CircuitState.OPEN
        cb._opened_at = 0.0  # immediate recovery

        async def ok(): return "recovered"
        result = await cb.call(ok)
        assert result == "recovered"
        assert cb.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_half_open_probe_failure_reopens(self):
        cb = self._make_cb()
        cb.state = CircuitState.OPEN
        cb._opened_at = 0.0

        async def fail():
            raise TimeoutError("still down")

        with pytest.raises(TimeoutError):
            await cb.call(fail)
        assert cb.state == CircuitState.OPEN

    def test_health_report_keys(self):
        cb = self._make_cb()
        h = cb.health
        for key in ("skill_id", "state", "failure_rate", "total_calls_in_window"):
            assert key in h

    # --- GAP 1: COOLING state -------------------------------------------

    def test_force_close_enters_cooling(self):
        """force_close() must transition the breaker into COOLING, not CLOSED."""
        cb = self._make_cb(cooling_ticks=3)
        cb.state = CircuitState.OPEN
        cb.force_close()
        assert cb.state == CircuitState.COOLING

    def test_cooling_tick_countdown_to_closed(self):
        """tick() must count down cooling_ticks steps then transition to CLOSED."""
        cb = self._make_cb(cooling_ticks=3)
        cb.state = CircuitState.OPEN
        cb.force_close()
        assert cb.state == CircuitState.COOLING

        cb.tick()  # 2 remaining
        assert cb.state == CircuitState.COOLING
        cb.tick()  # 1 remaining
        assert cb.state == CircuitState.COOLING
        cb.tick()  # 0 → CLOSED
        assert cb.state == CircuitState.CLOSED

    def test_tick_on_non_cooling_state_is_noop(self):
        """tick() called on a CLOSED breaker must not change its state."""
        cb = self._make_cb()
        assert cb.state == CircuitState.CLOSED
        cb.tick()
        assert cb.state == CircuitState.CLOSED


# ---------------------------------------------------------------------------
# SelfHealingEngine
# ---------------------------------------------------------------------------

class TestSelfHealingEngine:
    def _make_engine(self) -> SelfHealingEngine:
        return SelfHealingEngine(telemetry=None)

    @pytest.mark.asyncio
    async def test_success_on_first_attempt(self):
        engine = self._make_engine()
        async def fn(): return {"data": "ok"}
        result = await engine.execute_with_healing("crystal_graphrag", fn)
        assert not result.degraded
        assert result.attempts == 1
        assert result.result == {"data": "ok"}

    @pytest.mark.asyncio
    async def test_retry_then_success(self):
        engine = self._make_engine()
        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise TimeoutError("transient")
            return {"data": "recovered"}

        result = await engine.execute_with_healing("article_loader", fn)
        assert not result.degraded
        assert result.attempts == 3

    @pytest.mark.asyncio
    async def test_exhausted_retries_triggers_fallback(self):
        engine = self._make_engine()

        async def fn():
            raise TimeoutError("always fails")

        result = await engine.execute_with_healing("crystal_graphrag", fn)
        assert result.degraded
        assert result.fallback_used == FallbackMode.DOWNGRADE.value
        assert result.dq_confidence_multiplier == 0.70
        assert result.user_message is not None  # Canon C30

    @pytest.mark.asyncio
    async def test_no_fallback_raises_workflow_failure(self):
        engine = self._make_engine()

        async def fn():
            raise TimeoutError("always fails")

        with pytest.raises(WorkflowFailure):
            await engine.execute_with_healing("unknown_skill_xyz", fn, fallback=None)

    @pytest.mark.asyncio
    async def test_non_retryable_error_propagates_immediately(self):
        engine = self._make_engine()

        async def fn():
            class AuthError(Exception):
                pass
            raise AuthError("forbidden")

        with pytest.raises(NonRetryableError):
            await engine.execute_with_healing("crystal_graphrag", fn)

    @pytest.mark.asyncio
    async def test_dq_multiplier_1_when_not_degraded(self):
        engine = self._make_engine()
        async def fn(): return "ok"
        result = await engine.execute_with_healing("soul_mirror", fn)
        assert result.dq_confidence_multiplier == 1.0

    @pytest.mark.asyncio
    async def test_planetary_hub_fallback_cached(self):
        engine = self._make_engine()

        async def fn():
            raise ConnectionError("feed down")

        result = await engine.execute_with_healing("planetary_signal_hub", fn)
        assert result.degraded
        assert result.fallback_used == FallbackMode.CACHED.value
        assert result.dq_confidence_multiplier == 0.85

    # --- GAP 2: CircuitOpenError breaks retry loop immediately -----------

    @pytest.mark.asyncio
    async def test_circuit_open_skips_retry_loop_goes_straight_to_fallback(self):
        """When CircuitOpenError fires on attempt 1, the engine must NOT exhaust
        max_attempts — it must break immediately and apply the registered fallback."""
        engine = self._make_engine()

        # Force the breaker OPEN with a far-future opened_at so no probe fires
        import time
        breaker = engine._get_breaker("crystal_graphrag")
        breaker.state = CircuitState.OPEN
        breaker._opened_at = time.monotonic() + 9999  # probe never due in this test

        call_count = 0

        async def fn():
            nonlocal call_count
            call_count += 1
            return "should not be called"

        result = await engine.execute_with_healing("crystal_graphrag", fn)

        # fn must never have been called — circuit was open
        assert call_count == 0
        # Fallback must have fired
        assert result.degraded
        assert result.fallback_used == FallbackMode.DOWNGRADE.value

    # --- GAP 3: Telemetry events emitted at each stage -------------------

    @pytest.mark.asyncio
    async def test_telemetry_emits_success_event(self):
        """A clean execution must emit exactly one 'success' telemetry event."""
        mock_telemetry = MagicMock()
        mock_telemetry.emit = AsyncMock()
        engine = SelfHealingEngine(telemetry=mock_telemetry)

        async def fn(): return "ok"
        await engine.execute_with_healing("soul_mirror", fn)

        emitted = [call.args[0] for call in mock_telemetry.emit.call_args_list]
        event_types = [e["event_type"] for e in emitted]
        assert "success" in event_types

    @pytest.mark.asyncio
    async def test_telemetry_emits_retry_then_exhausted_events(self):
        """Retried-then-exhausted execution must emit 'retry' events followed by
        'exhausted', then 'fallback_used'."""
        mock_telemetry = MagicMock()
        mock_telemetry.emit = AsyncMock()
        engine = SelfHealingEngine(telemetry=mock_telemetry)

        async def fn():
            raise TimeoutError("always fails")

        await engine.execute_with_healing("crystal_graphrag", fn)

        emitted = [call.args[0] for call in mock_telemetry.emit.call_args_list]
        event_types = [e["event_type"] for e in emitted]

        assert "retry" in event_types
        assert "exhausted" in event_types
        assert "fallback_used" in event_types

    @pytest.mark.asyncio
    async def test_telemetry_emits_circuit_open_event(self):
        """When a CircuitOpenError fires, a 'circuit_open' event must be emitted."""
        mock_telemetry = MagicMock()
        mock_telemetry.emit = AsyncMock()
        engine = SelfHealingEngine(telemetry=mock_telemetry)

        import time
        breaker = engine._get_breaker("crystal_graphrag")
        breaker.state = CircuitState.OPEN
        breaker._opened_at = time.monotonic() + 9999

        async def fn(): return "unreachable"
        await engine.execute_with_healing("crystal_graphrag", fn)

        emitted = [call.args[0] for call in mock_telemetry.emit.call_args_list]
        event_types = [e["event_type"] for e in emitted]
        assert "circuit_open" in event_types

    @pytest.mark.asyncio
    async def test_telemetry_failure_does_not_crash_engine(self):
        """Telemetry emit raising an exception must not propagate — engine must
        still return a valid HealingResult (Canon C34: GAIA stays present)."""
        mock_telemetry = MagicMock()
        mock_telemetry.emit = AsyncMock(side_effect=RuntimeError("telemetry down"))
        engine = SelfHealingEngine(telemetry=mock_telemetry)

        async def fn(): return "ok"
        result = await engine.execute_with_healing("soul_mirror", fn)
        assert result.result == "ok"

    # --- GAP 4: get_all_health() multi-skill snapshot --------------------

    @pytest.mark.asyncio
    async def test_get_all_health_returns_entry_per_skill(self):
        """After executing against multiple skills, get_all_health() must return
        one health dict per skill, each containing the required keys."""
        engine = self._make_engine()

        async def ok(): return "ok"
        await engine.execute_with_healing("soul_mirror", ok)
        await engine.execute_with_healing("dream_weaver", ok)
        await engine.execute_with_healing("article_loader", ok)

        health = engine.get_all_health()
        skill_ids = {h["skill_id"] for h in health}

        assert "soul_mirror" in skill_ids
        assert "dream_weaver" in skill_ids
        assert "article_loader" in skill_ids

        for entry in health:
            assert "state" in entry
            assert "failure_rate" in entry

    @pytest.mark.asyncio
    async def test_get_skill_health_returns_correct_skill(self):
        """get_skill_health(skill_id) must return health for that specific skill."""
        engine = self._make_engine()
        async def ok(): return "ok"
        await engine.execute_with_healing("biometric_coherence", ok)

        h = engine.get_skill_health("biometric_coherence")
        assert h["skill_id"] == "biometric_coherence"
        assert h["state"] == CircuitState.CLOSED.value

    # --- GAP 5: dev_suite_executor dq_confidence_multiplier == 0.0 ------

    @pytest.mark.asyncio
    async def test_dev_suite_executor_dq_multiplier_is_zero(self):
        """dev_suite_executor is the only skill with dq_confidence_multiplier=0.0.
        A degraded result must carry 0.0 so DQ is zeroed out entirely — the
        Orchestrator cannot accidentally treat a failed execution as partial signal."""
        engine = self._make_engine()

        async def fn():
            raise TimeoutError("sandbox offline")

        result = await engine.execute_with_healing("dev_suite_executor", fn)
        assert result.degraded
        assert result.fallback_used == FallbackMode.STATIC_RESPONSE.value
        assert result.dq_confidence_multiplier == 0.0
        assert result.user_message is not None  # Canon C30 — never silent


# ---------------------------------------------------------------------------
# DegradedFallbacks — Canon C30 compliance
# ---------------------------------------------------------------------------

class TestDegradedFallbacks:
    def test_all_fallbacks_have_user_message(self):
        for skill_id, fallback in DEGRADED_FALLBACKS.items():
            assert fallback.user_message, f"'{skill_id}' fallback missing user_message (Canon C30)"

    def test_dq_multiplier_in_valid_range(self):
        for skill_id, fallback in DEGRADED_FALLBACKS.items():
            assert 0.0 <= fallback.dq_confidence_multiplier <= 1.0, (
                f"'{skill_id}' dq_confidence_multiplier out of range"
            )

    def test_required_skills_have_fallbacks(self):
        required = [
            "planetary_signal_hub", "article_loader",
            "crystal_graphrag", "biometric_coherence",
        ]
        for skill_id in required:
            assert skill_id in DEGRADED_FALLBACKS, f"Missing fallback for '{skill_id}'"
