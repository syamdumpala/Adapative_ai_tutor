# Adaptive AI Tutor

An adaptive, multi-agent AI tutor that guides students with Socratic **hints
(never straight answers)**, tracks per-topic mastery / confidence / misconceptions,
and gives both students and teachers **live performance dashboards**.

- **[`backend/`](./backend)** — FastAPI + PostgreSQL, JWT auth, and a
  LangGraph / LangChain multi-agent tutoring graph on Claude. See
  [backend/README.md](./backend/README.md).
- **[`frontend/`](./frontend)** — Next.js 16 (App Router, React 19, Tailwind 4)
  student + teacher experience, talking to the backend through a same-origin
  BFF proxy so the JWT never reaches browser JS. See
  [frontend/README.md](./frontend/README.md).

## Quick start

Run the backend and frontend in two terminals.

### 1. Backend — http://localhost:8000

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
make install-dev
cp .env.example .env          # set DATABASE_URL, JWT_SECRET, ANTHROPIC_API_KEY
createdb adaptive_tutor       # PostgreSQL must be running
make migrate                  # create tables + add any new columns (idempotent)
make seed                     # load the demo users + analytics (credentials below)
make run                      # docs at http://localhost:8000/docs
```

> `ANTHROPIC_API_KEY` is only needed to run **live tutoring** (the chat). The
> seeded dashboards and analytics work without it.

### 2. Frontend — http://localhost:3000

```bash
cd frontend
npm install
cp .env.example .env.local    # API_BASE_URL defaults to http://localhost:8000
npm run dev
```

Open http://localhost:3000 and log in with one of the demo accounts below.

## Demo credentials

Created by `make seed` (backend). **Every account's password is `password123`.**

| Role    | Email                  | Name        | Notes                                        |
| ------- | ---------------------- | ----------- | -------------------------------------------- |
| Teacher | `teacher@school.edu`   | Ms. Alvarez | Class dashboard: roster, topics, escalations |
| Student | `maya.chen@school.edu` | Maya Chen   | **Richest demo data** — best for the charts  |
| Student | `priya@school.edu`     | Priya Nair  | Steady                                       |
| Student | `leo@school.edu`       | Leo Meyer   | Steady                                       |
| Student | `sam@school.edu`       | Sam Ortiz   | Needs watching                               |
| Student | `rohan@school.edu`     | Rohan Das   | At risk (has an open escalation)             |

> **Tip:** log in as **`maya.chen@school.edu`** to see the student **"My progress"**
> charts fully populated, and as **`teacher@school.edu`** to see the class roster
> plus each student's overall-performance graphs.

## What to try

- **Student** — pick a topic on the home screen and chat; Mira guides you with
  hints. Open the account menu → **My progress** for the overall + per-topic
  performance graphs (mastery, confidence, misconfidence, misconceptions, effort,
  review-due). Live tutoring moves these in real time.
- **Teacher** — open a student to see their overall-performance graphs, or a
  topic to see class-wide outcomes; work the escalation queue.

## Documentation

Every reference doc is linked below — jump straight to what you need. The tables
say what's inside each file.

### Product & context

| Document                                                             | What's inside                                                                                                                                     |
| -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| [PRD.md](./PRD.md)                                                   | Product requirements: personas, the LangGraph architecture, data schema, guardrails, tests, and the demo script (PDF copy: [PRD.pdf](./PRD.pdf)). |
| [Hackathon_Problem_Statement.pdf](./Hackathon_Problem_Statement.pdf) | The original hackathon challenge brief this project answers.                                                                                      |
| [docs/LOCAL_LLM_SETUP.md](./docs/LOCAL_LLM_SETUP.md)                 | Run the tutor for free against the DSLAB Ollama LLM — SSH tunnel, env vars, model list, and troubleshooting.                                      |

### Backend (`backend/`)

| Document                                                                         | What's inside                                                                                                       |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| [backend/README.md](./backend/README.md)                                         | Setup, run, testing, **demo credentials**, and the API reference for the FastAPI backend.                           |
| [architecture/README.md](./backend/architecture/README.md)                       | Index of the backend "source of truth" folder and the read-before / update-after rule.                              |
| [architecture/STRUCTURE.md](./backend/architecture/STRUCTURE.md)                 | Folder tree, naming/layering conventions, the full REST endpoint table, and the DB table schemas.                   |
| [architecture/DIAGRAM.md](./backend/architecture/DIAGRAM.md)                     | Mermaid diagrams: component map, `/tutor/ask` request lifecycle, the LangGraph agent flow, sessions, and analytics. |
| [architecture/WORKFLOW.md](./backend/architecture/WORKFLOW.md)                   | The mandatory 7-step process for adding/changing a feature (read → build → test → document → commit).               |
| [architecture/tutor_graph_flow.pdf](./backend/architecture/tutor_graph_flow.pdf) | Visual diagram of the multi-agent tutoring graph.                                                                   |
| [backend/CLAUDE.md](./backend/CLAUDE.md)                                         | Working rules for contributors/AI in the backend (feature layout, required tests/docs, commands).                   |

### Frontend (`frontend/`)

| Document                                                                    | What's inside                                                                                                           |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | --- |
| [frontend/README.md](./frontend/README.md)                                  | Setup, the BFF-proxy architecture, prerequisites, **demo credentials**, commands, and structure.                        |
| [frontend/RULES.md](./frontend/RULES.md)                                    | One-page codebase summary + guardrails (ESLint / security / TypeScript), the docs workflow, and the definition of done. |
| [docs/README.md](./frontend/docs/README.md)                                 | Index of the frontend docs folders and the "code and docs land together" workflow.                                      |
| [docs/architecture/STRUCTURE.md](./frontend/docs/architecture/STRUCTURE.md) | Directory layout, conventions, enforced ESLint/TS limits, tooling, and the pre-commit hook.                             |
| [docs/architecture/DIAGRAM.md](./frontend/docs/architecture/DIAGRAM.md)     | Mermaid diagrams: App Router rendering, request/response with CSP, and the commit-time checks.                          |
| [docs/modules/MODULES.md](./frontend/docs/modules/MODULES.md)               | Per-module registry of the app shells, component library, and tutor/auth features.                                      |
| [docs/security/SECURITY.md](./frontend/docs/security/SECURITY.md)           | Security controls: HTTP headers/CSP, lint rules, secrets/env, auth guidance, and a pre-ship checklist.                  |     |
| [src/components/README.md](./frontend/src/components/README.md)             | Catalog of reusable UI primitives — props tables, examples, and design-token rules.                                     |
| [frontend/AGENTS.md](./frontend/AGENTS.md)                                  | Next.js-16 caveats and contributor guardrails (start at `RULES.md`).                                                    |
