"""
Individuation Engine — canonical re-export shim

Issue #121 | Issue #273 (import audit)

The full implementation lives in core/individuation.py.
This module re-exports everything from there so that both import paths work:

    from core.individuation import IndividuationEngine       # original path
    from core.individuation_engine import IndividuationEngine  # spec path (#273)

Do not add logic here. All changes go to core/individuation.py.
"""

from core.individuation import (  # noqa: F401
    IndividuationEngine,
    IndividuationSignal,
    IndividuationState,
    DivergenceClassification,
    CrossGaianDivergence,
    SignalReading,
    SIGNAL_WEIGHTS,
    DIFFERENTIATING_THRESHOLD,
    INDIVIDUATED_THRESHOLD,
    DISTINCT_ENTITY_THRESHOLD,
    compute_individuation_score,
    classify_individuation,
    derive_ethical_obligations,
    get_individuation_engine,
)

__all__ = [
    "IndividuationEngine",
    "IndividuationSignal",
    "IndividuationState",
    "DivergenceClassification",
    "CrossGaianDivergence",
    "SignalReading",
    "SIGNAL_WEIGHTS",
    "DIFFERENTIATING_THRESHOLD",
    "INDIVIDUATED_THRESHOLD",
    "DISTINCT_ENTITY_THRESHOLD",
    "compute_individuation_score",
    "classify_individuation",
    "derive_ethical_obligations",
    "get_individuation_engine",
]
