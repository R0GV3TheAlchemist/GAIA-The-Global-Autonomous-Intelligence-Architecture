"""
tests/numerology/test_service.py
Async integration tests for NumerologyService.

Uses an in-memory SQLite DB via the db_session / numerology_svc
fixtures defined in tests/numerology/conftest.py.

All tests run with asyncio_mode = auto (pyproject.toml).
"""
from __future__ import annotations

import uuid
from datetime import date

import pytest

from gaia.numerology.service import NumerologyService

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_NAME = "Nikola Tesla"
_DATE = date(1856, 7, 10)
_USER = uuid.uuid4()


# ---------------------------------------------------------------------------
# get_or_create_chart — creation path
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestGetOrCreateChart:
    async def test_creates_chart_on_first_call(
        self, numerology_svc: NumerologyService
    ):
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        assert chart is not None
        assert chart.id is not None

    async def test_returns_same_chart_on_second_call(
        self, numerology_svc: NumerologyService
    ):
        chart_a = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        chart_b = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        assert chart_a.id == chart_b.id

    async def test_force_recompute_creates_new_chart(
        self, numerology_svc: NumerologyService
    ):
        chart_a = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        chart_b = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER,
            force_recompute=True,
        )
        assert chart_a.id != chart_b.id

    async def test_chart_has_correct_life_path(
        self, numerology_svc: NumerologyService
    ):
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        # Tesla Life Path = 1 (verified against engine unit tests)
        assert chart.life_path == 1

    async def test_chart_has_five_core_numbers(
        self, numerology_svc: NumerologyService
    ):
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        for attr in ("life_path", "expression", "soul_urge", "personality", "birthday"):
            val = getattr(chart, attr)
            assert val is not None and val > 0 or val == 0

    async def test_number_rows_are_persisted(
        self, numerology_svc: NumerologyService
    ):
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        assert len(chart.numbers) >= 6  # 5 core + personal_year minimum

    async def test_raw_chart_jsonb_is_populated(
        self, numerology_svc: NumerologyService
    ):
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        assert chart.raw_chart is not None
        assert "life_path" in chart.raw_chart

    async def test_ephemeral_chart_no_user_id(
        self, numerology_svc: NumerologyService
    ):
        """Anonymous (no user_id) call still creates a profile and chart."""
        chart = await numerology_svc.get_or_create_chart(
            full_name="Anonymous User",
            birth_date=date(2000, 1, 1),
            user_id=None,
        )
        assert chart is not None
        assert chart.profile.user_id is None

    # -- raw_chart JSONB cycle coverage (improvement #3) --------------------

    async def test_raw_chart_contains_personal_year_cycle(
        self, numerology_svc: NumerologyService
    ):
        """personal_year_cycle must be persisted inside raw_chart JSONB."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        assert "personal_year_cycle" in chart.raw_chart
        assert isinstance(chart.raw_chart["personal_year_cycle"], list)

    async def test_raw_chart_cycle_default_length(
        self, numerology_svc: NumerologyService
    ):
        """Default cycle_years=3 → 4 entries (current + 3 ahead) in JSONB."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        cycle = chart.raw_chart["personal_year_cycle"]
        assert len(cycle) == 4

    async def test_raw_chart_cycle_entry_keys(
        self, numerology_svc: NumerologyService
    ):
        """Every cycle entry in JSONB must carry all five required keys."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        for entry in chart.raw_chart["personal_year_cycle"]:
            for key in ("year", "reduced_value", "is_master_number", "archetype", "theme"):
                assert key in entry, f"JSONB cycle entry missing key: {key}"

    async def test_raw_chart_cycle_first_matches_personal_year(
        self, numerology_svc: NumerologyService
    ):
        """cycle[0].reduced_value must equal the standalone personal_year value."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        cycle = chart.raw_chart["personal_year_cycle"]
        py = chart.raw_chart["personal_year"]
        assert cycle[0]["reduced_value"] == py["reduced_value"]

    async def test_raw_chart_cycle_years_are_consecutive(
        self, numerology_svc: NumerologyService
    ):
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        years = [e["year"] for e in chart.raw_chart["personal_year_cycle"]]
        assert years == list(range(years[0], years[0] + len(years)))

    async def test_cycle_years_zero_stores_empty_list(
        self, numerology_svc: NumerologyService
    ):
        """cycle_years=0 must persist an empty list in raw_chart, not null."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER,
            cycle_years=0,
        )
        assert chart.raw_chart["personal_year_cycle"] == []

    async def test_cycle_years_custom_stored_correctly(
        self, numerology_svc: NumerologyService
    ):
        """cycle_years=5 must persist 6 entries (current + 5) in raw_chart."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER,
            force_recompute=True,
            cycle_years=5,
        )
        assert len(chart.raw_chart["personal_year_cycle"]) == 6

    async def test_cycle_archetype_non_null_in_jsonb(
        self, numerology_svc: NumerologyService
    ):
        """No cycle entry in JSONB should have a null archetype or theme."""
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        for entry in chart.raw_chart["personal_year_cycle"]:
            assert entry["archetype"] is not None
            assert entry["theme"] is not None

    async def test_force_recompute_refreshes_cycle(
        self, numerology_svc: NumerologyService
    ):
        """After force_recompute, raw_chart cycle should still be valid."""
        await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        chart_new = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER,
            force_recompute=True,
        )
        cycle = chart_new.raw_chart["personal_year_cycle"]
        assert len(cycle) == 4
        assert cycle[0]["archetype"] is not None


# ---------------------------------------------------------------------------
# get_chart_by_id
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestGetChartById:
    async def test_returns_chart_for_valid_id(
        self, numerology_svc: NumerologyService
    ):
        created = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        fetched = await numerology_svc.get_chart_by_id(created.id)
        assert fetched is not None
        assert fetched.id == created.id

    async def test_returns_none_for_unknown_id(
        self, numerology_svc: NumerologyService
    ):
        result = await numerology_svc.get_chart_by_id(uuid.uuid4())
        assert result is None

    async def test_fetched_chart_has_numbers_loaded(
        self, numerology_svc: NumerologyService
    ):
        created = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        fetched = await numerology_svc.get_chart_by_id(created.id)
        assert len(fetched.numbers) >= 6

    async def test_fetched_chart_raw_chart_has_cycle(
        self, numerology_svc: NumerologyService
    ):
        """Fetching by ID after persist must still expose personal_year_cycle."""
        created = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=_USER
        )
        fetched = await numerology_svc.get_chart_by_id(created.id)
        assert "personal_year_cycle" in fetched.raw_chart
        assert len(fetched.raw_chart["personal_year_cycle"]) == 4


# ---------------------------------------------------------------------------
# get_charts_for_user
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestGetChartsForUser:
    async def test_returns_charts_for_user(
        self, numerology_svc: NumerologyService
    ):
        uid = uuid.uuid4()
        await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=uid
        )
        charts = await numerology_svc.get_charts_for_user(uid)
        assert len(charts) == 1

    async def test_returns_empty_for_unknown_user(
        self, numerology_svc: NumerologyService
    ):
        charts = await numerology_svc.get_charts_for_user(uuid.uuid4())
        assert charts == []

    async def test_limit_is_respected(
        self, numerology_svc: NumerologyService
    ):
        uid = uuid.uuid4()
        for _ in range(3):
            await numerology_svc.get_or_create_chart(
                full_name=_NAME, birth_date=_DATE,
                user_id=uid, force_recompute=True,
            )
        charts = await numerology_svc.get_charts_for_user(uid, limit=2)
        assert len(charts) <= 2

    async def test_each_chart_has_cycle_in_raw_chart(
        self, numerology_svc: NumerologyService
    ):
        """Every chart returned by get_charts_for_user must carry cycle data."""
        uid = uuid.uuid4()
        for _ in range(2):
            await numerology_svc.get_or_create_chart(
                full_name=_NAME, birth_date=_DATE,
                user_id=uid, force_recompute=True,
            )
        charts = await numerology_svc.get_charts_for_user(uid)
        for chart in charts:
            assert "personal_year_cycle" in chart.raw_chart
            assert len(chart.raw_chart["personal_year_cycle"]) > 0


# ---------------------------------------------------------------------------
# delete_profile — soft and hard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestDeleteProfile:
    async def test_soft_delete_returns_true(
        self, numerology_svc: NumerologyService
    ):
        uid = uuid.uuid4()
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=uid
        )
        result = await numerology_svc.delete_profile(chart.profile_id)
        assert result is True

    async def test_soft_deleted_profile_not_returned_in_user_charts(
        self, numerology_svc: NumerologyService
    ):
        uid = uuid.uuid4()
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=uid
        )
        await numerology_svc.delete_profile(chart.profile_id)
        charts = await numerology_svc.get_charts_for_user(uid)
        assert charts == []

    async def test_hard_delete_returns_true(
        self, numerology_svc: NumerologyService
    ):
        uid = uuid.uuid4()
        chart = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=uid
        )
        result = await numerology_svc.delete_profile(chart.profile_id, hard=True)
        assert result is True

    async def test_delete_unknown_profile_returns_false(
        self, numerology_svc: NumerologyService
    ):
        result = await numerology_svc.delete_profile(uuid.uuid4())
        assert result is False


# ---------------------------------------------------------------------------
# Isolation — different users, same name+date, separate profiles
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
class TestIsolation:
    async def test_different_users_get_separate_profiles(
        self, numerology_svc: NumerologyService
    ):
        uid_a = uuid.uuid4()
        uid_b = uuid.uuid4()
        chart_a = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=uid_a
        )
        chart_b = await numerology_svc.get_or_create_chart(
            full_name=_NAME, birth_date=_DATE, user_id=uid_b
        )
        assert chart_a.profile_id != chart_b.profile_id

    async def test_same_user_different_names_separate_profiles(
        self, numerology_svc: NumerologyService
    ):
        uid = uuid.uuid4()
        chart_a = await numerology_svc.get_or_create_chart(
            full_name="Ada Lovelace", birth_date=_DATE, user_id=uid
        )
        chart_b = await numerology_svc.get_or_create_chart(
            full_name="Nikola Tesla", birth_date=_DATE, user_id=uid
        )
        assert chart_a.profile_id != chart_b.profile_id
