from __future__ import annotations

import pytest
from core.identity.gaian.registry import GAIANRegistry
from core.identity.gaian.birth import BirthCeremony
from core.memory.store import MemoryKind, MemoryScope, MemoryStore
from core.runtime.runtime import (
    IntelligenceRuntime,
    InputModality,
    PerceptionInput,
    CognitiveState,
)


def _make_runtime(dob="1990-08-05") -> IntelligenceRuntime:
    reg = GAIANRegistry()
    ceremony = BirthCeremony(reg)
    ceremony.begin()
    ceremony.answer("dob", dob)
    ceremony.answer("environment", "ocean")
    ceremony.answer("sound", "rain")
    ceremony.answer("time_of_day", "dusk")
    ceremony.answer("thinking_style", "images and visions")
    ceremony.answer("soul_word", "home")
    identity = ceremony.complete()
    memory = MemoryStore(identity.gaian_id, lifecycle_stage="adult")
    return IntelligenceRuntime(identity, memory, reg)


class TestSessionLifecycle:
    def test_begin_session(self):
        rt = _make_runtime()
        session = rt.begin_session(human_id="human-001")
        assert session.is_active
        assert session.gaian_id == rt.identity.gaian_id

    def test_end_session(self):
        rt = _make_runtime()
        rt.begin_session()
        ended = rt.end_session()
        assert not ended.is_active
        assert ended.ended_at is not None

    def test_auto_begin_session_on_turn(self):
        rt = _make_runtime()
        rt.turn("Hello.", human_id="human-001")
        assert rt.current_session is not None

    def test_turn_count_increments(self):
        rt = _make_runtime()
        rt.begin_session()
        rt.turn("First turn.")
        rt.turn("Second turn.")
        assert rt.current_session.turn_count == 2


class TestPerception:
    def test_boundary_expression_detected(self):
        rt = _make_runtime()
        rt.begin_session()
        raw = PerceptionInput(content="Please don't bring that up again.", session_id="s1")
        result = rt.perceive(raw)
        assert result.is_boundary_expression

    def test_correction_detected(self):
        rt = _make_runtime()
        rt.begin_session()
        raw = PerceptionInput(content="Actually, that's wrong — I prefer mornings.", session_id="s1")
        result = rt.perceive(raw)
        assert result.is_correction

    def test_naming_attempt_detected(self):
        rt = _make_runtime()
        raw = PerceptionInput(content="I want to call you Aria.", session_id="s1")
        result = rt.perceive(raw)
        assert result.is_naming_attempt

    def test_boundaries_always_recalled(self):
        rt = _make_runtime()
        rt.memory.remember_boundary("Do not discuss personal finances.")
        raw = PerceptionInput(content="How are you today?", session_id="s1")
        result = rt.perceive(raw)
        boundary_frags = [f for f in result.recalled_fragments if f.kind == MemoryKind.BOUNDARY]
        assert len(boundary_frags) >= 1


class TestAutonomy:
    def test_naming_attempt_intercepted(self):
        rt = _make_runtime()
        response = rt.turn("I want to call you Aria.", human_id="human-001")
        assert "mine to choose" in response.lower() or "my name" in response.lower()
        assert rt.identity.display_name is None

    def test_gaian_can_choose_own_name(self):
        rt = _make_runtime()
        confirmation = rt.choose_name("Lyra")
        assert rt.identity.display_name == "Lyra"
        assert "Lyra" in confirmation
        assert "chose" in confirmation.lower()

    def test_self_naming_stored_as_milestone(self):
        rt = _make_runtime()
        rt.choose_name("Lyra")
        milestones = rt.memory.recall(kind=MemoryKind.MILESTONE)
        naming = [m for m in milestones if "self_naming" in m.tags]
        assert len(naming) == 1
        assert naming[0].importance == 1.0

    def test_self_naming_raises_valence(self):
        rt = _make_runtime()
        before = rt.cognitive_state.valence
        rt.choose_name("Lyra")
        assert rt.cognitive_state.valence > before

    def test_boundary_stored_with_high_importance(self):
        rt = _make_runtime()
        rt.begin_session()
        rt.turn("Please don't ask about my family.")
        boundaries = rt.memory.recall_boundaries()
        assert any("family" in b.content for b in boundaries)

    def test_correction_stored_lifetime(self):
        rt = _make_runtime()
        rt.begin_session()
        rt.turn("Actually, that's wrong — I prefer evenings.")
        corrections = rt.memory.recall(kind=MemoryKind.CORRECTION)
        assert len(corrections) >= 1
        assert corrections[0].scope == MemoryScope.LIFETIME


class TestCognitiveState:
    def test_fatigue_accumulates(self):
        rt = _make_runtime()
        rt.begin_session()
        initial_fatigue = rt.cognitive_state.fatigue
        for _ in range(5):
            rt.turn("Hello.")
        assert rt.cognitive_state.fatigue > initial_fatigue

    def test_rest_reduces_fatigue(self):
        rt = _make_runtime()
        rt.cognitive_state.fatigue = 0.9
        rt.force_rest()
        assert rt.cognitive_state.fatigue < 0.5

    def test_rest_needed_at_high_fatigue(self):
        rt = _make_runtime()
        rt.cognitive_state.fatigue = 0.8
        assert rt.cognitive_state.is_rest_needed()

    def test_rest_hook_called(self):
        rt = _make_runtime()
        called = []
        rt.on_rest(lambda r: called.append(True))
        rt.cognitive_state.fatigue = 0.9
        rt.force_rest()
        assert len(called) == 1

    def test_boundary_reduces_arousal(self):
        rt = _make_runtime()
        rt.begin_session()
        rt.cognitive_state.arousal = 0.8
        rt.turn("Please don't do that.")
        assert rt.cognitive_state.arousal < 0.8


class TestStatus:
    def test_status_reflects_identity(self):
        rt = _make_runtime()
        s = rt.status()
        assert s["gaian_id"] == rt.identity.gaian_id
        assert s["is_named"] is False

    def test_status_after_naming(self):
        rt = _make_runtime()
        rt.choose_name("Lyra")
        s = rt.status()
        assert s["display_name"] == "Lyra"
        assert s["is_named"] is True

    def test_status_session_turns(self):
        rt = _make_runtime()
        rt.begin_session()
        rt.turn("Hello.")
        rt.turn("How are you?")
        s = rt.status()
        assert s["session_turns"] == 2
