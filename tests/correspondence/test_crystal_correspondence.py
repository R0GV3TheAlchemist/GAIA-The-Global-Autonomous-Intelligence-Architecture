"""Test suite for crystal correspondence infrastructure — v2.0.

Covers schema validation, ingestion/upsert, scalar extraction, ORM helper
methods, correspondence lookup, alchemical/SoulMirror integration patterns,
affect inference, safety flags, sovereignty flags, and v2.0 consequential
properties.

The tests intentionally focus on infrastructure behavior, not metaphysical
truth claims.
"""
from __future__ import annotations

import copy
import datetime as dt

import pytest
from jsonschema import ValidationError

from core.crystal_correspondence.ingestion import (
    clear_validation_errors,
    get_validation_errors,
    ingest_record,
    validate_record,
)
from core.crystal_correspondence.models import CrystalCorrespondence


# ---------------------------------------------------------------------------
# Fixtures / sample records
# ---------------------------------------------------------------------------

@pytest.fixture()
def sample_record_v2() -> dict:
    return {
        "subject_id": "crystal:actinolite",
        "subject_kind": "crystal",
        "aliases": ["Byssolite", "Smaragdite"],
        "correspondences": {
            "physical_properties": {
                "chemical_formula": "Ca2(Mg,Fe)5Si8O22(OH)2",
                "crystal_system": "monoclinic",
                "mohs_hardness": "5-6",
                "piezoelectric": False,
                "pyroelectric": False,
                "photonic_properties": "silky to vitreous when fibrous",
                "luminance_profile": "forest green fibrous glow with low reflectance",
                "color_spectrum": [
                    {
                        "label": "forest green",
                        "hex": "#2E6F4E",
                        "rgb": {"r": 46, "g": 111, "b": 78},
                        "wavelength_nm": 530,
                        "is_primary": True,
                    },
                    {
                        "label": "dark olive",
                        "hex": "#556B2F",
                        "rgb": {"r": 85, "g": 107, "b": 47},
                        "wavelength_nm": 560,
                        "is_primary": False,
                    },
                ],
            },
            "resonant_frequencies": [
                {
                    "hz": 7.83,
                    "label": "Schumann fundamental",
                    "source": "schumann",
                    # FIX 1: was "empirical" which is valid for .source but NOT
                    # in evidence_level_enum. "clinical_study" is correct here
                    # because Schumann resonance is a measured geophysical fact.
                    "evidence_level": "clinical_study",
                    "confidence": "medium",
                },
                {
                    "hz": 528.0,
                    "label": "restorative harmonic",
                    "source": "traditional",
                    "evidence_level": "traditional",
                    "confidence": "speculative",
                },
            ],
            "chakra_system": [
                {
                    "chakra": "heart",
                    "system": "traditional_7",
                    "role": "opens protective compassion",
                    "weight": 0.9,
                    "confidence": "high",
                },
                {
                    "chakra": "earth_star",
                    "system": "gaia_extended",
                    "role": "grounds transmutation into embodiment",
                    "weight": 0.6,
                    "confidence": "medium",
                },
            ],
            "alchemical": {
                "stage_primary": "VIRIDITAS",
                "stages_secondary": ["ALBEDO", "COAGULATIO"],
                "archetypal_meaning": "green renewal after contraction",
                "transmutation_corridor": "NIGREDO dissolution -> VIRIDITAS regrowth",
                "confidence": "high",
            },
            "healing": {
                "physical": [
                    {
                        "description": "supports connective tissue recovery symbolism",
                        "target_system": "musculoskeletal",
                        "evidence_level": "traditional",
                        "confidence": "medium",
                    }
                ],
                "emotional_mental": [
                    {
                        "description": "softens defended grief",
                        "target_system": "affect_regulation",
                        "evidence_level": "gaian_observed",
                        "confidence": "medium",
                    }
                ],
                "spiritual_energetic": [
                    {
                        "description": "strengthens heart-field grounding",
                        "target_system": "subtle_body",
                        "evidence_level": "traditional",
                        "confidence": "high",
                    }
                ],
                "contraindications": [
                    {
                        "description": "Avoid direct inhalation of fibrous dust.",
                        "severity": "contraindicated",
                        "applies_to": "lapidary processing",
                    }
                ],
            },
            "consequential_properties": {
                "coherence_impact": {
                    "scalar": 0.72,
                    "vector": {
                        "04-Emotion": 0.81,
                        "01-Physical": 0.55,
                    },
                },
                "grey_state_risk": {
                    "mitigates": ["flatness", "collapse", "numb grief"],
                    "may_exacerbate": ["rumination"],
                    "recommended_phase": "re-emergence",
                },
                "transmutation_effect": {
                    "primary_corridor": "NIGREDO -> VIRIDITAS",
                    "mechanism": "restores green movement after psychic petrification",
                    "duration_typical": "days to weeks",
                },
                "collective_field_impact": {
                    "noospheric_role": "local recovery anchor",
                    "planetary_resonance": "Earth",
                    "grid_amplification": True,
                },
                "interaction_matrix": [
                    {
                        "partner": "crystal:selenite",
                        "type": "synergy",
                        "effect": "Actinolite grounds what Selenite illuminates.",
                        "confidence": "medium",
                    },
                    {
                        "partner": "state:acute_overactivation",
                        "type": "conditional",
                        "effect": "May need softer pairing if the system is already highly activated.",
                        "confidence": "medium",
                    },
                ],
                "long_term_consequences": [
                    {
                        "description": "Can increase sovereignty through gradual emotional re-rooting.",
                        "timeframe": "1-3 months",
                        "valence": "positive",
                        "evidence_level": "gaian_observed",
                    },
                    {
                        "description": "May surface defended grief material before stabilisation.",
                        "timeframe": "2-6 weeks",
                        "valence": "challenging",
                        "evidence_level": "traditional",
                    },
                ],
                "measurable_outcomes": [
                    {
                        "metric": "affect_valence_score",
                        "expected_direction": "increase",
                        "magnitude": "moderate",
                        "evidence_level": "simulated",
                        "study_ref": "sim-run-2026-06-15-a1",
                    },
                    {
                        "metric": "gaia_coherence_index",
                        "expected_direction": "increase",
                        "magnitude": "+5-10%",
                        "evidence_level": "gaian_observed",
                    },
                ],
            },
            "gaia_layers": [
                {"layer_id": "04-Emotion", "weight": 0.9, "role": "heart-regulation"},
                {"layer_id": "01-Physical", "weight": 0.4, "role": "embodied grounding"},
            ],
            "emotions": [
                {
                    "primary": "renewal",
                    "transmutes": "defended grief",
                    "activates": "gentle courage",
                    "body_location": "chest and sternum",
                    "felt_as": "a warming loosening through the center of the chest",
                }
            ],
            "senses": [
                {"sense": "touch", "strength": 0.7},
                {"sense": "interoception", "strength": 0.8},
            ],
            "zodiac": [
                {
                    "tradition": "western_tropical",
                    "sign": "Virgo",
                    "role": "supporting",
                    "ruling_planet": "Mercury",
                    "dignity": "neutral",
                    "confidence": "medium",
                }
            ],
            "angel_numbers": [
                {
                    "number": 444,
                    "role": "stability in regrowth",
                    "gaia_layer_id": "01-Physical",
                    "digits": [4, 4, 4],
                    "digit_sum": 12,
                    "confidence": "medium",
                }
            ],
            "lunar_phases": [
                {
                    "phase_id": "waxing_gibbous",
                    "role": "supports gradual rebuilding",
                    "special_events": ["super_moon"],
                }
            ],
            "sacred_geometry": [
                {"pattern": "vesica_piscis", "role": "bridges rupture and reunion"}
            ],
            "archetypes": [
                {
                    "name": "The Regreening Guardian",
                    "system": "GAIA-C32",
                    "role_in_story": "protective renewer",
                    "behavioral_markers": ["steady care", "protective softness"],
                    "noospheric_role": "local stabilizer",
                    "confidence": "medium",
                }
            ],
            "metals": [
                {"metal": "Copper", "planet": "Venus", "role": "heart conductor", "confidence": "medium"}
            ],
            "elements": [
                {"element": "Earth", "weight": 0.7, "role": "grounds repair"},
                {"element": "Water", "weight": 0.3, "role": "restores flow"},
            ],
            "periodic_elements": [
                {"atomic_number": 20, "symbol": "Ca", "name": "Calcium", "role": "matrix support"},
                {"atomic_number": 12, "symbol": "Mg", "name": "Magnesium", "role": "stability"},
                {"atomic_number": 26, "symbol": "Fe", "name": "Iron", "role": "embodiment"},
                {"atomic_number": 14, "symbol": "Si", "name": "Silicon", "role": "lattice"},
            ],
            "grid_resonance": {
                "lattice_analogue": "monoclinic",
                "grid_role": "recovery anchor",
                "frequency_band_hz": "7.83-20.8",
                "piezoelectric": False,
                "pyroelectric": False,
                "topology": "toroidal",
            },
            "evidence_profile": {
                "basis": "cross-tradition",
                "sources": [
                    {"kind": "gaia_canon", "ref": "C32"},
                    {"kind": "traditional_source", "ref": "crystal_healing_lineages"},
                ],
                "falsifiable_by": [
                    "No reliable change in repeated coherence simulations.",
                    "Cross-tradition review fails to reproduce the renewal motif.",
                ],
                "confidence": "medium",
            },
            "safety_profile": {
                "clinical_use": "supportive_only",
                "trauma_flags": ["active_crisis"],
                "requires_opt_in": True,
                "physical_caution": "Fibrous varieties may be hazardous if cut or inhaled.",
                "usage_notes": "Use metaphorically and with explicit consent.",
            },
            "provenance": {
                "confidence_score": 0.74,
                "last_verified": "2026-06-15",
                "source_references": [
                    {"kind": "gaia_canon", "ref": "C32"},
                    {"kind": "scientific_literature", "ref": "mineralogy-handbook"},
                ],
                "gaian_user_feedback": [
                    {
                        "observation": "Helped me feel emotionally mobile again after numbness.",
                        "user_id_hash": "abc123",
                        "date": "2026-06-10",
                        "confidence": "medium",
                        "verified_by_gaia": False,
                    }
                ],
            },
        },
        "metadata": {
            "schema_version": "2.0.0",
            "version": "1.2.0",
            "change_log": [
                {"version": "1.0.0", "date": "2026-06-01", "summary": "Initial crystal record."},
                {"version": "1.2.0", "date": "2026-06-15", "summary": "Expanded v2 consequential fields."},
            ],
            "review_status": "approved",
            "reviewed_by": "gaia-architect",
            "next_review_date": "2026-09-15",
            "created_at": "2026-06-01T00:00:00Z",
            "updated_at": "2026-06-15T00:00:00Z",
            "created_by": "test-suite",
            "canon_refs": ["C32", "C118"],
            # FIX 2: sovereignty_flags lives under metadata (schema-correct location)
            "sovereignty_flags": {
                "user_overridable": True,
                "community_contributions_enabled": True,
                "override_log": [],
            },
        },
    }


class FakeSession:
    """Tiny in-memory stand-in for the Session API used by ingest_record()."""

    def __init__(self):
        self.rows: dict[str, CrystalCorrespondence] = {}
        self.logs = []
        self.last_added = None
        self.did_rollback = False

    def add(self, obj):
        if isinstance(obj, CrystalCorrespondence):
            if obj.id is None:
                obj.id = len(self.rows) + 1
            self.rows[obj.subject_id] = obj
        else:
            self.logs.append(obj)
        self.last_added = obj

    def flush(self):
        return None

    def rollback(self):
        self.did_rollback = True

    def execute(self, stmt):
        class _Result:
            def __init__(self, row):
                self._row = row

            def scalar_one_or_none(self):
                return self._row

        try:
            subject_id = stmt.right.value
        except Exception:
            subject_id = None
        return _Result(self.rows.get(subject_id))


# ---------------------------------------------------------------------------
# Group 1: Schema validation
# ---------------------------------------------------------------------------

def test_validate_record_accepts_valid_v2_record(sample_record_v2):
    validate_record(sample_record_v2)


def test_validate_record_rejects_missing_subject_id(sample_record_v2):
    broken = copy.deepcopy(sample_record_v2)
    broken.pop("subject_id")
    with pytest.raises(ValidationError):
        validate_record(broken)


def test_validate_record_rejects_invalid_alchemical_stage(sample_record_v2):
    broken = copy.deepcopy(sample_record_v2)
    broken["correspondences"]["alchemical"]["stage_primary"] = "BLUEBO"
    with pytest.raises(ValidationError):
        validate_record(broken)


def test_validate_record_rejects_bad_hex_color(sample_record_v2):
    broken = copy.deepcopy(sample_record_v2)
    broken["correspondences"]["physical_properties"]["color_spectrum"][0]["hex"] = "green"
    with pytest.raises(ValidationError):
        validate_record(broken)


def test_validate_record_rejects_bad_evidence_level(sample_record_v2):
    """'empirical' is a valid .source value but NOT a valid evidence_level_enum value."""
    broken = copy.deepcopy(sample_record_v2)
    broken["correspondences"]["resonant_frequencies"][0]["evidence_level"] = "empirical"
    with pytest.raises(ValidationError):
        validate_record(broken)


def test_validate_record_rejects_bad_chakra_system(sample_record_v2):
    broken = copy.deepcopy(sample_record_v2)
    broken["correspondences"]["chakra_system"][0]["system"] = "wrong_system"
    with pytest.raises(ValidationError):
        validate_record(broken)


# ---------------------------------------------------------------------------
# Group 2: Ingestion / upsert / provenance
# ---------------------------------------------------------------------------

def test_ingest_record_creates_new_row(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2, changed_by="pytest", change_note="initial")

    assert row.subject_id == "crystal:actinolite"
    assert row.crystal_system == "monoclinic"
    assert row.primary_color == "forest green"
    assert float(row.frequency_hz_low) == pytest.approx(7.83)
    assert float(row.frequency_hz_high) == pytest.approx(528.0)
    assert row.alchemical_stage_primary == "VIRIDITAS"
    assert row.primary_chakra == "heart"
    assert float(row.coherence_impact_scalar) == pytest.approx(0.72)
    assert row.review_status == "approved"
    assert row.record_version == "1.2.0"
    assert row.provenance_v2["confidence_score"] == 0.74


def test_ingest_record_updates_existing_row_and_creates_provenance_log(sample_record_v2):
    session = FakeSession()
    row1 = ingest_record(session, sample_record_v2, changed_by="pytest", change_note="initial")

    updated = copy.deepcopy(sample_record_v2)
    updated["correspondences"]["consequential_properties"]["coherence_impact"]["scalar"] = 0.81
    updated["metadata"]["version"] = "1.3.0"

    row2 = ingest_record(session, updated, changed_by="pytest", change_note="raise coherence")

    assert row1 is row2
    assert float(row2.coherence_impact_scalar) == pytest.approx(0.81)
    assert row2.record_version == "1.3.0"
    assert len(session.logs) == 1
    assert session.logs[0].change_note == "raise coherence"
    assert session.logs[0].snapshot["record_version"] == "1.2.0"


def test_ingest_record_dry_run_rolls_back(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2, dry_run=True)
    assert row.subject_id == "crystal:actinolite"
    assert session.did_rollback is True


def test_invalid_record_enters_validation_error_queue(sample_record_v2):
    clear_validation_errors()
    session = FakeSession()
    bad = copy.deepcopy(sample_record_v2)
    bad["correspondences"]["chakra_system"][0]["system"] = "wrong_system"

    with pytest.raises(ValidationError):
        ingest_record(session, bad)

    errs = get_validation_errors()
    assert len(errs) == 1
    assert errs[0]["subject_id"] == "crystal:actinolite"


# ---------------------------------------------------------------------------
# Group 3: Scalar extraction + ORM helpers
# ---------------------------------------------------------------------------

def test_helper_methods_expose_v2_axes(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    assert row.chakra_set() == ["heart", "earth_star"]
    assert row.alchemical_stage() == "VIRIDITAS"
    assert row.primary_archetype() == "The Regreening Guardian"
    assert row.emotion_set() == ["renewal"]
    assert row.gaia_layers()[0]["layer_id"] == "04-Emotion"
    assert row.primary_color_hex() == "#2E6F4E"
    assert row.resonant_hz_values() == [7.83, 528.0]
    assert row.transmutation_corridor() == "NIGREDO dissolution -> VIRIDITAS regrowth"


def test_coherence_and_grey_state_helpers(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    assert row.coherence_scalar() == pytest.approx(0.72)
    grey = row.grey_state_risks()
    assert "flatness" in grey["mitigates"]
    assert "rumination" in grey["may_exacerbate"]
    assert row.grey_state_risk_level == "context_dependent"


def test_healing_helper_by_domain(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    physical  = row.healing_entries("physical")
    emotional = row.healing_entries("emotional_mental")
    spiritual = row.healing_entries("spiritual_energetic")

    assert physical[0]["target_system"] == "musculoskeletal"
    assert emotional[0]["description"] == "softens defended grief"
    assert spiritual[0]["confidence"] == "high"


def test_interaction_matrix_helpers(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    assert row.synergy_partners() == ["crystal:selenite"]
    assert row.antagonism_partners() == []
    assert row.interaction_partners()[1]["partner"] == "state:acute_overactivation"


# ---------------------------------------------------------------------------
# Group 4: Correspondence lookup patterns
# ---------------------------------------------------------------------------

def test_lookup_by_layer_emotion_zodiac_and_angel_number(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    assert any(x["layer_id"] == "04-Emotion" for x in row.gaia_layers())
    assert "renewal" in row.emotion_set()
    assert row.correspondences["zodiac"][0]["sign"] == "Virgo"
    assert row.correspondences["angel_numbers"][0]["number"] == 444


# ---------------------------------------------------------------------------
# Group 5: Alchemical / SoulMirror integration pattern
# ---------------------------------------------------------------------------

def test_alchemical_hook_for_soul_mirror_pattern(sample_record_v2):
    """Infrastructure-level pattern: a SoulMirror engine reads the crystal's
    transmutation corridor + archetype + emotion to generate a reflective
    mirror state without touching raw JSON paths."""
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    soul_mirror_seed = {
        "archetype":      row.primary_archetype(),
        "alchemical_stage": row.alchemical_stage(),
        "corridor":       row.transmutation_corridor(),
        "emotion":        row.emotion_set()[0],
    }

    assert soul_mirror_seed == {
        "archetype":        "The Regreening Guardian",
        "alchemical_stage": "VIRIDITAS",
        "corridor":         "NIGREDO dissolution -> VIRIDITAS regrowth",
        "emotion":          "renewal",
    }


# ---------------------------------------------------------------------------
# Group 6: Affect inference hook
# ---------------------------------------------------------------------------

def test_affect_inference_hook_builds_support_vector(sample_record_v2):
    """Infrastructure-level pattern: affect inference combines emotional,
    archetypal, and measurable outcome data into a support vector."""
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    support_vector = {
        "valence_bias":      +1 if row.coherence_scalar() > 0 else -1,
        "emotion":           row.emotion_set()[0],
        "archetype":         row.primary_archetype(),
        "expected_metrics":  [m["metric"] for m in row.measurable_outcomes()],
    }

    assert support_vector["valence_bias"] == 1
    assert support_vector["emotion"] == "renewal"
    assert "affect_valence_score"  in support_vector["expected_metrics"]
    assert "gaia_coherence_index"  in support_vector["expected_metrics"]


# ---------------------------------------------------------------------------
# Group 7: Safety / sovereignty / versioning
# ---------------------------------------------------------------------------

def test_safety_profile_and_requires_opt_in(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)
    sp = row.correspondences["safety_profile"]

    assert row.safety_flags() == ["active_crisis"]
    assert sp["requires_opt_in"] is True
    assert "fibrous" in sp["physical_caution"].lower() or "hazardous" in sp["physical_caution"].lower()


def test_user_override_and_community_flags(sample_record_v2):
    """FIX 2: sovereignty_flags is read from metadata (schema-correct location)."""
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    # sovereignty_flags is written into the sovereignty_flags JSONB column
    # by ingestion reading payload['metadata']['sovereignty_flags']
    assert row.is_user_overridable() is True
    assert row.community_contributions_enabled() is True


def test_sovereignty_flags_read_from_metadata_not_top_level(sample_record_v2):
    """Confirm that sovereignty_flags is NOT expected at the record root."""
    session = FakeSession()
    # Remove from metadata — ingestion should get an empty dict, flags = False
    no_flags = copy.deepcopy(sample_record_v2)
    no_flags["metadata"].pop("sovereignty_flags")
    row = ingest_record(session, no_flags)
    assert row.is_user_overridable() is False
    assert row.community_contributions_enabled() is False


def test_versioning_and_review_metadata(sample_record_v2):
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)

    assert row.record_version == "1.2.0"
    assert row.review_status  == "approved"
    assert row.reviewed_by    == "gaia-architect"
    assert row.next_review_date == dt.date(2026, 9, 15)
    assert row.change_log[1]["summary"] == "Expanded v2 consequential fields."


def test_common_name_derives_from_subject_id_slug(sample_record_v2):
    """FIX 3: common_name falls back to titleized subject_id slug.
    This is intentional — metadata has no 'display_name' key in v2.0 schema."""
    session = FakeSession()
    row = ingest_record(session, sample_record_v2)
    # subject_id = 'crystal:actinolite' -> slug = 'actinolite' -> 'Actinolite'
    assert row.common_name == "Actinolite"


# ---------------------------------------------------------------------------
# Group 8: Regression / backward compatibility
# ---------------------------------------------------------------------------

def test_v1_compatibility_frequency_falls_back_to_grid_resonance(sample_record_v2):
    session = FakeSession()
    legacyish = copy.deepcopy(sample_record_v2)
    legacyish["correspondences"].pop("resonant_frequencies")

    row = ingest_record(session, legacyish)
    assert float(row.frequency_hz_low)  == pytest.approx(7.83)
    assert float(row.frequency_hz_high) == pytest.approx(20.8)


def test_missing_optional_v2_fields_still_ingest(sample_record_v2):
    session = FakeSession()
    minimal = copy.deepcopy(sample_record_v2)
    minimal["correspondences"].pop("consequential_properties")
    minimal["correspondences"].pop("healing")
    minimal["correspondences"].pop("chakra_system")
    minimal["metadata"].pop("version")
    minimal["metadata"].pop("review_status")

    row = ingest_record(session, minimal)
    assert row.subject_id    == "crystal:actinolite"
    assert row.primary_chakra is None
    assert row.review_status in ("draft", None)
