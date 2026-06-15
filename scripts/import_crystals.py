#!/usr/bin/env python
"""Bulk crystal correspondence loader.

Usage
-----
  python scripts/import_crystals.py data/correspondence/
  python scripts/import_crystals.py data/correspondence/ --dry-run
  python scripts/import_crystals.py data/correspondence/ --verbose
  python scripts/import_crystals.py data/correspondence/ --glob 'crystal_*.json'

The loader:
  1. Discovers all matching JSON files in the given directory (recursive).
  2. Validates each file against schemas/correspondence-schema.json.
  3. Upserts valid entries into the crystal_correspondence table.
  4. Auto-links ingested crystals to Prismatic and resonance_field_engine.
  5. Rolls back the entire transaction on any unrecoverable error (unless
     --continue-on-error is passed).
  6. Prints a final summary report.
"""
from __future__ import annotations

import argparse
import logging
import pathlib
import sys

# ── Ensure project root is on sys.path ──────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.crystal_correspondence.ingestion import (
    clear_validation_errors,
    get_validation_errors,
    ingest_crystal_file,
)


def _build_session():
    """Build a SQLAlchemy session from GAIA's standard DB config."""
    try:
        from core.database import get_session_factory  # type: ignore[import]
        SessionFactory = get_session_factory()
        return SessionFactory()
    except ImportError:
        # Fallback: build a session from DATABASE_URL env var
        import os
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        db_url = os.environ.get("DATABASE_URL", "postgresql://localhost/gaia")
        engine = create_engine(db_url)
        return sessionmaker(bind=engine)()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bulk-import crystal correspondence JSON files into GAIA-OS."
    )
    parser.add_argument("directory",        help="Directory to scan for crystal JSON files")
    parser.add_argument("--glob",           default="crystal_*.json", help="Glob pattern (default: crystal_*.json)")
    parser.add_argument("--dry-run",        action="store_true",       help="Validate and report without writing to the DB")
    parser.add_argument("--verbose",        action="store_true",       help="Verbose per-file logging")
    parser.add_argument("--continue-on-error", action="store_true",   help="Continue after per-file errors instead of rolling back")
    parser.add_argument("--changed-by",     default="bulk-import",     help="Provenance: who ran this import")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-8s %(message)s",
    )
    log = logging.getLogger("import_crystals")

    directory = pathlib.Path(args.directory)
    if not directory.is_dir():
        log.error("Directory not found: %s", directory)
        return 1

    files = sorted(directory.rglob(args.glob))
    if not files:
        log.warning("No files matched '%s' in %s", args.glob, directory)
        return 0

    log.info("Found %d crystal file(s) to process.", len(files))

    ok_count = err_count = skip_count = 0
    clear_validation_errors()

    if args.dry_run:
        session = None
    else:
        session = _build_session()

    try:
        for path in files:
            if args.verbose:
                log.debug("Processing: %s", path)

            success, errors = ingest_crystal_file(
                path,
                session,
                changed_by=args.changed_by,
                dry_run=args.dry_run,
            )

            if success:
                ok_count += 1
            else:
                err_count += 1
                for e in errors:
                    log.error("  [%s] %s", path.name, e)
                if not args.continue_on_error:
                    log.error("Stopping due to error (use --continue-on-error to skip).")
                    if session:
                        session.rollback()
                    return 1

        if not args.dry_run and session:
            session.commit()
            log.info("Transaction committed.")

    except Exception as exc:  # noqa: BLE001
        log.exception("Unrecoverable error: %s", exc)
        if session:
            session.rollback()
        return 1
    finally:
        if session:
            session.close()

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print("═" * 50)
    print(f"  Crystal Import {'(DRY RUN) ' if args.dry_run else ''}Summary")
    print("═" * 50)
    print(f"  ✅  Successful : {ok_count}")
    print(f"  ❌  Errors     : {err_count}")
    print(f"  ⏭   Skipped    : {skip_count}")
    print(f"  Total files   : {len(files)}")

    validation_errors = get_validation_errors()
    if validation_errors:
        print()
        print("  Validation error queue:")
        for ve in validation_errors:
            print(f"    • {ve['subject_id']}: {ve['error']}")

    print("═" * 50)
    return 0 if err_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
