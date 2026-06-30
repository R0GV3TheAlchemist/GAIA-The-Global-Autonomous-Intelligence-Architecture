"""
core/workflows/__init__.py

GAIA Workflow Engine — multi-step plan chaining for autonomous tasks.

A Workflow is an ordered sequence of WorkflowSteps. Each step names a
skill and declares how its inputs are resolved — from static values,
from the original workflow inputs, or from a prior step's output. The
WorkflowEngine executes steps in order, threading outputs through the
plan. Failed steps can be configured to halt the workflow or be skipped.

Canon: C01, C03
"""
from __future__ import annotations

from core.workflows.plan import Workflow, WorkflowStep, InputSource
from core.workflows.engine import WorkflowEngine, WorkflowRun, StepRun

__all__ = [
    "Workflow",
    "WorkflowStep",
    "InputSource",
    "WorkflowEngine",
    "WorkflowRun",
    "StepRun",
]
