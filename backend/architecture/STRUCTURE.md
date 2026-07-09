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
│   │   ├── observability.py         # LangSmith tracing wiring (configure_observability)
│   │   └── security.py             # password hashing + JWT encode/decode (framework-agnostic)
│   ├── api/
│   │   └── router.py               # ROUTE INDEX — aggregates every feature router
│   └── features/                   # one folder per API/domain
│       ├── auth/
│       │   ├── models.py           # Student ORM model
│       │   ├── schemas.py          # Pydantic request/response models + validators
│       │   ├── service.py          # business logic (register/authenticate); domain errors
│       │   ├── dependencies.py     # get_current_student (JWT -> Student)
│       │   ├── routes.py           # /auth/register, /auth/login, /auth/token, /auth/me
│       │   └── tests/
│       │       └── test_auth.py
│       └── tutor/
│           ├── models.py           # StudentProfile, TutorSession, ConversationHistory,
│           │                       #   EvidenceEvent, TeacherEscalation
│           ├── repository.py       # async DB helpers (profile/session/misconceptions)
│           ├── schemas.py          # AskRequest / AskResponse + validators
│           ├── service.py          # ask_question(): hydrate session -> run graph -> persist
│           ├── routes.py           # /tutor/ask (multi-turn)
│           ├── graph/              # LangGraph multi-agent tutor
│           │   ├── state.py        # TutorState, new_state(), detect_distress()
│           │   ├── llm.py          # run_agent(stage,schema,...) seam via create_agent (mock point)
│           │   ├── schemas.py      # per-agent Pydantic response schemas (JSON restriction)
│           │   ├── router.py       # supervisor routing (conditional edges per guide §2)
│           │   ├── graph.py        # build_graph() -> compiled `tutor_graph`
│           │   ├── prompts/        # one module per agent: SYSTEM + USER prompt templates
│           │   └── nodes/          # one file per agent
│           │       ├── profile.py       diagnostic.py   misconception.py
│           │       ├── planner.py       hint.py   guard.py
│           │       ├── evaluator.py     memory.py       revision.py   escalation.py
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
  - `graph/`        — AI/graph logic (tutor feature only; nodes + router + state).
  - `tests/test_<feature>.py` — unit/API tests for the feature.
- **Route index**: `app/api/router.py` exposes `api_router`; every feature router is
  `include_router`-ed here. `main.py` mounts only `api_router`.
- **Tables**: snake_case (`students`, `tutor_sessions`, `conversation_history`).
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
| POST   | `/auth/login`    | —      | auth    | Login (email + password JSON) → JWT  |
| POST   | `/auth/token`    | —      | auth    | OAuth2 form login (Swagger Authorize)|
| GET    | `/auth/me`       | Bearer | auth    | Current student                      |
| POST   | `/tutor/ask`     | Bearer | tutor   | One turn of the multi-agent tutor graph (multi-turn via `session_id`) |
| GET    | `/health`        | —      | —       | Health check                         |

## Tables

| Table                  | Feature | Columns                                                        |
| ---------------------- | ------- | -------------------------------------------------------------- |
| `students`             | auth    | id, student_id(unique), student_name, email(unique), hashed_password, created_at |
| `student_profile`      | tutor   | id, student_id(FK, unique), mastery, confidence, misconceptions(JSON), evidence_count, next_review, updated_at |
| `tutor_sessions`       | tutor   | id(uuid), student_id(FK), concept, status, state(JSON graph state), created/updated_at |
| `conversation_history` | tutor   | id, session_id(FK), student_id(FK), role(user/assistant), content, created_at |
| `evidence_events`      | tutor   | id, student_id(FK), session_id(FK), concept, correct, error_type, created_at |
| `teacher_escalations`  | tutor   | id, student_id(FK), session_id(FK), reason, created_at         |
