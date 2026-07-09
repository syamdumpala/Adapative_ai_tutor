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

## 2026-07-09 — Switch auth to HTTP Bearer (fix Swagger "Authorize")
**Author:** AI (Claude)
**Summary:** Replaced the `OAuth2PasswordBearer(tokenUrl="/auth/login")` scheme with
`HTTPBearer`. The OAuth2 password flow made Swagger POST a form (`username`/`password`)
to `/auth/login`, but that route reads a JSON body, so "Authorize" always failed with
422. With `HTTPBearer`, Swagger's Authorize dialog is a single field: log in via
`/auth/login`, paste the returned `access_token`. JSON login is unchanged (frontend
unaffected). Used `auto_error=False` and an explicit `None` check so a missing/malformed
header still returns **401** (HTTPBearer's default is 403), preserving existing behavior
and tests.
**Files:** Modified `app/features/auth/dependencies.py`.
**Tests:** `pytest` green (16 passed — `test_me_requires_auth` / `test_ask_requires_auth`
still assert 401); `ruff check` clean.

## 2026-07-09 — Add local LLM provider (OpenAI-compatible: LM Studio / Ollama / vLLM)
**Author:** AI (Claude)
**Summary:** Extended the provider factory with a fourth option, `LLM_PROVIDER=local`,
so the tutor can run entirely against a self-hosted model server. LM Studio, Ollama,
vLLM, llama.cpp, etc. all expose an OpenAI-compatible `/v1/chat/completions` endpoint,
so the new `_build_local` builder reuses the existing `langchain-openai` `ChatOpenAI`
client with `base_url=LOCAL_BASE_URL` and a placeholder key — **no new dependency**.
Config gained `local_base_url` / `local_api_key`; `llm_is_configured()` and
`llm_config_detail()` treat `local` as configured once `LOCAL_BASE_URL` is set (no real
key required). The pipeline, routes, and 503 gate are unchanged — the factory still
returns a LangChain `BaseChatModel`. Switching to a local model is a pure `.env` change.
**Files:**
- Modified: `app/core/llm.py` (docstring + `_build_local` + local branch in
  `get_chat_model` / `llm_is_configured` / `llm_config_detail`),
  `app/core/config.py` (`local_base_url`, `local_api_key`), `.env.example`
  (local provider section + LM Studio/Ollama/vLLM examples, Docker note),
  `architecture/{DIAGRAM,STRUCTURE}.md`.
- Added: `app/core/tests/{__init__.py,test_llm.py}` (gate + local-builder unit tests).
**Tests:** `pytest` green (16 passed, incl. 5 new `test_llm.py`); `ruff check` clean.
Builder verified to construct a `ChatOpenAI` without any network call; a live local
server was not exercised here (no LM Studio/Ollama running in this environment).

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
