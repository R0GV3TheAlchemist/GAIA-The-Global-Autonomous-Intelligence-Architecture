# =============================================================================
# GAIA-OS Makefile
# =============================================================================
# Prerequisites: python >= 3.11, postgresql running, DATABASE_URL set.
# All python commands run via 'python' — use a venv or conda env as needed.
# =============================================================================

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
PYTHON     ?= python
ALEMBIC    ?= alembic
CRYSTAL_DIR ?= data/correspondence

# ---------------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------------
.PHONY: help
help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*##"}; {printf "  \033[36m%-28s\033[0m %s\n", $$1, $$2}'

# ---------------------------------------------------------------------------
# Database migrations
# ---------------------------------------------------------------------------
.PHONY: db-upgrade
db-upgrade:  ## Run all pending Alembic migrations (alembic upgrade head)
	$(ALEMBIC) upgrade head

.PHONY: db-downgrade
db-downgrade:  ## Roll back the most recent Alembic migration (alembic downgrade -1)
	$(ALEMBIC) downgrade -1

.PHONY: db-history
db-history:  ## Show Alembic migration history
	$(ALEMBIC) history --verbose

.PHONY: db-current
db-current:  ## Show current Alembic migration revision
	$(ALEMBIC) current

# ---------------------------------------------------------------------------
# Crystal correspondence import commands
# ---------------------------------------------------------------------------

.PHONY: crystals-import
crystals-import:  ## Import all crystal JSONs from DIR (default: data/correspondence)
	$(PYTHON) scripts/import_crystals.py $(CRYSTAL_DIR)

.PHONY: crystals-import-dry
crystals-import-dry:  ## Validate crystal JSONs against schema — no DB writes
	$(PYTHON) scripts/import_crystals.py $(CRYSTAL_DIR) --dry-run

.PHONY: crystals-validate
crystals-validate:  ## Alias for crystals-import-dry (schema validation only)
	$(PYTHON) scripts/import_crystals.py $(CRYSTAL_DIR) --dry-run

.PHONY: crystals-import-verbose
crystals-import-verbose:  ## Import with per-crystal scalar extraction preview
	$(PYTHON) scripts/import_crystals.py $(CRYSTAL_DIR) --verbose

.PHONY: crystals-import-recursive
crystals-import-recursive:  ## Import all JSONs recursively from DIR
	$(PYTHON) scripts/import_crystals.py $(CRYSTAL_DIR) --recursive

.PHONY: crystals-import-safe
crystals-import-safe:  ## Import, continue after per-file errors (partial import OK)
	$(PYTHON) scripts/import_crystals.py $(CRYSTAL_DIR) --continue-on-error

.PHONY: crystals-errors
crystals-errors:  ## Show queued validation errors from last import run
	@$(PYTHON) -c "\
import sys; sys.path.insert(0, '.'); \
from core.crystal_correspondence.ingestion import get_validation_errors; \
errs = get_validation_errors(); \
print(f'{len(errs)} validation error(s) in queue.'); \
[print(f\"  [{i+1}] {e}\") for i, e in enumerate(errs)]"

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
.PHONY: test
test:  ## Run the full test suite
	$(PYTHON) -m pytest tests/ -v

.PHONY: test-correspondence
test-correspondence:  ## Run correspondence-specific tests only
	$(PYTHON) -m pytest tests/correspondence/ -v

.PHONY: test-fast
test-fast:  ## Run tests, stop on first failure
	$(PYTHON) -m pytest tests/ -x -q

# ---------------------------------------------------------------------------
# Code quality
# ---------------------------------------------------------------------------
.PHONY: lint
lint:  ## Run ruff linter
	ruff check .

.PHONY: format
format:  ## Format code with ruff
	ruff format .

.PHONY: typecheck
typecheck:  ## Run mypy type checker
	mypy core/ scripts/

# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------
.PHONY: install
install:  ## Install Python dependencies
	pip install -r requirements.txt

.PHONY: install-dev
install-dev:  ## Install development dependencies
	pip install -r requirements-dev.txt

.PHONY: clean
clean:  ## Remove __pycache__ and .pyc files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete 2>/dev/null || true
