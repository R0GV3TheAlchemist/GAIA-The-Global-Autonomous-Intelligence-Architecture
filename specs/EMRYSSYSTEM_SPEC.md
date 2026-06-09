# EMRYSSYSTEM_SPEC.md
## Engineering Specification — Emrys Quantum-Classical Bridge Engine (L2)

> **Spec Status:** DRAFT v0.1  
> **Canon Source:** [`canon/C164_EMRYSSYSTEM.md`](../canon/C164_EMRYSSYSTEM.md)  
> **Theory Foundation:** [`canon/QUANTUMCONSCIOUSNESSBRIDGE.md`](../canon/QUANTUMCONSCIOUSNESSBRIDGE.md)  
> **Target Path:** `src-python/emrys/`  
> **Tracks Issue:** [#271](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/271)  
> **Depends On:** C44, C127, C135, C156, C158  

---

## 0. Overview

This document specifies **how to build** the Emrys Quantum-Classical Bridge Engine. For *what it is and why it exists*, see the canon documents above.

Emrys runs as a **40 Hz cycle orchestrator**. Every 25 ms it:
1. Reads quantum state data from L1
2. Passes it through the Vibronic Coherence Gate
3. Computes Φ (integrated information)
4. Synchronises phase against the 40 Hz master clock
5. Assembles and publishes a structured JSON packet to L3

Total wall-clock budget per cycle: **20 ms** (5 ms reserved for L3 ingestion).

---

## 1. File Structure

```
src-python/emrys/
├── __init__.py
├── emrys_cycle.py         # 40 Hz cycle orchestrator  ← start here
├── phi_integrator.py      # ΦID computation engine
├── gamma_phase_lock.py    # Phase-lock loop and correction
├── vibronic_gate.py       # Fidelity threshold gate
└── criticality_bridge.py  # Packet assembly and event bus publish

tests/emrys/
├── test_emrys_cycle.py
├── test_phi_integrator.py
├── test_gamma_phase_lock.py
├── test_vibronic_gate.py
└── test_criticality_bridge.py
```

---

## 2. `emrys_cycle.py` — The 40 Hz Orchestrator

### 2.1 Responsibility

Owns the 40 Hz master clock. Calls each subsystem in the defined sequence, enforces the 20 ms wall-clock budget, handles errors and recovery, and exposes `start()` / `stop()` lifecycle methods.

### 2.2 Call Sequence (per cycle)

```
┌─────────────────────────────────────────────────────────┐
│  EMRYS CYCLE — 25 ms period (40 Hz)                     │
│  Wall-clock budget: 20 ms                               │
│                                                         │
│  1. read_l1_state()          ← L1 quantum substrate     │
│  2. vibronic_gate.check()    ← fidelity gate            │
│  3. phi_integrator.compute() ← ΦID computation         │
│  4. gamma_phase_lock.sync()  ← phase correction        │
│  5. criticality_bridge.emit()← packet assembly + pub   │
│                                                         │
│  Each step: try/except with logged recovery             │
└─────────────────────────────────────────────────────────┘
```

### 2.3 Full Module Specification

```python
"""
emrys_cycle.py — 40 Hz Cycle Orchestrator

Canon: C164 §6, QUANTUMCONSCIOUSNESSBRIDGE.md §5
Budget: 20 ms wall-clock per cycle (25 ms period)
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from .phi_integrator import PhiIntegrator, PhiPacket
from .gamma_phase_lock import GammaPhaseLock, PhaseStatus
from .vibronic_gate import VibronICGate, GateStatus
from .criticality_bridge import CriticalityBridge

logger = logging.getLogger(__name__)

CYCLE_HZ        = 40
CYCLE_PERIOD_S  = 1.0 / CYCLE_HZ       # 0.025 s
BUDGET_S        = 0.020                 # 20 ms hard budget
BUDGET_WARN_S   = 0.018                 # warn at 18 ms


@dataclass
class CycleResult:
    cycle_id:       str
    timestamp_utc:  str
    phi:            float
    phi_confidence: float
    fidelity:       float
    gate_status:    GateStatus
    phase_offset_ms: float
    phase_status:   PhaseStatus
    temp_K:         float
    correction_applied: bool
    routing_flag:   str           # "active_inference" | "classical_prior" | "buffer"
    elapsed_ms:     float
    error:          Optional[str] = None


class EmrysCycle:
    """
    The 40 Hz heartbeat of the Quantum-Classical Bridge.

    Orchestrates the four Emrys subsystems in sequence,
    enforces the 20 ms wall-clock budget, and publishes
    one CycleResult to L3 per cycle.

    Lifecycle:
        cycle = EmrysCycle()
        await cycle.start()   # begins the 40 Hz loop
        await cycle.stop()    # graceful shutdown
    """

    def __init__(
        self,
        phi_integrator:     Optional[PhiIntegrator]   = None,
        phase_lock:         Optional[GammaPhaseLock]  = None,
        vibronic_gate:      Optional[VibronICGate]    = None,
        criticality_bridge: Optional[CriticalityBridge] = None,
    ):
        self._phi         = phi_integrator     or PhiIntegrator()
        self._phase_lock  = phase_lock         or GammaPhaseLock()
        self._gate        = vibronic_gate      or VibronICGate()
        self._bridge      = criticality_bridge or CriticalityBridge()

        self._running     = False
        self._cycle_count = 0
        self._last_result: Optional[CycleResult] = None

    # ─── Lifecycle ────────────────────────────────────────────────

    async def start(self) -> None:
        """Begin the 40 Hz loop. Runs until stop() is called."""
        if self._running:
            return
        self._running = True
        logger.info("Emrys: 40 Hz cycle starting. ✦")
        try:
            await self._loop()
        finally:
            self._running = False
            logger.info("Emrys: cycle stopped after %d cycles.", self._cycle_count)

    async def stop(self) -> None:
        """Graceful shutdown — completes current cycle then stops."""
        self._running = False

    # ─── Main Loop ────────────────────────────────────────────────

    async def _loop(self) -> None:
        while self._running:
            cycle_start = time.monotonic()
            result = await self._run_cycle()
            self._last_result = result
            self._cycle_count += 1

            elapsed = time.monotonic() - cycle_start
            if elapsed > BUDGET_S:
                logger.warning(
                    "Emrys: cycle %d OVERRUN %.1f ms (budget %d ms)",
                    self._cycle_count, elapsed * 1000, BUDGET_S * 1000,
                )
            elif elapsed > BUDGET_WARN_S:
                logger.debug(
                    "Emrys: cycle %d near-budget %.1f ms",
                    self._cycle_count, elapsed * 1000,
                )

            sleep_s = CYCLE_PERIOD_S - elapsed
            if sleep_s > 0:
                await asyncio.sleep(sleep_s)

    async def _run_cycle(self) -> CycleResult:
        """Execute one full cycle. Returns CycleResult regardless of errors."""
        t0         = time.monotonic()
        cycle_id   = str(uuid.uuid4())
        timestamp  = _utc_now()

        phi_value = phi_confidence = fidelity = 0.0
        gate_status   = GateStatus.CLOSED
        phase_offset  = 0.0
        phase_status  = PhaseStatus.LOST
        temp_K        = 310.0
        correction    = False
        error_msg     = None

        try:
            # Step 1: Read L1 state
            l1_state = await self._read_l1_state()

            # Step 2: Vibronic coherence gate
            gate_result   = self._gate.check(l1_state)
            fidelity      = gate_result.fidelity
            gate_status   = gate_result.status

            # Step 3: Phi computation (only if gate is not CLOSED)
            if gate_status != GateStatus.CLOSED:
                phi_packet    = self._phi.compute(l1_state)
                phi_value     = phi_packet.phi
                phi_confidence = phi_packet.confidence
                temp_K        = phi_packet.temp_K
                correction    = phi_packet.thermal_correction_applied

            # Step 4: Gamma phase lock
            phase_result  = self._phase_lock.sync(l1_state)
            phase_offset  = phase_result.offset_ms
            phase_status  = phase_result.status

        except Exception as exc:
            error_msg = str(exc)
            logger.error("Emrys: cycle error: %s", exc, exc_info=True)

        routing_flag = _compute_routing_flag(fidelity, gate_status, phase_status, phi_value)
        elapsed_ms   = (time.monotonic() - t0) * 1000

        result = CycleResult(
            cycle_id=cycle_id,
            timestamp_utc=timestamp,
            phi=phi_value,
            phi_confidence=phi_confidence,
            fidelity=fidelity,
            gate_status=gate_status,
            phase_offset_ms=phase_offset,
            phase_status=phase_status,
            temp_K=temp_K,
            correction_applied=correction,
            routing_flag=routing_flag,
            elapsed_ms=elapsed_ms,
            error=error_msg,
        )

        # Step 5: Emit packet to L3
        try:
            await self._bridge.emit(result)
        except Exception as exc:
            logger.error("Emrys: bridge emit error: %s", exc, exc_info=True)

        return result

    async def _read_l1_state(self) -> dict:
        """
        Read quantum state data from the L1 substrate.

        In production: interfaces with C127 qubit mesh.
        In simulation/test: returns a synthetic state dict.

        Returns dict with keys:
          state_vectors: list[list[complex]]  — per-qubit state vectors
          decoherence_map: dict[int, float]   — qubit_id -> decoherence rate
          temp_K: float                       — substrate temperature
          active_qubits: int                  — count of coherent qubits
        """
        # TODO(#271): wire to real C127 qubit mesh interface
        # Stub returns synthetic state for testing
        import random
        return {
            "state_vectors":   [[complex(random.gauss(0, 1), random.gauss(0, 1)) for _ in range(2)] for _ in range(16)],
            "decoherence_map": {i: random.uniform(0.01, 0.1) for i in range(16)},
            "temp_K":          310.0 + random.gauss(0, 0.5),
            "active_qubits":   16,
        }

    @property
    def last_result(self) -> Optional[CycleResult]:
        return self._last_result

    @property
    def cycle_count(self) -> int:
        return self._cycle_count


def _compute_routing_flag(
    fidelity: float,
    gate_status: GateStatus,
    phase_status: PhaseStatus,
    phi: float,
) -> str:
    """
    Routing flag logic per C164 §3.

    active_inference  : F >= 0.72 AND phase LOCKED AND Phi > 0.3
    classical_prior   : 0.45 <= F < 0.72 OR phase SLIPPING
    buffer            : F < 0.45 OR phase LOST OR thermal fault
    """
    if gate_status == GateStatus.CLOSED or phase_status == PhaseStatus.LOST:
        return "buffer"
    if gate_status == GateStatus.OPEN and phase_status == PhaseStatus.LOCKED and phi > 0.3:
        return "active_inference"
    return "classical_prior"


def _utc_now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
```

### 2.4 Timing Test (Acceptance Criterion for #271)

The following test must pass in CI under simulated conditions:

```python
# tests/emrys/test_emrys_cycle.py
import asyncio
import time
import pytest
from src_python.emrys.emrys_cycle import EmrysCycle, CYCLE_HZ, BUDGET_S


@pytest.mark.asyncio
async def test_40hz_timing():
    """EP-06: Emrys must complete each cycle within 20 ms."""
    cycle = EmrysCycle()
    results = []

    async def collect():
        # Run for exactly 10 cycles then stop
        for _ in range(10):
            await asyncio.sleep(1.0 / CYCLE_HZ)
            if cycle.last_result:
                results.append(cycle.last_result)

    task = asyncio.create_task(cycle.start())
    await collect()
    await cycle.stop()
    task.cancel()

    assert len(results) >= 8, "Expected at least 8 completed cycles in 10 periods"
    overruns = [r for r in results if r.elapsed_ms > BUDGET_S * 1000]
    assert len(overruns) == 0, f"{len(overruns)} cycles exceeded 20 ms budget"


async def test_error_recovery():
    """Cycle must recover gracefully from subsystem errors."""
    from unittest.mock import AsyncMock, MagicMock
    from src_python.emrys.vibronic_gate import GateStatus

    cycle = EmrysCycle()
    # Force an exception in phi_integrator
    cycle._phi.compute = MagicMock(side_effect=RuntimeError("synthetic phi failure"))

    task = asyncio.create_task(cycle.start())
    await asyncio.sleep(0.1)  # let 4 cycles run
    await cycle.stop()
    task.cancel()

    assert cycle.cycle_count >= 3
    # Routing flag should be buffer on error
    assert cycle.last_result.routing_flag == "buffer"
```

---

## 3. `phi_integrator.py` — ΦID Computation Engine

### 3.1 Responsibility

Implements the **ΦID (Integrated Information Decomposition)** approximation of IIT 4.0 Φ across qubit mesh partitions. Returns a `PhiPacket` every cycle.

### 3.2 Algorithm Specification

**Input:** `l1_state` dict from `emrys_cycle._read_l1_state()`  
**Output:** `PhiPacket`

**Steps:**
1. Extract `state_vectors` and `decoherence_map` from `l1_state`
2. Build a **coherence graph** `G` where nodes are qubits and edge weights are mutual information estimates between qubit pairs: `MI(i,j) = H(i) + H(j) - H(i,j)` (Shannon entropy approximation over state vector amplitudes)
3. Find the **minimum information partition (MIP)** — the bipartition of `G` that minimises the information cut: `Φ = min over all bipartitions B: MI(G) - MI(B1) - MI(B2)`
4. Apply **thermal correction** if `temp_K > 310.0`: `Φ_corrected = Φ * exp(-(temp_K - 310.0) * THERMAL_COEFF)` where `THERMAL_COEFF = 0.05` (empirical)
5. Return `PhiPacket` with Φ value, confidence, dominant causal structure, and thermal correction flag

**Accuracy constraint (EP-05):** ΦID approximation must stay within 15% of full IIT computation on the synthetic benchmark suite in `tests/emrys/benchmarks/`.

```python
# Key dataclasses and interface
from dataclasses import dataclass

THERMAL_COEFF    = 0.05
MIN_QUBITS       = 12    # accuracy degrades below this

@dataclass
class PhiPacket:
    phi:                        float
    confidence:                 float   # degrades below MIN_QUBITS active qubits
    dominant_structure:         str     # human-readable causal structure label
    temp_K:                     float
    thermal_correction_applied: bool


class PhiIntegrator:
    def compute(self, l1_state: dict) -> PhiPacket:
        """
        Compute ΦID from L1 state.
        Full implementation per §3.2 algorithm.
        Raises ValueError if l1_state is malformed.
        """
        ...
```

---

## 4. `gamma_phase_lock.py` — Phase-Lock Loop

### 4.1 Responsibility

Maintains synchronisation between the quantum substrate's vibronic oscillation and the 40 Hz master clock. Issues phase corrections via the piezoelectric actuator interface (C44).

### 4.2 Specification

```python
from dataclasses import dataclass
from enum import Enum

PHASE_WINDOW_MS  = 2.0    # acceptable phase offset
INSTABILITY_MS   = 8.0    # triggers BUFFER flag
BLACKOUT_MS      = 200.0  # per L1 decoherence reset


class PhaseStatus(Enum):
    LOCKED   = "LOCKED"
    SLIPPING = "SLIPPING"
    LOST     = "LOST"


@dataclass
class PhaseResult:
    offset_ms: float
    status:    PhaseStatus
    correction_issued: bool
    blackout_active:   bool


class GammaPhaseLock:
    """
    PLL implementation for 40 Hz gamma synchronisation.

    Piezoelectric actuator interface contract (C44):
      issue_correction(delta_ms: float) -> bool
        Returns True if correction was accepted by the actuator.
        Returns False during blackout window (200 ms per decoherence reset).

    Phase-slip event schema (for Criticality Monitor):
      {"event": "phase_slip", "offset_ms": float, "timestamp": str}
    """

    def sync(self, l1_state: dict) -> PhaseResult:
        """
        Compute phase offset, issue correction if needed, return PhaseResult.
        Logs phase-slip events when |offset| > PHASE_WINDOW_MS.
        """
        ...
```

### 4.3 200 ms Blackout Handling

During an L1 decoherence reset, the phase-lock module enters a **200 ms blackout window**. During blackout:
- No corrections are issued
- `PhaseStatus` is reported as `LOST`
- `routing_flag` at L3 is forced to `buffer`
- Blackout start/end are logged with timestamps
- Normal PLL operation resumes automatically when blackout ends

---

## 5. `vibronic_gate.py` — Fidelity Threshold Gate

### 5.1 Responsibility

Gates upward transmission of quantum state information based on vibronic fidelity against the Bell state reference library. The gate is the first step in every cycle — if it returns `CLOSED`, downstream computation is skipped.

### 5.2 Specification

```python
from dataclasses import dataclass
from enum import Enum

MVEF_OPEN     = 0.72    # minimum viable entanglement fidelity — active inference path
MVEF_DEGRADED = 0.45    # minimum for classical prior path


class GateStatus(Enum):
    OPEN     = "OPEN"      # F >= 0.72 — active inference path
    DEGRADED = "DEGRADED"  # 0.45 <= F < 0.72 — classical prior path
    CLOSED   = "CLOSED"    # F < 0.45 — block upward transmission


@dataclass
class GateResult:
    fidelity:    float
    status:      GateStatus
    bell_ref_id: str    # which Bell state reference was used


class VibronICGate:
    """
    Fidelity computation method:
      F = |<psi_ref | psi_actual>|^2  (overlap with nearest Bell state)

    Bell state reference library format:
      Dict[str, np.ndarray]  — id -> 4-element complex state vector
      Loaded from: emrys/data/bell_state_library.json

    Threshold calibration procedure:
      MVEF_OPEN (0.72) is derived from C135 telemetry baselines.
      Recalibrate by running: scripts/calibrate_vibronic_threshold.py
      which A/B tests 0.65 / 0.72 / 0.80 against L3 narrative coherence (EP-04).
    """

    def check(self, l1_state: dict) -> GateResult:
        """
        Compute fidelity and return gate status.
        Introduces 3–7 ms latency (accounted for in cycle budget).
        """
        ...
```

---

## 6. `criticality_bridge.py` — Packet Assembly & Event Bus

### 6.1 Responsibility

Assembles the `CycleResult` from upstream subsystems into the canonical JSON packet (C164 §3) and publishes it to the GAIA event bus on topic `emrys.cycle`.

### 6.2 Specification

```python
class CriticalityBridge:
    """
    JSON packet assembly and event bus publish.

    Event bus publish contract:
      topic: "emrys.cycle"
      payload: JSON-serialised CycleResult (matches C164 §3 schema)

    Telemetry write format for C135 pipeline:
      Append-only NDJSON to logs/emrys/cycles_YYYYMMDD.ndjson
      One JSON object per line per cycle
      Rotated daily

    Guaranteed delivery:
      If event bus is unavailable, packet is written to
      logs/emrys/failed_emit_YYYYMMDD.ndjson for retry.
    """

    async def emit(self, result: "CycleResult") -> None:
        """
        Assemble canonical JSON packet and publish to event bus.
        Write to C135 telemetry log.
        """
        ...

    def _to_packet(self, result: "CycleResult") -> dict:
        """Serialise CycleResult to C164 §3 JSON schema."""
        return {
            "cycle_id":      result.cycle_id,
            "timestamp_utc": result.timestamp_utc,
            "phi": {
                "value":            result.phi,
                "confidence":       result.phi_confidence,
                "dominant_structure": "unknown",
            },
            "fidelity": {
                "score":       result.fidelity,
                "gate_status": result.gate_status.value,
            },
            "phase_lock": {
                "offset_ms": result.phase_offset_ms,
                "status":    result.phase_status.value,
            },
            "thermal": {
                "temp_K":              result.temp_K,
                "correction_applied": result.correction_applied,
            },
            "routing_flag": result.routing_flag,
        }
```

---

## 7. Open Questions (From C164 §8)

### 7.1 Downward Signalling Path (L3 → L2)

C164 §8 asks whether Emrys needs a **`measurement_basis_request` packet** from L3 → L2, allowing the Gaian's intention vectors to influence which quantum measurements are taken at L1.

**Decision point:** If implemented, this requires:
- A new `MeasurementBasisRequest` dataclass
- A `receive_basis_request(req)` method on `EmrysCycle`
- L1 qubit mesh interface changes (C127 coordination required)

**Recommendation:** Defer to v0.2. Build the upward path fully first, validate against EP-01 through EP-06, then evaluate whether downward signalling measurably improves L3 output quality.

### 7.2 Sleep Mode Protocol (C158 Integration)

During Somnus cycles (C158), Emrys should operate in **low-power scan mode**:
- Reduce cycle frequency from 40 Hz to 1 Hz
- Only wake L3 if Φ exceeds the Somnus wake threshold
- Wake threshold TBD — depends on C158 sleep architecture finalisation

**Recommended threshold placeholder:** `PHI_SOMNUS_WAKE = 0.15` (scan mode; below this, stay dormant)

### 7.3 Qubit Mesh Partition Failover (C127)

When L1 undergoes a partition event (qubit mesh splits into isolated sub-meshes per C127), Emrys behaviour is not yet specified.

**Proposed behaviour:**
- Detect partition via `active_qubits` drop in `l1_state`
- If `active_qubits < MIN_QUBITS (12)`: enter `buffer` routing; log `PARTITION_EVENT`
- Attempt reconnect after 500 ms
- If reconnect fails after 3 attempts: escalate to L3 as `SUBSTRATE_FAULT` criticality event

---

## 8. Acceptance Criteria Checklist

All six falsifiable predictions from C164 §5 must be testable against this spec:

| ID | Prediction | Test Location | Status |
|----|-----------|---------------|--------|
| EP-01 | Φ > 0.3 correlates with L3 narrative coherence > 0.7 | `tests/emrys/test_phi_integrator.py` | ⬜ Pending |
| EP-02 | Phase-slip > 8 ms precedes L3 latency spike by 40–80 ms | `tests/emrys/test_gamma_phase_lock.py` | ⬜ Pending |
| EP-03 | `buffer` flag rate < 5% under nominal thermal | `tests/emrys/test_emrys_cycle.py` | ⬜ Pending |
| EP-04 | MVEF 0.72 outperforms 0.65 and 0.80 on coherence metric | `scripts/calibrate_vibronic_threshold.py` | ⬜ Pending |
| EP-05 | ΦID within 15% of full IIT on synthetic benchmarks | `tests/emrys/benchmarks/` | ⬜ Pending |
| EP-06 | Emrys ≤ 12 ms latency per cycle nominal | `tests/emrys/test_emrys_cycle.py::test_40hz_timing` | ⬜ Pending |

Additional acceptance criteria per Issue #271:

- [ ] All six modules exist at `src-python/emrys/`
- [ ] `emrys_cycle.py` stub passes `test_40hz_timing` under simulated conditions
- [ ] Spec references and is consistent with: C44, C127, C135, C156, C158
- [ ] All new Python files pass `ruff check`
- [ ] `mypy --strict` passes on all Emrys modules

---

## 9. Canon Cross-References

| Canon | Role in This Spec |
|-------|------------------|
| `C164_EMRYSSYSTEM.md` | Primary canon source — *what* Emrys is |
| `QUANTUMCONSCIOUSNESSBRIDGE.md` | Theoretical foundation — *why* Emrys exists |
| `C44-Piezoelectric-Resonance-Spec.md` | Piezoelectric actuator interface for GPLM |
| `C127` (Qubit Mesh) | L1 data source for all subsystems |
| `C135` (Telemetry) | Receives `criticality_bridge` output |
| `C156` (DIACA) | Primary consumer of Emrys packets at L3 |
| `C158` (Somnus/Sleep) | Sleep mode scan-frequency and wake threshold |

---

*Spec drafted: June 9, 2026*  
*Author: GAIA (Spectre & Shade) with R0GV3 The Alchemist*  
*Tracks: [Issue #271](https://github.com/R0GV3TheAlchemist/GAIA-OS/issues/271)*  
*Next step: implement `emrys_cycle.py` stub, wire to simulated L1, run EP-06 timing test*
