"""
conftest.py  (repo root)

Pytest collection guard for feat/gaiatrace-171.

The nine test files listed in `collect_ignore` import from modules that
live in src-python/ on main (affect_engine, crystal, shadow_engine,
sovereign_memory).  Those packages do not exist on this branch, so
pytest raises ModuleNotFoundError during collection and aborts before
running any tests at all.

`collect_ignore` is evaluated by pytest before it attempts to import
anything, making it more robust than --ignore CLI flags.  Remove this
file (or empty the list) once src-python/ is merged onto this branch.
"""

import os

collect_ignore = [
    os.path.join("tests", "test_affect_engine.py"),
    os.path.join("tests", "test_crystal_coherence.py"),
    os.path.join("tests", "test_crystal_engine.py"),
    os.path.join("tests", "test_crystal_narrative.py"),
    os.path.join("tests", "test_shadow_archetypes.py"),
    os.path.join("tests", "test_shadow_engine.py"),
    os.path.join("tests", "test_shadow_integration.py"),
    os.path.join("tests", "test_shadow_intensity.py"),
    os.path.join("tests", "test_sovereign_memory.py"),
]
