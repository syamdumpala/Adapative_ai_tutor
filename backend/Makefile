.PHONY: install install-dev run test lint format hooks

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

# Install the git pre-commit hook (config lives at the repo root).
hooks:
	cd .. && pre-commit install
