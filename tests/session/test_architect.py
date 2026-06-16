"""Unit tests: ArchitectRepository and ArchitectProfile."""

import pytest
from core.session.architect import ArchitectProfile, ArchitectRepository


@pytest.fixture
def repo():
    return ArchitectRepository()


class TestArchitectRepository:
    def test_create_profile(self, repo):
        profile = repo.create("Kyle Steen", foundation_statement="Build GAIA OS")
        assert profile.name == "Kyle Steen"
        assert profile.session_count == 0

    def test_get_by_name(self, repo):
        repo.create("Kyle Steen")
        profile = repo.get_by_name("Kyle Steen")
        assert profile is not None

    def test_get_or_create_returns_existing(self, repo):
        repo.create("Kyle Steen")
        profile, created = repo.get_or_create("Kyle Steen")
        assert not created

    def test_get_or_create_makes_new(self, repo):
        profile, created = repo.get_or_create("New Architect")
        assert created
        assert profile.name == "New Architect"

    def test_duplicate_name_raises(self, repo):
        repo.create("Kyle Steen")
        with pytest.raises(ValueError, match="already exists"):
            repo.create("Kyle Steen")

    def test_record_session_open_increments(self, repo):
        profile = repo.create("Kyle Steen")
        profile.record_session_open("session-001")
        assert profile.session_count == 1
        assert profile.last_session_id == "session-001"

    def test_update_stage(self, repo):
        profile = repo.create("Kyle Steen")
        profile.update_stage("ALBEDO")
        assert profile.current_stage == "ALBEDO"
