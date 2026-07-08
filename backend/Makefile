# All targets run through the project virtualenv so they never fall back to a
# system Python that is missing dependencies. Override with `make VENV=/path run`.
VENV ?= .venv
PY := $(VENV)/bin/python

.PHONY: venv install install-dev run test lint format hooks

venv:
	python3 -m venv $(VENV)

install:
	$(PY) -m pip install -r requirements.txt

install-dev:
	$(PY) -m pip install -r requirements-dev.txt

run:
	$(PY) -m uvicorn app.main:app --reload

test:
	$(PY) -m pytest

lint:
	$(PY) -m ruff check .

format:
	$(PY) -m ruff format .

# Install the git pre-commit hook (config lives at the repo root).
hooks:
	cd .. && $(PY) -m pre_commit install
