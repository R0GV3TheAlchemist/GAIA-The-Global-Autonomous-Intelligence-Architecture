"""Unit tests: SessionSeal — immutable session close."""

import pytest
from core.ontology import GAIARuntime
from core.session.architect import ArchitectRepository
from core.session.bootstrap import SessionBootstrap
from core.session.seal import SessionSeal


@pytest.fixture
def runtime():
    r = GAIARuntime()
    r.register_gaia()
    return r


@pytest.fixture
def session_data(runtime):
    repo = ArchitectRepository()
    bootstrap = SessionBootstrap(runtime=runtime, architect_repo=repo)
    result = bootstrap.run(architect_name="Kyle Steen")
    mm = bootstrap.get_memory_manager(result.gaian_id)
    return result, mm, runtime


class TestSessionSeal:
    def test_seal_produces_record(self, session_data):
        result, mm, runtime = session_data
        seal = SessionSeal(runtime=runtime)
        record = seal.run(
            session_id=result.session_id,
            gaian_id=result.gaian_id,
            memory_manager=mm,
        )
        assert record.is_sealed

    def test_sealed_record_is_immutable(self, session_data):
        result, mm, runtime = session_data
        seal = SessionSeal(runtime=runtime)
        record = seal.run(
            session_id=result.session_id,
            gaian_id=result.gaian_id,
            memory_manager=mm,
        )
        with pytest.raises(RuntimeError, match="already sealed"):
            record.seal()

    def test_cannot_write_log_after_seal(self, session_data):
        result, mm, runtime = session_data
        seal = SessionSeal(runtime=runtime)
        record = seal.run(
            session_id=result.session_id,
            gaian_id=result.gaian_id,
            memory_manager=mm,
        )
        with pytest.raises(RuntimeError, match="Cannot write"):
            record.log_seal_step(99, "too late")

    def test_persist_records_m1_count(self, session_data):
        result, mm, runtime = session_data
        # Add records to M0
        buf = mm.get_session(result.session_id)
        buf.append("important note", tags=[])
        buf.append("another note", tags=[])

        seal = SessionSeal(runtime=runtime)
        record = seal.run(
            session_id=result.session_id,
            gaian_id=result.gaian_id,
            memory_manager=mm,
            authorise_persist=True,
        )
        # 2 user records + 1 session open record from bootstrap
        assert record.m1_records_persisted >= 2

    def test_audit_trail_records_seal(self, session_data):
        result, mm, runtime = session_data
        seal = SessionSeal(runtime=runtime)
        seal.run(
            session_id=result.session_id,
            gaian_id=result.gaian_id,
            memory_manager=mm,
        )
        trail = runtime.get_audit_trail(result.gaian_id)
        sealed_entries = trail.filter(action="SESSION_SEALED")
        assert len(sealed_entries) == 1
