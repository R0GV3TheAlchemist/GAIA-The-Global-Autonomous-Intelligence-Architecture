"""Ingestion pipeline for crystal correspondence JSON files.

Responsibilities:
  1. Validate JSON against schemas/correspondence-schema.json
  2. Extract indexed scalars (color, frequency, alchemical_stage, etc.)
  3. Upsert into crystal_correspondence (duplicate-safe)
  4. Auto-link to engine registries: Prismatic, resonance_field_engine
  5. Append provenance log entry on every change
  6. Push invalid files to a validation error queue
"""
from __future__ import annotations

import json
import logging
import pathlib
import traceback
from datetime import datetime, timezone
from typing import Any

try:
    import jsonschema
except ImportError:
    jsonschema = None  # type: ignore[assignment]

from sqlalchemy.orm import Session

from core.crystal_correspondence.models import CrystalCorrespondence, CrystalCorrespondenceProvenanceLog

log = logging.getLogger(__name__)

# Path to the canonical JSON Schema
SCHEMA_PATH = pathlib.Path(__file__).parents[2] / "schemas" / "correspondence-schema.json"

# ── Validation error queue (in-memory; swap for Redis/SQS in prod) ──────────
_VALIDATION_ERROR_QUEUE: list[dict] = []


def get_validation_errors() -> list[dict]:
    """Return accumulated validation errors since last clear."""
    return list(_VALIDATION_ERROR_QUEUE)


def clear_validation_errors() -> None:
    _VALIDATION_ERROR_QUEUE.clear()


# ── Schema loader ────────────────────────────────────────────────────────────
_SCHEMA_CACHE: dict | None = None


def _load_schema() -> dict | None:
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is not None:
        return _SCHEMA_CACHE
    if SCHEMA_PATH.exists():
        with SCHEMA_PATH.open() as fh:
            _SCHEMA_CACHE = json.load(fh)
        return _SCHEMA_CACHE
    log.warning("correspondence-schema.json not found at %s — skipping schema validation", SCHEMA_PATH)
    return None


# ── Scalar extractor ─────────────────────────────────────────────────────────
def _extract_scalars(data: dict) -> dict[str, Any]:
    """Pull indexed scalar columns from the correspondence JSON payload."""
    corr = data.get("correspondences", {})
    grid = corr.get("grid_resonance", {})
    elements = corr.get("elements", [])
    gaia_layers = corr.get("gaia_layers", [])
    physical = corr.get("physical", {})
    color_data = corr.get("color", {})

    # Primary color: first entry in color.primary_colors list, or grid color hint
    primary_color = None
    pc_list = color_data.get("primary_colors", [])
    if pc_list:
        primary_color = pc_list[0] if isinstance(pc_list[0], str) else pc_list[0].get("color")
    if not primary_color:
        primary_color = physical.get("primary_color")

    # Frequency: from grid_resonance.frequency_band_hz or spectral data
    freq_low = freq_high = None
    freq_band = grid.get("frequency_band_hz", "")
    if freq_band and isinstance(freq_band, str) and "-" in freq_band:
        parts = freq_band.split("-")
        try:
            freq_low  = float(parts[0].strip())
            freq_high = float(parts[1].strip())
        except (ValueError, IndexError):
            pass
    elif isinstance(freq_band, (int, float)):
        freq_low = freq_high = float(freq_band)

    # Alchemical stage: from correspondences.alchemical_stage or metadata
    alchemical_stage = (
        corr.get("alchemical_stage")
        or data.get("metadata", {}).get("alchemical_stage")
    )

    # Primary GAIA layer: highest-weight layer_id
    primary_gaia_layer = None
    if gaia_layers:
        top = max(gaia_layers, key=lambda x: x.get("weight", 0))
        primary_gaia_layer = top.get("layer_id")

    # Primary element: first element entry with weight == 1.0 or first overall
    primary_element = None
    if elements:
        top_el = max(elements, key=lambda x: x.get("weight", 0))
        primary_element = top_el.get("element")

    # Mohs hardness
    mohs_low = mohs_high = None
    mohs_raw = physical.get("mohs_hardness", "")
    if mohs_raw:
        if isinstance(mohs_raw, str) and "-" in mohs_raw:
            try:
                parts = mohs_raw.split("-")
                mohs_low  = float(parts[0].strip())
                mohs_high = float(parts[1].strip())
            except (ValueError, IndexError):
                pass
        elif isinstance(mohs_raw, (int, float)):
            mohs_low = mohs_high = float(mohs_raw)

    return {
        "common_name":       data.get("subject_id", "").replace("crystal:", "").title(),
        "mineral_formula":   physical.get("formula") or corr.get("formula"),
        "crystal_system":    grid.get("lattice_analogue") or physical.get("crystal_system"),
        "mohs_hardness_low": mohs_low,
        "mohs_hardness_high": mohs_high,
        "primary_color":     primary_color,
        "frequency_hz_low":  freq_low,
        "frequency_hz_high": freq_high,
        "alchemical_stage":  alchemical_stage,
        "primary_gaia_layer": primary_gaia_layer,
        "primary_element":   primary_element,
    }


# ── Engine auto-link hooks ────────────────────────────────────────────────────
def _link_to_prismatic(crystal: CrystalCorrespondence) -> None:
    """Notify the Prismatic engine that a new/updated crystal is available.

    In production this would POST to the Prismatic engine registry or
    publish a message to the internal event bus.  Stubbed here with a log.
    """
    log.info("[Prismatic] Auto-linked crystal: %s (layer=%s)", crystal.subject_id, crystal.primary_gaia_layer)
    # TODO: replace with actual Prismatic engine registration call
    # e.g.  prismatic_engine.register_crystal(crystal.subject_id, crystal.correspondences)


def _link_to_resonance_field_engine(crystal: CrystalCorrespondence) -> None:
    """Notify the resonance_field_engine of a new/updated crystal frequency range."""
    log.info(
        "[ResonanceField] Auto-linked crystal: %s (%.2f–%.2f Hz)",
        crystal.subject_id,
        crystal.frequency_hz_low or 0,
        crystal.frequency_hz_high or 0,
    )
    # TODO: resonance_field_engine.register_node(crystal.subject_id, freq_low, freq_high, crystal.correspondences)


def _auto_link_engines(crystal: CrystalCorrespondence) -> None:
    """Call all engine auto-link hooks.  Failures are logged, not raised."""
    for hook in (_link_to_prismatic, _link_to_resonance_field_engine):
        try:
            hook(crystal)
        except Exception:  # noqa: BLE001
            log.exception("Engine auto-link failed for %s", crystal.subject_id)


# ── Core ingest function ──────────────────────────────────────────────────────
def ingest_crystal(
    data: dict,
    session: Session,
    *,
    changed_by: str = "GAIA-OS",
    change_note: str | None = None,
    dry_run: bool = False,
) -> tuple[bool, list[str]]:
    """Validate and upsert a single crystal correspondence dict.

    Returns
    -------
    (success: bool, errors: list[str])
    """
    errors: list[str] = []

    # 1. JSON Schema validation ──────────────────────────────────────────────
    schema = _load_schema()
    if schema and jsonschema:
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as exc:
            msg = f"Schema validation failed: {exc.message} at {list(exc.path)}"
            errors.append(msg)
            _VALIDATION_ERROR_QUEUE.append({"subject_id": data.get("subject_id"), "error": msg, "ts": datetime.now(tz=timezone.utc).isoformat()})
            return False, errors

    subject_id = data.get("subject_id")
    if not subject_id:
        errors.append("subject_id is required")
        return False, errors

    if dry_run:
        log.info("[DryRun] Would ingest: %s", subject_id)
        return True, []

    # 2. Extract scalars ─────────────────────────────────────────────────────
    scalars = _extract_scalars(data)
    schema_version = data.get("metadata", {}).get("schema_version", "1.0.0")
    now_iso = datetime.now(tz=timezone.utc).isoformat()

    provenance = {
        "source":       data.get("metadata", {}).get("created_by", "GAIA-OS"),
        "confidence":   data.get("correspondences", {}).get("evidence_profile", {}).get("confidence", "high"),
        "last_updated": data.get("metadata", {}).get("updated_at") or now_iso,
        "canon_refs":   data.get("metadata", {}).get("canon_refs", []),
        "basis":        data.get("correspondences", {}).get("evidence_profile", {}).get("basis"),
    }

    # 3. Upsert ──────────────────────────────────────────────────────────────
    crystal = session.query(CrystalCorrespondence).filter_by(subject_id=subject_id).one_or_none()
    is_new = crystal is None

    if is_new:
        crystal = CrystalCorrespondence(subject_id=subject_id)
        session.add(crystal)

    # Snapshot before update for provenance log
    old_snapshot = {
        "correspondences": crystal.correspondences if not is_new else {},
        "provenance":      crystal.provenance      if not is_new else {},
    }

    # Apply scalar fields
    for field, value in scalars.items():
        setattr(crystal, field, value)

    crystal.correspondences  = data.get("correspondences", {})
    crystal.schema_version   = schema_version
    crystal.provenance       = provenance
    crystal.updated_at       = datetime.now(tz=timezone.utc)

    session.flush()  # get crystal.id before log insert

    # 4. Append provenance log ───────────────────────────────────────────────
    log_entry = CrystalCorrespondenceProvenanceLog(
        crystal_id=crystal.id,
        version=schema_version,
        changed_by=changed_by,
        change_note=change_note or ("initial import" if is_new else "upsert update"),
        snapshot=old_snapshot["correspondences"],
        provenance_snapshot=old_snapshot["provenance"],
    )
    session.add(log_entry)

    # 5. Engine auto-link ────────────────────────────────────────────────────
    _auto_link_engines(crystal)

    log.info("%s crystal: %s", "Created" if is_new else "Updated", subject_id)
    return True, []


def ingest_crystal_file(
    path: pathlib.Path,
    session: Session,
    **kwargs: Any,
) -> tuple[bool, list[str]]:
    """Load a JSON file from disk and ingest it."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return False, [f"Failed to read/parse {path}: {exc}"]
    return ingest_crystal(data, session, **kwargs)
