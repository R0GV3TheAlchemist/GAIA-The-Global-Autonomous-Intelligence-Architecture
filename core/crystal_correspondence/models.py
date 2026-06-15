"""SQLAlchemy ORM models for the crystal_correspondence table."""
from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CrystalCorrespondence(Base):
    """One row per crystal subject_id.  Full correspondence payload stored in JSONB."""

    __tablename__ = "crystal_correspondence"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # ── Identity ──────────────────────────────────────────────────────────
    subject_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    common_name: Mapped[str] = mapped_column(Text, nullable=False)
    mineral_formula: Mapped[str | None] = mapped_column(Text, nullable=True)
    crystal_system: Mapped[str | None] = mapped_column(Text, nullable=True)
    mohs_hardness_low: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    mohs_hardness_high: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)

    # ── Indexed fast-lookup scalars ───────────────────────────────────────
    primary_color: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    frequency_hz_low: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, index=True)
    frequency_hz_high: Mapped[float | None] = mapped_column(Numeric(12, 4), nullable=True, index=True)
    alchemical_stage: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    primary_gaia_layer: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)
    primary_element: Mapped[str | None] = mapped_column(Text, nullable=True, index=True)

    # ── JSONB payload ─────────────────────────────────────────────────────
    correspondences: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    schema_version: Mapped[str] = mapped_column(Text, nullable=False, default="1.0.0", index=True)

    # ── Provenance ────────────────────────────────────────────────────────
    provenance: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=lambda: {"source": "GAIA-OS", "confidence": "high", "last_updated": None},
    )

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Relationship ──────────────────────────────────────────────────────
    provenance_log: Mapped[list["CrystalCorrespondenceProvenanceLog"]] = relationship(
        back_populates="crystal", cascade="all, delete-orphan", order_by="CrystalCorrespondenceProvenanceLog.changed_at"
    )

    # ── Helpers ───────────────────────────────────────────────────────────
    def gaia_layers(self) -> list[dict]:
        """Return the list of GAIA layer entries from the correspondences JSONB."""
        return self.correspondences.get("gaia_layers", [])

    def primary_archetype(self) -> str | None:
        archetypes = self.correspondences.get("archetypes", [])
        if archetypes:
            return archetypes[0].get("name")
        return None

    def emotion_set(self) -> list[str]:
        return [
            e.get("primary", "") for e in self.correspondences.get("emotions", [])
        ]

    def safety_flags(self) -> list[str]:
        sp = self.correspondences.get("safety_profile", {})
        return sp.get("trauma_flags", [])

    def __repr__(self) -> str:
        return f"<CrystalCorrespondence id={self.id} subject_id={self.subject_id!r}>"


class CrystalCorrespondenceProvenanceLog(Base):
    """Append-only log of every change to a crystal_correspondence row."""

    __tablename__ = "crystal_correspondence_provenance_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crystal_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("crystal_correspondence.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    provenance_snapshot: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    crystal: Mapped["CrystalCorrespondence"] = relationship(back_populates="provenance_log")

    def __repr__(self) -> str:
        return f"<ProvenanceLog crystal_id={self.crystal_id} version={self.version!r} at={self.changed_at}>"
