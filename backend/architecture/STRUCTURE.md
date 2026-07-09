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
│   │   ├── llm.py                   # LLM provider factory (subscription / Anthropic / OpenAI / Gemini / local)
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
  - `models.py` — SQLAlchemy ORM models (tables) for this feature.
  - `schemas.py` — Pydantic models for request/response + field validators.
  - `service.py` — business logic; raises domain exceptions, never HTTP exceptions.
  - `routes.py` — `APIRouter` with `prefix="/<feature>"`; maps HTTP ↔ service.
  - `dependencies.py` — FastAPI dependencies specific to the feature (optional).
  - `graph/` — AI/graph logic (tutor feature only; nodes + router + state).
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

All collection endpoints share the query contract from `app/core/query.py`:
`limit`/`offset` pagination, `q` search, `sort=field`/`sort=-field`, returning
`Page[T] = {items,total,limit,offset,has_more}`.

| Method | Path | Auth | Feature | Description |
| ------ | ---- | ---- | ------- | ----------- |
| POST | `/auth/register` | — | auth | Register (role student\|teacher; `student_id` auto-generated if omitted) |
| POST | `/auth/login` / `/auth/token` | — | auth | Login → JWT |
| GET | `/auth/me` | Bearer | auth | Current user (split name + initials + role) |
| POST | `/auth/logout` | Bearer | auth | Stateless logout hook |
| GET | `/subjects` · `/subjects/{id}` | Bearer | catalog | Subject catalog (+ per-student `progress`) |
| POST/PATCH | `/subjects` · `/subjects/{id}` | Teacher | catalog | Create / update subject |
| GET | `/topics` · `/topics/{id}` | Bearer | catalog | Concept/topic list + detail |
| POST/PATCH | `/topics` · `/topics/{id}` | Teacher | catalog | Create / update topic |
| POST | `/tutor/ask` | Bearer | tutor | One turn of the multi-agent tutor graph |
| GET | `/tutor/sessions` · `/{id}` · `/{id}/messages` | Bearer | tutor | Chat list · detail · conversation history |
| GET | `/me/profile` · `/me/performance` | Bearer | tutor | Student profile · performance record |
| GET | `/teacher/overview` | Teacher | teacher | Class context + counts |
| GET | `/teacher/students` · `/{id}` · `/{id}/topics` · `/{id}/evidence` | Teacher | teacher | Roster · record · explored topics · evidence |
| GET | `/teacher/topics` · `/{id}` · `/{id}/students` | Teacher | teacher | Topics+aggregate · detail · per-student outcomes |
| GET | `/teacher/escalations` | Teacher | teacher | Escalation queue (filter status/trigger) |
| POST | `/teacher/escalations/{id}/resolve` | Teacher | teacher | Resolve an escalation |
| POST | `/teacher/simulate-day` | Teacher | teacher | Advance the spaced-repetition clock |
| GET | `/health` | — | — | Health check |

## Tables

| Table                  | Feature | Columns                                                                                                        |
| ---------------------- | ------- | -------------------------------------------------------------------------------------------------------------- |
| `students`             | auth    | id, student_id(unique), student_name, email(unique), hashed_password, **role**, created_at                     |
| `subjects`             | catalog | id(slug), name, glyph, tone, description, meta, status, is_new, position, created_at                            |
| `concepts`             | catalog | id(slug), subject_id(FK), name, glyph, tone, short, long, difficulty_band, position, created_at                 |
| `student_profile`      | tutor   | …mastery, confidence, misconceptions, evidence_count, next_review, **status_label, risk_tone, improvement_pct, day_streak, recent_accuracy, concepts_mastered, grade**, updated_at |
| `student_concept_state`| tutor   | id, student_id(FK), concept_id(FK), mastery, confidence, understanding, attempts, streak, last_seen, next_review (uniq student+concept) |
| `misconceptions`       | tutor   | id, student_id(FK), concept_id(FK), label, name, status, evidence_count, prereq_concept_id, first/last_seen     |
| `tutor_sessions`       | tutor   | id(uuid), student_id(FK), **subject_id, title, hint_rung, leak_checks**, concept, status, state(JSON), created/updated_at |
| `conversation_history` | tutor   | id, session_id(FK), student_id(FK), role, **kind, payload(JSON)**, content, created_at                          |
| `evidence_events`      | tutor   | id, student_id(FK), session_id(FK), concept, correct, error_type, created_at                                   |
| `teacher_escalations`  | tutor   | id, student_id(FK), session_id(FK), **trigger, excerpt, status, teacher_notes, resolved_at**, reason, created_at |
