"""
tests/numerology/conftest.py
Async DB fixtures for the numerology test suite.

Uses an in-memory SQLite database (aiosqlite) so these tests run
entirely without Postgres, Docker, or network access.

Fixtures available to all tests in this directory:
  db_session     — AsyncSession on an isolated in-memory DB (function scope)
  numerology_svc — NumerologyService bound to db_session
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ── Path guard ────────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from gaia.db.base import Base
from gaia.db.models.numerology import NumerologyChart, NumerologyNumber, NumerologyProfile  # noqa: F401
from gaia.numerology.service import NumerologyService

# In-memory SQLite URL — each test gets a fresh DB via unique URL.
_SQLITE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncSession:
    """Yield a fresh async DB session backed by an in-memory SQLite database.

    Creates all tables via Base.metadata, yields the session, then drops
    everything — giving each test a perfectly clean slate.
    """
    engine = create_async_engine(_SQLITE_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def numerology_svc(db_session: AsyncSession) -> NumerologyService:
    """NumerologyService bound to the test DB session."""
    return NumerologyService(db_session)
