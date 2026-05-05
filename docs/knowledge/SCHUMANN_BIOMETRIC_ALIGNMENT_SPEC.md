# SCHUMANN BIOMETRIC ALIGNMENT — Engineering Specification

**Pillar:** Viriditas (Pillar II)
**Status:** Specification — Ready for Implementation
**Priority:** High (Core differentiator)

---

## Overview

The Schumann Biometric Alignment layer continuously compares the user's physiological coherence (HRV) against the Earth's electromagnetic resonance field (Schumann resonance, ~7.83 Hz fundamental) and uses the alignment or divergence to modulate system behavior, UI state, and AI interaction tone.

---

## Data Sources

### User Biometric Data
| Signal | Source | Sampling Rate | Privacy |
|---|---|---|---|
| HRV (RMSSD) | Apple HealthKit / Garmin / Oura / Polar | 1-min intervals | Local only |
| Resting Heart Rate | Same | 1-min intervals | Local only |
| SpO2 (optional) | Apple Health / Oura | 5-min intervals | Local only |
| Sleep stages | Apple Health / Oura / Garmin | Per-night | Local only |

### Environmental / Schumann Data
| Signal | Source | Update Frequency |
|---|---|---|
| Schumann amplitude | HeartMath GCI feed (public) | 10-min |
| Schumann frequency | NOAA GOES magnetometer | 1-min |
| Solar wind Kp | NOAA Space Weather API | 15-min |
| Local weather pressure | OpenWeatherMap API | 1-hour |

---

## Signal Processing Pipeline

```
[Wearable API] ──► [HRV Normalizer] ──► [Coherence Calculator]
                                                   │
[Schumann Feed] ──► [Amplitude Parser] ──────────────┘
                                                   │
                                        [Alignment Score 0-100]
                                                   │
                         ┌──────────────────────────┤
                         │                          │
                  [UI State Engine]        [AI Tone Modulator]
```

### Step 1: HRV Normalization
- Read raw RMSSD from wearable
- Apply user-specific baseline normalization (rolling 30-day mean ± 2σ)
- Output: `hrv_score` (0–100, where 50 = user's personal baseline)

### Step 2: Schumann Amplitude Parsing
- Fetch latest GCI feed data
- Extract fundamental frequency power (7.83 Hz band)
- Normalize against 30-day historical mean
- Output: `schumann_score` (0–100)

### Step 3: Alignment Score
```python
def compute_alignment(hrv_score: float, schumann_score: float,
                      solar_kp: float) -> float:
    base = 100 - abs(hrv_score - schumann_score)
    kp_penalty = min(solar_kp * 3, 30)  # max 30-point penalty
    return max(0, base - kp_penalty)
```

### Step 4: Behavioral Output
| Alignment Score | UI State | AI Tone | Features |
|---|---|---|---|
| 80–100 | Full vibrancy, rich animations | Expansive | All unlocked |
| 60–79 | Normal | Balanced, warm | Full |
| 40–59 | Slightly muted | Grounded | Full |
| 20–39 | Simplified, calm | Gentle | Core only |
| 0–19 | Minimal, breath-focused | Quiet | Essential + breathing prompt |

---

## Implementation Notes

### Rust (Tauri Backend)
```rust
pub async fn poll_schumann_feed() -> Result<SchumannReading> {
    let client = reqwest::Client::new();
    let response = client
        .get("https://www.heartmath.org/gci-api/coherence")
        .timeout(Duration::from_secs(10))
        .send()
        .await?;
    let data: GciResponse = response.json().await?;
    Ok(SchumannReading {
        amplitude: data.schumann_amplitude,
        timestamp: Utc::now(),
        kp_index: fetch_kp_index().await?,
    })
}
```

### TypeScript (Frontend)
```typescript
interface AlignmentState {
  score: number;
  hrv_score: number;
  schumann_score: number;
  ui_tier: 'minimal' | 'core' | 'standard' | 'full' | 'vibrant';
  last_updated: string;
}

function applyAlignmentTheme(state: AlignmentState): void {
  const root = document.documentElement;
  root.style.setProperty('--animation-speed', getAnimSpeed(state.ui_tier));
  root.style.setProperty('--color-saturation', getSaturation(state.ui_tier));
  root.style.setProperty('--info-density', getDensity(state.ui_tier));
}
```

---

## Privacy Model
- All biometric data stays on-device
- Schumann data fetched anonymously
- Alignment scores stored in encrypted local SQLite
- User can disable Schumann integration entirely
- No inferences shared with third parties

## Failure Modes
| Condition | Fallback |
|---|---|
| Wearable not connected | HRV-less mode: time-of-day + sleep data |
| Schumann feed unavailable | HRV-only alignment |
| Both unavailable | Default to standard UI tier |
| Kp > 8 (severe storm) | Auto-switch to restorative mode |

---

*Cross-reference: `PILLARS.md` (Pillar II), `PHILOSOPHY_ORIGIN.md` (Viriditas)*
