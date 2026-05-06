"""
core.audit — Phase 2D: Action Ledger & Epistemic Audit
=====================================================
Provides GAIA-OS with a tamper-evident append-only ledger of actions,
policy decisions, memory writes, tool executions, and state snapshots.

The audit layer answers three core questions:

  1. What did GAIA do?
  2. Why did GAIA believe it was justified?
  3. Which policy, memory, and quantum-state context influenced the action?

Quick-start
-----------
    from core.audit import ActionLedger, AuditEvent, EventType

    ledger = ActionLedger("gaia_audit.sqlite")
    event_id = ledger.append(
        AuditEvent(
            event_type=EventType.ACTION_EXECUTED,
            actor="gaia",
            user_id="user_001",
            session_id="sess_abc",
            action="web_search",
            outcome="success",
            justification="User asked for recent papers on QEC.",
            metadata={"query": "quantum error correction 2025"},
        )
    )

    recent = ledger.recent(limit=10)
    chain_ok = ledger.verify_chain()
"""

from .ledger import ActionLedger, AuditEvent, EventType, LedgerVerificationResult

__all__ = [
    "ActionLedger",
    "AuditEvent",
    "EventType",
    "LedgerVerificationResult",
]
