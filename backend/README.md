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

4. **Run:**

   ```bash
   make run                # uvicorn app.main:app --reload
   ```

   Interactive docs at http://localhost:8000/docs

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
