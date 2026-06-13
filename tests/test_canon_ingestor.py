"""
tests/test_canon_ingestor.py
Tests for core/canon_ingestor.py

Covers:
  - Frontmatter parsing (with and without YAML header)
  - ref_id derivation from filenames
  - Single-file parsing into CanonEntry
  - Full directory ingestion
  - assert_full_coverage() helper
  - Graceful handling of empty / unreadable files
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from core.canon.canon_entry import CanonEntry, RegisterSignal
from core.canon_ingestor import (
    IngestionReport,
    _derive_ref_id,
    _parse_frontmatter,
    _parse_canon_file,
    assert_full_coverage,
    ingest_canon_directory,
)
from core.canon_loader import CanonLoader


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


# ---------------------------------------------------------------------------
# _derive_ref_id
# ---------------------------------------------------------------------------

def test_derive_ref_id_c100():
    assert _derive_ref_id("C100_Personal_Gaian_Architecture.md") == "C100"

def test_derive_ref_id_c00():
    assert _derive_ref_id("C00_Sovereign_Principles.md") == "C00"

def test_derive_ref_id_c168():
    assert _derive_ref_id("C168_Collective_Intelligence.md") == "C168"

def test_derive_ref_id_non_numeric():
    result = _derive_ref_id("ELEMENTAL_STAR.md")
    assert result == "ELEMENTAL_STAR"

def test_derive_ref_id_uppercase():
    assert _derive_ref_id("c107_test.md") == "C107"


# ---------------------------------------------------------------------------
# _parse_frontmatter
# ---------------------------------------------------------------------------

def test_frontmatter_present():
    raw = textwrap.dedent("""\
        ---
        ref_id: C107
        author: GAIA-OS
        timestamp: 2026-06-01T00:00:00Z
        version: 1.0.0
        tags: [sovereignty, memory, gaian]
        ---

        # Personal Gaian Architecture

        Body text here.
    """)
    meta, body = _parse_frontmatter(raw)
    assert meta["ref_id"] == "C107"
    assert meta["author"] == "GAIA-OS"
    assert "sovereignty" in meta["tags"]
    assert "Personal Gaian Architecture" in body

def test_frontmatter_absent():
    raw = "# Just a header\n\nSome body content."
    meta, body = _parse_frontmatter(raw)
    assert meta == {}
    assert "body content" in body

def test_frontmatter_empty_body_falls_back():
    raw = textwrap.dedent("""\
        ---
        ref_id: C101
        author: test
        timestamp: 2026-01-01T00:00:00Z
        version: 1.0.0
        ---
    """)
    meta, body = _parse_frontmatter(raw)
    assert meta["ref_id"] == "C101"
    # body is empty string after frontmatter
    assert body == ""


# ---------------------------------------------------------------------------
# _parse_canon_file
# ---------------------------------------------------------------------------

def test_parse_canon_file_with_frontmatter(tmp_path):
    p = _write(tmp_path, "C107_test.md", """\
        ---
        ref_id: C107
        author: GAIA-OS
        timestamp: 2026-06-01T00:00:00Z
        version: 1.0.0
        tags: [gaian, memory]
        ---

        This is the body of the canon entry.
    """)
    entry = _parse_canon_file(p)
    assert entry is not None
    assert entry.ref_id == "C107"
    assert entry.author == "GAIA-OS"
    assert "body of the canon entry" in entry.body
    assert "gaian" in entry.tags

def test_parse_canon_file_no_frontmatter(tmp_path):
    p = _write(tmp_path, "C108_no_fm.md", """\
        # Heading

        Canon body content without frontmatter.
    """)
    entry = _parse_canon_file(p)
    assert entry is not None
    assert entry.ref_id == "C108"
    assert entry.author == "GAIA-OS"  # default
    assert "Canon body" in entry.body

def test_parse_canon_file_empty(tmp_path):
    p = tmp_path / "C109_empty.md"
    p.write_text("", encoding="utf-8")
    entry = _parse_canon_file(p)
    assert entry is None

def test_parse_canon_file_whitespace_only(tmp_path):
    p = tmp_path / "C110_ws.md"
    p.write_text("   \n\n  ", encoding="utf-8")
    entry = _parse_canon_file(p)
    assert entry is None

def test_parse_canon_file_timestamp_date_only(tmp_path):
    """A date-only timestamp (YYYY-MM-DD) should be normalised to ISO-8601."""
    p = _write(tmp_path, "C111_date.md", """\
        ---
        ref_id: C111
        author: test
        timestamp: 2026-06-01
        version: 1.0.0
        ---
        Body.
    """)
    entry = _parse_canon_file(p)
    assert entry is not None
    assert entry.timestamp == "2026-06-01T00:00:00Z"


# ---------------------------------------------------------------------------
# ingest_canon_directory
# ---------------------------------------------------------------------------

def test_ingest_directory_basic(tmp_path):
    _write(tmp_path, "C100_Alpha.md", """\
        ---
        ref_id: C100
        author: GAIA-OS
        timestamp: 2026-01-01T00:00:00Z
        version: 1.0.0
        ---
        Alpha canon entry body text.
    """)
    _write(tmp_path, "C101_Beta.md", """\
        ---
        ref_id: C101
        author: GAIA-OS
        timestamp: 2026-01-01T00:00:00Z
        version: 1.0.0
        ---
        Beta canon entry body text.
    """)
    loader = CanonLoader()
    report = ingest_canon_directory(canon_dir=tmp_path, loader=loader, skip_validation=True)
    assert report.loaded == 2
    assert report.failed == 0
    assert "C100" in loader.list_ids()
    assert "C101" in loader.list_ids()

def test_ingest_directory_skips_empty(tmp_path):
    _write(tmp_path, "C100_Good.md", """\
        Body text for good entry.
    """)
    empty = tmp_path / "C101_Empty.md"
    empty.write_text("", encoding="utf-8")
    loader = CanonLoader()
    report = ingest_canon_directory(canon_dir=tmp_path, loader=loader, skip_validation=True)
    assert report.loaded == 1
    assert report.skipped == 1
    assert report.failed == 0

def test_ingest_directory_missing(tmp_path):
    missing = tmp_path / "does_not_exist"
    loader = CanonLoader()
    report = ingest_canon_directory(canon_dir=missing, loader=loader)
    assert report.failed >= 1
    assert report.loaded == 0

def test_ingest_recursive(tmp_path):
    """Files in subdirectories are also ingested."""
    sub = tmp_path / "sub"
    sub.mkdir()
    _write(sub, "C200_Sub.md", "Sub-directory canon body text.")
    _write(tmp_path, "C100_Root.md", "Root level canon body text.")
    loader = CanonLoader()
    report = ingest_canon_directory(canon_dir=tmp_path, loader=loader, skip_validation=True)
    assert report.loaded == 2
    assert "C200" in loader.list_ids()
    assert "C100" in loader.list_ids()


# ---------------------------------------------------------------------------
# TF-IDF search after ingestion
# ---------------------------------------------------------------------------

def test_search_after_ingestion(tmp_path):
    _write(tmp_path, "C100_Sovereignty.md", """\
        Gaian sovereignty means the individual controls their own data,
        memory, and relationship with their Gaian companion.
    """)
    _write(tmp_path, "C101_Schumann.md", """\
        The Schumann Resonance is Earth's electromagnetic heartbeat
        pulsing at approximately 7.83 Hz.
    """)
    loader = CanonLoader()
    ingest_canon_directory(canon_dir=tmp_path, loader=loader, skip_validation=True)

    results = loader.search("sovereignty memory", max_results=3)
    assert len(results) >= 1
    assert results[0]["doc_id"] == "C100"

    results2 = loader.search("Schumann electromagnetic", max_results=3)
    assert len(results2) >= 1
    assert results2[0]["doc_id"] == "C101"


# ---------------------------------------------------------------------------
# assert_full_coverage
# ---------------------------------------------------------------------------

def test_assert_full_coverage_passes(tmp_path):
    _write(tmp_path, "C100_Full.md", "Full coverage body text for testing.")
    loader = CanonLoader()
    ingest_canon_directory(canon_dir=tmp_path, loader=loader, skip_validation=True)
    missing = assert_full_coverage(canon_dir=tmp_path, loader=loader)
    assert missing == []

def test_assert_full_coverage_detects_missing(tmp_path):
    _write(tmp_path, "C100_Present.md", "Present entry body text.")
    _write(tmp_path, "C101_Missing.md", "Missing entry body text.")
    loader = CanonLoader()
    # Only ingest C100, not C101
    p = tmp_path / "C100_Present.md"
    from core.canon_ingestor import _parse_canon_file
    entry = _parse_canon_file(p)
    loader.load(entry)
    missing = assert_full_coverage(canon_dir=tmp_path, loader=loader)
    assert "C101_Missing.md" in missing
