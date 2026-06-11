"""
core/orchestrator_integration.py
Sprint G-7 — Synergy Orchestrator ↔ AlchemicalPipeline wiring.

This module is the single seam between AlchemicalPipeline and SynergyEngine.
It is imported once at GAIA startup (see core/__init__.py or gaian_runtime.py).

Responsibilities
----------------
1. Apply the Sprint-G7 bridge mixin so SynergyEngine gains
   `compute_from_adapter()` / `compute_from_params()`.
2. Attach a post-stage hook to AlchemicalPipeline that calls
   SynergyEngine.evaluate() and stores the SynergyResult in the
   pipeline output under the key "synergy".
3. Expose `wire_orchestrator()` as the single public entry point —
   safe to call multiple times (idempotent).

Canon Refs: C01, C32
"""
from __future__ import annotations

import importlib
import logging
import sys
from typing import Any, Dict, Optional

log = logging.getLogger(__name__)

_wired: bool = False


# --------------------------------------------------------------------------- #
#  Test utility                                                                #
# --------------------------------------------------------------------------- #

def fresh_module(module_path: str):
    """Force-reimport a module (test utility for isolation)."""
    if module_path in sys.modules:
        del sys.modules[module_path]
    return importlib.import_module(module_path)


# --------------------------------------------------------------------------- #
#  Orchestrator wiring                                                         #
# --------------------------------------------------------------------------- #

def wire_orchestrator(
    pipeline: Optional[Any] = None,
) -> None:
    """
    Wire the SynergyEngine orchestrator into AlchemicalPipeline.

    Args:
        pipeline: An AlchemicalPipeline instance to wire.  When *None* the
                  module-level singleton is retrieved via
                  ``get_alchemical_pipeline()``.

    Idempotent — calling more than once is harmless.
    """
    global _wired

    # 1. Apply the bridge mixin
    _apply_bridge_patch()

    # 2. Resolve pipeline
    if pipeline is None:
        pipeline = _get_default_pipeline()

    if pipeline is None:
        log.warning("wire_orchestrator: no AlchemicalPipeline available — skipping hook install")
        return

    # 3. Install post-stage hook (idempotent)
    _install_synergy_hook(pipeline)

    _wired = True
    log.info("Synergy Orchestrator wired to AlchemicalPipeline ✓")


def is_wired() -> bool:
    """Return True once wire_orchestrator() has completed successfully."""
    return _wired


# --------------------------------------------------------------------------- #
#  Internal helpers                                                            #
# --------------------------------------------------------------------------- #

def _apply_bridge_patch() -> None:
    """Apply SynergyEngineBridgeMixin to SynergyEngine (idempotent)."""
    try:
        from core.synergy_engine_patch import SynergyEngineBridgeMixin, patch_synergy_engine
        from core.synergy_engine import SynergyEngine
        patch_synergy_engine()
        # Guarantee issubclass check passes
        if SynergyEngineBridgeMixin not in SynergyEngine.__bases__:
            SynergyEngine.__bases__ = (SynergyEngineBridgeMixin,) + SynergyEngine.__bases__
        log.debug("SynergyEngine bridge mixin applied")
    except Exception as exc:  # pragma: no cover
        log.error("Failed to apply SynergyEngine bridge patch: %s", exc)


def _get_default_pipeline() -> Optional[Any]:
    """Retrieve the module-level AlchemicalPipeline singleton, or None."""
    try:
        from core.alchemical_pipeline import get_alchemical_pipeline  # type: ignore
        return get_alchemical_pipeline()
    except (ImportError, AttributeError):
        return None


def _install_synergy_hook(pipeline: Any) -> None:
    """
    Attach a ``_synergy_hook`` to *pipeline* that is called after every
    pipeline stage completes.  Uses the ``register_post_stage_hook`` API
    if available; otherwise monkey-patches ``_run_stage``.
    """
    if getattr(pipeline, "_synergy_hook_installed", False):
        return  # already wired

    from core.synergy_engine import get_synergy_engine
    engine = get_synergy_engine()

    def _synergy_hook(stage_name: str, output: Dict[str, Any]) -> None:
        """
        Post-stage callback: evaluate the current keyword/score payload
        through SynergyEngine and attach the result to *output*.
        """
        keywords = output.get("keywords") or []
        score = float(output.get("score") or 0.0)
        synergy_result = engine.evaluate(keywords=keywords, score=score)
        output["synergy"] = synergy_result.to_dict()
        log.debug(
            "[synergy] stage=%s score=%.3f stage_band=%s",
            stage_name,
            score,
            synergy_result.stage.value,
        )

    # Preferred API ---------------------------------------------------------
    if hasattr(pipeline, "register_post_stage_hook"):
        pipeline.register_post_stage_hook(_synergy_hook)
    else:
        # Fallback: wrap _run_stage if it exists
        original_run = getattr(pipeline, "_run_stage", None)
        if original_run is not None:
            def _wrapped_run_stage(stage_name: str, *args: Any, **kwargs: Any) -> Any:
                result = original_run(stage_name, *args, **kwargs)
                if isinstance(result, dict):
                    _synergy_hook(stage_name, result)
                return result
            pipeline._run_stage = _wrapped_run_stage  # type: ignore[attr-defined]
        else:
            log.warning(
                "wire_orchestrator: pipeline has neither register_post_stage_hook "
                "nor _run_stage — synergy hook NOT installed"
            )
            return

    pipeline._synergy_hook_installed = True  # type: ignore[attr-defined]
    log.debug("Synergy hook installed on %s", type(pipeline).__name__)
