"""crystal_correspondence: versioned table with JSONB, provenance, and indexed fast-lookup columns.

Revision ID: 20260615_crystal_corr
Revises: (update to your latest head)
Create Date: 2026-06-15
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "20260615_crystal_corr"
down_revision = None  # Update to your current head revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Main crystal_correspondence table ────────────────────────────────────
    op.create_table(
        "crystal_correspondence",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        # Identity
        sa.Column("subject_id", sa.Text, nullable=False, unique=True),
        sa.Column("common_name", sa.Text, nullable=False),
        sa.Column("mineral_formula", sa.Text, nullable=True),
        sa.Column("crystal_system", sa.Text, nullable=True),
        sa.Column("mohs_hardness_low", sa.Numeric(4, 2), nullable=True),
        sa.Column("mohs_hardness_high", sa.Numeric(4, 2), nullable=True),
        # Fast-lookup indexed columns ──────────────────────────────────────
        sa.Column("primary_color", sa.Text, nullable=True),       # e.g. 'green'
        sa.Column("frequency_hz_low", sa.Numeric(12, 4), nullable=True),
        sa.Column("frequency_hz_high", sa.Numeric(12, 4), nullable=True),
        sa.Column("alchemical_stage", sa.Text, nullable=True),     # e.g. 'nigredo'
        sa.Column("primary_gaia_layer", sa.Text, nullable=True),  # e.g. '01-Physical'
        sa.Column("primary_element", sa.Text, nullable=True),     # e.g. 'Earth'
        # Full correspondence payload ──────────────────────────────────────
        sa.Column("correspondences", JSONB, nullable=False, server_default="'{}'"),
        # Provenance ───────────────────────────────────────────────────────
        sa.Column(
            "provenance",
            JSONB,
            nullable=False,
            server_default=sa.text("'{\"source\": \"GAIA-OS\", \"confidence\": \"high\", \"last_updated\": null}'"),
        ),
        sa.Column("schema_version", sa.Text, nullable=False, server_default="'1.0.0'"),
        # Timestamps ───────────────────────────────────────────────────────
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )

    # ── Scalar fast-lookup indexes ──────────────────────────────────────────
    op.create_index("ix_cc_primary_color",       "crystal_correspondence", ["primary_color"])
    op.create_index("ix_cc_frequency_low",        "crystal_correspondence", ["frequency_hz_low"])
    op.create_index("ix_cc_frequency_high",       "crystal_correspondence", ["frequency_hz_high"])
    op.create_index("ix_cc_alchemical_stage",     "crystal_correspondence", ["alchemical_stage"])
    op.create_index("ix_cc_primary_gaia_layer",   "crystal_correspondence", ["primary_gaia_layer"])
    op.create_index("ix_cc_primary_element",      "crystal_correspondence", ["primary_element"])
    op.create_index("ix_cc_schema_version",       "crystal_correspondence", ["schema_version"])

    # ── GIN index for fast JSONB key/value resonance queries ───────────────
    # Enables queries like:  correspondences @> '{"gaia_layers": [{"layer_id": "04-Emotion"}]}'
    op.execute(
        "CREATE INDEX ix_cc_correspondences_gin ON crystal_correspondence USING gin (correspondences)"
    )
    op.execute(
        "CREATE INDEX ix_cc_provenance_gin ON crystal_correspondence USING gin (provenance)"
    )

    # ── Provenance version history table ───────────────────────────────────
    op.create_table(
        "crystal_correspondence_provenance_log",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "crystal_id",
            sa.Integer,
            sa.ForeignKey("crystal_correspondence.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version",      sa.Text,    nullable=False),
        sa.Column("changed_by",   sa.Text,    nullable=True),
        sa.Column("change_note",  sa.Text,    nullable=True),
        sa.Column("snapshot",     JSONB,      nullable=False),  # full row snapshot at change time
        sa.Column("provenance_snapshot", JSONB, nullable=False),
        sa.Column("changed_at",   sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index(
        "ix_ccpl_crystal_id",
        "crystal_correspondence_provenance_log",
        ["crystal_id", "changed_at"],
    )


def downgrade() -> None:
    op.drop_table("crystal_correspondence_provenance_log")
    op.drop_index("ix_cc_correspondences_gin", table_name="crystal_correspondence")
    op.drop_index("ix_cc_provenance_gin", table_name="crystal_correspondence")
    op.drop_table("crystal_correspondence")
