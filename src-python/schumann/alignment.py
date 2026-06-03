"""Schumann alignment tolerance utilities.

The `is_aligned` helper centralises the tolerance boundary check so that
test_schumann_alignment.py and the engine both use the same logic.

Previous bug: `alignment_score > tolerance` used strict greater-than,
causing boundary values (score == tolerance) to return False.
Fix: use `alignment_score >= tolerance` (inclusive lower bound).
"""

from __future__ import annotations


DEFAULT_TOLERANCE: float = 0.50


def is_aligned(
    alignment_score : float,
    tolerance       : float = DEFAULT_TOLERANCE,
) -> bool:
    """Return True when the alignment score meets or exceeds the tolerance.

    Parameters
    ----------
    alignment_score:
        Computed alignment value from SchumannEngine, in [0, 1].
    tolerance:
        Minimum score required to be considered 'aligned'.
        Defaults to DEFAULT_TOLERANCE (0.50).

    Notes
    -----
    The check is INCLUSIVE (>=) so that a score exactly equal to the
    tolerance boundary is considered aligned. This matches the documented
    contract "aligned if score ≥ tolerance".
    """
    return alignment_score >= tolerance
