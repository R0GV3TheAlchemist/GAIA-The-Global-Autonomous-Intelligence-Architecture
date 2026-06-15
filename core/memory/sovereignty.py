"""
GAIA Memory Engine — Sovereignty Layer
Issue #453

The user owns their memory. Full export, edit, delete at any time.
This module enforces the GAIA Sovereignty Doctrine for memory:

  1. No memory is written without consent where required
  2. No memory surfaces trauma content without explicit opt-in
  3. No memory is ever used to infer clinical/mental-health status
  4. User can export, correct, or delete any memory in one call
  5. Every action is audit-logged and immutable
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy.orm import sessionmaker, Session

from core.memory.memory_models import MemoryRecord, MemoryAuditLog, MemoryType


class SovereigntyLayer:
    """
    Sovereignty enforcement for the GAIA Memory Engine.
    """

    # In production, consent records would live in a dedicated store.
    # v1: in-memory dict keyed by (user_id_hash, memory_type)
    _consent_registry: Dict[str, bool] = {}

    def __init__(self, session_factory: sessionmaker):
        self.SessionLocal = session_factory

    def _consent_key(self, user_id_hash: str, memory_type: MemoryType) -> str:
        return f"{user_id_hash}:{memory_type.value}"

    def grant_consent(self, user_id_hash: str, memory_type: MemoryType):
        """User grants consent for a memory type to be written."""
        key = self._consent_key(user_id_hash, memory_type)
        self._consent_registry[key] = True

    def revoke_consent(self, user_id_hash: str, memory_type: MemoryType):
        """User revokes consent for a memory type. No new memories of this type will be written."""
        key = self._consent_key(user_id_hash, memory_type)
        self._consent_registry[key] = False

    def has_consent(self, user_id_hash: str, memory_type: MemoryType) -> bool:
        """Check if user has granted consent for this memory type."""
        key = self._consent_key(user_id_hash, memory_type)
        return self._consent_registry.get(key, False)

    def export_all(
        self,
        user_id_hash: str,
        space_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Export all memories for a user as a list of dicts.
        Honours exportable=True sovereignty flag.
        """
        with self.SessionLocal() as db:
            q = db.query(MemoryRecord).filter(
                MemoryRecord.user_id_hash == user_id_hash,
                MemoryRecord.exportable == True,
            )
            if space_id:
                q = q.filter(MemoryRecord.space_id == space_id)

            records = q.all()

            exported = []
            for r in records:
                exported.append({
                    "memory_id": r.memory_id,
                    "type": r.type.value,
                    "content": r.content,
                    "confidence": r.confidence.value,
                    "evidence_level": r.evidence_level.value,
                    "created_at": r.created_at.isoformat(),
                    "last_reinforced": r.last_reinforced.isoformat() if r.last_reinforced else None,
                    "staleness_score": r.staleness_score,
                    "trauma_flags": r.trauma_flags,
                    "canon_refs": r.canon_refs,
                    "correspondence_refs": r.correspondence_refs,
                    "space_id": r.space_id,
                    "superseded_by": r.superseded_by,
                })

            # Log the export action
            for r in records:
                log = MemoryAuditLog(
                    log_id=str(uuid.uuid4()),
                    memory_id=r.memory_id,
                    user_id_hash=user_id_hash,
                    action="export",
                    actor="user",
                    timestamp=datetime.utcnow(),
                    details={"export_count": len(records)}
                )
                db.add(log)

            db.commit()
            return exported

    def delete_all(self, user_id_hash: str, session_id: Optional[str] = None) -> int:
        """
        Nuclear sovereignty option: delete ALL memories for a user.
        Returns count of deleted records.
        Audit log entries are preserved (they are immutable).
        """
        with self.SessionLocal() as db:
            records = db.query(MemoryRecord).filter(
                MemoryRecord.user_id_hash == user_id_hash,
                MemoryRecord.user_deletable == True
            ).all()

            count = len(records)

            for r in records:
                log = MemoryAuditLog(
                    log_id=str(uuid.uuid4()),
                    memory_id=r.memory_id,
                    user_id_hash=user_id_hash,
                    action="delete_all",
                    actor="user",
                    timestamp=datetime.utcnow(),
                    session_id=session_id,
                    details={"reason": "user_initiated_full_deletion"}
                )
                db.add(log)
                db.delete(r)

            db.commit()
            return count

    def get_audit_log(
        self,
        user_id_hash: str,
        limit: int = 100
    ) -> List[Dict]:
        """Return the consent audit log for a user."""
        with self.SessionLocal() as db:
            logs = db.query(MemoryAuditLog).filter(
                MemoryAuditLog.user_id_hash == user_id_hash
            ).order_by(
                MemoryAuditLog.timestamp.desc()
            ).limit(limit).all()

            return [
                {
                    "log_id": l.log_id,
                    "memory_id": l.memory_id,
                    "action": l.action,
                    "actor": l.actor,
                    "timestamp": l.timestamp.isoformat(),
                    "details": l.details,
                }
                for l in logs
            ]

    def safe_reentry_check(
        self,
        user_id_hash: str,
        last_session_at: Optional[datetime] = None
    ) -> Dict:
        """
        Safe re-entry protocol:
        When a user returns after a significant gap, check their emotional
        memory profile before surfacing heavy memories.

        Returns a dict with:
          - gap_days: days since last session
          - has_trauma_memories: bool
          - recommended_approach: 'gentle' | 'standard' | 'check_in_first'
        """
        if last_session_at is None:
            return {
                "gap_days": None,
                "has_trauma_memories": False,
                "recommended_approach": "standard"
            }

        gap_days = (datetime.utcnow() - last_session_at).days

        with self.SessionLocal() as db:
            trauma_count = db.query(MemoryRecord).filter(
                MemoryRecord.user_id_hash == user_id_hash,
                MemoryRecord.trauma_flags != [],
                MemoryRecord.superseded_by.is_(None)
            ).count()

        has_trauma = trauma_count > 0

        if gap_days > 30 and has_trauma:
            approach = "check_in_first"
        elif gap_days > 7:
            approach = "gentle"
        else:
            approach = "standard"

        return {
            "gap_days": gap_days,
            "has_trauma_memories": has_trauma,
            "recommended_approach": approach
        }
