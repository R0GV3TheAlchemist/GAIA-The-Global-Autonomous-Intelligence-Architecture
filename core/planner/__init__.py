"""
core.planner — Phase 2C: Planner / Policy Layer
================================================
Gives GAIA-OS the ability to:

  1. Represent and track multi-step *Goals* across sessions.
  2. Gate every proposed action through a *PolicyEngine* that checks
     consent, safety rules, and ethical constraints before execution.
  3. Schedule discrete *Tasks* (tool calls, memory writes, API calls)
     in a priority queue with async execution, retries, and TTL.

Quick-start
-----------
    from core.planner import Goal, GoalRegistry, PolicyEngine, TaskScheduler
    from core.planner import PolicyRule, Task, GoalStatus

    # Create and register a goal
    registry = GoalRegistry()
    goal = Goal(
        user_id="user_001",
        title="Research quantum computing",
        description="Gather and summarise 5 key papers on quantum error correction.",
    )
    registry.add(goal)

    # Gate an action through the policy engine
    engine = PolicyEngine()
    decision = engine.evaluate(action="web_search", context={"user_id": "user_001"})

    # Schedule a task
    scheduler = TaskScheduler()
    task = Task(name="embed_memory", coroutine=my_coro, priority=5)
    scheduler.submit(task)
    await scheduler.run_once()   # or await scheduler.run_forever()
"""

from .goal      import Goal, GoalStatus, GoalPriority, GoalRegistry
from .policy    import PolicyRule, PolicyDecision, PolicyAction, PolicyEngine
from .scheduler import Task, TaskStatus, TaskScheduler

__all__ = [
    # goal
    "Goal",
    "GoalStatus",
    "GoalPriority",
    "GoalRegistry",
    # policy
    "PolicyRule",
    "PolicyDecision",
    "PolicyAction",
    "PolicyEngine",
    # scheduler
    "Task",
    "TaskStatus",
    "TaskScheduler",
]
