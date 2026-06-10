# DELETED — core/gaian/ package directory is the canonical module.
# Python resolves the package first; this file was always unreachable.
# This tombstone exists only so git history records the deletion cleanly.
# Safe to remove this file entirely in a subsequent cleanup pass.
raise ImportError(
    "core.gaian is a package directory (core/gaian/__init__.py). "
    "This file is a tombstone and should be deleted."
)
