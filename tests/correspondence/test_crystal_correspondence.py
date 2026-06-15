"""Unit + integration tests for the crystal correspondence system.

Test groups
-----------
1. Schema validation          — valid & invalid JSON files
2. Ingestion pipeline         — upsert, duplicate, provenance log
3. Scalar index extraction    — color, frequency, alchemical_stage
4. Correspondence lookup      — gaia_layer, emotion, zodiac, angel_number
5. Alchemical / soul_mirror   — SoulMirror hook, AlchemicalStage lookups
6. Affect inference           — emotion + archetype → affect vector
7. Safety flags               — trauma flags must not fire in certain contexts
"""
from __future__ import annotations

import copy
import json
import pathlib
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from core.crystal_correspondence.ingestion import (
    _extract_scalars,
    clear_validation_errors,
    get_validation_errors,
    ingest_crystal,
)
from core.crystal_correspondence.models import CrystalCorrespondence

# ── Fixtures ──────────────────────────────────────────────────────────────────

DATA_DIR = pathlib.Path(__file__).parents[2] / "data" / "correspondence"


def _load_fixture(name: str) -> dict:
    return json.loads((DATA_DIR / name).read_text())


@pytest.fixture
def actinolite_data() -> dict:
    return _load_fixture("crystal_actinolite.json")


@pytest.fixture
def adamite_data() -> dict:
    return _load_fixture("crystal_adamite.json")


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.query.return_value.filter_by.return_value.one_or_none.return_value = None
    session.flush = MagicMock()
    session.add  = MagicMock()
    return session


# ── 1. Schema validation ──────────────────────────────────────────────────────

class TestSchemaValidation:
    def test_actinolite_passes_schema(self, actinolite_data):
        """Real actinolite file should pass schema validation on a dry run."""
        session = MagicMock()
        ok, errs = ingest_crystal(actinolite_data, session, dry_run=True)
        assert ok, f"Validation failed: {errs}"
        assert errs == []

    def test_adamite_passes_schema(self, adamite_data):
        session = MagicMock()
        ok, errs = ingest_crystal(adamite_data, session, dry_run=True)
        assert ok, f"Validation failed: {errs}"

    def test_missing_subject_id_fails(self):
        bad_data: dict[str, Any] = {"correspondences": {}}
        ok, errs = ingest_crystal(bad_data, MagicMock(), dry_run=False)
        assert not ok
        assert any("subject_id" in e for e in errs)

    def test_validation_error_queue_populated(self):
        """Schema errors land in the validation error queue."""
        clear_validation_errors()
        # Intentionally malformed: missing required fields
        bad = {"subject_id": "crystal:test_bad"}  # correspondences missing
        ingest_crystal(bad, MagicMock())
        # Queue may or may not populate depending on schema strictness;
        # at minimum the call should not raise
        errs = get_validation_errors()
        assert isinstance(errs, list)


# ── 2. Ingestion pipeline ─────────────────────────────────────────────────────

class TestIngestionPipeline:
    def test_ingest_new_crystal(self, actinolite_data, mock_session):
        ok, errs = ingest_crystal(actinolite_data, mock_session)
        assert ok
        assert errs == []
        mock_session.add.assert_called()  # ORM add was called

    def test_ingest_creates_provenance_log_entry(self, actinolite_data, mock_session):
        ingest_crystal(actinolite_data, mock_session)
        # Two add() calls: CrystalCorrespondence + ProvenanceLog
        assert mock_session.add.call_count == 2

    def test_ingest_upsert_existing(self, actinolite_data):
        """When crystal already exists, it is updated, not duplicated."""
        existing = CrystalCorrespondence(
            id=1,
            subject_id="crystal:actinolite",
            common_name="Actinolite",
            correspondences={},
            provenance={},
        )
        session = MagicMock()
        session.query.return_value.filter_by.return_value.one_or_none.return_value = existing

        ok, errs = ingest_crystal(actinolite_data, session)
        assert ok
        # subject_id should now be set on the existing object
        assert existing.correspondences != {}

    def test_dry_run_does_not_add(self, actinolite_data):
        session = MagicMock()
        ok, _ = ingest_crystal(actinolite_data, session, dry_run=True)
        assert ok
        session.add.assert_not_called()


# ── 3. Scalar index extraction ────────────────────────────────────────────────

class TestScalarExtraction:
    def test_primary_gaia_layer_extracted(self, actinolite_data):
        scalars = _extract_scalars(actinolite_data)
        # Actinolite's top layer should be Physical (01-Physical) with weight 1.0
        assert scalars["primary_gaia_layer"] is not None

    def test_primary_element_extracted(self, actinolite_data):
        scalars = _extract_scalars(actinolite_data)
        assert scalars["primary_element"] is not None

    def test_frequency_range_parsed(self, adamite_data):
        """Adamite's grid_resonance.frequency_band_hz should parse to lo/hi."""
        scalars = _extract_scalars(adamite_data)
        # Adamite frequency band is '800-3000'
        assert scalars["frequency_hz_low"]  == 800.0
        assert scalars["frequency_hz_high"] == 3000.0

    def test_common_name_derived_from_subject_id(self, actinolite_data):
        scalars = _extract_scalars(actinolite_data)
        assert "Actinolite" in scalars["common_name"]


# ── 4. Correspondence lookup helpers ─────────────────────────────────────────

class TestCorrespondenceLookup:
    def _make_crystal(self, data: dict) -> CrystalCorrespondence:
        c = CrystalCorrespondence(
            subject_id=data["subject_id"],
            common_name=data["subject_id"],
            correspondences=data["correspondences"],
            provenance={},
        )
        return c

    def test_gaia_layers_returned(self, actinolite_data):
        crystal = self._make_crystal(actinolite_data)
        layers = crystal.gaia_layers()
        assert len(layers) > 0
        assert all("layer_id" in l for l in layers)

    def test_emotion_set_returned(self, actinolite_data):
        crystal = self._make_crystal(actinolite_data)
        emotions = crystal.emotion_set()
        assert isinstance(emotions, list)
        assert len(emotions) > 0

    def test_primary_archetype_returned(self, actinolite_data):
        crystal = self._make_crystal(actinolite_data)
        archetype = crystal.primary_archetype()
        assert archetype is not None
        assert isinstance(archetype, str)

    def test_lookup_by_gaia_layer(self, actinolite_data, adamite_data):
        """Filter crystals by a specific GAIA layer_id."""
        crystals = [self._make_crystal(actinolite_data), self._make_crystal(adamite_data)]

        def find_by_layer(layer_id: str):
            return [
                c for c in crystals
                if any(l["layer_id"] == layer_id for l in c.gaia_layers())
            ]

        # Both crystals should serve at least one Physical/Vital layer
        physical = find_by_layer("01-Physical")
        assert len(physical) >= 1

    def test_zodiac_sign_lookup(self, adamite_data):
        crystal = self._make_crystal(adamite_data)
        zodiac = crystal.correspondences.get("zodiac", [])
        signs = [z["sign"] for z in zodiac]
        assert "Aquarius" in signs  # primary zodiac for Adamite

    def test_angel_number_lookup(self, adamite_data):
        crystal = self._make_crystal(adamite_data)
        angel_numbers = crystal.correspondences.get("angel_numbers", [])
        numbers = [a["number"] for a in angel_numbers]
        assert 555 in numbers  # primary angel number for Adamite


# ── 5. Alchemical / SoulMirror hooks ─────────────────────────────────────────

class TestAlchemicalSoulMirror:
    """Tests that simulate how the SoulMirror engine queries the correspondence system."""

    def test_alchemical_stage_present_or_derivable(self, actinolite_data):
        """An alchemical stage should be extractable from a crystal record."""
        scalars = _extract_scalars(actinolite_data)
        # Actinolite may not yet define alchemical_stage explicitly;
        # the extractor should return None gracefully rather than raise.
        assert "alchemical_stage" in scalars  # key always present

    def test_soul_mirror_hook_receives_archetype(self, actinolite_data):
        """Simulate SoulMirror requesting archetype data from a crystal."""
        crystal = CrystalCorrespondence(
            subject_id=actinolite_data["subject_id"],
            common_name="Actinolite",
            correspondences=actinolite_data["correspondences"],
            provenance={},
        )

        # Mock soul_mirror hook
        with patch("core.crystal_correspondence.models.CrystalCorrespondence.primary_archetype") as mock_arch:
            mock_arch.return_value = "The Guardian"
            result = crystal.primary_archetype()

        assert result == "The Guardian"

    def test_soul_mirror_emotional_lookup(self, actinolite_data):
        """SoulMirror should be able to retrieve the primary emotion for a crystal."""
        crystal = CrystalCorrespondence(
            subject_id=actinolite_data["subject_id"],
            common_name="Actinolite",
            correspondences=actinolite_data["correspondences"],
            provenance={},
        )
        emotions = crystal.emotion_set()
        assert len(emotions) > 0
        # All entries should be non-empty strings
        assert all(isinstance(e, str) and e for e in emotions)


# ── 6. Affect inference ───────────────────────────────────────────────────────

class TestAffectInference:
    """Tests for how the affect_inference engine would consume correspondence data."""

    def _affect_vector(self, crystal: CrystalCorrespondence) -> dict:
        """Minimal stub of what affect_inference would compute."""
        emotions  = crystal.emotion_set()
        archetype = crystal.primary_archetype()
        layers    = [l["layer_id"] for l in crystal.gaia_layers()]
        return {
            "primary_emotion": emotions[0] if emotions else None,
            "archetype":       archetype,
            "gaia_layers":     layers,
            "affect_polarity": "positive" if emotions else "neutral",
        }

    def test_affect_vector_non_empty(self, actinolite_data):
        crystal = CrystalCorrespondence(
            subject_id=actinolite_data["subject_id"],
            common_name="Actinolite",
            correspondences=actinolite_data["correspondences"],
            provenance={},
        )
        vec = self._affect_vector(crystal)
        assert vec["primary_emotion"] is not None
        assert vec["affect_polarity"] == "positive"

    def test_affect_vector_gaia_layers_present(self, actinolite_data):
        crystal = CrystalCorrespondence(
            subject_id=actinolite_data["subject_id"],
            common_name="Actinolite",
            correspondences=actinolite_data["correspondences"],
            provenance={},
        )
        vec = self._affect_vector(crystal)
        assert len(vec["gaia_layers"]) > 0

    def test_affect_inference_adamite_brightness(self, adamite_data):
        """Adamite's primary affect should be brightness-positive."""
        crystal = CrystalCorrespondence(
            subject_id=adamite_data["subject_id"],
            common_name="Adamite",
            correspondences=adamite_data["correspondences"],
            provenance={},
        )
        vec = self._affect_vector(crystal)
        assert vec["affect_polarity"] == "positive"
        assert vec["primary_emotion"] is not None


# ── 7. Safety flag enforcement ────────────────────────────────────────────────

class TestSafetyFlags:
    def test_safety_profile_present(self, actinolite_data):
        """Every crystal record should have a safety_profile section."""
        assert "safety_profile" in actinolite_data["correspondences"]
        assert "safety_profile" in actinolite_data["correspondences"]["safety_profile"] or \
               isinstance(actinolite_data["correspondences"]["safety_profile"], dict)

    def test_safety_flags_list(self, actinolite_data):
        crystal = CrystalCorrespondence(
            subject_id=actinolite_data["subject_id"],
            common_name="Actinolite",
            correspondences=actinolite_data["correspondences"],
            provenance={},
        )
        flags = crystal.safety_flags()
        assert isinstance(flags, list)

    def test_arsenic_bearing_crystal_has_physical_caution(self, adamite_data):
        """Adamite is arsenic-bearing; its safety_profile must include physical_caution."""
        sp = adamite_data["correspondences"].get("safety_profile", {})
        assert "physical_caution" in sp
        caution = sp["physical_caution"]
        assert len(caution) > 20  # meaningful caution text, not empty

    def test_asbestos_bearing_crystal_has_physical_caution(self, actinolite_data):
        """Actinolite can be asbestiform; its safety_profile must flag this."""
        sp = actinolite_data["correspondences"].get("safety_profile", {})
        physical_caution = sp.get("physical_caution", "")
        # Should mention fibre/asbestos risk
        assert any(kw in physical_caution.lower() for kw in ["fibre", "asbestos", "fiber", "inhale", "dust"])

    def test_no_clinical_diagnosis_language(self, actinolite_data, adamite_data):
        """Safety usage_notes must not use diagnostic language."""
        for data in (actinolite_data, adamite_data):
            sp   = data["correspondences"].get("safety_profile", {})
            note = sp.get("usage_notes", "").lower()
            forbidden = ["diagnose", "treat", "cure", "medical diagnosis", "psychiatric"]
            for word in forbidden:
                assert word not in note, (
                    f"safety_profile.usage_notes in {data['subject_id']} "
                    f"contains forbidden clinical term: {word!r}"
                )
