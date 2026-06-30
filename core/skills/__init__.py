"""
core/skills/__init__.py

GAIA Skill Registry — the callable unit layer for the agentic loop.

A Skill is a discrete, named, permission-guarded capability that GAIA
can invoke on behalf of a Human Principal. Skills plug into the agentic
loop through the SkillRegistry and are executed by the SkillExecutor.

Canon: C01 (GAIA as orchestration layer), C03 (action_gate consent)
"""
from __future__ import annotations

from core.skills.registry import Skill, SkillRegistry, SkillCategory
from core.skills.executor import SkillExecutor, SkillResult, SkillStatus

__all__ = [
    "Skill",
    "SkillRegistry",
    "SkillCategory",
    "SkillExecutor",
    "SkillResult",
    "SkillStatus",
]
