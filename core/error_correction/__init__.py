# Copyright (c) 2026 R0GV3 The Alchemist
# GAIA — The Global Autonomous Intelligence Architecture
# Licensed under the GAIA Sovereign License (see LICENSE.md)
"""
core/error_correction/__init__.py

GAIA Error Correction — Phase 1: Detection Layer

Public surface:
    GAIAErrorFinding     — normalized error record
    GAIASeverity         — severity enum
    GAIAErrorCategory    — error category enum
    ErrorDetector        — runs Ruff + static checks, yields GAIAErrorFinding
    ErrorReporter        — writes Markdown + JSON artifact reports

Canon Ref: C01 (Sovereignty), C30 (No silent failures), Issue #755
"""
from core.error_correction.models import (
    GAIAErrorCategory,
    GAIAErrorFinding,
    GAIASeverity,
)
from core.error_correction.detector import ErrorDetector
from core.error_correction.reporter import ErrorReporter

__all__ = [
    "GAIAErrorFinding",
    "GAIASeverity",
    "GAIAErrorCategory",
    "ErrorDetector",
    "ErrorReporter",
]
