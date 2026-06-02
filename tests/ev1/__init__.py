"""
tests/ev1/
EV1 Empirical Validation Gates — Sprint G-7

Five validation gates that must all pass before the v1.0.0 release:
    EV1-A  Affect Inference Accuracy          (F1 >= 0.75)
    EV1-B  Stage Engine Transition Validity   (no false promotions)
    EV1-C  Schumann Biometric Alignment       (live data — deferred to v1.0.0)
    EV1-D  HRV Coherence Integration          (hardware-dependent — deferred)
    EV1-E  Memory Retrieval Fidelity          (MRR@3 >= 0.80)

EV1-C and EV1-D require live sensor data and are tracked separately in
docs/EV1_METHODOLOGY.md. EV1-A, EV1-B, and EV1-E run fully in CI.

Canon Ref: GAIAmanifest.json → release_gate.EV1_empirical_validation_gates
"""
