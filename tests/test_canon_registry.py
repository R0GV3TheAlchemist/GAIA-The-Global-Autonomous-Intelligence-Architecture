"""
tests/test_canon_registry.py

Canon Governance Test Suite — Block 5

Tests scripts/validate_canon_registry.py against synthetic fixtures
built entirely with tmp_path. No real canon/ directory is read.

Coverage:
  - Happy-path: valid registry + files → exit 0
  - Error conditions that must exit 1
  - Warning conditions that exit 0 by default, exit 2 with --strict
  - Helper functions: is_suffixed, extract_canon_id_prefix
  - Edge cases: _meta skip, non-path authoritative, --strict clean pass
  - Output content assertions (counts, PASS/FAIL labels)
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALIDATOR = Path("scripts/validate_canon_registry.py")


def run_validator(cwd: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Run the validator in *cwd* and return the CompletedProcess."""
    cmd = [sys.executable, str(VALIDATOR.resolve())]
    if extra_args:
        cmd.extend(extra_args)
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd))


def make_canon_dir(base: Path) -> Path:
    """Create base/canon/ and return its path."""
    canon = base / "canon"
    canon.mkdir(parents=True, exist_ok=True)
    return canon


def make_registry(base: Path, data: dict) -> None:
    """Write canon/REGISTRY.json inside *base*."""
    (base / "canon" / "REGISTRY.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def make_md(canon: Path, filename: str, status: str = "CANONICAL") -> Path:
    """Create a minimal .md file with a Status: header."""
    f = canon / filename
    f.write_text(
        f"# {filename}\n\nStatus: {status}\n\nBody text.",
        encoding="utf-8",
    )
    return f


def minimal_registry(canon_id: str, filename: str) -> dict:
    """Return a minimal valid REGISTRY.json dict for one entry."""
    return {
        "_meta": {
            "version": "1.0.0",
            "description": "test",
        },
        canon_id: {
            "authoritative": f"canon/{filename}",
            "status": "CANONICAL",
            "ratified": "2026-06-25",
            "supersedes": [],
            "deprecated": [],
            "archived": [],
            "primary_law": "L1",
            "key_xrefs": [],
        },
    }


# ---------------------------------------------------------------------------
# 1. Happy path — valid registry + file → exit 0
# ---------------------------------------------------------------------------


class TestHappyPath:
    def test_valid_single_entry_passes(self, tmp_path):
        """Single canonical entry with matching file and Status header: exit 0."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C100_Math_Foundations.md")
        make_registry(tmp_path, minimal_registry("C100", "C100_Math_Foundations.md"))

        result = run_validator(tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr
        assert "[PASS]" in result.stdout

    def test_valid_multiple_entries_pass(self, tmp_path):
        """Multiple canonical entries all passing: exit 0."""
        canon = make_canon_dir(tmp_path)
        ids = ["C101", "C102", "C103"]
        registry = {"_meta": {"version": "1.0.0", "description": "test"}}
        for cid in ids:
            fname = f"{cid}_Title.md"
            make_md(canon, fname)
            registry[cid] = {
                "authoritative": f"canon/{fname}",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [],
                "deprecated": [],
                "archived": [],
                "primary_law": "L1",
                "key_xrefs": [],
            }
        make_registry(tmp_path, registry)

        result = run_validator(tmp_path)
        assert result.returncode == 0, result.stdout + result.stderr

    def test_output_shows_correct_counts(self, tmp_path):
        """Summary output shows accurate file and ID counts."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C200_Doc.md")
        make_registry(tmp_path, minimal_registry("C200", "C200_Doc.md"))

        result = run_validator(tmp_path)
        assert "Canon files scanned : 1" in result.stdout
        assert "Registry IDs loaded : 1" in result.stdout

    def test_meta_key_excluded_from_id_count(self, tmp_path):
        """_meta key must not be counted as a Canon ID."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C201_Doc.md")
        data = minimal_registry("C201", "C201_Doc.md")
        # _meta is already in minimal_registry; confirm it's not counted
        make_registry(tmp_path, data)

        result = run_validator(tmp_path)
        assert "Registry IDs loaded : 1" in result.stdout  # only C201, not _meta


# ---------------------------------------------------------------------------
# 2. Error conditions — must exit 1
# ---------------------------------------------------------------------------


class TestErrorConditions:
    def test_missing_registry_file_exits_1(self, tmp_path):
        """No REGISTRY.json at all: validator exits 1 immediately."""
        make_canon_dir(tmp_path)  # canon/ exists but no REGISTRY.json
        result = run_validator(tmp_path)
        assert result.returncode == 1
        assert "not found" in result.stdout.lower() or "not found" in result.stderr.lower()

    def test_missing_canon_directory_exits_1(self, tmp_path):
        """No canon/ directory at all: validator exits 1."""
        # Write REGISTRY.json at root level — canon/ dir doesn't exist
        (tmp_path / "canon").mkdir()
        (tmp_path / "canon" / "REGISTRY.json").write_text(
            json.dumps({"_meta": {}}), encoding="utf-8"
        )
        # Now remove the canon dir to trigger missing-dir error
        import shutil
        shutil.rmtree(tmp_path / "canon")
        result = run_validator(tmp_path)
        assert result.returncode == 1

    def test_malformed_json_exits_1(self, tmp_path):
        """REGISTRY.json with invalid JSON: validator exits 1."""
        canon = make_canon_dir(tmp_path)
        (canon / "REGISTRY.json").write_text("{this is not json", encoding="utf-8")
        result = run_validator(tmp_path)
        assert result.returncode == 1

    def test_duplicate_non_suffixed_files_exits_1(self, tmp_path):
        """
        Two non-suffixed .md files sharing the same Canon ID prefix
        are an ERROR — validator must exit 1.
        """
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C154_AI_Personhood_Thresholds.md")
        make_md(canon, "C154_Cultural_Calibration_Archetypes.md")
        # Registry doesn't matter for duplicate detection
        make_registry(tmp_path, {
            "_meta": {"version": "1.0.0", "description": "test"},
            "C154_A": {
                "authoritative": "canon/C154_AI_Personhood_Thresholds.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L1", "key_xrefs": [],
            },
            "C154_B": {
                "authoritative": "canon/C154_Cultural_Calibration_Archetypes.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L2", "key_xrefs": [],
            },
        })
        result = run_validator(tmp_path)
        assert result.returncode == 1
        assert "ERROR" in result.stdout
        assert "C154" in result.stdout

    def test_authoritative_file_missing_on_disk_exits_1(self, tmp_path):
        """
        Registry entry points to a file that doesn’t exist on disk: ERROR.
        """
        canon = make_canon_dir(tmp_path)
        # Do NOT create the file on disk
        make_registry(tmp_path, minimal_registry("C300", "C300_Ghost_File.md"))

        result = run_validator(tmp_path)
        assert result.returncode == 1
        assert "ERROR" in result.stdout
        assert "C300" in result.stdout

    def test_error_message_names_conflicting_id(self, tmp_path):
        """Error output must name the specific Canon ID with duplicate files."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C158_Sleep_Dream_Full_Spec.md")
        make_md(canon, "C158_Sleep_Dream_Short_Spec.md")
        make_registry(tmp_path, {
            "_meta": {"version": "1.0.0", "description": "test"},
            "C158_FULL": {
                "authoritative": "canon/C158_Sleep_Dream_Full_Spec.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L3", "key_xrefs": [],
            },
            "C158_SHORT": {
                "authoritative": "canon/C158_Sleep_Dream_Short_Spec.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L3", "key_xrefs": [],
            },
        })
        result = run_validator(tmp_path)
        assert result.returncode == 1
        # C158 prefix should appear in the error message
        assert "C158" in result.stdout

    def test_errors_and_warnings_exit_1_not_2(self, tmp_path):
        """
        When both errors and warnings are present, exit code is 1
        (errors take priority over warnings).
        """
        canon = make_canon_dir(tmp_path)
        # Duplicate files → error
        make_md(canon, "C999_Alpha.md")
        make_md(canon, "C999_Beta.md")
        # File without Status header → warning
        (canon / "C888_NoStatus.md").write_text("# No status here", encoding="utf-8")
        make_registry(tmp_path, {
            "_meta": {"version": "1.0.0", "description": "test"},
            "C999_A": {
                "authoritative": "canon/C999_Alpha.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L1", "key_xrefs": [],
            },
            "C999_B": {
                "authoritative": "canon/C999_Beta.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L1", "key_xrefs": [],
            },
            "C888": {
                "authoritative": "canon/C888_NoStatus.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L1", "key_xrefs": [],
            },
        })
        result = run_validator(tmp_path)
        assert result.returncode == 1  # errors take priority


# ---------------------------------------------------------------------------
# 3. Warning conditions — exit 0 normally, exit 2 with --strict
# ---------------------------------------------------------------------------


class TestWarningConditions:
    def test_missing_status_header_is_warning_by_default(self, tmp_path):
        """File without Status: header produces WARNING but exits 0 normally."""
        canon = make_canon_dir(tmp_path)
        (canon / "C400_NoStatus.md").write_text("# Doc\n\nNo status here.", encoding="utf-8")
        make_registry(tmp_path, minimal_registry("C400", "C400_NoStatus.md"))

        result = run_validator(tmp_path)
        assert result.returncode == 0
        assert "WARN" in result.stdout
        assert "[PASS]" in result.stdout

    def test_file_not_in_registry_is_warning_by_default(self, tmp_path):
        """File on disk but not in registry: WARNING, exits 0 normally."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C500_Registered.md")
        make_md(canon, "C501_Unregistered.md")  # not in registry
        make_registry(tmp_path, minimal_registry("C500", "C500_Registered.md"))

        result = run_validator(tmp_path)
        assert result.returncode == 0
        assert "WARN" in result.stdout
        assert "C501_Unregistered.md" in result.stdout

    def test_strict_missing_status_exits_2(self, tmp_path):
        """--strict: missing Status: header upgrades to exit 2."""
        canon = make_canon_dir(tmp_path)
        (canon / "C600_NoStatus.md").write_text("# Doc\n\nNo status.", encoding="utf-8")
        make_registry(tmp_path, minimal_registry("C600", "C600_NoStatus.md"))

        result = run_validator(tmp_path, ["--strict"])
        assert result.returncode == 2
        assert "FAIL" in result.stdout

    def test_strict_unregistered_file_exits_2(self, tmp_path):
        """--strict: file not in registry upgrades to exit 2."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C700_Reg.md")
        make_md(canon, "C701_Unreg.md")
        make_registry(tmp_path, minimal_registry("C700", "C700_Reg.md"))

        result = run_validator(tmp_path, ["--strict"])
        assert result.returncode == 2

    def test_strict_clean_registry_still_exits_0(self, tmp_path):
        """--strict with a perfectly clean registry: exits 0."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C800_Clean.md")
        make_registry(tmp_path, minimal_registry("C800", "C800_Clean.md"))

        result = run_validator(tmp_path, ["--strict"])
        assert result.returncode == 0
        assert "[PASS]" in result.stdout


# ---------------------------------------------------------------------------
# 4. Suffix / prefix helper behaviour
# ---------------------------------------------------------------------------


class TestSuffixAndPrefixHelpers:
    """
    Import the helpers directly so we can unit-test them without subprocess.
    """

    @pytest.fixture(autouse=True)
    def _import_helpers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "validate_canon_registry",
            str(VALIDATOR.resolve()),
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.is_suffixed = mod.is_suffixed
        self.extract_prefix = mod.extract_canon_id_prefix

    # is_suffixed
    def test_deprecated_suffix_is_suffixed(self):
        assert self.is_suffixed("C154_AI_Personhood_DEPRECATED.md") is True

    def test_canonical_suffix_is_suffixed(self):
        assert self.is_suffixed("C154_AI_Personhood_CANONICAL.md") is True

    def test_archived_suffix_is_suffixed(self):
        assert self.is_suffixed("C154_AI_Personhood_ARCHIVED.md") is True

    def test_deprecated_fso002_suffix_is_suffixed(self):
        assert self.is_suffixed("C158_Sleep_DEPRECATED_FSO002.md") is True

    def test_plain_file_is_not_suffixed(self):
        assert self.is_suffixed("C154_AI_Personhood_Thresholds.md") is False

    def test_file_with_deprecated_in_middle_is_not_suffixed(self):
        # DEPRECATED only counts when it's the final suffix
        assert self.is_suffixed("C154_DEPRECATED_Extended_Title.md") is False

    # extract_canon_id_prefix
    def test_prefix_strips_deprecated(self):
        assert self.extract_prefix("C154_AI_Personhood_DEPRECATED.md") == "C154_AI_Personhood"

    def test_prefix_strips_canonical(self):
        assert self.extract_prefix("C154_AI_Personhood_CANONICAL.md") == "C154_AI_Personhood"

    def test_prefix_strips_archived(self):
        assert self.extract_prefix("C154_AI_Personhood_ARCHIVED.md") == "C154_AI_Personhood"

    def test_prefix_strips_deprecated_fso002(self):
        assert self.extract_prefix("C158_Sleep_DEPRECATED_FSO002.md") == "C158_Sleep"

    def test_prefix_plain_file_unchanged(self):
        assert self.extract_prefix("C200_Math_Foundations.md") == "C200_Math_Foundations"

    def test_prefix_biophoton_id(self):
        assert self.extract_prefix("BIOPHOTON_01_DNA_Optical_Waveguide.md") == "BIOPHOTON_01_DNA_Optical_Waveguide"


# ---------------------------------------------------------------------------
# 5. Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_meta_key_not_checked_as_canon_id(self, tmp_path):
        """
        _meta must never be treated as a Canon ID entry.
        A registry with only _meta (no Canon IDs) should pass cleanly.
        """
        canon = make_canon_dir(tmp_path)
        make_registry(tmp_path, {"_meta": {"version": "1.0.0", "description": "test"}})
        result = run_validator(tmp_path)
        # No errors because there's nothing to validate
        assert result.returncode == 0

    def test_non_path_authoritative_value_skipped(self, tmp_path):
        """
        CANON_COVENANT_001 style entries where authoritative is a prose string
        (not starting with 'canon/') must not trigger a file-existence error.
        """
        canon = make_canon_dir(tmp_path)
        make_registry(tmp_path, {
            "_meta": {"version": "1.0.0", "description": "test"},
            "CANON_COVENANT_001": {
                "authoritative": "GAIA's Promise — documented in GitHub Issue #631",
                "status": "CANONICAL",
                "ratified": "2026-06-23",
                "supersedes": [], "deprecated": [], "archived": [],
                "primary_law": "L1",
                "key_xrefs": [],
            },
        })
        result = run_validator(tmp_path)
        # Prose authoritative value must not cause an error
        assert result.returncode == 0

    def test_deprecated_stub_not_counted_as_duplicate(self, tmp_path):
        """
        A _DEPRECATED file alongside its authoritative non-suffixed counterpart
        must NOT trigger a duplicate-ID error.
        """
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C133_Regenerative_Economics_Resource_Allocation_GAIA_OS.md")
        make_md(canon, "C133_Axiology_Metaphysics_of_Value_Charter_Authority_DEPRECATED.md")
        make_registry(tmp_path, minimal_registry(
            "C133",
            "C133_Regenerative_Economics_Resource_Allocation_GAIA_OS.md",
        ))
        result = run_validator(tmp_path)
        # _DEPRECATED file is suffixed → no duplicate
        assert result.returncode == 0

    def test_archived_file_alongside_active_not_duplicate(self, tmp_path):
        """
        A _ARCHIVED file alongside an active file for the same ID:
        not a duplicate (archived is suffixed).
        """
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C00_FOUNDATIONAL_COSMOLOGY.md")
        make_md(canon, "C00_FOUNDATIONAL_COSMOLOGY_ARCHIVED.md")
        make_registry(tmp_path, minimal_registry(
            "C00",
            "C00_FOUNDATIONAL_COSMOLOGY.md",
        ))
        result = run_validator(tmp_path)
        assert result.returncode == 0

    def test_empty_canon_directory_no_crash(self, tmp_path):
        """
        An empty canon/ directory with a valid (but empty) registry:
        validator should exit 0 without crashing.
        """
        canon = make_canon_dir(tmp_path)
        make_registry(tmp_path, {"_meta": {"version": "1.0.0", "description": "test"}})
        result = run_validator(tmp_path)
        assert result.returncode == 0

    def test_registry_with_only_archived_entries_passes(self, tmp_path):
        """
        Registry entry whose authoritative file path starts with 'canon/'
        and exists on disk: passes even if file is an archived variant.
        """
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C00_FOUNDATIONAL_COSMOLOGY.md")
        registry = {
            "_meta": {"version": "1.0.0", "description": "test"},
            "C00": {
                "authoritative": "canon/C00_FOUNDATIONAL_COSMOLOGY.md",
                "status": "CANONICAL",
                "ratified": "2026-06-25",
                "supersedes": [],
                "deprecated": [],
                "archived": [],
                "primary_law": "L1",
                "key_xrefs": [],
            },
        }
        make_registry(tmp_path, registry)
        result = run_validator(tmp_path)
        assert result.returncode == 0

    def test_output_includes_pass_label_on_success(self, tmp_path):
        """Successful run always prints [PASS] in stdout."""
        canon = make_canon_dir(tmp_path)
        make_md(canon, "C999_Clean.md")
        make_registry(tmp_path, minimal_registry("C999", "C999_Clean.md"))
        result = run_validator(tmp_path)
        assert "[PASS]" in result.stdout

    def test_output_includes_fail_label_on_error(self, tmp_path):
        """Failed run always prints [FAIL] in stdout."""
        canon = make_canon_dir(tmp_path)
        # Registry points to a non-existent file
        make_registry(tmp_path, minimal_registry("C998", "C998_Ghost.md"))
        result = run_validator(tmp_path)
        assert result.returncode == 1
        assert "[FAIL]" in result.stdout
