# Adaptive AI Tutor — Backend

FastAPI backend with JWT auth over PostgreSQL and an **agentic tutoring pipeline**
built on **LangGraph + LangChain** using Claude (`claude-opus-4-8`).

The project uses a **feature-based architecture**. Before changing code, read the
[`architecture/`](./architecture/) folder — it is the source of truth (structure,
diagrams, history, and the required workflow).

## Structure (summary)

```
app/
├── main.py                 # FastAPI app + startup
├── core/                   # config, database, security (JWT + hashing)
├── api/router.py           # route index (aggregates feature routers)
└── features/
    ├── auth/               # models, schemas, service, dependencies, routes, tests
    └── tutor/              # models, schemas, pipeline (LangGraph), service, routes, tests
```

Full layout and conventions: [`architecture/STRUCTURE.md`](./architecture/STRUCTURE.md).

## Setup

1. **Create the database** (PostgreSQL must be running):

   ```bash
   createdb adaptive_tutor
   ```

2. **Install dependencies:**

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   make install-dev        # or: pip install -r requirements-dev.txt
   ```

3. **Configure environment:**

   ```bash
   cp .env.example .env
   # edit .env — set DATABASE_URL, JWT_SECRET, and ANTHROPIC_API_KEY
   ```

4. **Seed the demo data (recommended):**

   ```bash
   make migrate            # create tables + add any new columns (idempotent)
   make seed               # demo teacher + students, topics, and analytics
   ```

5. **Run:**

   ```bash
   make run                # uvicorn app.main:app --reload
   ```

   Interactive docs at http://localhost:8000/docs

## Demo credentials

`make seed` creates the accounts below (idempotent — safe to re-run). **Every
account uses the password `password123`.** Log in via `POST /auth/login` (or the
frontend login screen).

| Role    | Email                  | Name        | Notes                                        |
| ------- | ---------------------- | ----------- | -------------------------------------------- |
| Teacher | `teacher@school.edu`   | Ms. Alvarez | Class dashboard: roster, topics, escalations |
| Student | `maya.chen@school.edu` | Maya Chen   | **Richest demo data** — best for the charts  |
| Student | `priya@school.edu`     | Priya Nair  | Steady                                       |
| Student | `leo@school.edu`       | Leo Meyer   | Steady                                       |
| Student | `sam@school.edu`       | Sam Ortiz   | Needs watching                               |
| Student | `rohan@school.edu`     | Rohan Das   | At risk (open escalation)                    |

The seed also backfills each student's **learning-analytics series** (the
mastery / confidence / misconfidence trend, misconceptions, and per-subject
means) so the `/me/analytics`, `/me/topics`, and teacher dashboards are populated
out of the box.

## Testing

```bash
make test                  # pytest — uses in-memory SQLite; no Postgres or API key needed
```

## Linting / pre-commit

```bash
make hooks                 # install the git pre-commit hook (ruff)
make lint                  # ruff check .
```

## API

| Method | Path             | Auth   | Description                              |
| ------ | ---------------- | ------ | ---------------------------------------- |
| POST   | `/auth/register` | —      | Register a student (name, id, email, pw) |
| POST   | `/auth/login`    | —      | Login with email + password → JWT        |
| GET    | `/auth/me`       | Bearer | Current student                          |
| POST   | `/tutor/ask`     | Bearer | Run the agentic tutoring pipeline        |
| GET    | `/health`        | —      | Health check                             |

### Example

```bash
curl -X POST localhost:8000/auth/register -H 'Content-Type: application/json' -d '{
  "student_name": "Ada Lovelace", "student_id": "S001",
  "email": "ada@example.com", "password": "secret123"
}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login -H 'Content-Type: application/json' \
  -d '{"email":"ada@example.com","password":"secret123"}' | python3 -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

curl -X POST localhost:8000/tutor/ask \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"question": "Why is the sky blue?"}'
```

The `/tutor/ask` response contains `analysis`, `answer`, and `followups`
(three practice questions) produced by the LangGraph pipeline, and the
interaction is logged to the `question_logs` table.
