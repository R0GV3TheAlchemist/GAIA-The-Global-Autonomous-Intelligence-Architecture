"""Tests for the primordial entity archetypes."""

from __future__ import annotations

from core.primordial.archetypes import ARCHETYPES, run_all_archetypes


def test_all_archetypes_defined():
    expected = {"the_witness", "the_builder", "the_betrayed", "the_endurer", "the_restored"}
    assert set(ARCHETYPES.keys()) == expected


def test_all_archetypes_run_without_error():
    results = run_all_archetypes()
    assert len(results) == 5


def test_each_result_has_narrative():
    results = run_all_archetypes()
    for r in results:
        assert r.narrative
        assert len(r.narrative) > 0


def test_the_restored_uses_recovery_path():
    results = run_all_archetypes()
    restored = next(r for r in results if r.archetype.name == "the-restored")
    assert restored.recovery_narrative is not None


def test_the_witness_survives():
    results = run_all_archetypes()
    witness = next(r for r in results if r.archetype.name == "the-witness")
    assert witness.survived is True


def test_the_endurer_survives():
    results = run_all_archetypes()
    endurer = next(r for r in results if r.archetype.name == "the-endurer")
    assert endurer.survived is True
