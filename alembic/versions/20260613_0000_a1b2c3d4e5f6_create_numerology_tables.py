"""create numerology tables

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-06-13 00:00:00.000000

Creates:
  - gaia_numerology_profiles  — one row per user; stores the birth input data
  - gaia_numerology_charts    — one row per computed chart; keyed to a profile
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # gaia_numerology_profiles
    # Stores the raw identity inputs (name + birthdate) tied to a user.
    # ------------------------------------------------------------------
    op.create_table(
        "gaia_numerology_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            index=True,
            comment="Foreign key to the Gaian user identity; NULL for anonymous sessions",
        ),
        sa.Column(
            "full_name",
            sa.String(length=512),
            nullable=False,
            comment="Full birth name as given at registration; used for Expression/Soul Urge/Personality numbers",
        ),
        sa.Column(
            "birth_date",
            sa.Date(),
            nullable=False,
            comment="ISO 8601 birth date used for Life Path and Personal Year computation",
        ),
        sa.Column(
            "system",
            sa.String(length=32),
            nullable=False,
            server_default="pythagorean",
            comment="Numerology system: 'pythagorean' (default) or 'chaldean' (future)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Soft-delete timestamp; NULL means the record is active (C139 compliance)",
        ),
    )

    # Index to support Right to Be Forgotten queries by user_id
    op.create_index(
        "ix_gaia_numerology_profiles_user_id",
        "gaia_numerology_profiles",
        ["user_id"],
        unique=False,
    )

    # ------------------------------------------------------------------
    # gaia_numerology_charts
    # Stores the fully computed chart for a given profile.
    # Recomputed on request; the latest chart per profile is canonical.
    # ------------------------------------------------------------------
    op.create_table(
        "gaia_numerology_charts",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "profile_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey(
                "gaia_numerology_profiles.id",
                ondelete="CASCADE",
                name="fk_numerology_chart_profile",
            ),
            nullable=False,
            index=True,
        ),
        # Core five numbers -----------------------------------------------
        sa.Column(
            "life_path",
            sa.SmallInteger(),
            nullable=False,
            comment="Life Path number (1-9, 11, 22, 33)",
        ),
        sa.Column(
            "expression",
            sa.SmallInteger(),
            nullable=False,
            comment="Expression (Destiny) number",
        ),
        sa.Column(
            "soul_urge",
            sa.SmallInteger(),
            nullable=False,
            comment="Soul Urge (Heart's Desire) number",
        ),
        sa.Column(
            "personality",
            sa.SmallInteger(),
            nullable=False,
            comment="Personality number",
        ),
        sa.Column(
            "birthday",
            sa.SmallInteger(),
            nullable=False,
            comment="Birthday number (reduced day of birth)",
        ),
        # Timing numbers --------------------------------------------------
        sa.Column(
            "personal_year",
            sa.SmallInteger(),
            nullable=False,
            comment="Personal Year number at time of computation",
        ),
        sa.Column(
            "computed_for_year",
            sa.SmallInteger(),
            nullable=False,
            comment="Calendar year for which personal_year was computed",
        ),
        # Master number flags ---------------------------------------------
        sa.Column(
            "life_path_is_master",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "expression_is_master",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "soul_urge_is_master",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        # Full JSON payload for forward compatibility ---------------------
        sa.Column(
            "raw_chart",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="Full NumerologyChart Pydantic model serialised as JSONB for future fields",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    # Index for fetching latest chart per profile
    op.create_index(
        "ix_gaia_numerology_charts_profile_id",
        "gaia_numerology_charts",
        ["profile_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gaia_numerology_charts_profile_id",
        table_name="gaia_numerology_charts",
    )
    op.drop_table("gaia_numerology_charts")

    op.drop_index(
        "ix_gaia_numerology_profiles_user_id",
        table_name="gaia_numerology_profiles",
    )
    op.drop_table("gaia_numerology_profiles")
