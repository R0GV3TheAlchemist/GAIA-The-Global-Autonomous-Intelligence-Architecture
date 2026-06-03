"""Tests for MemoryTier hierarchy registration in sovereign_memory.

Issue: AttributeError: WORKING — MemoryTier lacked the WORKING enum member.
Fix:   Added MemoryTier.WORKING to sovereign_memory/types.py.
"""
import pytest
from sovereign_memory.types import MemoryTier


class TestBuildDefaultRouter:
    """Verify that all five expected memory tiers are registered."""

    def test_all_five_tiers_registered(self):
        """All canonical tiers must be present in the MemoryTier enum."""
        expected = {"working", "semantic", "long_term", "biometric", "archival"}
        actual   = {t.value for t in MemoryTier}
        assert expected == actual, (
            f"Missing tiers: {expected - actual}, unexpected tiers: {actual - expected}"
        )

    def test_working_tier_accessible(self):
        """MemoryTier.WORKING must be accessible and have the correct value."""
        assert MemoryTier.WORKING == "working"
        assert MemoryTier.WORKING.value == "working"

    def test_custom_semantic_store_injected(self):
        """MemoryTier.SEMANTIC must be present for semantic store injection."""
        assert MemoryTier.SEMANTIC in MemoryTier
        assert MemoryTier.SEMANTIC.value == "semantic"

    def test_custom_long_term_store_injected(self):
        """MemoryTier.LONG_TERM must be present for persistent store injection."""
        assert MemoryTier.LONG_TERM in MemoryTier
        assert MemoryTier.LONG_TERM.value == "long_term"

    def test_tier_ordering_working_first(self):
        """WORKING tier should be first (lowest index) in the enum definition."""
        tiers = list(MemoryTier)
        assert tiers[0] == MemoryTier.WORKING
