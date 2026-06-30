"""Tests for core/skills — registry, executor, and consent gating."""
from __future__ import annotations

import pytest

from core.skills.registry import Skill, SkillCategory, SkillRegistry
from core.skills.executor import SkillExecutor, SkillStatus


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_skill(name: str = "echo", requires_consent: bool = False) -> Skill:
    return Skill(
        name=name,
        description=f"Echo skill '{name}'",
        handler=lambda text="": text.upper(),
        category=SkillCategory.CUSTOM,
        required_params=["text"],
        requires_consent=requires_consent,
    )


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestSkillRegistry:
    def test_register_and_get(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill("echo"))
        assert reg.get("echo") is not None

    def test_duplicate_raises(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill("echo"))
        with pytest.raises(ValueError):
            reg.register(_make_skill("echo"))

    def test_require_missing_raises(self) -> None:
        reg = SkillRegistry()
        with pytest.raises(KeyError):
            reg.require("nope")

    def test_list_by_category(self) -> None:
        reg = SkillRegistry()
        reg.register(Skill("mem", "memory", lambda: None, SkillCategory.MEMORY))
        reg.register(Skill("comp", "compute", lambda: None, SkillCategory.COMPUTATION))
        mem_skills = reg.list_by_category(SkillCategory.MEMORY)
        assert len(mem_skills) == 1
        assert mem_skills[0].name == "mem"

    def test_search_by_name(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill("fetch_page"))
        results = reg.search("fetch")
        assert any(s.name == "fetch_page" for s in results)

    def test_search_by_tag(self) -> None:
        reg = SkillRegistry()
        skill = Skill("tag_skill", "tagged", lambda: None, tags=["web", "search"])
        reg.register(skill)
        results = reg.search("web")
        assert results[0].name == "tag_skill"

    def test_stats(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill("s1", requires_consent=True))
        reg.register(_make_skill("s2", requires_consent=False))
        stats = reg.stats()
        assert stats["total"] == 2
        assert stats["consent_required"] == 1

    def test_contains(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill())
        assert "echo" in reg
        assert "missing" not in reg


# ---------------------------------------------------------------------------
# Executor tests
# ---------------------------------------------------------------------------

class TestSkillExecutor:
    def test_run_success(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill())
        executor = SkillExecutor(reg)
        result = executor.run("echo", {"text": "hello"})
        assert result.ok
        assert result.output == "HELLO"

    def test_run_not_found(self) -> None:
        executor = SkillExecutor(SkillRegistry())
        result = executor.run("ghost")
        assert result.status == SkillStatus.NOT_FOUND

    def test_run_missing_params(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill())
        executor = SkillExecutor(reg)
        result = executor.run("echo", {})
        assert result.status == SkillStatus.MISSING_PARAMS

    def test_run_handler_exception(self) -> None:
        def boom(**_: object) -> None:
            raise RuntimeError("exploded")

        reg = SkillRegistry()
        reg.register(Skill("boom", "explodes", boom))
        executor = SkillExecutor(reg)
        result = executor.run("boom")
        assert result.status == SkillStatus.FAILED
        assert "exploded" in (result.error or "")

    def test_consent_allowed(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill("guarded", requires_consent=True))
        executor = SkillExecutor(reg, consent_checker=lambda name, params: True)
        result = executor.run("guarded", {"text": "ok"})
        assert result.ok

    def test_consent_denied(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill("guarded", requires_consent=True))
        executor = SkillExecutor(reg, consent_checker=lambda name, params: False)
        result = executor.run("guarded", {"text": "ok"})
        assert result.status == SkillStatus.BLOCKED

    def test_duration_ms_populated(self) -> None:
        reg = SkillRegistry()
        reg.register(_make_skill())
        executor = SkillExecutor(reg)
        result = executor.run("echo", {"text": "time"})
        assert result.duration_ms >= 0
