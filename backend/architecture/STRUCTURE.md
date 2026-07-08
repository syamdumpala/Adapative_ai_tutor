# Project Structure & Conventions

_Last updated: 2026-07-08_

## Folder tree

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI app + lifespan (create tables), mounts api_router
│   ├── core/                       # cross-cutting infrastructure (no feature logic)
│   │   ├── config.py               # Settings (env / .env) — DB URL, JWT, LLM provider/auth-mode/model, keys
│   │   ├── database.py             # async SQLAlchemy engine, session factory, Base, get_db()
│   │   ├── llm.py                   # LLM provider factory (subscription / Anthropic / OpenAI / Gemini)
│   │   └── security.py             # password hashing + JWT encode/decode (framework-agnostic)
│   ├── api/
│   │   └── router.py               # ROUTE INDEX — aggregates every feature router
│   └── features/                   # one folder per API/domain
│       ├── auth/
│       │   ├── models.py           # Student ORM model
│       │   ├── schemas.py          # Pydantic request/response models + validators
│       │   ├── service.py          # business logic (register/authenticate); domain errors
│       │   ├── dependencies.py     # get_current_student (JWT -> Student)
│       │   ├── routes.py           # /auth/register, /auth/login, /auth/me
│       │   └── tests/
│       │       └── test_auth.py
│       └── tutor/
│           ├── models.py           # QuestionLog ORM model
│           ├── schemas.py          # QuestionRequest / QuestionResponse + validators
│           ├── pipeline.py         # LangGraph agentic pipeline (analyze -> tutor -> followup)
│           ├── service.py          # ask_question(): run pipeline + persist QuestionLog
│           ├── routes.py           # /tutor/ask
│           └── tests/
│               └── test_tutor.py
├── architecture/                   # SOURCE OF TRUTH (read before changing code)
│   ├── README.md
│   ├── WORKFLOW.md
│   ├── STRUCTURE.md                # this file
│   ├── DIAGRAM.md
│   └── HISTORY.md
├── conftest.py                     # shared pytest fixtures (in-memory SQLite test client)
├── pyproject.toml                  # pytest + ruff config
├── requirements.txt                # runtime deps
├── requirements-dev.txt            # dev/test deps (pytest, ruff, pre-commit, aiosqlite, httpx)
├── Makefile                        # install / run / test / lint / hooks
├── .env.example
├── .gitignore
└── README.md

# repo root:
.pre-commit-config.yaml             # ruff lint/format hook (scoped to backend/)
```

## Naming conventions

- **Feature folder**: `app/features/<feature>/` — lowercase, singular domain noun (`auth`, `tutor`).
- **Files inside a feature** (fixed names, one responsibility each):
  - `models.py`     — SQLAlchemy ORM models (tables) for this feature.
  - `schemas.py`    — Pydantic models for request/response + field validators.
  - `service.py`    — business logic; raises domain exceptions, never HTTP exceptions.
  - `routes.py`     — `APIRouter` with `prefix="/<feature>"`; maps HTTP ↔ service.
  - `dependencies.py` — FastAPI dependencies specific to the feature (optional).
  - `pipeline.py`   — AI/graph logic (tutor feature only; optional per feature).
  - `tests/test_<feature>.py` — unit/API tests for the feature.
- **Route index**: `app/api/router.py` exposes `api_router`; every feature router is
  `include_router`-ed here. `main.py` mounts only `api_router`.
- **Tables**: snake_case plural (`students`, `question_logs`).
- **Domain errors**: named `*Error` in the feature's `service.py`; translated to HTTP in `routes.py`.

## Layering rules

- `routes.py` → depends on `service.py`, `schemas.py`, `dependencies.py`.
- `service.py` → depends on `models.py`, `core/`, other features' models if needed.
- `core/` → depends on nothing in `features/` (except `security` primitives which are pure).
- Validation happens in `schemas.py` (Pydantic). Never trust raw request data in services.

## Endpoints

| Method | Path             | Auth   | Feature | Description                          |
| ------ | ---------------- | ------ | ------- | ------------------------------------ |
| POST   | `/auth/register` | —      | auth    | Register a student                   |
| POST   | `/auth/login`    | —      | auth    | Login (email + password) → JWT       |
| GET    | `/auth/me`       | Bearer | auth    | Current student                      |
| POST   | `/tutor/ask`     | Bearer | tutor   | Run the agentic tutoring pipeline    |
| GET    | `/health`        | —      | —       | Health check                         |

## Tables

| Table           | Feature | Columns                                                        |
| --------------- | ------- | -------------------------------------------------------------- |
| `students`      | auth    | id, student_id(unique), student_name, email(unique), hashed_password, created_at |
| `question_logs` | tutor   | id, student_id(FK→students.id), question, answer, created_at   |
