"""
GAIA-OS Sovereign Memory — sqlite-vec integration

Handles:
  - Loading the sqlite-vec extension at DB open time
  - Creating / migrating vec0 virtual tables
  - Storing float32 embeddings alongside episodic + semantic rows
  - Running k-NN similarity search with importance + recency re-ranking
  - Periodic pruning (keeps the vec store from growing unbounded)

The embedding model is pluggable via GAIA_EMBED_MODEL env var:
  - "local"   : sentence-transformers all-MiniLM-L6-v2  (default, offline)
  - "openai"  : text-embedding-3-small via OpenAI API
  - "nomic"   : nomic-embed-text-v1.5 via Ollama
  - "none"    : disables embedding entirely (test / offline mode)

If embedding fails for any reason, the system degrades gracefully to
time-ordered recall — sovereign memory never blocks on a missing model.
"""

from __future__ import annotations

import logging
import os
import struct
import time
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    import sqlite3

logger = logging.getLogger(__name__)

# Embedding dimension constants
_DIM_MINILM  = 384   # all-MiniLM-L6-v2  (local default)
_DIM_OPENAI  = 1536  # text-embedding-3-small
_DIM_NOMIC   = 768   # nomic-embed-text-v1.5

# How many candidates to pull from vec0 before re-ranking
_VEC_CANDIDATES = 100

# ─────────────────────────────────────────────────────────────────
# Anchor the HuggingFace / sentence-transformers model cache to an
# absolute path inside the repo so CI never falls back to a relative
# path like  ../../blobs/<sha>  which breaks when pytest is invoked
# from a working directory other than the repo root.
# ─────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).resolve().parents[2]  # src-python/sovereign_memory -> repo root
_BLOB_CACHE = _REPO_ROOT / ".cache" / "huggingface"

# Only set if not already overridden by the environment (CI may set its own)
if not os.environ.get("HF_HOME"):
    os.environ["HF_HOME"] = str(_BLOB_CACHE)
if not os.environ.get("TRANSFORMERS_CACHE"):
    os.environ["TRANSFORMERS_CACHE"] = str(_BLOB_CACHE / "hub")
if not os.environ.get("SENTENCE_TRANSFORMERS_HOME"):
    os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(_BLOB_CACHE / "sentence_transformers")

_BLOB_CACHE.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────
# Extension loading
# ─────────────────────────────────────────────────────────────────

_VEC_AVAILABLE = False


def try_load_sqlite_vec(conn: "sqlite3.Connection") -> bool:
    """
    Attempt to load the sqlite-vec extension into *conn*.
    Returns True on success, False if the extension is not installed.
    Logs a warning on failure so CI (which may not have the extension)
    can still run without vector search.
    """
    global _VEC_AVAILABLE
    try:
        conn.enable_load_extension(True)
        import sqlite_vec  # type: ignore
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        _VEC_AVAILABLE = True
        logger.info("sqlite-vec extension loaded — vector search enabled")
    except Exception as exc:  # noqa: BLE001
        _VEC_AVAILABLE = False
        logger.warning(
            "sqlite-vec not available (%s). Memory search will use time-order fallback.",
            exc,
        )
    return _VEC_AVAILABLE


def is_vec_available() -> bool:
    return _VEC_AVAILABLE


# ─────────────────────────────────────────────────────────────────
# Schema helpers (called by migration v2)
# ─────────────────────────────────────────────────────────────────

def ensure_vec_tables(conn: "sqlite3.Connection", dim: int) -> None:
    """
    Create vec0 virtual tables if they don't exist.
    Safe to call multiple times (IF NOT EXISTS pattern via try/except).
    """
    if not _VEC_AVAILABLE:
        return
    try:
        conn.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_episodic_embeddings
            USING vec0(
                rowid INTEGER PRIMARY KEY,
                embedding FLOAT[{dim}]
            )
            """
        )
        conn.execute(
            f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS vec_semantic_embeddings
            USING vec0(
                rowid INTEGER PRIMARY KEY,
                embedding FLOAT[{dim}]
            )
            """
        )
        conn.commit()
        logger.info("vec0 tables ready (dim=%d)", dim)
    except Exception as exc:  # noqa: BLE001
        logger.error("Failed to create vec0 tables: %s", exc)


# ─────────────────────────────────────────────────────────────────
# Embedding
# ─────────────────────────────────────────────────────────────────

_embed_model = None
_embed_model_name: str = ""


def _get_embed_fn():
    """
    Lazy-load the embedding function once and cache it.
    Returns a callable: text -> list[float], or None if mode=="none".
    """
    global _embed_model, _embed_model_name
    mode = os.environ.get("GAIA_EMBED_MODEL", "local").lower()

    # ── Explicit no-op mode for tests that don’t need real embeddings ──────────
    if mode == "none":
        return None

    if mode == "openai":
        import openai  # type: ignore
        client = openai.OpenAI()
        def _embed(text: str) -> List[float]:
            resp = client.embeddings.create(
                model="text-embedding-3-small",
                input=text[:8191],
            )
            return resp.data[0].embedding
        _embed_model_name = "openai/text-embedding-3-small"
        return _embed

    if mode == "nomic":
        import httpx  # type: ignore
        base = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        def _embed(text: str) -> List[float]:
            resp = httpx.post(
                f"{base}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["embedding"]
        _embed_model_name = "ollama/nomic-embed-text"
        return _embed

    # Default: local sentence-transformers
    # HF_HOME / SENTENCE_TRANSFORMERS_HOME are set to absolute paths above
    if _embed_model is None:
        from sentence_transformers import SentenceTransformer  # type: ignore
        _embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        _embed_model_name = "local/all-MiniLM-L6-v2"
    def _embed(text: str) -> List[float]:
        return _embed_model.encode(text, normalize_embeddings=True).tolist()
    return _embed


def embed_text(text: str) -> Optional[List[float]]:
    """
    Embed *text* and return a float list, or None on any failure.
    Truncates to 512 chars for the local model to keep latency low.
    Returns None immediately when GAIA_EMBED_MODEL=none.
    """
    try:
        fn = _get_embed_fn()
        if fn is None:
            return None
        return fn(text[:512])
    except Exception as exc:  # noqa: BLE001
        logger.warning("Embedding failed: %s", exc)
        return None


def _pack(vec: List[float]) -> bytes:
    """Pack a float list into little-endian float32 bytes for sqlite-vec."""
    return struct.pack(f"{len(vec)}f", *vec)


# ─────────────────────────────────────────────────────────────────
# Store
# ─────────────────────────────────────────────────────────────────

def store_episodic_embedding(
    conn: "sqlite3.Connection",
    rowid: int,
    text: str,
) -> bool:
    """
    Embed *text* and upsert into vec_episodic_embeddings at *rowid*.
    Returns True on success, False if embedding or vec unavailable.
    """
    if not _VEC_AVAILABLE:
        return False
    vec = embed_text(text)
    if vec is None:
        return False
    try:
        conn.execute(
            "DELETE FROM vec_episodic_embeddings WHERE rowid=?", (rowid,)
        )
        conn.execute(
            "INSERT INTO vec_episodic_embeddings (rowid, embedding) VALUES (?, ?)",
            (rowid, _pack(vec)),
        )
        conn.commit()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("store_episodic_embedding failed: %s", exc)
        return False


def store_semantic_embedding(
    conn: "sqlite3.Connection",
    rowid: int,
    text: str,
) -> bool:
    """Same as store_episodic_embedding but for semantic_memory."""
    if not _VEC_AVAILABLE:
        return False
    vec = embed_text(text)
    if vec is None:
        return False
    try:
        conn.execute(
            "DELETE FROM vec_semantic_embeddings WHERE rowid=?", (rowid,)
        )
        conn.execute(
            "INSERT INTO vec_semantic_embeddings (rowid, embedding) VALUES (?, ?)",
            (rowid, _pack(vec)),
        )
        conn.commit()
        return True
    except Exception as exc:  # noqa: BLE001
        logger.warning("store_semantic_embedding failed: %s", exc)
        return False


# ─────────────────────────────────────────────────────────────────
# Search
# ─────────────────────────────────────────────────────────────────

def search_episodic_vec(
    conn: "sqlite3.Connection",
    principal_id: str,
    query: str,
    limit: int = 20,
    importance_weight: float = 0.2,
    recency_weight: float = 0.1,
) -> List[Tuple[str, float]]:
    """
    k-NN search over episodic_memory with importance + recency re-ranking.

    Returns a list of (episode_id, score) tuples, highest score first.
    Score = (1 - cosine_distance) + importance_weight * importance
             + recency_weight * normalised_recency.

    Falls back to [] if vec unavailable or embedding fails.
    """
    if not _VEC_AVAILABLE:
        return []
    query_vec = embed_text(query)
    if query_vec is None:
        return []

    try:
        now_ms = int(time.time() * 1000)
        one_year_ms = 365 * 24 * 3_600_000

        rows = conn.execute(
            """
            SELECT
                e.id,
                e.created_at,
                v.distance
            FROM vec_episodic_embeddings v
            JOIN episodic_memory e ON e.rowid = v.rowid
            WHERE
                v.embedding MATCH ?
                AND k = ?
                AND e.principal_id = ?
                AND e.deleted_at IS NULL
            """,
            (_pack(query_vec), _VEC_CANDIDATES, principal_id),
        ).fetchall()

        scored: List[Tuple[str, float]] = []
        for row in rows:
            similarity = max(0.0, 1.0 - row["distance"])
            recency    = max(0.0, 1.0 - (now_ms - row["created_at"]) / one_year_ms)
            score      = similarity + recency_weight * recency
            scored.append((row["id"], score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]
    except Exception as exc:  # noqa: BLE001
        logger.warning("search_episodic_vec failed: %s", exc)
        return []


def search_semantic_vec(
    conn: "sqlite3.Connection",
    principal_id: str,
    query: str,
    limit: int = 10,
    confidence_weight: float = 0.15,
) -> List[Tuple[str, float]]:
    """
    k-NN search over semantic_memory.
    Returns list of (pattern_id, score) tuples, highest score first.
    """
    if not _VEC_AVAILABLE:
        return []
    query_vec = embed_text(query)
    if query_vec is None:
        return []

    try:
        rows = conn.execute(
            """
            SELECT
                s.id,
                s.confidence,
                v.distance
            FROM vec_semantic_embeddings v
            JOIN semantic_memory s ON s.rowid = v.rowid
            WHERE
                v.embedding MATCH ?
                AND k = ?
                AND s.principal_id = ?
                AND s.deleted_at IS NULL
            """,
            (_pack(query_vec), _VEC_CANDIDATES, principal_id),
        ).fetchall()

        scored: List[Tuple[str, float]] = []
        for row in rows:
            similarity = max(0.0, 1.0 - row["distance"])
            score      = similarity + confidence_weight * row["confidence"]
            scored.append((row["id"], score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]
    except Exception as exc:  # noqa: BLE001
        logger.warning("search_semantic_vec failed: %s", exc)
        return []


# ─────────────────────────────────────────────────────────────────
# Pruning
# ─────────────────────────────────────────────────────────────────

def prune_orphaned_vectors(conn: "sqlite3.Connection") -> int:
    """
    Remove vec rows whose parent row no longer exists or is soft-deleted.
    Returns total rows removed. Safe to run on a schedule.
    """
    if not _VEC_AVAILABLE:
        return 0
    removed = 0
    try:
        cur = conn.execute(
            """
            DELETE FROM vec_episodic_embeddings
            WHERE rowid NOT IN (
                SELECT rowid FROM episodic_memory WHERE deleted_at IS NULL
            )
            """
        )
        removed += cur.rowcount
        cur = conn.execute(
            """
            DELETE FROM vec_semantic_embeddings
            WHERE rowid NOT IN (
                SELECT rowid FROM semantic_memory WHERE deleted_at IS NULL
            )
            """
        )
        removed += cur.rowcount
        conn.commit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("prune_orphaned_vectors failed: %s", exc)
    return removed
