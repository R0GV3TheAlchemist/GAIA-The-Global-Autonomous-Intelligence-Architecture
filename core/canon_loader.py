"""
core/canon_loader.py — Backward-compatibility shim.

CanonLoader and its helpers were moved to core.rag.canon_loader as part of
the RAG module reorganisation.  This shim re-exports everything so that any
legacy import path (e.g. `from core.canon_loader import CanonLoader`) works
without changes.

Do not add new logic here — use core.rag.canon_loader directly.
"""
from core.rag.canon_loader import (  # noqa: F401  (re-export)
    CanonLoader,
    CanonChunk,
    _tokenize,
    _term_freq,
    _chunk_text,
    _best_excerpt,
    _TFIDFIndex,
)

__all__ = [
    "CanonLoader",
    "CanonChunk",
    "_tokenize",
    "_term_freq",
    "_chunk_text",
    "_best_excerpt",
    "_TFIDFIndex",
]
