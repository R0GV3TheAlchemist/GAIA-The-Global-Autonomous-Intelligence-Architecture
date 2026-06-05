"""
core/rag/chunker.py
~~~~~~~~~~~~~~~~~~~
Text chunking utilities for the GAIA-OS RAG pipeline.

Public surface
--------------
Chunk            — dataclass representing a single text chunk.
chunk_text()     — split a markdown/plain-text string into Chunks.
chunk_file()     — chunk a single file on disk.
chunk_directory()— recursively chunk all .md / .txt files in a directory.

Chunk IDs are deterministic SHA-256 digests of (source + text) so the
same content always produces the same ID regardless of insertion order.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

_SUPPORTED_EXTENSIONS = {".md", ".txt", ".rst"}


# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """
    A single unit of text extracted from a source document.

    Attributes
    ----------
    chunk_id  : Deterministic hex digest (sha256 of source + text).
    text      : Raw text content of the chunk.
    source    : File path or URL the chunk came from.
    doc_title : First H1 heading found in the parent document, or source stem.
    section   : Nearest H2/H3 heading above this chunk, or empty string.
    char_start: Character offset in the original document (best-effort).
    """
    chunk_id:  str
    text:      str
    source:    str
    doc_title: str = ""
    section:   str = ""
    char_start: int = 0

    def provenance(self) -> dict:
        """Return a provenance dict suitable for citation."""
        return {
            "chunk_id":  self.chunk_id,
            "source":    self.source,
            "doc_title": self.doc_title,
            "section":   self.section,
            "char_start":self.char_start,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _make_id(source: str, text: str) -> str:
    digest = hashlib.sha256(f"{source}:{text}".encode()).hexdigest()
    return digest[:32]


def _extract_title(text: str, fallback: str = "") -> str:
    """Return the first H1 heading found, or fallback."""
    m = re.search(r"^#\s+(.+)", text, re.MULTILINE)
    return m.group(1).strip() if m else fallback


def _extract_section(text_before: str) -> str:
    """Return the last H2 or H3 heading seen before this chunk."""
    matches = re.findall(r"^#{2,3}\s+(.+)", text_before, re.MULTILINE)
    return matches[-1].strip() if matches else ""


def _split_into_windows(
    text: str,
    chunk_size: int,
    overlap: int,
) -> List[tuple[str, int]]:
    """
    Split *text* into overlapping windows.
    Returns list of (window_text, char_start) tuples.
    """
    if chunk_size <= 0:
        return [(text, 0)]

    windows: List[tuple[str, int]] = []
    start = 0
    length = len(text)
    step = max(1, chunk_size - overlap)

    while start < length:
        end = min(start + chunk_size, length)
        window = text[start:end].strip()
        if window:
            windows.append((window, start))
        if end >= length:
            break
        start += step

    return windows


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    source: str,
    chunk_size: int = 512,
    overlap: int = 64,
) -> List[Chunk]:
    """
    Split *text* into overlapping Chunks.

    Parameters
    ----------
    text       : Raw document text (markdown or plain).
    source     : Logical identifier (file path, URL, canon ID).
    chunk_size : Target character count per chunk.
    overlap    : Character overlap between adjacent chunks.

    Returns
    -------
    List[Chunk]  Ordered list of chunks; never empty if text is non-empty.
    """
    if not text or not text.strip():
        return []

    fallback_title = Path(source).stem if source else "unknown"
    doc_title = _extract_title(text, fallback=fallback_title)
    windows = _split_into_windows(text, chunk_size, overlap)

    chunks: List[Chunk] = []
    for window_text, char_start in windows:
        section = _extract_section(text[:char_start])
        chunk_id = _make_id(source, window_text)
        chunks.append(Chunk(
            chunk_id=chunk_id,
            text=window_text,
            source=source,
            doc_title=doc_title,
            section=section,
            char_start=char_start,
        ))
    return chunks


def chunk_file(
    path: Path,
    chunk_size: int = 512,
    overlap: int = 64,
    encoding: str = "utf-8",
) -> List[Chunk]:
    """
    Read *path* and return its chunks.
    Returns [] if the file extension is not supported.
    """
    path = Path(path)
    if path.suffix.lower() not in _SUPPORTED_EXTENSIONS:
        return []
    try:
        text = path.read_text(encoding=encoding, errors="replace")
    except OSError:
        return []
    return chunk_text(text, source=str(path), chunk_size=chunk_size, overlap=overlap)


def chunk_directory(
    directory: Path,
    chunk_size: int = 512,
    overlap: int = 64,
    recursive: bool = True,
    encoding: str = "utf-8",
) -> List[Chunk]:
    """
    Recursively chunk all supported files under *directory*.
    Unsupported extensions are silently skipped.
    """
    directory = Path(directory)
    if not directory.is_dir():
        return []

    glob = directory.rglob("*") if recursive else directory.glob("*")
    chunks: List[Chunk] = []
    for path in sorted(glob):
        if path.is_file() and path.suffix.lower() in _SUPPORTED_EXTENSIONS:
            chunks.extend(
                chunk_file(path, chunk_size=chunk_size, overlap=overlap, encoding=encoding)
            )
    return chunks
