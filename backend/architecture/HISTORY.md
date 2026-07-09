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

## 2026-07-10 — Demo analytics seed for the student "My progress" charts

**Author:** AI (Claude)
**Summary:** The overall progress charts read `session_analytics`, which is only
written on live session completion — so demo accounts had empty charts. Added a
backdated demo series: `seed._seed_session_analytics` creates, per student, a run
of completed `TutorSession`s (spaced 4 days apart, oldest→newest) each with a
short 2-line transcript and a `SessionAnalytics` snapshot following a rising
mastery curve, confidence that leads early then converges (over-confidence), and
early misconception categories. Also derives a `streak` for seeded
`StudentConceptState` rows so the effort-vs-mastery bubbles vary. Seeding is
**idempotent** (skips a student who already has analytics rows) and **gated**
behind `seed(..., with_analytics=True)` — on for the real entrypoint
(`python -m app.seed` / `make seed`), off for the test fixture whose assertions
count a fixed number of sessions.
**Files:** Modified `app/seed.py` (`ANALYTICS_SHAPE`, `MISCON_POOL`,
`ANALYTIC_TITLES`, `_analytics_series`, `_streak_for`, `_seed_session_analytics`,
`seed(with_analytics=...)`, `main`), `conftest.py` (thread `with_analytics`,
add `analytics_client` fixture), `app/features/tutor/tests/test_reads.py`
(integration test). **Tests:** full suite green (62 passed); verified end-to-end
by running the seed against in-memory SQLite (Maya 12 pts 0.30→0.85 across 2
subjects; Rohan 11 pts 0.15→0.30 with 5 misconceptions).

---

## 2026-07-10 — Per-topic student analytics endpoint (`GET /me/topics`)

**Author:** AI (Claude)
**Summary:** Added a student-facing, concept-grain analytics read so the student
dashboard can chart **per-topic** performance (the existing `/me/analytics` is
subject-grain only). `GET /me/topics` returns one `TopicAnalyticsPoint` per concept
the signed-in student has engaged with — `mastery`, `confidence`, `understanding`,
`attempts`, `streak`, `last_seen`, `next_review`, plus the concept's
`glyph`/`tone`/`difficulty_band` — ordered by concept position. The read
(`reads.get_topic_analytics`) is a student-scoped mirror of the teacher's
`list_student_topics` join (`concepts` × `student_concept_state`); no schema/model
changes were needed.
**Files:** Modified `app/features/tutor/{schemas,reads,routes}.py`
(`TopicAnalyticsPoint`/`TopicAnalyticsResponse`, `get_topic_analytics`,
`GET /me/topics`), `app/features/tutor/tests/test_reads.py` (two tests), and this
`architecture/{DIAGRAM,HISTORY}.md`.
**Tests:** `test_reads.py` green (8/8), incl. the two new `/me/topics` tests
(own concepts in position order; scoped to the signed-in student). Note: one
pre-existing uncommitted WIP test (`test_completing_a_session_writes_analytics`)
fails independently — it posts `subject_id="fractions"` while the seeded Fractions
subject id is `"1"`, so `subject_name` resolves to `None`; unrelated to this change.

---

## 2026-07-09 — Subject-aware graph state + learning analytics (subject vs mastery vs confidence)

**Author:** AI (Claude)
**Summary:** Two additions. (1) **Subject in state:** `ask_question` now fetches the
subject from the `subjects` table by the request's `subject_id`
(`fetch_subject_name`) and seeds `state["subject"]` in both the new-session and
existing-session branches, so every graph agent (diagnostic, misconception,
planner, hint, guard, evaluator) is scoped to the real subject instead of the
hardcoded `"Maths"` default. Unknown ids fall back gracefully. Note: `subject_id`
must be a catalog slug (`fractions`, `decimals`, `percentages`, `integers`,
`geometry`, `ratios`), not a numeric index. (2) **Learning analytics:** new
`session_analytics` table (one upserted row per session, keyed by `session_id`)
storing `student_id`, `session_id`, `subject_id`, `mastery`, `confidence`,
`misconception_category`. Written automatically when a session completes (enters
history mode) via `record_session_analytics`. New read `GET /me/analytics`
(`reads.get_analytics`) returns per-subject means (`by_subject`) plus the raw
per-session `points` — plot-ready for subject vs mastery vs confidence.
**Files:**

- Modified: `app/features/tutor/service.py` (`fetch_subject_name`,
  `record_session_analytics`, subject-in-state wiring, analytics write on
  completion), `app/features/tutor/models.py` (`SessionAnalytics`),
  `app/features/tutor/schemas.py` (`AnalyticsPoint`, `SubjectAnalytics`,
  `AnalyticsResponse`), `app/features/tutor/reads.py` (`get_analytics`),
  `app/features/tutor/routes.py` (`GET /me/analytics`),
  `app/features/tutor/tests/test_tutor.py` (subject-in-state + analytics tests).
  **Tests:** `make test` green (59 passed); analytics + subject-flow verified
  end-to-end against local PostgreSQL.

## 2026-07-09 — Subject ids are numeric (1..6) instead of slugs

**Author:** AI (Claude)
**Summary:** Changed subject ids from slugs (`fractions`, `decimals`, …) to
incremental numbers (`"1"`..`"6"`, catalog order). Concept ids are unchanged
(still `partition`, etc.); only `subjects.id` and the values that reference it
moved to numbers. Updated the seed (SUBJECTS ids, `concepts.subject_id`, the
demo sessions' `subject_id`, the escalation), the tutor default
(`subject_id or "1"`), and the catalog tests. Added an idempotent data migration
`app/migrate_subjects.py` (`make migrate-subjects`) that renames existing
subjects by creating the new numeric row, repointing `concepts.subject_id` (FK)
and `tutor_sessions.subject_id`, then deleting the old row — ran it on the live
Postgres (6 subjects renamed; concepts now under `1`, sessions repointed).
Frontend counterpart: static `SUBJECTS` ids → `1..6` and the two `"fractions"`
fallbacks → `"1"`.
**Files:** `app/seed.py`, `app/features/tutor/service.py`,
`app/features/catalog/tests/test_catalog.py`, `app/migrate_subjects.py` (new),
`Makefile`; frontend `data/subjects.ts`, `state/chatHelpers.ts`, `api/chat.ts`.
**Tests:** `make test` green; ruff clean; frontend `npm run check` green.
Migration verified on Postgres.

## 2026-07-09 — Fix /tutor/ask 500 (kind width) + restore frontend read routes after merge

**Author:** AI (Claude)
**Summary:** Two fixes. (1) `/tutor/ask` 500'd on Postgres with
`StringDataRightTruncationError`: `conversation_history.kind` was `VARCHAR(16)`
but now stores values like `diagnostic_question` (19 chars). `create_all` /
`ADD COLUMN IF NOT EXISTS` cannot widen an existing column, so `app/dbsync.py`
gained a `_WIDEN` step (`ALTER COLUMN … TYPE`) that idempotently widens `kind` to
`VARCHAR(32)` (runs on startup + `make migrate`). (2) A concurrent session's edit
had wiped the frontend-facing read routes from `tutor/routes.py` (only `/ask`
remained) and left a **duplicate `SessionSummary`** in `schemas.py` (the second
def shadowed the first, breaking `reads.py`). Restored `GET /tutor/sessions`
(Page), `/tutor/sessions/{id}`, `/tutor/sessions/{id}/messages`, `/me/profile`,
`/me/performance`; **kept** the other session's `/tutor/sessions/{id}/conversation`;
renamed the duplicate schema to `SessionIndexItem` (+ its `service.list_student_sessions`
usage). Adapted `test_sessions_list_and_conversation_isolation` to the reconciled
`Page` shape (`/tutor/sessions` is the rich chat rail; `/conversation` is the typed
transcript).
**Files:** `app/dbsync.py` (\_WIDEN), `app/features/tutor/routes.py` (restored routes),
`app/features/tutor/schemas.py` (rename), `app/features/tutor/service.py` (rename
usage), `app/features/tutor/tests/test_tutor.py`.
**Tests:** `make test` green (all passing); ruff clean. Widen verified on the live
Postgres (`kind` now width 32; the exact failing INSERT no longer truncates).

## 2026-07-09 — Session context for every agent, conversation API, unlimited hints

**Author:** AI (Claude)
**Summary:** Fixed context loss across agents. Each turn the service now rebuilds the
full session transcript from `conversation_history` (+ the current student message)
and passes it into the graph via `config.configurable.history`; `llm.run_agent` gained
`history` and `subject` params and prepends the transcript as chat messages (student →
Human, tutor → AI, labelled by event kind) before the agent's task. So every agent —
Diagnostic, Misconception, Planner, Hint, Guard, Evaluator — sees the whole
conversation. The **Evaluator** therefore judges the student's answer against the
**initial question** with all hints in context. A **subject guardrail** is appended to
every agent call at runtime (prompts unchanged) so agents refuse off-topic / role-change
input. The **3-hint cap was removed**: wrong answers loop back for a new hint
indefinitely; only student distress escalates to a teacher (router + evaluator +
escalation updated). Added a **conversation API**: `GET /tutor/sessions` and
`GET /tutor/sessions/{id}/conversation` return the typed transcript (question,
diagnostic_question/answer, hint, hint_answer, completed, escalation), backed by a new
nullable `conversation_history.kind` column (idempotent Postgres ALTER on startup).
**Files:**

- Modified: `graph/llm.py` (history + guardrail), all six LLM nodes (pass history/subject),
  `graph/nodes/evaluator.py` + `graph/router.py` + `graph/nodes/escalation.py` (unlimited
  hints, distress-only escalation), `models.py` (kind column), `main.py` (startup ALTER),
  `repository.py` (`get_conversation`, `list_sessions`), `service.py` (build/pass history,
  typed rows, conversation/session views), `schemas.py` (conversation schemas),
  `routes.py` (2 GET endpoints), `tests/test_tutor.py`, `architecture/DIAGRAM.md`.
  **Tests:** `make test` green (27 passing); ruff clean. Verified end-to-end that the
  transcript is prepended as messages and the subject guardrail + JSON schema hint are
  appended, against a stubbed subscription model.

## 2026-07-09 — Session context for every agent, conversation API, unlimited hints

**Author:** AI (Claude)
**Summary:** Fixed context loss across agents. Each turn the service now rebuilds the
full session transcript from `conversation_history` (+ the current student message)
and passes it into the graph via `config.configurable.history`; `llm.run_agent` gained
`history` and `subject` params and prepends the transcript as chat messages (student →
Human, tutor → AI, labelled by event kind) before the agent's task. So every agent —
Diagnostic, Misconception, Planner, Hint, Guard, Evaluator — sees the whole
conversation. The **Evaluator** therefore judges the student's answer against the
**initial question** with all hints in context. A **subject guardrail** is appended to
every agent call at runtime (prompts unchanged) so agents refuse off-topic / role-change
input. The **3-hint cap was removed**: wrong answers loop back for a new hint
indefinitely; only student distress escalates to a teacher (router + evaluator +
escalation updated). Added a **conversation API**: `GET /tutor/sessions` and
`GET /tutor/sessions/{id}/conversation` return the typed transcript (question,
diagnostic_question/answer, hint, hint_answer, completed, escalation), backed by a new
nullable `conversation_history.kind` column (idempotent Postgres ALTER on startup).
**Files:**

- Modified: `graph/llm.py` (history + guardrail), all six LLM nodes (pass history/subject),
  `graph/nodes/evaluator.py` + `graph/router.py` + `graph/nodes/escalation.py` (unlimited
  hints, distress-only escalation), `models.py` (kind column), `main.py` (startup ALTER),
  `repository.py` (`get_conversation`, `list_sessions`), `service.py` (build/pass history,
  typed rows, conversation/session views), `schemas.py` (conversation schemas),
  `routes.py` (2 GET endpoints), `tests/test_tutor.py`, `architecture/DIAGRAM.md`.
  **Tests:** `make test` green (27 passing); ruff clean. Verified end-to-end that the
  transcript is prepended as messages and the subject guardrail + JSON schema hint are
  appended, against a stubbed subscription model.

## 2026-07-09 — UI-driven query APIs: catalog, teacher dashboard, sessions/history, roles

**Author:** AI (Claude)
**Summary:** Added the full read/write API surface the frontend needs, all with a
shared **pagination + search + sort** contract (`app/core/query.py`: `Page[T]`
envelope `{items,total,limit,offset,has_more}`, `list_params` dep, `apply_search`
ILIKE, `apply_sort` with a `-field` descending token validated against a per-route
allowlist → clean 422). New/changed:

- **Auth/roles:** added `role` (student|teacher) to the user model; `register`
  now auto-generates `student_id` when the client omits it (the sign-up form only
  sends name/email/password/role) and accepts `role`; `require_teacher` guard;
  richer `GET /auth/me` (split name + initials); `POST /auth/logout`.
- **catalog feature** (new): `subjects`, `concepts` tables + `GET/POST /subjects`,
  `GET/PATCH /subjects/{id}`, `GET/POST /topics`, `GET/PATCH /topics/{id}` (subjects
  carry per-student `progress`).
- **tutor reads** (`reads.py`): `GET /tutor/sessions` (chat list, status/subject
  filter, recency sort), `GET /tutor/sessions/{id}`, `GET /tutor/sessions/{id}/messages`
  (conversation history; role→sender maps user→maya/assistant→tutor; owner-or-teacher
  guarded), `GET /me/profile`, `GET /me/performance` (the student performance record).
- **teacher feature** (new): `GET /teacher/overview`, `/students` (roster; tone/status
  filter, name/email search, improvement/name sort), `/students/{id}` (+`/topics`,
  `/evidence`), `/topics` (+aggregates), `/topics/{id}` (+`/students`),
  `/escalations` (filter status/trigger) + `POST /escalations/{id}/resolve`,
  `POST /simulate-day`.
- **Models:** new `StudentConceptState` (per-student×concept mastery — the grain the
  teacher surface needs), `Misconception`, plus columns on `student_profile`
  (roster/performance display fields), `tutor_sessions` (subject_id/title/hint_rung/
  leak_checks), `conversation_history` (kind/payload), `teacher_escalations`
  (trigger/status/excerpt/resolved_at/teacher_notes).
- **Seed:** `app/seed.py` (`make seed`, idempotent) mirrors the frontend mock data
  (6 subjects, 6 fraction concepts, Maya/Priya/Leo/Sam/Rohan + teacher, sessions,
  one open escalation). Demo password `password123`.
  **Files:** `app/core/{query,display}.py`; `app/features/catalog/**`;
  `app/features/teacher/**`; `app/features/tutor/{models,schemas,service,routes,reads}.py`;
  `app/features/auth/{models,schemas,service,dependencies,routes}.py`; `app/seed.py`;
  `app/api/router.py`; `app/main.py`; `conftest.py`; `Makefile`; `pyproject.toml`.
  **Tests:** `make test` green (55 passed — new catalog/teacher/tutor-reads/auth-role
  suites + existing); ruff clean. Live end-to-end verified against SQLite through the
  Next.js BFF (login→cookie→proxy), incl. role guard 403 and cross-student 404.

## 2026-07-09 — Switch auth to HTTP Bearer (fix Swagger "Authorize")

**Author:** AI (Claude)
**Summary:** Replaced the `OAuth2PasswordBearer(tokenUrl="/auth/login")` scheme with
`HTTPBearer`. The OAuth2 password flow made Swagger POST a form (`username`/`password`)
to `/auth/login`, but that route reads a JSON body, so "Authorize" always failed with 422. With `HTTPBearer`, Swagger's Authorize dialog is a single field: log in via
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

## 2026-07-09 — Agents via `create_agent`, JSON-restricted output, RAG removed

**Author:** AI (Claude)
**Summary:** Each LLM-backed agent is now built with LangChain's `create_agent`
and restricted to emit JSON matching a per-agent Pydantic schema. A new
`graph/llm.run_agent(stage, schema, system, user)` seam compiles/caches one
`create_agent` per system prompt and enforces the schema: it uses `response_format`
when the chat model supports structured output (API-key providers), and otherwise
(the dev-only Claude subscription model, which cannot bind tools) appends the schema
to the prompt at call time and validates the reply back into it. The old
`llm.complete()` text seam was removed. Prompts were extracted verbatim into a new
`graph/prompts/` package (one module per agent, SYSTEM + USER templates) — wording
unchanged. The **RAG node/stub was removed** entirely (node, graph wiring, router
branch, `docs` state field, evaluator's `docs` clearing, and the response `sources`
population).
**Files:**

- Added: `app/features/tutor/graph/prompts/{__init__,diagnostic,misconception,planner,hint,guard,evaluator}.py`,
  `app/features/tutor/graph/schemas.py`.
- Modified: `graph/llm.py` (new `run_agent`, removed `complete`), all six LLM nodes
  (`diagnostic,misconception,planner,hint,guard,evaluator`), `graph/graph.py`,
  `graph/router.py`, `graph/state.py` (dropped `docs`), `graph/trace.py` (docstring),
  `service.py` (dropped `sources` population), `tests/test_tutor.py` (mock the
  `run_agent` seam), `pyproject.toml` (E501 ignore for `graph/prompts/*`).
- Removed: `graph/nodes/rag.py`.
  **Tests:** `make test` green (24 passing); ruff clean. Verified the subscription
  schema-hint path end-to-end (noisy markdown/extra-key reply → validated restricted
  JSON) and that the graph compiles without the `rag` node.

## 2026-07-08 — Interactive Diagnostic phase (doctor-style probing)

**Author:** AI (Claude)
**Summary:** Turned the Diagnostic agent into an interactive, multi-turn probing phase
that runs BEFORE any teaching. Like a doctor, it asks the student `DIAGNOSTIC_ROUNDS`
(=3) short probing questions, ONE per turn, recording each answer; after the 3rd it
consolidates the Q&A into observations. The Misconception agent now uses that Q&A to
categorize the difficulty into one of: `unsure_of_concept`, `misunderstanding_concept`,
`missing_prerequisite`, `none` (was a free-form error label). Added a session `awaiting`
type (`diagnostic` | `hint` | None) and an `incoming` turn kind so a message is routed
as a diagnostic answer, a hint answer, or a new question. `/tutor/ask` can now return
`action: "diagnostic"` (the probing question) with a `(Diagnostic n/3)` prefix.
New flow: profile → [diagnostic ×3 interactive] → misconception → planner → rag →
hint → guard → (await) → evaluator → …
**Files:** `graph/state.py` (diagnostic_qa/pending/diag_asked_this_turn/incoming;
awaiting now str), `graph/router.py` (diagnostic phase), `graph/nodes/diagnostic.py`
(interactive loop), `graph/nodes/misconception.py` (3 categories), `service.py`
(awaiting types), `tests/test_tutor.py` (rewritten flows). Removed a stray debug
`print(session.state)`.
**Tests:** `pytest` — 24 passed; ruff clean; live-demoed the 3-probe → hint → complete
sequence. NOTE: `architecture/tutor_graph_flow.pdf` and DIAGRAM Flow A are now outdated
(no diagnostic loop) — regenerate when convenient.

## 2026-07-08 — Persist profile on EVERY answer (not just correct)

**Author:** AI (Claude)
**Summary:** The long-term profile (mastery, confidence, evidence_count,
misconceptions) was only saved by the `memory` node, which runs solely on a correct
answer — so wrong-only or escalated sessions never updated the profile. Centralized
the update in `repository.apply_evaluation()` and call it from the `evaluator` on
**every** answer (correct or wrong): confidence = 0.8*old+0.2*current, mastery =
0.8*old+0.2*(1 if correct else 0) clamped, evidence_count++, misconceptions
consolidated. `memory` node now just finalizes the success message (no double-write).
Verified: a wrong answer now decays mastery 0.3→0.24 and updates confidence, and the
next session fetches the new values. Also fixed a blocking `F841` (removed an unused
`docs_text` after reference material was commented out of the hint prompt).
**Files:** `app/features/tutor/repository.py` (+apply_evaluation),
`app/features/tutor/graph/nodes/evaluator.py` (call it), `memory.py` (simplified),
`hint.py` (lint).
**Tests:** `pytest` — 23 passed; ruff clean; verified correct- and wrong-answer
profile persistence + next-session fetch.

## 2026-07-08 — Per-agent input/output dump (DEBUG_AGENT_IO)

**Author:** AI (Claude)
**Summary:** Added a lightweight, in-process capture of each agent's LLM input
(system+user prompt) and output, independent of LangSmith. `graph/trace.py` uses a
ContextVar so concurrent requests don't mix; `graph/llm.complete()` records every
call; `service.ask_question()` starts a capture, builds a `{agent: {input, output}}`
dict, and — when `DEBUG_AGENT_IO=true` — prints it to the console AND returns it in
the `/tutor/ask` response (`AskResponse.agents`). Repeated agents in a turn become a
list. Dev-only (verbose, exposes prompts); default false, enabled in local `.env`.
**Files:** Added `app/features/tutor/graph/trace.py`,
`app/features/tutor/tests/test_trace.py`. Modified `app/core/config.py`
(`debug_agent_io`), `app/features/tutor/graph/llm.py` (record), `service.py`
(capture+print+attach), `schemas.py` (`agents` field), `.env.example`, local `.env`.
**Tests:** `pytest` — 23 passed (3 new trace tests); ruff clean; live-demoed the
printed dict + returned `agents`.

## 2026-07-08 — Fix LangSmith not tracing (auto-enable on key) + live verify

**Author:** AI (Claude)
**Summary:** Tracing wasn't working because `.env` had `LANGSMITH_TRACING=false`.
Changed the flag to tri-state (`bool | None`): a present `LANGSMITH_API_KEY` now
**auto-enables** tracing (the requested behavior); `LANGSMITH_TRACING=false` forces it
off, `=true` requires a key. Set `LANGSMITH_TRACING=true` in the local `.env`; made
`.env.example` safe (blank key = off, so copiers don't spam a bogus key). **Live-verified**:
ran the real graph with tracing on + the real key (fake chat model, no LLM cost) and
confirmed LangSmith accepted the trace — runs appear as `agent:<stage>` (llm) under a
`tutor-session:<id>` parent, each with its prompt (system+user) as input and the reply
as output.
**Files:** `app/core/config.py` (tri-state), `app/core/observability.py` (auto-enable),
`app/core/tests/test_observability.py`, `.env.example`, local `.env`.
**Tests:** `pytest` — 20 passed; ruff clean; live LangSmith trace confirmed.

## 2026-07-08 — Makefile uses venv; scrub leaked key from .env.example

**Author:** AI (Claude)
**Summary:** `make run`/`test`/`lint` were resolving bare `uvicorn`/`pytest` from
PATH, which could hit a system Python missing deps (`ModuleNotFoundError:
pydantic_settings`). Rewrote the Makefile to run everything through `$(VENV)/bin/python
-m ...` (override with `make VENV=… run`), added a `venv` target. Also replaced a
**real LangSmith API key** that had been pasted into the git-tracked `.env.example`
with a placeholder — real secrets belong only in the gitignored `.env`. **Action:
rotate that LangSmith key.**
**Files:** `backend/Makefile`, `backend/.env.example`.
**Tests:** `pytest` — 19 passed; app boots via `.venv/bin/python -m uvicorn`.

## 2026-07-08 — Observability: LangSmith tracing (per-agent)

**Author:** AI (Claude)
**Summary:** Added opt-in LangSmith tracing so every tutor run is inspectable —
each session appears as a `tutor-session:<id>` trace, each agent's LLM call as
`agent:<stage>` with model/provider metadata and full input/output, plus latency
and token usage. Env-driven (`LANGSMITH_TRACING`, `LANGSMITH_API_KEY`,
`LANGSMITH_PROJECT`, `LANGSMITH_ENDPOINT`); off by default (zero overhead when off).
`core/observability.py::configure_observability()` sets the LangSmith env at startup;
`graph/llm.py` tags each call by agent; `service.py` attaches session metadata
(student_id, session_id) to the graph run. Because the tutor is built on LangChain +
LangGraph, tracing needs no per-node instrumentation.
**Files:** Added `app/core/observability.py`, `app/core/tests/test_observability.py`.
Modified `app/core/config.py` (LangSmith settings), `app/main.py` (call at startup),
`app/features/tutor/graph/llm.py` (per-agent run name/tags/metadata),
`app/features/tutor/service.py` (session metadata), `requirements.txt` (+langsmith),
`.env.example`, `architecture/{STRUCTURE,DIAGRAM}.md`.
**Tests:** `pytest` — 19 passed (3 new observability tests); ruff clean.

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
