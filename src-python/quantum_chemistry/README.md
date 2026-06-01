# Quantum Chemistry — Environment Setup

This module provides the Qiskit Nature / PySCF-based molecular simulation
foundation for GAIA-OS's Gaianite substrate materials layer (Canon C65–C67).

## Dependencies

| Package | Min Version | Role |
|---|---|---|
| `qiskit-nature` | 0.7.0 | Fermionic Hamiltonians, `ElectronicStructureProblem`, VQE integration |
| `qiskit-aer` | 0.14.0 | `AerSimulator` statevector/CPU backend for circuit simulation |
| `pyscf` | 2.4.0 | Ab-initio driver: `Mole`, RHF, CCSD, basis set handling |

All three are declared in the top-level `requirements.txt` under
`# Quantum Chemistry (Gaianite Substrate Simulation #133)`.

---

## Local Development Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
.venv\Scripts\activate             # Windows
```

### 2. Install requirements

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> **Note:** `pyscf` compiles C extensions on install.
> Ensure you have a C compiler available (`gcc` / `clang`).
> On Ubuntu: `sudo apt install build-essential`.
> On macOS: `xcode-select --install`.

### 3. Validate the environment

```bash
python -m quantum_chemistry.env_check
```

Expected output:

```
============================================================
GAIA-OS Quantum Chemistry Environment Report
Python: 3.11.x
============================================================
  [✓] qiskit-nature         required>=0.7.0  installed=0.7.x
  [✓] qiskit-aer            required>=0.14.0 installed=0.14.x
  [✓] pyscf                 required>=2.4.0  installed=2.4.x
------------------------------------------------------------
  AerSimulator backend : available
  PySCF driver         : available
============================================================
  Overall: PASS
============================================================
```

---

## CPU vs. GPU

By default, `AerSimulator` runs on **CPU** using the `statevector` method.
This is sufficient for the initial Gaianite simulations (≤ 20 qubits).

For larger active spaces (future extension), GPU acceleration is available
via `qiskit-aer-gpu`:

```bash
pip install qiskit-aer-gpu          # requires CUDA 11.x or 12.x
```

Then instantiate the simulator with:

```python
from qiskit_aer import AerSimulator
sim = AerSimulator(method="statevector", device="GPU")
```

The `env_check.py` module always uses the CPU backend for portability.
Simulation drivers in `targets/` accept an optional `simulator` parameter
if you want to pass in a GPU-backed instance.

---

## Apple Silicon (M-series) Caveats

`pyscf` compiles native C/Cython extensions. On M-series Macs:

1. **Use a native arm64 Python** (not Rosetta x86_64).
   ```bash
   python3 --version  # should say arm64 in `file $(which python3)`
   ```
2. **Install Xcode Command Line Tools:**
   ```bash
   xcode-select --install
   ```
3. **If PySCF fails to compile**, try pinning to a prebuilt wheel:
   ```bash
   pip install pyscf --prefer-binary
   ```
4. **`qiskit-aer` GPU** is not available on Apple Silicon (no CUDA).
   CPU statevector mode works correctly via Metal-accelerated NumPy.

---

## Headless CI Setup

The environment works out-of-the-box on Ubuntu CI runners (GitHub Actions,
GitLab CI, CircleCI). The following is a minimal GitHub Actions step:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.11'

- name: Install quantum chemistry deps
  run: |
    pip install --upgrade pip
    pip install -r requirements.txt

- name: Validate quantum chemistry environment
  run: python -m quantum_chemistry.env_check

- name: Run quantum chemistry tests
  run: pytest src-python/tests/test_qchem_env.py -v
```

> **Note:** `pyscf` installs cleanly on `ubuntu-latest` runners without
> any extra system packages. On `macos-latest` runners, ensure
> `xcode-select --install` has been run or use `--prefer-binary`.

---

## Module Structure

```
src-python/quantum_chemistry/
├── __init__.py          # Module scaffold, version map
├── env_check.py         # Runtime environment validation
├── README.md            # This file
├── targets/             # Per-material simulation drivers (added in #136–#138)
│   ├── ysz.py           # Yttria-Stabilized Zirconia (#136)
│   ├── bts.py           # Barium Titanate-Strontium (#137)
│   └── alscn_gan.py     # AlScN / AlScN:GaN heterostructure (#138)
├── canon_mapper.py      # Maps results to Canon C65–C67 schema (#139)
└── validator.py         # RRUFF / Mindat cross-validation (#139)
```

---

## Running Tests

```bash
pytest src-python/tests/test_qchem_env.py -v
```

Tests that require the quantum chemistry packages to be installed are
automatically skipped (with a clear reason message) in environments where
`qiskit-nature`, `qiskit-aer`, or `pyscf` are absent — so the test suite
never fails in a base CI environment that hasn't installed the optional deps.
