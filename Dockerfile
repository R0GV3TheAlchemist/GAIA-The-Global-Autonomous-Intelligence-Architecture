# ─────────────────────────────────────────────────────────────────────────────
# GAIA-OS — Multi-Stage Dockerfile
# Tracks: Issue #265
#
# Stages:
#   dev   — hot-reload, dev deps, mounted source
#   prod  — minimal image, no dev deps, non-root user
#
# Usage:
#   docker build --target dev  -t gaia-dev  .
#   docker build --target prod -t gaia-prod .
#   docker-compose up   (uses dev target by default)
# ─────────────────────────────────────────────────────────────────────────────

# ── Base: shared dependency layer ─────────────────────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# System deps needed by chromadb / numpy / scipy
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# ── Dev stage ─────────────────────────────────────────────────────────────────
FROM base AS dev

# Dev-only extras: pytest, ruff, mypy, watchfiles (uvicorn reload)
RUN pip install \
    pytest pytest-asyncio httpx \
    ruff mypy \
    watchfiles

# Source mounted at runtime via docker-compose volume
# so we only copy the minimum needed for import resolution
COPY . .

EXPOSE 8008

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8008", \
     "--reload", \
     "--log-level", "info"]

# ── Prod stage ────────────────────────────────────────────────────────────────
FROM base AS prod

# Non-root user for security
RUN addgroup --system gaia && adduser --system --ingroup gaia gaia

COPY --chown=gaia:gaia . .

USER gaia

EXPOSE 8008

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8008/health || exit 1

CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8008", \
     "--workers", "2", \
     "--log-level", "warning"]
