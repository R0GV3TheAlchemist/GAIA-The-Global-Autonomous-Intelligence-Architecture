"""
targets
=======
Per-material simulation drivers for the GAIA-OS Gaianite substrate.

Each submodule defines:
  - A geometry / Mole builder function
  - A VQE simulation runner
  - A Canon-schema exporter

Modules
-------
ysz        -- Yttria-Stabilized Zirconia (Canon C65)   [#136]
bts        -- Barium Titanate-Strontium (Canon C66)     [#137]
alscn_gan  -- AlScN / AlScN:GaN heterostructure (C67)  [#138]
"""

__all__ = ["ysz", "bts", "alscn_gan"]
