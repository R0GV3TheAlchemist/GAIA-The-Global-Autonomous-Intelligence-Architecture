"""pytest — SelfHealingEngine integration tests — Issue #187."""

from __future__ import annotations

import asyncio
import pytest

from sidecar.resilience.retry_policy import RetryableError, NonRetryableError, WorkflowFailure
from sidecar.resilience.degraded_fallbacks import DEGRADED_FALLBACKS
from sidecar.resilience.self_healing_engine import SelfHealingEngine, HealingResult


@pytest.fixture
def engine() -> SelfHealingEngine:
    return SelfHealingEngine()


class TestSuccessPath:
    @pytest.mark.asyncio
    async def test_returns_result_on_first_attempt(self, engine):
        async def job():
            return {"data": "ok"}

        result = await engine.execute_with_healing("crystal_graphrag", job)
        assert result.degraded is False
        assert result.result == {"data": "ok"}
        assert result.attempts == 1


class TestRetryPath:
    @pytest.mark.asyncio
    async def test_retries_on_transient_error(self, engine):
        call_count = 0

        async def job():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RetryableError("transient")
            return "recovered"

        result = await engine.execute_with_healing(
            "planetary_signal_hub", job
        )
        assert result.result == "recovered"
        assert result.attempts == 3
        assert result.degraded is False

    @pytest.mark.asyncio
    async def test_non_retryable_error_raises_immediately(self, engine):
        async def job():
            raise NonRetryableError("permission denied")

        with pytest.raises(NonRetryableError):
            await engine.execute_with_healing("article_loader", job)


class TestFallbackPath:
    @pytest.mark.asyncio
    async def test_activates_fallback_after_all_retries(self, engine):
        async def job():
            raise RetryableError("always fails")

        fallback = DEGRADED_FALLBACKS["crystal_graphrag"]
        result = await engine.execute_with_healing(
            "crystal_graphrag", job, fallback=fallback
        )
        assert result.degraded is True
        assert result.fallback_used == "downgrade_to_vector"
        assert result.dq_confidence_factor == pytest.approx(0.70)
        assert "Graph search" in result.user_message

    @pytest.mark.asyncio
    async def test_raises_workflow_failure_with_no_fallback(self, engine):
        async def job():
            raise RetryableError("always fails")

        with pytest.raises(WorkflowFailure):
            await engine.execute_with_healing(
                "crystal_graphrag", job, fallback=None
            )


class TestDQConfidenceAdjustment:
    @pytest.mark.asyncio
    async def test_dq_factor_is_1_on_success(self, engine):
        async def job():
            return "ok"

        result = await engine.execute_with_healing("soul_mirror", job)
        assert result.dq_confidence_factor == pytest.approx(1.0)

    @pytest.mark.asyncio
    async def test_dq_factor_reduced_on_fallback(self, engine):
        async def job():
            raise RetryableError("fail")

        fallback = DEGRADED_FALLBACKS["biometric_coherence"]
        result = await engine.execute_with_healing(
            "biometric_coherence", job, fallback=fallback
        )
        assert result.dq_confidence_factor == pytest.approx(0.65)
