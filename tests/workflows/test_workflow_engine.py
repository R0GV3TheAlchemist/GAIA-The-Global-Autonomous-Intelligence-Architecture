"""Tests for core/workflows — plan model and engine execution."""
from __future__ import annotations

import pytest

from core.skills.registry import Skill, SkillRegistry
from core.skills.executor import SkillExecutor
from core.workflows.plan import InputSource, StepInput, Workflow, WorkflowStep
from core.workflows.engine import WorkflowEngine, WorkflowStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_engine() -> tuple[WorkflowEngine, SkillRegistry]:
    reg = SkillRegistry()
    executor = SkillExecutor(reg)
    engine = WorkflowEngine(executor)
    return engine, reg


def _add_echo(reg: SkillRegistry, name: str = "echo") -> None:
    reg.register(Skill(
        name=name,
        description="echo",
        handler=lambda text="": f"ECHO:{text}",
        required_params=["text"],
    ))


# ---------------------------------------------------------------------------
# Plan model
# ---------------------------------------------------------------------------

class TestWorkflowPlan:
    def test_step_ids(self) -> None:
        wf = Workflow(
            workflow_id="wf1",
            name="test",
            steps=[
                WorkflowStep("s1", "echo"),
                WorkflowStep("s2", "echo"),
            ]
        )
        assert wf.step_ids() == ["s1", "s2"]

    def test_get_step_found(self) -> None:
        step = WorkflowStep("s1", "echo")
        wf = Workflow(workflow_id="wf1", name="t", steps=[step])
        assert wf.get_step("s1") is step

    def test_get_step_missing(self) -> None:
        wf = Workflow(workflow_id="wf1", name="t")
        assert wf.get_step("nope") is None


# ---------------------------------------------------------------------------
# Engine execution
# ---------------------------------------------------------------------------

class TestWorkflowEngine:
    def test_single_step_static_input(self) -> None:
        engine, reg = _make_engine()
        _add_echo(reg)
        wf = Workflow(
            workflow_id="wf1",
            name="single",
            steps=[
                WorkflowStep(
                    step_id="e1",
                    skill_name="echo",
                    inputs=[StepInput("text", InputSource.STATIC, static_value="hello")],
                )
            ]
        )
        run = engine.run(wf)
        assert run.ok
        assert run.output_of("e1") == "ECHO:hello"

    def test_workflow_input_resolution(self) -> None:
        engine, reg = _make_engine()
        _add_echo(reg)
        wf = Workflow(
            workflow_id="wf2",
            name="wf_input",
            steps=[
                WorkflowStep(
                    step_id="e1",
                    skill_name="echo",
                    inputs=[StepInput("text", InputSource.WORKFLOW, workflow_key="msg")],
                )
            ]
        )
        run = engine.run(wf, inputs={"msg": "from_workflow"})
        assert run.output_of("e1") == "ECHO:from_workflow"

    def test_step_output_chaining(self) -> None:
        engine, reg = _make_engine()
        _add_echo(reg, "e1_skill")
        reg.register(Skill(
            name="upper",
            description="upper",
            handler=lambda text="": text.upper(),
            required_params=["text"],
        ))
        wf = Workflow(
            workflow_id="wf3",
            name="chain",
            steps=[
                WorkflowStep(
                    step_id="step1",
                    skill_name="e1_skill",
                    inputs=[StepInput("text", InputSource.STATIC, static_value="gaia")],
                ),
                WorkflowStep(
                    step_id="step2",
                    skill_name="upper",
                    inputs=[StepInput("text", InputSource.STEP, step_ref="step1")],
                ),
            ]
        )
        run = engine.run(wf)
        assert run.ok
        assert run.output_of("step2") == "ECHO:GAIA"

    def test_halt_on_failure(self) -> None:
        engine, reg = _make_engine()
        reg.register(Skill("fail", "always fails", lambda: 1/0))
        _add_echo(reg)
        wf = Workflow(
            workflow_id="wf4",
            name="halt",
            steps=[
                WorkflowStep("s1", "fail", halt_on_failure=True),
                WorkflowStep(
                    "s2", "echo",
                    inputs=[StepInput("text", InputSource.STATIC, static_value="should not run")]
                ),
            ]
        )
        run = engine.run(wf)
        assert run.status == WorkflowStatus.HALTED
        assert len(run.step_runs) == 1

    def test_continue_on_failure(self) -> None:
        engine, reg = _make_engine()
        reg.register(Skill("fail", "always fails", lambda: 1/0))
        _add_echo(reg)
        wf = Workflow(
            workflow_id="wf5",
            name="continue",
            steps=[
                WorkflowStep("s1", "fail", halt_on_failure=False),
                WorkflowStep(
                    "s2", "echo",
                    inputs=[StepInput("text", InputSource.STATIC, static_value="still ran")]
                ),
            ]
        )
        run = engine.run(wf)
        assert run.status == WorkflowStatus.COMPLETED
        assert len(run.step_runs) == 2
        assert run.output_of("s2") == "ECHO:still ran"

    def test_run_summary(self) -> None:
        engine, reg = _make_engine()
        _add_echo(reg)
        wf = Workflow(
            workflow_id="wf6",
            name="summary",
            steps=[
                WorkflowStep(
                    "s1", "echo",
                    inputs=[StepInput("text", InputSource.STATIC, static_value="x")]
                )
            ]
        )
        run = engine.run(wf)
        summary = run.summary()
        assert summary["steps_ok"] == 1
        assert summary["status"] == "completed"
