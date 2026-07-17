"""
tests/core/test_knowledge_matrix.py

57-test suite for core/memory/knowledge_matrix.py (and the
core/knowledge_matrix.py re-export stub).

Test classes
------------
 TestEpistemicTier          (6)   — enum values, ordering, labels
 TestKnowledgeDomain        (7)   — dataclass shape, to_dict() contracts
 TestKnowledgeMatrix        (6)   — all 18 domains, field completeness
 TestKnowledgeMatrixEngineInit (2) — matrix loaded on construction
 TestFindDomains            (15)  — semantic search, edge cases
 TestGetDomain              (3)   — known / unknown / type
 TestListDomains            (5)   — no filter, branch, tier, combined
 TestCrossCulturalReport    (4)   — valid domain, unknown domain
 TestEpistemicSummary       (5)   — counts, sums, keys
 TestSingletonEngine        (2)   — get_knowledge_engine() identity
 TestStubReexport           (2)   — core.knowledge_matrix wildcard export

Canon refs: C01, C04, C48
"""

from __future__ import annotations

import pytest

from core.memory.knowledge_matrix import (
    EpistemicTier,
    KnowledgeDomain,
    KnowledgeMatrixEngine,
    KNOWLEDGE_MATRIX,
    get_knowledge_engine,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ALL_IDS = [
    "NS-PHY", "NS-CHE", "NS-BIO", "NS-AST",
    "FS-MAT", "FS-CS",
    "SS-PSY", "SS-SOC", "SS-ECO", "SS-POL",
    "HU-PHI", "HU-HIS", "HU-LNG",
    "AP-ENG",
    "HM-MED",
    "ES-ENV",
    "AR-ART",
    "CW-SPI", "CW-ALC",
    "IK-TRD",
]

_EXPECTED_COUNT = 20  # total domains in KNOWLEDGE_MATRIX


def _make_engine() -> KnowledgeMatrixEngine:
    return KnowledgeMatrixEngine()


# ---------------------------------------------------------------------------
# Class 1 — EpistemicTier
# ---------------------------------------------------------------------------

class TestEpistemicTier:
    def test_tier_values(self):
        assert EpistemicTier.EMPIRICAL    == 1
        assert EpistemicTier.SCHOLARLY   == 2
        assert EpistemicTier.HYPOTHESIS  == 3
        assert EpistemicTier.INTERPRETIVE == 4
        assert EpistemicTier.CULTURAL    == 5

    def test_tier_ordering(self):
        assert (
            EpistemicTier.EMPIRICAL
            < EpistemicTier.SCHOLARLY
            < EpistemicTier.HYPOTHESIS
            < EpistemicTier.INTERPRETIVE
            < EpistemicTier.CULTURAL
        )

    def test_label_t1(self):
        assert EpistemicTier.EMPIRICAL.label() == "T1 \u2014 Empirically Verified"

    def test_label_t5(self):
        assert EpistemicTier.CULTURAL.label() == "T5 \u2014 Cultural / Contemplative"

    def test_all_labels_unique(self):
        labels = [t.label() for t in EpistemicTier]
        assert len(labels) == len(set(labels))

    def test_is_int_enum(self):
        assert isinstance(EpistemicTier.EMPIRICAL, int)


# ---------------------------------------------------------------------------
# Class 2 — KnowledgeDomain
# ---------------------------------------------------------------------------

class TestKnowledgeDomain:
    def _minimal(self) -> KnowledgeDomain:
        return KnowledgeDomain(
            domain_id="XX-TST",
            name="Test Domain",
            branch="Test Branch",
            epistemic_tier=EpistemicTier.EMPIRICAL,
            description="A minimal test domain.",
        )

    def test_required_fields_no_error(self):
        d = self._minimal()
        assert d.domain_id == "XX-TST"

    def test_optional_fields_default_empty(self):
        d = self._minimal()
        assert d.subfields == []
        assert d.keywords == []
        assert d.real_sources == []
        assert d.cross_cultural == {}
        assert d.gaia_lens is None
        assert d.isced_code is None
        assert d.oecd_ford_code is None
        assert d.lcc_code is None

    def test_to_dict_keys(self):
        expected_keys = {
            "domain_id", "name", "branch", "epistemic_tier",
            "description", "subfields", "cross_cultural", "gaia_lens",
            "isced_code", "oecd_ford_code", "lcc_code", "real_sources",
        }
        assert set(self._minimal().to_dict().keys()) == expected_keys

    def test_to_dict_tier_is_label_string(self):
        d = self._minimal().to_dict()
        assert isinstance(d["epistemic_tier"], str)
        assert d["epistemic_tier"] == EpistemicTier.EMPIRICAL.label()

    def test_to_dict_lists_are_lists(self):
        d = self._minimal().to_dict()
        assert isinstance(d["subfields"], list)
        assert isinstance(d["real_sources"], list)

    def test_to_dict_cross_cultural_is_dict(self):
        assert isinstance(self._minimal().to_dict()["cross_cultural"], dict)

    def test_to_dict_optional_none_survives(self):
        assert self._minimal().to_dict()["gaia_lens"] is None


# ---------------------------------------------------------------------------
# Class 3 — KNOWLEDGE_MATRIX global constant
# ---------------------------------------------------------------------------

class TestKnowledgeMatrix:
    def test_domain_count(self):
        assert len(KNOWLEDGE_MATRIX) >= 18  # allow future additions

    def test_all_known_ids_present(self):
        for domain_id in _ALL_IDS:
            assert domain_id in KNOWLEDGE_MATRIX, f"Missing domain: {domain_id}"

    def test_all_domains_have_keywords(self):
        for domain_id, domain in KNOWLEDGE_MATRIX.items():
            assert len(domain.keywords) >= 5, (
                f"{domain_id} has fewer than 5 keywords"
            )

    def test_all_domains_have_real_sources(self):
        for domain_id, domain in KNOWLEDGE_MATRIX.items():
            assert len(domain.real_sources) >= 1, (
                f"{domain_id} has no real_sources"
            )

    def test_all_epistemic_tiers_valid(self):
        valid = set(EpistemicTier)
        for domain_id, domain in KNOWLEDGE_MATRIX.items():
            assert domain.epistemic_tier in valid, (
                f"{domain_id} has invalid epistemic_tier: {domain.epistemic_tier}"
            )

    def test_gaia_lens_labeled_when_present(self):
        """Every non-None gaia_lens must start with a tier label tag."""
        valid_prefixes = ("[T4-lens]", "[T5-lens]")
        for domain_id, domain in KNOWLEDGE_MATRIX.items():
            if domain.gaia_lens is not None:
                assert domain.gaia_lens.startswith(valid_prefixes), (
                    f"{domain_id}.gaia_lens missing tier prefix: {domain.gaia_lens!r}"
                )


# ---------------------------------------------------------------------------
# Class 4 — KnowledgeMatrixEngine construction
# ---------------------------------------------------------------------------

class TestKnowledgeMatrixEngineInit:
    def test_init_loads_matrix(self):
        engine = _make_engine()
        assert engine.matrix is KNOWLEDGE_MATRIX

    def test_init_has_all_domains(self):
        engine = _make_engine()
        assert len(engine.matrix) >= 18


# ---------------------------------------------------------------------------
# Class 5 — find_domains  (15 tests)
# ---------------------------------------------------------------------------

class TestFindDomains:
    # --- structural contracts ---

    def test_returns_list(self):
        results = _make_engine().find_domains("physics")
        assert isinstance(results, list)
        for item in results:
            assert isinstance(item, tuple) and len(item) == 2
            domain, score = item
            assert isinstance(domain, KnowledgeDomain)
            assert isinstance(score, float)

    def test_top_k_respected(self):
        results = _make_engine().find_domains("physics", top_k=3)
        assert len(results) == 3

    def test_results_ordered_by_score(self):
        results = _make_engine().find_domains("biology chemistry", top_k=10)
        scores = [s for _, s in results]
        assert scores == sorted(scores, reverse=True)

    # --- semantic correctness ---

    def test_physics_query_ranks_ns_phy_first(self):
        results = _make_engine().find_domains("physics quantum relativity", top_k=5)
        top_id = results[0][0].domain_id
        assert top_id == "NS-PHY"
        assert results[0][1] > 0.3

    def test_cs_query_ranks_fs_cs_first(self):
        results = _make_engine().find_domains(
            "algorithm machine learning neural network Python", top_k=5
        )
        assert results[0][0].domain_id == "FS-CS"

    def test_alchemy_query_ranks_cw_alc_first(self):
        results = _make_engine().find_domains(
            "nigredo albedo magnum opus transmutation", top_k=5
        )
        assert results[0][0].domain_id == "CW-ALC"

    # --- filtering ---

    def test_min_score_filters_noise(self):
        results = _make_engine().find_domains("xqzwvb", min_score=0.5)
        assert results == []

    def test_tier_filter_empirical_only(self):
        results = _make_engine().find_domains(
            "quantum biology chemistry",
            top_k=10,
            tier_filter=[EpistemicTier.EMPIRICAL],
        )
        for domain, _ in results:
            assert domain.epistemic_tier == EpistemicTier.EMPIRICAL, (
                f"Non-empirical domain leaked through filter: {domain.domain_id}"
            )

    def test_tier_filter_multiple_tiers(self):
        """A filter listing T4 + T5 must admit both, exclude T1-T3."""
        allowed = {EpistemicTier.INTERPRETIVE, EpistemicTier.CULTURAL}
        results = _make_engine().find_domains(
            "ritual ceremony spirit alchemy hermetic",
            top_k=18,
            tier_filter=list(allowed),
        )
        for domain, _ in results:
            assert domain.epistemic_tier in allowed, (
                f"Domain {domain.domain_id} (tier {domain.epistemic_tier}) "
                f"should have been excluded by tier filter"
            )
        # At least CW-ALC and CW-SPI should appear
        ids = {d.domain_id for d, _ in results}
        assert "CW-ALC" in ids
        assert "CW-SPI" in ids

    # --- edge cases ---

    def test_empty_query_no_crash(self):
        """Empty string must not raise; all scores should be 0.0."""
        try:
            results = _make_engine().find_domains("")
        except Exception as exc:  # pragma: no cover
            pytest.fail(f"find_domains('') raised unexpectedly: {exc}")
        for _, score in results:
            assert score == 0.0

    def test_top_k_larger_than_matrix_no_crash(self):
        """Requesting more results than domains must not crash or pad with None."""
        results = _make_engine().find_domains("biology", top_k=9999)
        assert len(results) <= len(KNOWLEDGE_MATRIX)
        for domain, score in results:
            assert domain is not None
            assert isinstance(score, float)

    def test_single_token_match(self):
        """A single keyword is sufficient to surface the right domain."""
        results = _make_engine().find_domains("alchemy", top_k=5)
        ids = [d.domain_id for d, _ in results]
        assert "CW-ALC" in ids

    def test_cross_domain_query_scores_multiple(self):
        """Brain-focused query should score both SS-PSY and NS-BIO above 0.0."""
        results = _make_engine().find_domains(
            "brain neuroscience behavior cognition", top_k=10
        )
        scored_ids = {d.domain_id: s for d, s in results}
        assert "SS-PSY" in scored_ids, "SS-PSY not in top-10 for brain query"
        assert "NS-BIO" in scored_ids, "NS-BIO not in top-10 for brain query"
        assert scored_ids["SS-PSY"] > 0.0
        assert scored_ids["NS-BIO"] > 0.0

    def test_noise_query_returns_zero_scores(self):
        """Gibberish input must not produce positive scores."""
        results = _make_engine().find_domains("xqzwvb zzzzplork", top_k=18)
        for _, score in results:
            assert score == 0.0

    def test_score_is_bounded(self):
        """Scores must always lie in [0.0, 1.0] regardless of query."""
        queries = [
            "physics quantum relativity",
            "algorithm machine learning",
            "spirit ritual ceremony",
            "history civilization empire",
            "brain neuroscience",
        ]
        engine = _make_engine()
        for query in queries:
            for _, score in engine.find_domains(query, top_k=18):
                assert 0.0 <= score <= 1.0, (
                    f"Score {score} out of bounds for query: {query!r}"
                )


# ---------------------------------------------------------------------------
# Class 6 — get_domain
# ---------------------------------------------------------------------------

class TestGetDomain:
    def test_known_id_returns_domain(self):
        domain = _make_engine().get_domain("NS-PHY")
        assert domain is not None
        assert domain.domain_id == "NS-PHY"

    def test_unknown_id_returns_none(self):
        assert _make_engine().get_domain("XX-FAKE") is None

    def test_returned_type_is_knowledge_domain(self):
        domain = _make_engine().get_domain("FS-CS")
        assert isinstance(domain, KnowledgeDomain)


# ---------------------------------------------------------------------------
# Class 7 — list_domains
# ---------------------------------------------------------------------------

class TestListDomains:
    def test_no_filter_returns_all(self):
        results = _make_engine().list_domains()
        assert len(results) == len(KNOWLEDGE_MATRIX)

    def test_branch_filter(self):
        results = _make_engine().list_domains(branch="Natural Sciences")
        assert all(d.branch == "Natural Sciences" for d in results)
        ids = {d.domain_id for d in results}
        assert {"NS-PHY", "NS-CHE", "NS-BIO", "NS-AST"}.issubset(ids)

    def test_tier_filter(self):
        results = _make_engine().list_domains(tier=EpistemicTier.CULTURAL)
        assert all(d.epistemic_tier == EpistemicTier.CULTURAL for d in results)
        ids = {d.domain_id for d in results}
        assert {"CW-SPI", "CW-ALC", "IK-TRD"}.issubset(ids)

    def test_branch_filter_case_insensitive(self):
        upper = _make_engine().list_domains(branch="Natural Sciences")
        lower = _make_engine().list_domains(branch="natural sciences")
        assert {d.domain_id for d in upper} == {d.domain_id for d in lower}

    def test_combined_filter_exclusive(self):
        """Natural Sciences domains are all Empirical — Cultural filter => empty."""
        results = _make_engine().list_domains(
            branch="Natural Sciences",
            tier=EpistemicTier.CULTURAL,
        )
        assert results == []


# ---------------------------------------------------------------------------
# Class 8 — cross_cultural_report
# ---------------------------------------------------------------------------

class TestCrossCulturalReport:
    def test_valid_domain_keys(self):
        report = _make_engine().cross_cultural_report("NS-PHY")
        expected = {
            "domain_id", "name", "epistemic_tier",
            "cross_cultural", "gaia_lens", "real_sources",
        }
        assert set(report.keys()) == expected

    def test_valid_domain_cross_cultural_nonempty(self):
        report = _make_engine().cross_cultural_report("NS-PHY")
        assert isinstance(report["cross_cultural"], dict)
        assert len(report["cross_cultural"]) > 0

    def test_tier_is_label_string(self):
        report = _make_engine().cross_cultural_report("NS-PHY")
        assert isinstance(report["epistemic_tier"], str)
        assert "T1" in report["epistemic_tier"]

    def test_unknown_domain_returns_error_dict(self):
        report = _make_engine().cross_cultural_report("XX-FAKE")
        assert "error" in report
        assert "XX-FAKE" in report["error"]


# ---------------------------------------------------------------------------
# Class 9 — epistemic_summary
# ---------------------------------------------------------------------------

class TestEpistemicSummary:
    def test_total_domains(self):
        summary = _make_engine().epistemic_summary()
        assert summary["total_domains"] == len(KNOWLEDGE_MATRIX)

    def test_domains_by_tier_has_multiple_keys(self):
        tiers = _make_engine().epistemic_summary()["domains_by_tier"]
        assert isinstance(tiers, dict)
        assert len(tiers) >= 4  # at least T1, T2, T4, T5 are represented

    def test_domains_by_branch_has_expected_branches(self):
        branches = _make_engine().epistemic_summary()["domains_by_branch"]
        for expected in (
            "Natural Sciences", "Formal Sciences",
            "Humanities", "Social Sciences",
        ):
            assert expected in branches, f"Branch '{expected}' missing from summary"

    def test_tier_counts_sum_to_total(self):
        summary = _make_engine().epistemic_summary()
        assert sum(summary["domains_by_tier"].values()) == summary["total_domains"]

    def test_branch_counts_sum_to_total(self):
        summary = _make_engine().epistemic_summary()
        assert sum(summary["domains_by_branch"].values()) == summary["total_domains"]


# ---------------------------------------------------------------------------
# Class 10 — get_knowledge_engine singleton
# ---------------------------------------------------------------------------

class TestSingletonEngine:
    def test_same_instance(self):
        """Two calls must return the exact same object."""
        a = get_knowledge_engine()
        b = get_knowledge_engine()
        assert a is b

    def test_is_engine_type(self):
        assert isinstance(get_knowledge_engine(), KnowledgeMatrixEngine)


# ---------------------------------------------------------------------------
# Class 11 — core/knowledge_matrix.py stub re-export
# ---------------------------------------------------------------------------

class TestStubReexport:
    def test_stub_exports_knowledge_matrix(self):
        from core.knowledge_matrix import KNOWLEDGE_MATRIX as _KM  # noqa: PLC0415
        assert len(_KM) >= 18

    def test_stub_exports_same_engine_class(self):
        from core.knowledge_matrix import KnowledgeMatrixEngine as _KME  # noqa: PLC0415
        assert _KME is KnowledgeMatrixEngine
