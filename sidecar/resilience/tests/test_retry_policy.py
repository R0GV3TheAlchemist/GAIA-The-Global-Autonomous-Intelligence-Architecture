"""pytest — RetryPolicy backoff and error classification tests — Issue #187."""

from __future__ import annotations

import pytest

from sidecar.resilience.retry_policy import RetryPolicy, RetryableError, NonRetryableError


class TestBackoff:
    def test_fixed_backoff_constant(self):
        policy = RetryPolicy(backoff_strategy="fixed", base_delay_ms=500)
        assert policy.delay_seconds(1) == pytest.approx(0.5)
        assert policy.delay_seconds(3) == pytest.approx(0.5)

    def test_exponential_backoff_doubles(self):
        policy = RetryPolicy(
            backoff_strategy="exponential",
            base_delay_ms=500,
            max_delay_ms=10_000,
        )
        assert policy.delay_seconds(1) == pytest.approx(0.5)
        assert policy.delay_seconds(2) == pytest.approx(1.0)
        assert policy.delay_seconds(3) == pytest.approx(2.0)

    def test_exponential_backoff_capped(self):
        policy = RetryPolicy(
            backoff_strategy="exponential",
            base_delay_ms=500,
            max_delay_ms=1_000,
        )
        assert policy.delay_seconds(10) == pytest.approx(1.0)

    def test_jitter_backoff_within_bounds(self):
        policy = RetryPolicy(
            backoff_strategy="jitter",
            base_delay_ms=500,
            max_delay_ms=4_000,
        )
        for attempt in range(1, 6):
            delay = policy.delay_seconds(attempt)
            cap = min(0.5 * (2 ** (attempt - 1)), 4.0)
            assert 0.0 <= delay <= cap


class TestErrorClassification:
    def test_retryable_by_class_name(self):
        policy = RetryPolicy()
        assert policy.is_retryable(RetryableError("transient")) is True
        assert policy.is_retryable(TimeoutError()) is True
        assert policy.is_retryable(ConnectionError()) is True

    def test_non_retryable_by_class_name(self):
        policy = RetryPolicy()
        assert policy.is_non_retryable(NonRetryableError("perm")) is True
        assert policy.is_non_retryable(PermissionError()) is True

    def test_unknown_error_is_neither(self):
        policy = RetryPolicy()
        exc = ValueError("unknown")
        assert policy.is_retryable(exc) is False
        assert policy.is_non_retryable(exc) is False
