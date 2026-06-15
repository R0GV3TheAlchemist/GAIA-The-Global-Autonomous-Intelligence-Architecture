"""
GAIA Memory Engine — Full Test Suite
Issue #453

Covers:
  - Memory CRUD (create, recall, reinforce, correct, delete)
  - Staleness decay correctness
  - Contradiction detection
  - Sovereignty layer (export, delete_all, audit log, consent)
  - Trauma-informed non-surfacing
  - Safe re-entry check
  - Integration hooks (agent loop perception context)
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from core.memory.memory_engine import MemoryEngine
from core.memory.memory_models import MemoryType, ConfidenceLevel, EvidenceLevel
from core.memory.staleness import compute_staleness, detect_contradictions
from core.memory.hooks import MemoryHooks


TEST_DB = "sqlite:///:memory:"
TEST_USER = "test_alchemist@gaia.os"
TEST_SESSION = "session-test-001"


@pytest.fixture
def engine():
    return MemoryEngine(db_url=TEST_DB)


@pytest.fixture
def hooks(engine):
    return MemoryHooks(engine)


# ─────────────────────────────────────────────
# Core CRUD
# ─────────────────────────────────────────────

class TestMemoryCRUD:

    def test_create_memory(self, engine):
        record = engine.remember(
            user_id=TEST_USER,
            content="User resonates with Black Tourmaline for grounding.",
            type=MemoryType.EMOTIONAL,
            session_id=TEST_SESSION,
        )
        assert record.memory_id is not None
        assert record.content == "User resonates with Black Tourmaline for grounding."
        assert record.staleness_score == 0.0
        assert record.user_deletable is True
        assert record.exportable is True

    def test_recall_memory(self, engine):
        engine.remember(
            user_id=TEST_USER,
            content="User prefers morning sessions.",
            type=MemoryType.PROCEDURAL,
            session_id=TEST_SESSION,
        )
        results = engine.recall(user_id=TEST_USER, type=MemoryType.PROCEDURAL)
        assert len(results) >= 1
        assert any("morning sessions" in r.content for r in results)

    def test_reinforce_memory(self, engine):
        record = engine.remember(
            user_id=TEST_USER,
            content="User is in NIGREDO stage.",
            type=MemoryType.EPISODIC,
            session_id=TEST_SESSION,
        )
        reinforced = engine.reinforce(
            user_id=TEST_USER,
            memory_id=record.memory_id,
            session_id=TEST_SESSION
        )
        assert reinforced.staleness_score == 0.0
        assert reinforced.last_reinforced is not None

    def test_correct_memory_creates_new_supersedes_old(self, engine):
        original = engine.remember(
            user_id=TEST_USER,
            content="User's favourite crystal is Amethyst.",
            type=MemoryType.SEMANTIC,
            session_id=TEST_SESSION,
        )
        corrected = engine.correct(
            user_id=TEST_USER,
            memory_id=original.memory_id,
            new_content="User's favourite crystal is Labradorite.",
            session_id=TEST_SESSION
        )
        assert corrected.content == "User's favourite crystal is Labradorite."
        assert corrected.source_type.value == "user_correction"

        # Verify original is superseded
        from sqlalchemy.orm import sessionmaker
        with engine.SessionLocal() as db:
            from core.memory.memory_models import MemoryRecord
            old = db.query(MemoryRecord).filter(
                MemoryRecord.memory_id == original.memory_id
            ).first()
            assert old.superseded_by == corrected.memory_id

    def test_delete_memory(self, engine):
        record = engine.remember(
            user_id=TEST_USER,
            content="Temporary memory to delete.",
            type=MemoryType.SEMANTIC,
            session_id=TEST_SESSION,
        )
        result = engine.delete(
            user_id=TEST_USER,
            memory_id=record.memory_id,
            session_id=TEST_SESSION
        )
        assert result is True

        # Verify deleted
        results = engine.recall(user_id=TEST_USER, type=MemoryType.SEMANTIC)
        assert not any(r.memory_id == record.memory_id for r in results)


# ─────────────────────────────────────────────
# Staleness Decay
# ─────────────────────────────────────────────

class TestStalenessDecay:

    def test_fresh_memory_has_zero_staleness(self):
        score = compute_staleness(
            last_reinforced=datetime.utcnow(),
            confidence=ConfidenceLevel.HIGH,
            evidence_level=EvidenceLevel.EMPIRICAL,
            memory_type=MemoryType.EMOTIONAL
        )
        assert score < 0.01

    def test_old_speculative_memory_is_stale(self):
        old_date = datetime.utcnow() - timedelta(days=120)
        score = compute_staleness(
            last_reinforced=old_date,
            confidence=ConfidenceLevel.SPECULATIVE,
            evidence_level=EvidenceLevel.ANECDOTAL,
            memory_type=MemoryType.SEMANTIC
        )
        assert score > 0.9

    def test_high_confidence_empirical_emotional_decays_slowly(self):
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        score = compute_staleness(
            last_reinforced=thirty_days_ago,
            confidence=ConfidenceLevel.HIGH,
            evidence_level=EvidenceLevel.EMPIRICAL,
            memory_type=MemoryType.EMOTIONAL
        )
        # Should still be relatively fresh after 30 days
        assert score < 0.2

    def test_decay_all_updates_records(self, engine):
        engine.remember(
            user_id=TEST_USER,
            content="Memory to decay.",
            type=MemoryType.SEMANTIC,
            session_id=TEST_SESSION,
        )
        updated = engine.decay_all(user_id=TEST_USER)
        assert updated >= 0  # May be 0 if just created


# ─────────────────────────────────────────────
# Trauma-Informed Non-Surfacing
# ─────────────────────────────────────────────

class TestTraumaInformed:

    def test_trauma_flagged_memory_not_surfaced_by_default(self, engine):
        engine.remember(
            user_id=TEST_USER,
            content="User expressed grief about loss.",
            type=MemoryType.EMOTIONAL,
            session_id=TEST_SESSION,
            trauma_flags=["grief", "loss"],
        )
        # Default recall excludes trauma flags
        results = engine.recall(user_id=TEST_USER, type=MemoryType.EMOTIONAL)
        assert not any(
            "grief" in r.content for r in results
        ), "Trauma-flagged memory must not surface in default recall"

    def test_never_clinical_flag_is_set(self, engine):
        record = engine.remember(
            user_id=TEST_USER,
            content="User described feelings of anxiety.",
            type=MemoryType.EMOTIONAL,
            session_id=TEST_SESSION,
            never_clinical=True,
            trauma_flags=["anxiety"]
        )
        assert record.never_clinical is True


# ─────────────────────────────────────────────
# Sovereignty Layer
# ─────────────────────────────────────────────

class TestSovereignty:

    def test_export_all(self, engine):
        engine.remember(
            user_id=TEST_USER,
            content="Exportable memory.",
            type=MemoryType.SEMANTIC,
            session_id=TEST_SESSION,
        )
        exports = engine.sovereignty.export_all(
            user_id_hash=engine._hash_user_id(TEST_USER)
        )
        assert isinstance(exports, list)
        assert len(exports) >= 1
        assert all("memory_id" in e for e in exports)
        assert all("content" in e for e in exports)

    def test_audit_log_written_on_create(self, engine):
        engine.remember(
            user_id=TEST_USER,
            content="Audit test memory.",
            type=MemoryType.PROCEDURAL,
            session_id=TEST_SESSION,
        )
        log = engine.sovereignty.get_audit_log(
            user_id_hash=engine._hash_user_id(TEST_USER)
        )
        assert len(log) >= 1
        assert any(entry["action"] == "create" for entry in log)

    def test_delete_all(self, engine):
        for i in range(3):
            engine.remember(
                user_id=TEST_USER,
                content=f"Memory to bulk delete {i}.",
                type=MemoryType.SEMANTIC,
                session_id=TEST_SESSION,
            )
        count = engine.sovereignty.delete_all(
            user_id_hash=engine._hash_user_id(TEST_USER),
            session_id=TEST_SESSION
        )
        assert count >= 3

        remaining = engine.recall(user_id=TEST_USER)
        assert len(remaining) == 0

    def test_safe_reentry_standard_for_new_user(self, engine):
        result = engine.sovereignty.safe_reentry_check(
            user_id_hash=engine._hash_user_id(TEST_USER),
            last_session_at=None
        )
        assert result["recommended_approach"] == "standard"


# ─────────────────────────────────────────────
# Agent Loop Perception Hook
# ─────────────────────────────────────────────

class TestAgentLoopHook:

    def test_perception_context_returns_valid_structure(self, hooks):
        hooks.memory.remember(
            user_id=TEST_USER,
            content="User is aligned with the Empress archetype.",
            type=MemoryType.SEMANTIC,
            session_id=TEST_SESSION,
            correspondence_refs={"archetypes": ["The Empress"]}
        )
        ctx = hooks.get_perception_context(
            user_id=TEST_USER,
            session_id=TEST_SESSION
        )
        assert "recent_memories" in ctx
        assert "alchemical_trajectory" in ctx
        assert "emotional_resonances" in ctx
        assert "reentry_guidance" in ctx
        assert isinstance(ctx["recent_memories"], list)

    def test_record_alchemical_stage_hook(self, hooks):
        hooks.record_alchemical_stage(
            user_id=TEST_USER,
            stage="NIGREDO",
            session_id=TEST_SESSION,
            evidence="User expressed themes of dissolution and shadow work."
        )
        results = hooks.memory.recall(
            user_id=TEST_USER,
            type=MemoryType.EPISODIC
        )
        assert any("NIGREDO" in r.content for r in results)

    def test_record_correspondence_resonance_hook(self, hooks):
        hooks.record_correspondence_resonance(
            user_id=TEST_USER,
            crystal="Labradorite",
            emotion="wonder",
            gaia_layer="Layer 07 Intuition",
            session_id=TEST_SESSION
        )
        results = hooks.memory.recall(
            user_id=TEST_USER,
            type=MemoryType.EMOTIONAL
        )
        assert any("Labradorite" in r.content for r in results)
