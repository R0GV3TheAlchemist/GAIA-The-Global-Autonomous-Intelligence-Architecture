"""pytest — CircuitBreaker state machine tests — Issue #187."""

from __future__ import annotations

import time
import pytest

from sidecar.resilience.circuit_breaker import CircuitBreaker, CircuitOpenError, CircuitState


def make_cb(**kwargs) -> CircuitBreaker:
    return CircuitBreaker(skill_id="test_skill", **kwargs)


class TestClosedState:
    def test_allows_requests_by_default(self):
        cb = make_cb()
        assert cb.allow_request() is True

    def test_stays_closed_under_threshold(self):
        cb = make_cb(failure_rate_threshold=0.5, min_calls=2)
        cb.record_success()
        cb.record_failure(Exception("err"))
        # 50 % rate — threshold is >=0.5 so it should trip.
        # Re-test with 1 failure out of 3 (33 %).
        cb2 = make_cb(failure_rate_threshold=0.5, min_calls=2)
        cb2.record_success()
        cb2.record_success()
        cb2.record_failure(Exception("err"))
        assert cb2.state == CircuitState.CLOSED

    def test_trips_when_failure_rate_exceeds_threshold(self):
        cb = make_cb(failure_rate_threshold=0.5, min_calls=2)
        cb.record_failure(Exception("a"))
        cb.record_failure(Exception("b"))
        assert cb.state == CircuitState.OPEN


class TestOpenState:
    def test_raises_circuit_open_error(self):
        cb = make_cb(failure_rate_threshold=0.5, min_calls=2, open_duration_s=999)
        cb.record_failure(Exception("a"))
        cb.record_failure(Exception("b"))
        with pytest.raises(CircuitOpenError):
            cb.allow_request()


class TestHalfOpenState:
    def test_transitions_to_half_open_after_duration(self, monkeypatch):
        cb = make_cb(
            failure_rate_threshold=0.5,
            min_calls=2,
            open_duration_s=0.01,
        )
        cb.record_failure(Exception("a"))
        cb.record_failure(Exception("b"))
        assert cb.state == CircuitState.OPEN
        time.sleep(0.02)
        assert cb.state == CircuitState.HALF_OPEN

    def test_closes_on_probe_success(self):
        cb = make_cb(
            failure_rate_threshold=0.5,
            min_calls=2,
            open_duration_s=0.01,
        )
        cb.record_failure(Exception("a"))
        cb.record_failure(Exception("b"))
        time.sleep(0.02)
        cb.allow_request()  # probe
        cb.record_success()
        assert cb.state == CircuitState.CLOSED

    def test_reopens_on_probe_failure(self):
        cb = make_cb(
            failure_rate_threshold=0.5,
            min_calls=2,
            open_duration_s=0.01,
        )
        cb.record_failure(Exception("a"))
        cb.record_failure(Exception("b"))
        time.sleep(0.02)
        cb.allow_request()  # probe
        cb.record_failure(Exception("probe_fail"))
        assert cb.state == CircuitState.OPEN
