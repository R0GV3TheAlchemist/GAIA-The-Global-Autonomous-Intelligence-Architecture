"""Skill Executor — runs a registered skill with validated parameters.

The SkillExecutor is the runtime bridge between the agentic loop's
tool-call decisions and the actual Python handlers registered in the
SkillRegistry. It validates parameters, gates consent-required skills
against the action_gate, and returns a structured SkillResult.
"""
from __future__ import annotations

import asyncio
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Mapping, Optional

from core.skills.registry import Skill, SkillRegistry


class SkillStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    MISSING_PARAMS = "missing_params"
    NOT_FOUND = "not_found"


@dataclass
class SkillResult:
    skill_name: str
    status: SkillStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @property
    def ok(self) -> bool:
        return self.status == SkillStatus.SUCCESS


class SkillExecutor:
    """Executes skills from the registry with parameter validation.

    Pass a consent_checker callable to gate skills that require Human
    Principal approval before execution. The checker receives the skill
    name and the resolved params and must return True to allow execution.

    Usage:
        executor = SkillExecutor(registry)
        result = executor.run("search_web", {"query": "GAIA OS"})
    """

    def __init__(
        self,
        registry: SkillRegistry,
        consent_checker: Optional[Any] = None,
    ) -> None:
        self.registry = registry
        self.consent_checker = consent_checker

    def run(
        self,
        skill_name: str,
        params: Mapping[str, Any] | None = None,
    ) -> SkillResult:
        params = dict(params or {})
        start = datetime.now(timezone.utc)

        skill = self.registry.get(skill_name)
        if skill is None:
            return SkillResult(
                skill_name=skill_name,
                status=SkillStatus.NOT_FOUND,
                error=f"Skill '{skill_name}' is not registered.",
            )

        missing = self._check_params(skill, params)
        if missing:
            return SkillResult(
                skill_name=skill_name,
                status=SkillStatus.MISSING_PARAMS,
                error=f"Missing required params: {missing}",
            )

        if skill.requires_consent and self.consent_checker is not None:
            allowed = self.consent_checker(skill_name, params)
            if not allowed:
                return SkillResult(
                    skill_name=skill_name,
                    status=SkillStatus.BLOCKED,
                    error="Consent denied by action_gate.",
                )

        try:
            if skill.is_async:
                output = asyncio.get_event_loop().run_until_complete(
                    skill.handler(**params)
                )
            else:
                output = skill.handler(**params)
            end = datetime.now(timezone.utc)
            duration_ms = (end - start).total_seconds() * 1000
            return SkillResult(
                skill_name=skill_name,
                status=SkillStatus.SUCCESS,
                output=output,
                duration_ms=duration_ms,
            )
        except Exception as exc:
            end = datetime.now(timezone.utc)
            duration_ms = (end - start).total_seconds() * 1000
            return SkillResult(
                skill_name=skill_name,
                status=SkillStatus.FAILED,
                error=f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}",
                duration_ms=duration_ms,
            )

    @staticmethod
    def _check_params(skill: Skill, params: Dict[str, Any]) -> list[str]:
        return [p for p in skill.required_params if p not in params]
