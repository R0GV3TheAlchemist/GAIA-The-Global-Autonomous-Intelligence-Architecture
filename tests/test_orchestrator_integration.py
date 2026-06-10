"""
tests/test_orchestrator_integration.py
Sprint G-7 — Integration tests: SynergyEngine ↔ AlchemicalPipeline wiring.

These tests exercise core/orchestrator_integration.py end-to-end using
lightweight stubs so no heavyweight GAIA subsystems are required.
"""
from __future__ import annotations

import importlib
import sys
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import MagicMock, patch

import pytest


# --------------------------------------------------------------------------- #
#  Helpers / stubs                                                             #
# --------------------------------------------------------------------------- #

class _StubPipeline:
    """Minimal AlchemicalPipeline stub with register_post_stage_hook support."""

    def __init__(self) -> None:
        self._hooks: List[Callable] = []
        self._synergy_hook_installed: bool = False

    def register_post_stage_hook(self, fn: Callable) -> None:
        self._hooks.append(fn)
        self._synergy_hook_installed = True

    def run_stage(self, stage_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate a stage completing and firing all hooks."""
        for hook in self._hooks:
            hook(stage_name, output)
        return output


class _StubPipelineNoAPI:
    """Stub without register_post_stage_hook — triggers _run_stage fallback."""

    def __init__(self) -> None:
        self._synergy_hook_installed: bool = False

    def _run_stage(self, stage_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        return output


def _fresh_module():
    """Re-import orchestrator_integration with a clean _wired state."""
    mod_name = "core.orchestrator_integration"
    if mod_name in sys.modules:
        del sys.modules[mod_name]
    return importlib.import_module(mod_name)


# --------------------------------------------------------------------------- #
#  Tests: wire_orchestrator()                                                  #
# --------------------------------------------------------------------------- #

class TestWireOrchestrator:

    def test_is_wired_false_before_call(self):
        """is_wired() returns False before wire_orchestrator() is called."""
        mod = _fresh_module()
        assert mod.is_wired() is False

    def test_wire_sets_is_wired_true(self):
        """wire_orchestrator(pipeline=stub) sets is_wired() True."""
        mod = _fresh_module()
        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)
        assert mod.is_wired() is True

    def test_wire_idempotent(self):
        """Calling wire_orchestrator() twice does not add duplicate hooks."""
        mod = _fresh_module()
        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)
        hook_count_after_first = len(stub._hooks)
        mod.wire_orchestrator(pipeline=stub)  # second call
        assert len(stub._hooks) == hook_count_after_first

    def test_wire_without_pipeline_does_not_crash(self):
        """
        wire_orchestrator(pipeline=None) with no default pipeline available
        logs a warning but does NOT raise.
        """
        mod = _fresh_module()
        # Patch _get_default_pipeline to return None
        with patch.object(mod, "_get_default_pipeline", return_value=None):
            mod.wire_orchestrator(pipeline=None)  # must not raise

    def test_wire_applies_bridge_patch(self):
        """wire_orchestrator() calls _apply_bridge_patch()."""
        mod = _fresh_module()
        stub = _StubPipeline()
        with patch.object(mod, "_apply_bridge_patch") as mock_patch:
            mod.wire_orchestrator(pipeline=stub)
        mock_patch.assert_called_once()


# --------------------------------------------------------------------------- #
#  Tests: synergy hook execution                                               #
# --------------------------------------------------------------------------- #

class TestSynergyHook:

    def test_hook_attached_to_stub_pipeline(self):
        """A hook is registered on the stub pipeline after wiring."""
        from core.orchestrator_integration import wire_orchestrator
        stub = _StubPipeline()
        wire_orchestrator(pipeline=stub)
        assert len(stub._hooks) >= 1

    def test_hook_injects_synergy_key_into_output(self):
        """
        After a stage fires, the output dict gains a 'synergy' key
        containing stage, score, conflicts, resolved, metadata.
        """
        from core.orchestrator_integration import _fresh_module  # won't exist; use direct import
        from core import orchestrator_integration as mod
        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)

        output = {"keywords": ["fire", "water"], "score": 0.55}
        stub.run_stage("activation", output)

        assert "synergy" in output
        syn = output["synergy"]
        assert "stage" in syn
        assert "score" in syn
        assert syn["score"] == pytest.approx(0.55)

    def test_hook_maps_score_to_correct_stage_band(self):
        """score=0.75 → SYNTHESIS stage band."""
        from core import orchestrator_integration as mod
        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)

        output = {"score": 0.75}
        stub.run_stage("synthesis", output)
        assert output["synergy"]["stage"] == "synthesis"

    def test_hook_deduplicates_keywords(self):
        """Duplicate keywords in the output are resolved (deduped) by the engine."""
        from core import orchestrator_integration as mod
        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)

        output = {"keywords": ["fire", "FIRE", "water", "Water"], "score": 0.3}
        stub.run_stage("activation", output)
        resolved = output["synergy"]["resolved"]
        assert sorted(resolved) == ["fire", "water"]

    def test_hook_handles_missing_keywords_gracefully(self):
        """Output with no 'keywords' key must not raise."""
        from core import orchestrator_integration as mod
        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)

        output = {"score": 0.1}  # no 'keywords'
        stub.run_stage("initiation", output)  # must not raise
        assert "synergy" in output

    def test_hook_records_in_engine_history(self):
        """Every hooked stage call is persisted in SynergyEngine history."""
        from core import orchestrator_integration as mod
        from core.synergy_engine import get_synergy_engine

        engine = get_synergy_engine()
        engine.reset()  # clean slate

        stub = _StubPipeline()
        mod.wire_orchestrator(pipeline=stub)

        stub.run_stage("s1", {"score": 0.1})
        stub.run_stage("s2", {"score": 0.5})
        stub.run_stage("s3", {"score": 0.9})

        history = engine.get_history()
        # At least 3 entries (may be more if previous tests ran evaluate())
        assert len(history) >= 3


# --------------------------------------------------------------------------- #
#  Tests: _run_stage fallback path                                             #
# --------------------------------------------------------------------------- #

class TestRunStageFallback:

    def test_fallback_wraps_run_stage_when_no_register_api(self):
        """
        When the pipeline lacks register_post_stage_hook, the fallback
        wraps _run_stage and still injects 'synergy' into dict outputs.
        """
        mod = _fresh_module()
        stub = _StubPipelineNoAPI()
        mod.wire_orchestrator(pipeline=stub)
        assert stub._synergy_hook_installed is True

        output = {"score": 0.65, "keywords": ["earth"]}
        result = stub._run_stage("synthesis", output)
        assert "synergy" in result
        assert result["synergy"]["stage"] == "synthesis"

    def test_fallback_non_dict_return_passes_through_unchanged(self):
        """
        If _run_stage returns a non-dict, the wrapper must not crash and
        must return the value unchanged.
        """
        mod = _fresh_module()
        stub = _StubPipelineNoAPI()
        # Override _run_stage to return a plain string
        stub._run_stage = lambda name, *a, **kw: "raw-result"  # type: ignore
        # Wiring after override — should still work
        mod._install_synergy_hook(stub)

        result = stub._run_stage("any", {})
        assert result == "raw-result"


# --------------------------------------------------------------------------- #
#  Tests: bridge patch                                                         #
# --------------------------------------------------------------------------- #

class TestBridgePatch:

    def test_patch_adds_compute_from_adapter(self):
        """After wire_orchestrator(), SynergyEngine has compute_from_adapter."""
        from core import orchestrator_integration as mod
        from core.synergy_engine import SynergyEngine
        from core.synergy_engine_patch import SynergyEngineBridgeMixin

        mod.wire_orchestrator(pipeline=_StubPipeline())
        assert issubclass(SynergyEngine, SynergyEngineBridgeMixin)
        assert hasattr(SynergyEngine, "compute_from_adapter")

    def test_compute_from_params_delegates_to_evaluate(self):
        """compute_from_params() calls evaluate() with the unpacked dict."""
        from core.synergy_engine import get_synergy_engine
        from core.synergy_engine_patch import patch_synergy_engine

        patch_synergy_engine()
        engine = get_synergy_engine()
        result = engine.compute_from_params({"keywords": ["aether"], "score": 0.85})
        assert result.stage.value == "completion"
        assert "aether" in result.resolved
