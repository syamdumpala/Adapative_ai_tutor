# Development Workflow (Mandatory)

Every feature addition or rectification **must** follow these steps in order.
This applies to human developers and AI agents alike.

## 0. Read the architecture first

Before writing a single line of code:

1. Read [`STRUCTURE.md`](./STRUCTURE.md) — understand the current file/folder layout and conventions.
2. Read [`DIAGRAM.md`](./DIAGRAM.md) — understand how components and requests flow.
3. Read [`HISTORY.md`](./HISTORY.md) — understand what has already been done and why.

## 1. Implement the feature

- Follow the **feature-based** layout: every API/domain lives in its own folder
  under `app/features/<feature>/` with `models.py`, `schemas.py`, `service.py`,
  `routes.py`, and a `tests/` folder. See `STRUCTURE.md` for the full convention.
- **Validation is mandatory** — request/response bodies are validated with Pydantic
  schemas (`schemas.py`), including field validators for domain rules.
- Business logic lives in `service.py`, never in `routes.py`. Routes only translate
  HTTP ↔ service calls and map domain errors to status codes.
- Register any new feature router in `app/api/router.py` (the route index).

## 2. Write unit tests

- Add tests in the feature's `tests/` folder (`app/features/<feature>/tests/test_*.py`).
- Tests use the in-memory SQLite fixture from `conftest.py` — **no Postgres or API key required**.
- External/LLM calls must be mocked (see `tutor/tests/test_tutor.py` for the pattern).

## 3. Run the tests

```bash
cd backend
make test        # or: pytest
```

All tests must pass (green) before proceeding.

## 4. Update the architecture folder

- Update `STRUCTURE.md` if files/folders were added, removed, or moved.
- Update `DIAGRAM.md` if the component or request flow changed.
- **Always** append an entry to `HISTORY.md` describing the change.

## 5. Ask the developer to test

Hand off for manual/QA testing (run the app, hit the endpoints). Do **not** commit
until the developer has confirmed the change works.

## 6. Lint via pre-commit, then commit

- Ensure the pre-commit hook is installed once: `make hooks` (or `pre-commit install` at repo root).
- On `git commit`, the hook runs **ruff** (lint + format) automatically.
- Fix anything the hook reports, then commit.

## Quick checklist

- [ ] Read `STRUCTURE.md`, `DIAGRAM.md`, `HISTORY.md`
- [ ] Feature follows the folder convention; validation present
- [ ] Unit tests written and passing (`make test`)
- [ ] `STRUCTURE.md` / `DIAGRAM.md` updated if needed
- [ ] `HISTORY.md` entry appended
- [ ] Developer manually tested and approved
- [ ] Pre-commit (ruff) passes; committed
