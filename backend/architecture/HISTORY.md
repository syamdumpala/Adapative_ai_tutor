# Change History

Newest entries first. Append an entry for **every** change. Format:

```
## YYYY-MM-DD — <short title>
**Author:** <human | AI>
**Summary:** what changed and why.
**Files:** key files added/modified/removed.
**Tests:** what was verified.
```

---

## 2026-07-08 — Multi-agent LangGraph tutor (replaces 3-node pipeline)
**Author:** AI (Claude)
**Summary:** Rebuilt the tutor feature per the LangGraph AI Tutor guides into a
supervisor-routed multi-agent graph with per-session state. Added a graph package
(`graph/state.py`, `graph/llm.py`, `graph/router.py`, `graph/graph.py`, and 11
agent nodes: profile, diagnostic, misconception, planner, rag(stub), hint, guard,
evaluator, memory, revision, escalation) implementing the guide's conditional-edge
routing (§2), confidence formulas (§5) and memory rules (§7). `/tutor/ask` is now
**multi-turn**: omit `session_id` to start (returns Hint 1), send it back with the
student's answer to loop (evaluate → next hint / complete / escalate). Added 5 core
tables (`student_profile`, `tutor_sessions`, `conversation_history`,
`evidence_events`, `teacher_escalations`) + `repository.py`. Replaced `QuestionLog`
and `pipeline.py`. Re-added the `503` guard when `ANTHROPIC_API_KEY` is unset.
**v1 simplifications:** RAG is a stub retriever (no vector store); long-term profile
updates on the success path (memory node); distress is keyword-based; `misconceptions`
and `mastery` live in `student_profile` rather than separate tables.
**Files:** `app/features/tutor/{models,repository,schemas,service,routes}.py`,
`app/features/tutor/graph/**`, `app/features/tutor/tests/test_tutor.py`.
Removed `app/features/tutor/pipeline.py`.
**Tests:** `pytest` — 16 passed (8 tutor multi-turn flows + 8 auth); ruff clean.
Smoke-tested against local PostgreSQL.

## 2026-07-08 — Add OAuth2 form token endpoint for Swagger Authorize
**Author:** AI (Claude)
**Summary:** The Swagger UI "Authorize" dialog (OAuth2 password flow) posts
form-encoded `username`/`password` to the token URL, which the JSON `/auth/login`
endpoint could not accept. Added `POST /auth/token` accepting
`OAuth2PasswordRequestForm` (username = student email) and pointed the
`OAuth2PasswordBearer(tokenUrl=...)` at it. JSON `/auth/login` is unchanged for
API clients. Now the Authorize dialog works: enter email as username + password,
leave client_id/client_secret blank, no scopes.
**Files:** `app/features/auth/routes.py` (+`/token`), `app/features/auth/dependencies.py`
(tokenUrl → `/auth/token`), `app/features/auth/tests/test_auth.py` (+test).
**Tests:** `pytest` — 12 passed; ruff clean.

## 2026-07-08 — Refactor to feature-based architecture
**Author:** AI (Claude)
**Summary:** Restructured the flat `app/` layout into a robust feature-based
architecture. Introduced a `core/` layer (config, database, security), a route
index (`app/api/router.py`), and per-feature folders (`auth`, `tutor`) each owning
`models`, `schemas`, `service`, `routes`, and `tests`. Added Pydantic field
validators for input validation, a `QuestionLog` model so the tutor feature
persists interactions, unit tests with an in-memory SQLite fixture, ruff + pytest
config, a pre-commit linting hook, a Makefile, and this `architecture/` folder as
the source of truth.
**Files:**
- Added: `app/core/{config,database,security}.py`, `app/api/router.py`,
  `app/features/auth/{models,schemas,service,dependencies,routes}.py`,
  `app/features/tutor/{models,schemas,pipeline,service,routes}.py`,
  `app/features/*/tests/test_*.py`, `conftest.py`, `pyproject.toml`,
  `requirements-dev.txt`, `Makefile`, `architecture/*`, repo-root
  `.pre-commit-config.yaml`, `backend/CLAUDE.md`.
- Removed (flat layout): `app/{config,database,models,schemas,auth}.py`,
  `app/routers/`, `app/ai/`.
- Modified: `app/main.py` (mounts route index, imports feature models).
**Tests:** `pytest` (auth + tutor suites) run green; app smoke-tested against
local PostgreSQL (register/login/me/ask flow).

## 2026-07-08 — Initial backend scaffold
**Author:** AI (Claude)
**Summary:** Initialized FastAPI backend with async SQLAlchemy/PostgreSQL, JWT
auth (register/login/me), and an agentic LangGraph + LangChain tutoring pipeline
(`/tutor/ask`) using Claude `claude-opus-4-8`.
**Files:** initial `app/` package, `requirements.txt`, `.env.example`, `README.md`.
**Tests:** Manual end-to-end smoke test of all endpoints against local PostgreSQL.
