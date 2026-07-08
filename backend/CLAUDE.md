# Working in this backend

**Before writing or changing any code, read the `architecture/` folder** — it is
the source of truth:

1. `architecture/STRUCTURE.md` — file/folder layout and conventions
2. `architecture/DIAGRAM.md` — component, request-flow, and pipeline diagrams
3. `architecture/HISTORY.md` — what has already been done
4. `architecture/WORKFLOW.md` — the mandatory step-by-step process

## Rules

- Use the **feature-based** layout: each API lives in `app/features/<feature>/`
  with `models.py`, `schemas.py`, `service.py`, `routes.py`, and `tests/`.
- Business logic goes in `service.py`; `routes.py` only maps HTTP ↔ services.
- Register new routers in `app/api/router.py` (the route index).
- Input validation is mandatory (Pydantic schemas + field validators).
- When a feature is complete: **write unit tests, run them (`make test`), and get
  a green suite** before asking the developer to test.
- **After any change, update `architecture/`** (`STRUCTURE.md` / `DIAGRAM.md` if
  layout or flow changed) and always append an entry to `architecture/HISTORY.md`.
- Commit only after the developer confirms; the pre-commit hook runs ruff linting.

## Commands

```bash
make install-dev   # install runtime + dev deps
make run           # run the dev server (uvicorn)
make test          # run pytest (in-memory SQLite; no Postgres/API key needed)
make lint          # ruff check
make hooks         # install the pre-commit hook
```
