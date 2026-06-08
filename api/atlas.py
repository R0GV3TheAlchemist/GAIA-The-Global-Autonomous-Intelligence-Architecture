"""
api/atlas.py — P5 ATLAS: GAIA as Living Digital Twin of Earth

Endpoints:
  GET /atlas/clouds      — current satellite cloud tile URLs (NASA GIBS)
  GET /atlas/terminator  — real-time sun position for day/night line
  GET /atlas/events      — active global events (USGS earthquakes, NOAA storms)
  GET /atlas/health      — Earth health metric bundle

All external calls are cached for 3 hours (TTL = 10800 s).
If external APIs are unreachable, last-known cached data is returned
so GAIA works fully offline.
"""

from __future__ import annotations

import json
import math
import time
import httpx
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/atlas", tags=["atlas"])

# ── Cache ────────────────────────────────────────────────────────────────────

CACHE_DIR = Path.home() / ".local" / "share" / "GAIA" / "atlas-cache"
CACHE_TTL = 10_800  # 3 hours in seconds


def _cache_path(key: str) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return CACHE_DIR / f"{key}.json"


def _read_cache(key: str) -> Any | None:
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text())
        if time.time() - data["ts"] < CACHE_TTL:
            return data["payload"]
        # Stale but keep for offline fallback — we return it below if fetch fails
    except Exception:
        pass
    return None


def _read_cache_offline(key: str) -> Any | None:
    """Return cached data regardless of age (offline fallback)."""
    p = _cache_path(key)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())["payload"]
    except Exception:
        return None


def _write_cache(key: str, payload: Any) -> None:
    try:
        _cache_path(key).write_text(json.dumps({"ts": time.time(), "payload": payload}))
    except Exception:
        pass


async def _fetch(url: str, params: dict | None = None, timeout: int = 8) -> Any | None:
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            return r.json()
    except Exception:
        return None


# ── Sun position (terminator) ───────────────────────────────────────────────────

def _compute_sun_position() -> dict:
    """
    Compute approximate solar declination and hour angle from UTC time.
    Accurate to within ~1 degree for the terminator visualisation.
    """
    now = datetime.now(timezone.utc)
    day_of_year = now.timetuple().tm_yday

    # Solar declination (degrees)
    declination = -23.45 * math.cos(math.radians(360 / 365 * (day_of_year + 10)))

    # Greenwich hour angle (degrees) — sun longitude at UTC noon = 0
    utc_hours = now.hour + now.minute / 60 + now.second / 3600
    sun_longitude = (utc_hours - 12) * 15  # 15 deg per hour
    # Normalise to -180..180
    if sun_longitude > 180:
        sun_longitude -= 360
    elif sun_longitude < -180:
        sun_longitude += 360

    return {
        "latitude": round(declination, 4),
        "longitude": round(sun_longitude, 4),
        "utc": now.isoformat(),
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/clouds")
async def get_clouds():
    """
    Return current satellite cloud tile URLs from NASA GIBS.
    Tiles are WMTS-standard; the frontend renders them as a
    scrolling transparent texture over the GaianOrb.
    """
    KEY = "clouds"
    cached = _read_cache(KEY)
    if cached:
        return cached

    # NASA GIBS WMTS base — MODIS Terra True Color, updated daily
    # We return the tile template URL + today's date so the frontend
    # can construct individual tile requests at its chosen zoom level.
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    payload = {
        "source": "NASA GIBS",
        "layer": "MODIS_Terra_CorrectedReflectance_TrueColor",
        "date": today,
        "tile_url_template": (
            "https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/"
            "MODIS_Terra_CorrectedReflectance_TrueColor/default/"
            f"{today}/250m/{{z}}/{{y}}/{{x}}.jpg"
        ),
        "opacity": 0.55,
        "cached": False,
    }

    _write_cache(KEY, payload)
    return payload


@router.get("/terminator")
async def get_terminator():
    """
    Return the current sun position for rendering the day/night terminator.
    Computed locally — no external API needed, always accurate in real time.
    Updates every time the endpoint is called (no cache needed).
    """
    return _compute_sun_position()


@router.get("/events")
async def get_events():
    """
    Return active global events:
      - Earthquakes M4.5+ from USGS (past 24 h)
      - Significant weather events from NOAA (past 24 h)
    """
    KEY = "events"
    cached = _read_cache(KEY)
    if cached:
        return cached

    events = []

    # ─ USGS Earthquakes ──────────────────────────────────────────────
    usgs = await _fetch(
        "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson"
    )
    if usgs and "features" in usgs:
        for feat in usgs["features"][:10]:  # cap at 10
            props = feat.get("properties", {})
            coords = feat.get("geometry", {}).get("coordinates", [0, 0, 0])
            events.append({
                "type": "earthquake",
                "title": props.get("title", "Earthquake"),
                "magnitude": props.get("mag", 0),
                "latitude": coords[1],
                "longitude": coords[0],
                "depth_km": coords[2],
                "time": props.get("time"),
                "url": props.get("url"),
            })

    # ─ NOAA Active Alerts (US) ─────────────────────────────────────────
    # Filter to hurricane/tropical storm events only for global significance
    noaa = await _fetch(
        "https://api.weather.gov/alerts/active",
        params={"event": "Hurricane Warning,Tropical Storm Warning,Tornado Warning"},
    )
    if noaa and "features" in noaa:
        for feat in noaa["features"][:5]:  # cap at 5
            props = feat.get("properties", {})
            geo = feat.get("geometry") or {}
            coords = (geo.get("coordinates") or [[[]]])[0]
            # Use centroid of the polygon if available
            if coords and isinstance(coords[0], list):
                lats = [c[1] for c in coords if len(c) >= 2]
                lons = [c[0] for c in coords if len(c) >= 2]
                lat = sum(lats) / len(lats) if lats else 0
                lon = sum(lons) / len(lons) if lons else 0
            else:
                lat, lon = 0, 0

            events.append({
                "type": "storm",
                "title": props.get("event", "Storm Warning"),
                "severity": props.get("severity", "Unknown"),
                "latitude": lat,
                "longitude": lon,
                "expires": props.get("expires"),
            })

    payload = {"events": events, "fetched_at": datetime.now(timezone.utc).isoformat()}

    # Fall back to offline cache if both APIs failed
    if not events:
        offline = _read_cache_offline(KEY)
        if offline:
            offline["offline"] = True
            return offline

    _write_cache(KEY, payload)
    return payload


@router.get("/health")
async def get_earth_health():
    """
    Return Earth health metrics that modulate GaianOrb visuals:
      - CO2 ppm (NOAA Mauna Loa)       → atmosphere colour temperature
      - Global temperature anomaly      → aurora intensity at poles
      - Ocean health index (0–1)        → ocean texture saturation
      - Biodiversity index (0–1)         → land texture greenness
    """
    KEY = "health"
    cached = _read_cache(KEY)
    if cached:
        return cached

    # ─ CO2 from NOAA GML (latest monthly mean) ────────────────────────
    co2_ppm: float | None = None
    # co2_data will be None since it returns CSV not JSON; use direct text fetch
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(
                "https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_weekly_mlo.csv"
            )
            lines = [ln for ln in r.text.splitlines() if not ln.startswith("#") and ln.strip()]
            if lines:
                last = lines[-1].split(",")
                co2_ppm = float(last[4]) if len(last) > 4 else None
    except Exception:
        co2_ppm = None

    # ─ Normalised health indices (curated baselines, 2026) ──────────────
    # These are slow-changing indices; we use known 2026 values as defaults
    # and will update when live APIs for ocean/biodiversity become available.
    co2_baseline = 280.0   # pre-industrial
    co2_current = co2_ppm or 424.0  # ~2026 measured value
    co2_index = max(0.0, min(1.0, (co2_current - co2_baseline) / (500 - co2_baseline)))

    payload = {
        "co2_ppm": co2_current,
        "co2_index": round(co2_index, 4),          # 0 = clean, 1 = critical
        "temp_anomaly_c": 1.3,                      # 2026 running mean vs 1850-1900
        "temp_index": round(1.3 / 3.0, 4),          # 0 = baseline, 1 = +3C
        "ocean_health_index": 0.61,                 # Ocean Health Index 2025 global
        "biodiversity_index": 0.73,                 # Living Planet Index (normalised)
        "aurora_intensity": round(1.3 / 3.0, 4),    # mirrors temp_index
        "atmosphere_hue_shift": round(co2_index * 15, 2),  # degrees warm shift
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    offline = _read_cache_offline(KEY)
    if co2_ppm is None and offline:
        offline["offline"] = True
        return offline

    _write_cache(KEY, payload)
    return payload
