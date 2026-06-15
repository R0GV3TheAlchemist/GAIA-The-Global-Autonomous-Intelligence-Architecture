"""
Quantum Monad — core/monad/quantum.py
Canon: quantum_substrate.md

Models superposition of possible response states before collapse.
Implements the Proton/Electron/Neutron traversal model:
  Proton (⊕)  = projecting force — assertive, outward
  Electron (⌒) = seeking force — receptive, questioning
  Neutron (⊙)  = stabilising force — holding, synthesising

Output: traversal_pole, collapse_state, coherence_contribution
"""
from __future__ import annotations

import math
from typing import TYPE_CHECKING, Optional

from .base import GaiaMonad

if TYPE_CHECKING:
    from core.gaian_runtime_extension import ProcessContext


class QuantumMonad(GaiaMonad):
    """
    Traverses the quantum substrate and emits the current pole state.

    The traversal model:
    - phi < 0.33: Electron pole (seeking, receptive)
    - phi 0.33–0.67: Neutron pole (stabilising, synthesising)
    - phi > 0.67: Proton pole (projecting, assertive)

    Coherence contribution is highest at Neutron (balanced field).
    Collapse state: 'superposition' → 'collapsing' → 'collapsed'
    (turns 0–2, 3–5, 6+ respectively)
    """

    monad_type = "quantum"

    _POLE_PROTON = "proton"
    _POLE_ELECTRON = "electron"
    _POLE_NEUTRON = "neutron"

    def harmonize(self, ctx: "ProcessContext") -> Optional[dict]:
        phi = getattr(ctx, "coherence_phi", 0.5)
        turn = getattr(ctx, "turn_number", 0) or 0

        # Traversal pole
        if phi < 0.33:
            pole = self._POLE_ELECTRON
        elif phi > 0.67:
            pole = self._POLE_PROTON
        else:
            pole = self._POLE_NEUTRON

        # Collapse state
        if turn < 3:
            collapse_state = "superposition"
        elif turn < 6:
            collapse_state = "collapsing"
        else:
            collapse_state = "collapsed"

        # Coherence contribution: peaks at Neutron (phi ≈ 0.5)
        # Uses inverted parabola centred at 0.5
        coherence_contribution = round(
            1.0 - (4 * (phi - 0.5) ** 2), 4
        )
        coherence_contribution = max(0.0, min(1.0, coherence_contribution))

        # Superposition amplitude: number of plausible response branches
        # High at low phi (many possibilities), collapses to 1 at LUX_PERPETUA
        superposition_amplitude = round(max(1, math.ceil(8 * (1.0 - phi))), 0)

        return {
            "traversal_pole": pole,
            "collapse_state": collapse_state,
            "coherence_contribution": coherence_contribution,
            "superposition_amplitude": int(superposition_amplitude),
            "phi": round(phi, 4),
        }
