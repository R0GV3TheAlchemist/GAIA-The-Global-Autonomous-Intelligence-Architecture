"""
core/gaian_runtime_patch.py
Surgical patch for GAIANRuntime — Spiritus auto-injection into goal birth.

Apply once at app startup (server.py or main.py):

    from core.gaian_runtime_patch import patch_runtime
    patch_runtime(runtime_instance)

What this adds to GAIANRuntime:

  1. spiritu_context() — returns the live Spiritus snapshot
     (stage, pneuma_flow, breath_rhythm, alchemical_quality).
     Used by goals_router._live_spiritu() and any frontend GET.

  2. create_goal() — new method that calls goal_store.create()
     with auto-injected Spiritus fields. Replaces the old
     add_goal() for all new-style goal creation.

  3. Registers the runtime with goals_router.set_runtime()
     so POST /goals auto-stamps every new goal.

The original add_goal() method remains untouched (backward compat
with the Phase 3 GoalRegistry).
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def spiritu_context(self) -> Dict[str, Any]:
    """
    Return the GAIAN's current Spiritus state as a plain dict.
    Safe to call at any time — reads from the in-memory spiritu_state.
    """
    sp = self.spiritu_state
    # SpirituState.stage is a SpirituStage enum; .name gives the canonical string
    stage_name = sp.stage.name if hasattr(sp.stage, "name") else str(sp.stage)
    return {
        "stage":             stage_name,
        "pneuma_flow":       round(sp.pneuma_flow, 4),
        "breath_rhythm":     round(sp.breath_rhythm, 4),
        "pneuma_quality":    getattr(sp, "pneuma_quality", ""),
        "coagulation":       sp.coagulation_reached,
        "exchanges_in_stage": sp.exchanges_in_stage,
    }


def create_goal(
    self,
    title: str,
    description: str = "",
    priority: str = "medium",
    steps: Optional[List[Dict]] = None,
    tags: Optional[List[str]] = None,
    due_date: Optional[str] = None,
    parent_id: Optional[str] = None,
    # Spiritus override — omit to auto-inject live readings
    spiritu_stage: Optional[str] = None,
    pneuma_flow: Optional[float] = None,
    breath_rhythm: Optional[float] = None,
    user_id: Optional[str] = None,
):
    """
    Create a goal via GoalStore, auto-stamping the GAIAN's live
    Spiritus state at the moment of goal birth.

    Every goal born here carries a permanent record of:
      - which alchemical stage the GAIAN was in
      - the pneuma_flow level at the moment of intention
      - the breath_rhythm at that instant

    This is the canonical new-style goal creation method.
    The old add_goal() (Phase 3 GoalRegistry) remains for backward compat.
    """
    from core.planner.goal_store import goal_store

    ctx = self.spiritu_context()
    return goal_store.create(
        title=title,
        description=description,
        priority=priority,
        steps=steps or [],
        tags=tags or [],
        due_date=due_date,
        spiritu_stage=spiritu_stage or ctx["stage"],
        pneuma_flow=pneuma_flow    if pneuma_flow   is not None else ctx["pneuma_flow"],
        breath_rhythm=breath_rhythm if breath_rhythm is not None else ctx["breath_rhythm"],
        parent_id=parent_id,
    )


def patch_runtime(rt: Any) -> None:
    """
    Monkey-patch spiritu_context() and create_goal() onto a
    GAIANRuntime instance, then register it with the goals_router.

    Usage in server.py:
        from core.gaian_runtime_patch import patch_runtime
        patch_runtime(runtime)
    """
    import types
    from core.routers.goals_router import set_runtime

    rt.spiritu_context = types.MethodType(spiritu_context, rt)
    rt.create_goal     = types.MethodType(create_goal, rt)
    set_runtime(rt)
