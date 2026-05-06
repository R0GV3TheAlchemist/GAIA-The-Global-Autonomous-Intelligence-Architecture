"""
core.runtime — Phase 3: Runtime Orchestration Layer
====================================================
GAIAOrchestrator is the central nervous system of GAIA-OS.

It is a singleton that boots once at server startup and is shared
across all requests.  Every chat turn passes through it:

  before_turn()   → retrieve memory, advance quantum kernel,
                    build enriched system prompt, log audit event
  after_turn()    → store new memories, advance goals, schedule
                    background tasks, log completion audit event

Quick-start
-----------
    from core.runtime import GAIAOrchestrator, get_orchestrator

    orchestrator = get_orchestrator()       # returns the global singleton
    ctx = await orchestrator.before_turn(
        user_id="user_001",
        session_id="sess_abc",
        user_message="Tell me about quantum computing.",
    )
    # ctx.system_suffix  → inject into system prompt before LLM call
    # ctx.memory_items   → top-k recalled memory items
    # ctx.kernel         → live QuantumKernel for this session

    await orchestrator.after_turn(
        user_id="user_001",
        session_id="sess_abc",
        user_message="Tell me about quantum computing.",
        gaia_reply="Quantum computing uses qubits ...",
        ctx=ctx,
    )
"""

from .orchestrator import GAIAOrchestrator, TurnContext, get_orchestrator, init_orchestrator
from .session import SessionInfo, SessionRegistry

__all__ = [
    "GAIAOrchestrator",
    "TurnContext",
    "get_orchestrator",
    "init_orchestrator",
    "SessionInfo",
    "SessionRegistry",
]
