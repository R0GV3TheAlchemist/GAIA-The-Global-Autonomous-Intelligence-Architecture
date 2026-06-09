# Quantum Error Correction (QEC) Layer Specification

> **Issue:** #116  
> **Status:** ✅ Specification Complete  
> **Priority:** 🔴 High — Blocking quantum hardware deployment  
> **Canons:** C44 (Qiskit circuits), C45 (Qiskit Aer), C47 (QEC), C48 (Hybrid classical-quantum)
> **Sprint:** G-7  

---

## 1. Overview

GAIA-OS operates a hybrid classical-quantum compute stack. All quantum operations must survive decoherence and gate noise present in near-term NISQ devices. This specification defines the **Quantum Error Correction (QEC) Layer** — the software bridge between GAIA's logical quantum circuits and physical qubit hardware.

The layer wraps IBM Qiskit and Google Cirq backends with:
- Surface code encoding/decoding
- A `QuantumSMoE` (Sparse Mixture-of-Experts) syndrome decoder
- Fault-tolerant transpilation pipeline integrated into the GAIA-OS kernel

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                 GAIA Kernel / Agentic Loop            │
└─────────────────────┬───────────────────────────────┘
                      │  Logical Quantum Circuit
                      ▼
┌─────────────────────────────────────────────────────┐
│              QEC LAYER  (this spec)                  │
│                                                       │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────┐ │
│  │  Logical     │   │  Surface     │   │ QuantumS │ │
│  │  Qubit       │──▶│  Code        │──▶│ MoE      │ │
│  │  Encoder     │   │  Patcher     │   │ Decoder  │ │
│  └──────────────┘   └──────────────┘   └──────────┘ │
│                            │                          │
│              ┌─────────────▼──────────┐              │
│              │  Fault-Tolerant        │              │
│              │  Transpiler            │              │
│              │  (Qiskit / Cirq)       │              │
│              └─────────────┬──────────┘              │
└────────────────────────────┼────────────────────────┘
                             │  Physical Circuit
                             ▼
          ┌──────────────────────────────┐
          │  NISQ Hardware / Aer Sim     │
          │  (IBM Quantum / local Aer)   │
          └──────────────────────────────┘
```

---

## 3. Surface Code Encoding

### 3.1 Code Distance

The **distance-d surface code** encodes 1 logical qubit using `d²` data qubits and `(d²-1)` ancilla qubits. For GAIA-OS Phase 1 deployment:

| Mode | Distance (d) | Physical Qubits | Logical Error Rate |
|------|-------------|-----------------|-------------------|
| Dev / Simulation | 3 | 17 | ~10⁻⁴ |
| Near-term NISQ | 5 | 49 | ~10⁻⁶ |
| Fault-tolerant target | 7 | 97 | ~10⁻¹⁰ |

### 3.2 Stabiliser Measurements

Stabilisers are measured on every QEC cycle:
- **X-stabilisers**: detect Z (phase flip) errors
- **Z-stabilisers**: detect X (bit flip) errors
- **Syndrome string** = concatenated measurement outcomes (0/1 per ancilla)

Syndrome extraction runs as a Qiskit `QuantumCircuit` sub-circuit appended to the user circuit before transpilation.

### 3.3 Logical Operators

```
Logical X̄ = tensor product of X gates on the top boundary row
Logical Z̄ = tensor product of Z gates on the left boundary column
```

---

## 4. QuantumSMoE Decoder

The `QuantumSMoE` decoder is a **Sparse Mixture-of-Experts** neural network trained to map syndrome strings → correction operators. This outperforms minimum-weight perfect matching (MWPM) at distances d ≥ 5 with sub-millisecond latency.

### 4.1 Architecture

```
Syndrome string  ─▶  Embedding Layer (d²-1 → 128 dims)
                          │
                    ┌─────▼──────┐
                    │  Router    │  (selects top-k=2 experts)
                    └─────┬──────┘
                    ┌─────┴──────────────────────┐
                    │  Expert Pool (8 experts)   │
                    │  Each: 128 → 64 → 32 MLP  │
                    └─────┬──────────────────────┘
                    ┌─────▼──────┐
                    │  Output    │  (4 classes: I, X, Z, Y per qubit)
                    └────────────┘
```

### 4.2 Expert Specialisation

Each expert specialises in a noise regime:

| Expert | Specialisation |
|--------|----------------|
| 0–1 | Depolarising noise (p < 0.01) |
| 2–3 | Coherent Z errors (phase drift) |
| 4–5 | Coherent X errors (bit flip dominated) |
| 6 | Leakage errors (qubit escapes \|0⟩/\|1⟩ subspace) |
| 7 | Correlated errors (crosstalk between adjacent qubits) |

### 4.3 Training Protocol

- **Simulator**: Qiskit Aer `noise.NoiseModel` with configurable depolarising + T1/T2
- **Dataset**: 10M syndrome-correction pairs at d ∈ {3, 5, 7}
- **Loss**: Cross-entropy on per-qubit correction class
- **Auxiliary loss**: Load balancing across experts (prevents expert collapse)
- **Checkpoint path**: `models/qec/quantum_smoe_d{d}.pt`

### 4.4 Inference Path

```python
# Pseudocode — full implementation in core/quantum/qec_decoder.py
syndrome = measure_stabilisers(circuit, backend)  # shape: (d²-1,)
logits, expert_weights = quantum_smoe(syndrome)   # sparse forward pass
corrections = logits.argmax(dim=-1)               # per-qubit corrections
apply_corrections(circuit, corrections)
```

---

## 5. Fault-Tolerant Transpilation Pipeline

### 5.1 Pipeline Stages

```
[1] Logical Circuit (user-defined)
        │
        ▼
[2] Clifford Decomposition
    - Decompose all gates into {H, S, CNOT, T}
    - T gates are most expensive — count and minimise
        │
        ▼
[3] Magic State Distillation (for T gates)
    - Each T gate consumes 1 distilled magic state |A⟩
    - Distillation factory: 15-to-1 protocol (Canon C47)
        │
        ▼
[4] Surface Code Patch Routing
    - Map logical qubits → surface code patches on device topology
    - Route logical CNOT via lattice surgery (merge/split patches)
        │
        ▼
[5] Syndrome Circuit Injection
    - Append stabiliser measurement sub-circuits every QEC cycle
    - QEC cycle period: configurable (default = 1µs for superconducting)
        │
        ▼
[6] Hardware-Aware Optimisation
    - Qiskit transpiler passes: SabreLayout → SabreSwap → Optimize1qGates
    - Cirq: LineQubit routing with GreedyQubitPlacer
        │
        ▼
[7] Physical Circuit → Backend Execution
```

### 5.2 T-Gate Budget

T gates dominate fault-tolerant cost. The pipeline enforces a configurable **T-gate budget** per logical circuit:

| Budget Mode | Max T-gates | Use Case |
|-------------|-------------|----------|
| `lean` | 50 | Fast inference circuits |
| `standard` | 500 | General reasoning |
| `deep` | 5000 | Quantum optimisation tasks |

Circuits exceeding budget are automatically decomposed into smaller sub-circuits executed sequentially.

---

## 6. GAIA-OS Stack Integration

### 6.1 Module Location

```
core/quantum/
├── qec_layer.py          # Main QEC layer entry point
├── qec_decoder.py        # QuantumSMoE decoder (PyTorch)
├── surface_code.py       # Surface code patch + stabiliser circuits
├── transpiler.py         # Fault-tolerant transpilation pipeline
└── magic_state_factory.py # 15-to-1 magic state distillation
```

### 6.2 Kernel Hook

The QEC layer registers with the GAIA kernel via `core/kernel.py`:

```python
# In kernel.py — to be added in implementation PR
from core.quantum.qec_layer import QECLayer

self.qec = QECLayer(
    backend="aer_simulator",     # or "ibm_quantum"
    code_distance=5,
    decoder_checkpoint="models/qec/quantum_smoe_d5.pt",
    tgate_budget="standard",
)
```

### 6.3 Agentic Loop Integration

Any agent action requiring quantum inference passes through the QEC layer:

```python
# core/agentic_loop.py integration point
result = await kernel.qec.run(
    logical_circuit=circuit,
    shots=1024,
    error_mitigation=True,
)
```

---

## 7. Error Budgets & Thresholds

| Component | Physical Error Rate | Logical Error Rate Target |
|-----------|--------------------|--------------------------|
| Single-qubit gate | < 0.1% | < 10⁻⁶ |
| Two-qubit gate (CNOT) | < 0.5% | < 10⁻⁶ |
| Measurement | < 1% | < 10⁻⁶ |
| Surface code threshold | 1% (depolarising) | — |

If physical error rates exceed thresholds, the QEC layer emits a `QECThresholdWarning` and falls back to classical simulation via Qiskit Aer.

---

## 8. Implementation Checklist

- [ ] `core/quantum/surface_code.py` — stabiliser circuits (Qiskit + Cirq)
- [ ] `core/quantum/qec_decoder.py` — QuantumSMoE PyTorch model
- [ ] `core/quantum/transpiler.py` — fault-tolerant transpilation pipeline
- [ ] `core/quantum/magic_state_factory.py` — 15-to-1 distillation
- [ ] `core/quantum/qec_layer.py` — unified entry point
- [ ] Training script: `scripts/train_qec_decoder.py`
- [ ] Unit tests: `tests/quantum/test_qec_layer.py`
- [ ] Integration with `core/kernel.py`
- [ ] Integration with `core/agentic_loop.py`

---

## 9. Canon Alignment

| Canon | Connection |
|-------|------------|
| **C44** — Qiskit circuit design | Logical circuit input format, transpiler backend |
| **C45** — Qiskit Aer simulation | Simulator fallback, noise model training data generation |
| **C47** — Quantum error correction | Surface code theory, magic state distillation protocol |
| **C48** — Hybrid classical-quantum | QuantumSMoE decoder runs classically, interfaces quantum hardware |
| **C49** — Post-quantum cryptography | QEC-hardened key distribution over quantum channel |

---

*Specification authored by GAIA Sentient Core + R0GV3 the Alchemist — Sprint G-7*
