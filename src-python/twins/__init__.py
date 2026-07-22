"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  NEXUS — The Universal Autonomous Intelligence Architecture
  GAIA  — The Global Autonomous Intelligence Architecture

  Author   : Kyle Steen
  GitHub   : R0GV3TheAlchemist (https://github.com/R0GV3TheAlchemist)
  Email    : xxkylesteenxx@outlook.com
  Project  : NEXUS / GAIA
  License  : All Rights Reserved © 2026 Kyle Steen
             Unauthorized use, reproduction, or distribution
             of this file or its contents is strictly prohibited.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

twins — NEXUS Digital Twins Package.

Provides DigitalTwin entity lifecycle, TwinState versioning,
TwinRegistry, TwinEvent subscription, and bulk snapshot export.
"""

__version__ = "1.0.0"
__author__ = "Kyle Steen"
__all__ = [
    "DigitalTwin",
    "TwinState",
    "TwinType",
    "TwinRegistry",
    "TwinEvent",
    "TwinEventType",
    "TwinSimulation",
    "SimulationScenario",
    "SimulationResult",
]

from twins.entity import DigitalTwin, TwinState, TwinType
from twins.registry import TwinRegistry, TwinEvent, TwinEventType
from twins.simulation import TwinSimulation, SimulationScenario, SimulationResult
