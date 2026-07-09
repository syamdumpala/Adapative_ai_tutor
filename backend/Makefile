# All targets run through the project virtualenv so they never fall back to a
# system Python that is missing dependencies. Override with `make VENV=/path run`.
VENV ?= .venv
PY := $(VENV)/bin/python

.PHONY: venv install install-dev run migrate migrate-subjects seed test lint format hooks

venv:
	python3 -m venv $(VENV)

install:
	$(PY) -m pip install -r requirements.txt

install-dev:
	$(PY) -m pip install -r requirements-dev.txt

run:
	$(PY) -m uvicorn app.main:app --reload

# Additively sync the schema (create tables + add new columns). Idempotent.
migrate:
	$(PY) -m app.dbsync

# One-off: rename subject slug ids to numeric ids (1..6) in an existing DB.
migrate-subjects:
	$(PY) -m app.migrate_subjects

# Populate the configured database with the demo dataset (idempotent).
seed:
	$(PY) -m app.seed

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

format:
	$(PY) -m ruff format .

# Install the git pre-commit hook (config lives at the repo root).
hooks:
	cd .. && $(PY) -m pre_commit install
