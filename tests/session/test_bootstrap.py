"""Unit tests: SessionBootstrap — 10-step init sequence."""

import pytest
from core.ontology import GAIARuntime
from core.session.architect import ArchitectRepository
from core.session.bootstrap import SessionBootstrap
from core.session.result import SessionState


@pytest.fixture
def runtime():
    r = GAIARuntime()
    r.register_gaia()
    return r


@pytest.fixture
def bootstrap(runtime):
    return SessionBootstrap(
        runtime=runtime,
        architect_repo=ArchitectRepository(),
    )


class TestSessionBootstrap:
    def test_run_returns_open_session(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert result.state == SessionState.OPEN

    def test_session_id_is_uuid(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert len(result.session_id) == 36

    def test_architect_loaded(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen", foundation_statement="Build GAIA")
        assert result.architect_name == "Kyle Steen"
        assert result.architect_id != ""

    def test_gaian_id_assigned(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert result.gaian_id != ""

    def test_bootstrap_log_has_all_steps(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        steps = [entry for entry in result.bootstrap_log if entry.startswith("[STEP")]
        # Should have entries for all 10 steps
        step_numbers = {int(s.split("]")[0].replace("[STEP ", "")) for s in steps}
        assert step_numbers == {1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

    def test_first_session_flag(self, bootstrap):
        result = bootstrap.run(architect_name="New Architect")
        assert result.is_first_session

    def test_second_session_not_first(self, bootstrap, runtime):
        bootstrap.run(architect_name="Kyle Steen")
        # Second session with same architect
        bootstrap2 = SessionBootstrap(runtime=runtime, architect_repo=bootstrap._architect_repo)
        result2 = bootstrap2.run(architect_name="Kyle Steen")
        assert not result2.is_first_session

    def test_stage_report_present(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert result.stage_report is not None
        assert result.stage_report.stage in ("NIGREDO", "ALBEDO", "CITRINITAS", "RUBEDO")

    def test_circadian_phase_present(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert result.circadian_phase is not None

    def test_shadow_report_present(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert result.shadow_report is not None

    def test_opening_prompt_generated(self, bootstrap):
        result = bootstrap.run(architect_name="Kyle Steen")
        assert len(result.opening_system_prompt) > 0
        assert "GAIA SESSION CONTEXT" in result.opening_system_prompt

    def test_space_context_in_prompt(self, bootstrap):
        result = bootstrap.run(
            architect_name="Kyle Steen",
            space_context="GAIA-OS Development Space"
        )
        assert "GAIA-OS Development Space" in result.opening_system_prompt
