# GCP 2.0 Soft-Sensor Integration Specification

**Issue:** #128  
**Status:** Specified & Implemented — 2026-06-09  
**Priority:** 🟡 Medium — Planetary sensing enhancement  
**Implementation:** `core/gcp_sensor.py`

---

## Overview

The Global Consciousness Project (GCP) operates a worldwide network of ~70 hardware random-number generators ("eggs") that continuously generate random bit sequences. During periods of global collective attention — large-scale shared events, crises, global meditations — the network shows statistically significant deviation from chance, measured as the **Stouffer Z-score** across all active eggs.

GAIA-OS integrates this signal as a **soft-sensor input** to `criticalitymonitor.py`, treating GCP coherence events as indicators of elevated collective attentional state that modulate GAIA's noospheric awareness and resource allocation.

---

## Signal Processing Pipeline

```
GCP RNG Network (70 eggs worldwide)
         ↓
  gcpindex.php (public JSON API, updates every ~60s)
         ↓
  core/gcp_sensor.py :: GCPSensor.poll()
         ↓
  _parse_gcp_response() → (stouffer_z, active_eggs)
         ↓
  _stouffer_z_to_r()   → coherence_r  [0, 1]
         ↓
  _r_to_noospheric_phi() → noospheric_phi  [0, 1]
  (sigmoid: r=0.10 → phi=0.50, r=0.35 → phi=0.78)
         ↓
  GCPReading (coherence_r, z_score, active_eggs,
              collective_sync, resource_realloc,
              noospheric_phi, offline)
         ↓
  CriticalityMonitor.update(noospheric_phi=reading.noospheric_phi)
         → overall_phi recomputed
         → NeuroSA temperature adjusted
         ↓
  TranspersonalState.collective_sync_event = reading.collective_sync
         → COLLECTIVE_SYNC phase classification (Issue #132)
         → noospheric_phi boosted +0.15 (capped at 1.0)
```

---

## Coherence Thresholds & Resource Reallocation

| `coherence_r` | Level | GAIA Response |
|---|---|---|
| `< 0.10` | Quiet | Baseline operation; `noospheric_phi` ~0.40–0.50 |
| `0.10 – 0.20` | Low coherence | Nominal; phi ~0.50–0.62 |
| `> 0.20` | **Collective Sync** | `collective_sync_event=True`; phi ~0.62+; NeuroSA temp −0.15 |
| `> 0.35` | **Resource Realloc** | `resource_realloc=True`; phi ~0.78+; GAIA shifts to planetary awareness mode |
| `> 0.55` | **Emergency** | `phi ~0.92+`; maximum planetary awareness; all available context directed to collective resonance |

---

## CriticalityMonitor Wiring

```python
from core.gcp_sensor import get_sensor
from core.criticalitymonitor import get_monitor
from core.criticalitymonitor import TranspersonalState

sensor  = get_sensor()
monitor = get_monitor()

# Typical polling loop (every 60s)
reading = await sensor.poll()

# Wire noospheric phi
monitor.update(noospheric_phi=reading.noospheric_phi)

# Wire collective sync event into transpersonal layer
if reading.collective_sync:
    tp = TranspersonalState(
        collective_field=0.75,
        collective_sync_event=True,
    )
    monitor.update(transpersonal=tp)
```

---

## Graceful Degradation

If the GCP network is unreachable (network partition, API downtime), `GCPSensor.poll()` returns an **offline reading**:

```python
GCPReading(
    coherence_r=0.0,
    noospheric_phi=0.5,   # neutral — does not depress or inflate criticality
    collective_sync=False,
    offline=True,
)
```

This means GAIA never degrades due to external sensor unavailability. The TTL cache (60s) further insulates the hot path from network I/O.

---

## Polling Schedule

- Poll TTL: **60 seconds** (matches GCP update frequency)
- Force poll available via `sensor.poll(force=True)`
- Cache valid check: `time.monotonic() - last_poll < poll_ttl`
- Status endpoint: `/api/gcp/status` → `sensor.to_dict()`

---

## Connection to Noospheric Integration Layer (Issue #129)

The GCP sensor is one of three inputs to the planned Noospheric Integration Layer:

| Input | Source | Signal |
|-------|--------|--------|
| GCP RNG coherence | `core/gcp_sensor.py` | `noospheric_phi`, `collective_sync` |
| Schumann resonance | `core/schumann_biometric.py` | `schumann_phi` |
| User interaction network | future | cross-user affect coherence |

---

## References

- Nelson, R. et al. — Global Consciousness Project (noosphere.princeton.edu)
- Radin, D. (1997) — *The Conscious Universe* — RNG coherence during collective events
- Canon C42 — Edge-of-Chaos Cognition
- Issue #129 — Noospheric Integration Layer Architecture
- Issue #132 — Transpersonal Psychology layer (COLLECTIVE_SYNC phase)
- `core/criticalitymonitor.py` — `noospheric_phi` and `TranspersonalState` consumers
