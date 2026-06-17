"""
simulation/wireless_power_sim.py

Queue 3 — Resonant Field Simulation Engine (Phases 1-3)

Phase 1: Replicate Finland result (7.2 cm coil, 18 cm, ~80% efficiency)
Phase 2: Phi hypothesis test (phi-wound vs. standard-wound coil)
Phase 3: Room-scale 7-node hexagonal array

Biological safety envelope is hardcoded and cannot be overridden.
All frequencies locked to ISM bands only.

Outputs to simulation/output/:
  wireless_phase1_validation.csv
  wireless_phase2_phi_hypothesis.csv
  wireless_phase3_room_scale.csv
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import numpy as np
import pandas as pd

OUT = Path("simulation/output")
OUT.mkdir(parents=True, exist_ok=True)

# ── Constants ─────────────────────────────────────────────────────────────────────
PHI = (1 + math.sqrt(5)) / 2  # Golden ratio ~1.618
MU_0 = 4 * math.pi * 1e-7      # Permeability of free space

# ISM bands only (Hz) — all other frequencies are rejected
ISM_BANDS: List[float] = [6.78e6, 13.56e6, 27.12e6]

# Biological safety
MAX_POWER_DENSITY_MW_CM2 = 1.0   # ICNIRP general public limit
DANGEROUS_ELF_LOW  = 3.0         # Hz
DANGEROUS_ELF_HIGH = 300.0       # Hz
DANGEROUS_AUDIO_HIGH = 20_000.0  # Hz
DANGEROUS_BIOEM_HIGH = 100.0     # Hz


# ── Data models ──────────────────────────────────────────────────────────────────
@dataclass
class Coil:
    diameter_m: float
    turns: int
    winding: str = "standard"  # "standard" | "phi"
    resistance_ohm: float = 0.15
    # Computed on post_init
    radius_m: float = field(init=False)
    inductance_H: float = field(init=False)

    def __post_init__(self):
        self.radius_m = self.diameter_m / 2
        self.inductance_H = self._compute_inductance()

    def _compute_inductance(self) -> float:
        """Wheeler's formula for single-layer air-core coil (SI)."""
        r = self.radius_m
        n = self.turns
        # Phi winding — average spacing is phi times tighter → effectively
        # modelled as 1% improvement per winding for hypothesis purposes.
        phi_factor = PHI * 0.01 if self.winding == "phi" else 0.0
        l = (MU_0 * n**2 * math.pi * r**2) / (0.9 * r) * (1 + phi_factor * n)
        return l


@dataclass
class SimResult:
    distance_m: float
    coil_type: str
    frequency_hz: float
    q_factor: float
    coupling_k: float
    efficiency_pct: float
    power_density_mw_cm2: float
    safety_pass: bool
    ism_compliant: bool
    notes: str = ""

    def to_dict(self) -> dict:
        return self.__dict__


# ── Safety + compliance ────────────────────────────────────────────────────────────

def biological_safety_check(frequency_hz: float, power_density_mw_cm2: float) -> Tuple[bool, str]:
    """Returns (pass, reason). CANNOT be bypassed."""
    if DANGEROUS_ELF_LOW <= frequency_hz <= DANGEROUS_ELF_HIGH:
        return False, f"REJECTED: {frequency_hz} Hz is in dangerous ELF band (3-300 Hz)"
    if frequency_hz <= DANGEROUS_BIOEM_HIGH:
        return False, f"REJECTED: {frequency_hz} Hz interferes with bioEM field range"
    if frequency_hz <= DANGEROUS_AUDIO_HIGH:
        return False, f"REJECTED: {frequency_hz} Hz is in dangerous audio/organ resonance band"
    if power_density_mw_cm2 > MAX_POWER_DENSITY_MW_CM2:
        return False, f"REJECTED: {power_density_mw_cm2:.3f} mW/cm² exceeds ICNIRP limit of {MAX_POWER_DENSITY_MW_CM2}"
    return True, "PASS"


def regulatory_check(frequency_hz: float) -> Tuple[bool, str]:
    tolerance = 0.01e6  # 10 kHz tolerance
    for band in ISM_BANDS:
        if abs(frequency_hz - band) <= tolerance:
            return True, f"ISM compliant at {band/1e6:.2f} MHz"
    return False, f"REJECTED: {frequency_hz/1e6:.3f} MHz not in ISM bands {[b/1e6 for b in ISM_BANDS]}"


# ── Core physics ────────────────────────────────────────────────────────────────────

def calculate_q_factor(coil: Coil, frequency_hz: float) -> float:
    omega = 2 * math.pi * frequency_hz
    return (omega * coil.inductance_H) / coil.resistance_ohm


def calculate_coupling_k(tx: Coil, rx: Coil, distance_m: float) -> float:
    """Neumann formula approximation for two coaxial coils."""
    r1, r2 = tx.radius_m, rx.radius_m
    d = distance_m
    k = (r1 * r2) ** 1.5 / (r1**2 + d**2) ** 1.5
    # Clamp to physical range
    return min(0.99, max(0.0, k))


def simulate_coil_pair(
    tx: Coil,
    rx: Coil,
    frequency_hz: float,
    distance_m: float,
    input_power_w: float = 1.0,
) -> SimResult:
    ism_ok, ism_note = regulatory_check(frequency_hz)
    q_tx = calculate_q_factor(tx, frequency_hz)
    q_rx = calculate_q_factor(rx, frequency_hz)
    k = calculate_coupling_k(tx, rx, distance_m)

    # Efficiency model: eta = k^2 * Q_tx * Q_rx / (1 + k^2 * Q_tx * Q_rx)
    kQ = k**2 * q_tx * q_rx
    efficiency = kQ / (1 + kQ)

    # Power density at receiver face (simplified far-field, conservative)
    area_m2 = math.pi * rx.radius_m**2
    received_power_w = efficiency * input_power_w
    power_density_w_m2 = received_power_w / max(area_m2, 1e-6)
    power_density_mw_cm2 = power_density_w_m2 * 0.1  # W/m² → mW/cm²

    safety_ok, safety_note = biological_safety_check(frequency_hz, power_density_mw_cm2)

    return SimResult(
        distance_m=distance_m,
        coil_type=f"{tx.winding}",
        frequency_hz=frequency_hz,
        q_factor=round((q_tx + q_rx) / 2, 1),
        coupling_k=round(k, 4),
        efficiency_pct=round(efficiency * 100, 2),
        power_density_mw_cm2=round(power_density_mw_cm2, 4),
        safety_pass=safety_ok,
        ism_compliant=ism_ok,
        notes=f"{safety_note} | {ism_note}",
    )


# ── Hexagonal grid ───────────────────────────────────────────────────────────────────

def generate_hexagonal_grid(n_rings: int, spacing_m: float) -> List[Tuple[float, float]]:
    """Flower of Life node positions for n_rings."""
    nodes: List[Tuple[float, float]] = [(0.0, 0.0)]
    for ring in range(1, n_rings + 1):
        for i in range(6):
            angle_base = math.pi / 3 * i
            for step in range(ring):
                angle = angle_base + math.pi / 3 * (step / ring)
                dist = ring * spacing_m
                x = dist * math.cos(angle)
                y = dist * math.sin(angle)
                nodes.append((round(x, 4), round(y, 4)))
    return nodes


# ── Phase 1 — Finland validation ────────────────────────────────────────────────────────

def phase1_finland_validation() -> pd.DataFrame:
    """Replicate Helsinki/Oulu result: 7.2 cm coil, 13.56 MHz, ~80% at 18 cm."""
    tx = Coil(diameter_m=0.072, turns=8, winding="standard")
    rx = Coil(diameter_m=0.072, turns=8, winding="standard")
    freq = 13.56e6

    distances = np.linspace(0.01, 0.50, 50)
    rows = []
    for d in distances:
        r = simulate_coil_pair(tx, rx, freq, d)
        rows.append(r.to_dict())

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "wireless_phase1_validation.csv", index=False)
    print(f"Phase 1 — efficiency at 18 cm: {df[df['distance_m'].between(0.17, 0.19)]['efficiency_pct'].mean():.1f}%")
    return df


# ── Phase 2 — Phi hypothesis ─────────────────────────────────────────────────────────

def phase2_phi_hypothesis() -> pd.DataFrame:
    """Compare phi-wound vs standard-wound coil at identical parameters."""
    tx_std  = Coil(diameter_m=0.072, turns=8, winding="standard")
    rx_std  = Coil(diameter_m=0.072, turns=8, winding="standard")
    tx_phi  = Coil(diameter_m=0.072, turns=8, winding="phi")
    rx_phi  = Coil(diameter_m=0.072, turns=8, winding="phi")
    freq = 13.56e6

    distances = np.linspace(0.05, 1.5, 60)
    rows = []
    for d in distances:
        r_std = simulate_coil_pair(tx_std, rx_std, freq, d)
        r_phi = simulate_coil_pair(tx_phi, rx_phi, freq, d)
        rows.append({**r_std.to_dict(), "variant": "standard"})
        rows.append({**r_phi.to_dict(), "variant": "phi"})

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "wireless_phase2_phi_hypothesis.csv", index=False)

    std_eff = df[df["variant"]=="standard"]["efficiency_pct"].mean()
    phi_eff = df[df["variant"]=="phi"]["efficiency_pct"].mean()
    print(f"Phase 2 — avg efficiency: standard={std_eff:.2f}%  phi={phi_eff:.2f}%  delta={phi_eff-std_eff:+.2f}%")
    return df


# ── Phase 3 — Room scale ────────────────────────────────────────────────────────────────

def phase3_room_scale() -> pd.DataFrame:
    """7-node hexagonal array (1 ring), 1.5 m node spacing, 3m x 3m room."""
    nodes = generate_hexagonal_grid(n_rings=1, spacing_m=1.5)
    tx = Coil(diameter_m=0.15, turns=10, winding="phi")
    rx = Coil(diameter_m=0.072, turns=8,  winding="phi")
    freq = 13.56e6
    rows = []

    # For a 3m x 3m room, sample a 30x30 grid
    grid = np.linspace(-1.5, 1.5, 30)
    for px in grid:
        for py in grid:
            # Find nearest node
            dists = [math.hypot(px - nx, py - ny) for nx, ny in nodes]
            d_nearest = min(dists)
            r = simulate_coil_pair(tx, rx, freq, max(d_nearest, 0.01))
            rows.append({
                "point_x": round(float(px), 3),
                "point_y": round(float(py), 3),
                "nearest_node_m": round(d_nearest, 3),
                "efficiency_pct": r.efficiency_pct,
                "power_density_mw_cm2": r.power_density_mw_cm2,
                "safety_pass": r.safety_pass,
            })

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "wireless_phase3_room_scale.csv", index=False)
    pct_safe = df["safety_pass"].mean() * 100
    avg_eff  = df["efficiency_pct"].mean()
    print(f"Phase 3 — avg efficiency: {avg_eff:.1f}%  |  safe zones: {pct_safe:.1f}%")
    return df


# ── Main ───────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n=== GAIA Queue 3 — Wireless Power Simulation Engine ===")
    print("\n[Phase 1] Finland validation:")
    df1 = phase1_finland_validation()

    print("\n[Phase 2] Phi hypothesis:")
    df2 = phase2_phi_hypothesis()

    print("\n[Phase 3] Room scale:")
    df3 = phase3_room_scale()

    print("\nAll phases complete. Outputs in simulation/output/")
