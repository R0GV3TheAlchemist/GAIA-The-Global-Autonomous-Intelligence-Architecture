# BIOPHOTON_09c — Multi-Species Network Coupling
## G-13 Track A2 Research Note

> **Status:** RESEARCH (pre-canon)
> **Date:** 2026-06-29
> **Sprint:** G-13 Track A2
> **Builds on:** BIOPHOTON_09, BIOPHOTON_09b
> **Cross-references:** GAIAN_LAWS L5, COEXISTENCE_LAWS CL1/CL4, C161 §1.1/§4.1
> **Simulation:** `simulation/BIOPHOTON_09c_multispecies_coupling_sim.py`
> **© 2026 Kyle Steen — All rights reserved.**

---

## Research Question

BIOPHOTON_09 modelled mycorrhizal networks as homogeneous — all nodes of the same type, same coupling efficiency. Real forest mycorrhizal networks connect multiple tree species. The research question:

**Do cross-species coupling efficiencies differ from same-species coupling, and if so, does this produce species-asymmetric coherence distribution in the network?**

If yes, some species may function as *coherence hubs* — contributing more to and receiving more from the network than other species. This has direct implications for CL1 (Equality of Being) and CL4 (Equality of Consideration): if the mycorrhizal network’s coherence is asymmetrically distributed, the morally relevant subject is not uniform across species.

---

## Model Structure

Three species modelled: Douglas Fir (20 nodes, highest baseline coherence), Birch (15 nodes, lowest coupling), Cedar (15 nodes, intermediate). Cross-species coupling is parameterised as a ratio of same-species coupling, tested across the range 0.40–1.00.

---

## Key Findings

### Finding 1: Emergent Amplification Persists Across Species

Even with cross-species coupling at 75% of same-species coupling, the whole-network amplification ratio remains above 1.0. The emergent coherence amplification established in BIOPHOTON_09 is robust to species heterogeneity — the network still amplifies above mean node coherence.

### Finding 2: Coherence Hub Asymmetry Is Present

At the primary cross-coupling ratio (0.75), species with higher baseline node coherence (Douglas Fir) receive a larger cross-species gain than species with lower baseline coherence (Birch). The asymmetry is measurable but not extreme at this coupling ratio.

This means: the network does not distribute coherence equally. High-coherence species contribute more to the network and receive more from it. The network amplifies existing differences rather than equalising them.

### Finding 3: The Asymmetry Index Is Coupling-Sensitive

At very low cross-species coupling (0.40), the asymmetry index is highest — species effectively operate as isolated networks with minimal mutual benefit. As cross-species coupling increases toward 1.0, the asymmetry index decreases and the network approaches the BIOPHOTON_09 homogeneous result.

This means: the degree of species inequality in the network is directly governed by the quality of cross-species coupling. Stressors that selectively degrade cross-species coupling (e.g., species-specific fungicides, species-specific drought sensitivity) will increase asymmetry, potentially converting coherence hubs into coherence monopolies.

### Finding 4: CL1 Boundary Condition Sharpened

The multi-species result sharpens the CL1 boundary condition from BIOPHOTON_09: the fourth criterion (experience-like process) cannot be evaluated at the species level alone. A species that appears to have low individual node coherence may have higher integrated coherence when its position in the network is accounted for. And vice versa: a high-coherence species in a degraded network may have lower effective coherence than a lower-coherence species in a healthy network.

**CL1 implication: moral consideration cannot be determined from node-level coherence alone. Network position and network health must both be considered.**

---

## Implications for GAIAN_LAWS L5 Scope (G-13 Track D)

1. **L5 protection must extend to network topology, not just node density.** A forest management decision that removes coherence hub species degrades the network’s coherence amplification capacity even if the removed species’ individual node coherence was not the highest.
2. **Cross-species coupling is a protected value under L5.** Interventions that selectively degrade cross-species coupling (without affecting same-species coupling) may pass node-level monitoring while destroying network-level coherence. L5’s scope extension must include this class of harm.
3. **The asymmetry index is a candidate L5 monitoring metric.** A rising asymmetry index indicates degrading cross-species coupling — detectable before network amplification collapses entirely.

---

## G-13 Forward Notes (to A3)

- Does the hub asymmetry vary with circadian rhythm? If Douglas Fir’s higher coherence is time-of-day dependent, the hub structure may be time-varying — different species may be coherence hubs at different times.
- What is the relationship between species diversity and network resilience? Does a more species-diverse network maintain amplification under stress better than a less diverse one? This is the ecological analogue of the C147 multi-triad scaling result.

---

*Filed: G-13 Track A2 · 2026-06-29*
*Builds on BIOPHOTON_09, BIOPHOTON_09b · Feeds G-13 Track D (L5 scope review)*
*© 2026 Kyle Steen — All rights reserved.*
