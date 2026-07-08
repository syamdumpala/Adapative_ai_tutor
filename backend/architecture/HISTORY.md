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

## 2026-07-08 — Security hardening + dependency audit
**Author:** AI (Claude)
**Summary:** Added CORS middleware (configurable `CORS_ORIGINS`, defaults to the
Next.js dev origin `http://localhost:3000`; specific origins + credentials, never
wildcard). Added a startup warning when `JWT_SECRET` is the insecure default. Made
`/tutor/ask` return `503` (not an unhandled `500`) when the provider is selected but
its package/build fails (`LLMConfigError`). Verified `.env` is gitignored, no secrets
staged, `.env.example` placeholders only. Ran `pip-audit`: the only findings were 5
CVEs in build-time `setuptools 65.5.0` — upgraded to ≥78.1.1; audit now clean.
**Files:** `app/main.py` (CORS + JWT warning), `app/core/config.py` (CORS settings +
`DEFAULT_JWT_SECRET`), `app/features/tutor/routes.py` (LLMConfigError→503), `.env.example`.
**Tests:** `pytest` — 16 passed; ruff clean; `pip-audit` clean; server boots, CORS
preflight verified.

## 2026-07-08 — Reconcile LLM-provider factory with the multi-agent graph (post-merge)
**Author:** AI (Claude)
**Summary:** Pulled another branch's configurable LLM-provider feature (`core/llm.py`
factory + `config.py` settings + provider deps) which had been written against the
old 3-node `pipeline.py`. Reconciled it with the current multi-agent graph: the graph's
`graph/llm.py` seam now builds its chat model via `core.llm.get_chat_model()` (so the
whole graph is provider-agnostic — Anthropic subscription/API key, OpenAI, or Gemini),
and `/tutor/ask`'s 503 gate now uses `llm_is_configured()` / `llm_config_detail()`.
Fixed the merge-broken `test_tutor.py` (`mock_llm` referenced an unimported `settings`;
now patches `routes.llm_is_configured`). Updated the stale request-lifecycle diagram.
**Files:** `app/features/tutor/graph/llm.py`, `app/features/tutor/routes.py`,
`app/features/tutor/tests/test_tutor.py`, `architecture/{DIAGRAM,STRUCTURE}.md`.
**Tests:** `pytest` — 16 passed; ruff clean; backend boots + smoke-tested vs PostgreSQL.

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

## 2026-07-08 — Configurable LLM provider (subscription in dev, API keys in prod)
**Author:** AI (Claude)
**Summary:** Decoupled the tutoring pipeline from a single hard-wired Anthropic API
key. Added a provider **factory** (`app/core/llm.py`) selected purely by env:
`LLM_PROVIDER` (anthropic | openai | google), `LLM_AUTH_MODE` (subscription |
api_key, Anthropic only), and `LLM_MODEL` (any model — applies to the subscription
too, e.g. `claude-sonnet-5` vs `claude-opus-4-8`). In development, `subscription`
routes calls through a Claude Pro/Max subscription via the Claude Agent SDK
(`CLAUDE_CODE_OAUTH_TOKEN`) so no metered API tokens are spent — wrapped as a
LangChain `BaseChatModel` so the LangGraph nodes are unchanged. In production, an
API key for Anthropic / OpenAI / Google Gemini is used; switching environments is a
config change, not a code change. Provider packages are imported lazily. The
`/tutor/ask` 503 gate is now provider-aware (`llm_is_configured()`). Subscription
mode is dev-only (a subscription does not include API access; the OAuth token is
licensed for individual Claude Code / Agent SDK use), which is why prod is
API-key-based.
**Files:**
- Added: `app/core/llm.py`.
- Modified: `app/core/config.py` (provider settings + per-provider keys),
  `app/features/tutor/pipeline.py` (uses the factory), `app/features/tutor/routes.py`
  (provider-aware 503), `app/features/tutor/tests/test_tutor.py`, `.env.example`,
  `requirements.txt` (+langchain-openai, +langchain-google-genai),
  `requirements-dev.txt` (+claude-agent-sdk), `architecture/{DIAGRAM,STRUCTURE}.md`.
**Tests:** Unit tests updated to patch `llm_is_configured` (pipeline still mocked;
no real LLM calls). NOTE: suite not run here — the project has no Python 3.11+ venv
yet (system Python is 3.9); run `make test` once a venv exists.

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
