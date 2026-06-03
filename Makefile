# GAIA-OS — developer task runner
# Usage: make <target>
# Requires: Python 3.11+, pip

PYTHON      ?= python
PYTHONPATH  := $(CURDIR):$(CURDIR)/src-python
SRC_DIRS    := core src-python tests

.PHONY: help install test lint typecheck ci clean

help:          ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install:       ## Install all dependencies (runtime + dev)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -e ".[dev]"

test:          ## Run the full test suite
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests/ \
		--tb=short \
		--asyncio-mode=auto \
		-v

lint:          ## Run ruff linter across all source dirs
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m ruff check $(SRC_DIRS)

typecheck:     ## Run mypy type checker
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m mypy core src-python --ignore-missing-imports

ci:            ## Run exactly what CI runs (lint + test + coverage)
	PYTHONPATH=$(PYTHONPATH) $(PYTHON) -m pytest tests/ \
		--tb=short \
		--asyncio-mode=auto \
		--cov=core \
		--cov-report=term-missing \
		-v

clean:         ## Remove compiled Python files and cache dirs
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
