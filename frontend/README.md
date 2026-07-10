# Adaptive AI Tutor — Frontend

The student + teacher experience for the Adaptive AI Tutor, built with
**Next.js 16** (App Router, React 19, TypeScript 5, Tailwind CSS 4).

The browser only ever calls same-origin `/api/*` routes; a **BFF proxy**
(`src/app/api/*`) attaches the session JWT from an httpOnly cookie and forwards
to the FastAPI backend, so the token is never exposed to client JS.

> **Before changing code, read [`RULES.md`](./RULES.md)** — the one-page summary
> of the codebase, its guardrails, and the required workflow (detailed docs live
> under [`docs/`](./docs)). Note this is Next.js **16**, which has breaking
> changes vs. earlier versions.

## Prerequisites

The backend must be running and **seeded** so there are accounts to log in with
and data to display — see [`../backend/README.md`](../backend/README.md)
(`make seed`).

## Getting started

```bash
npm install
cp .env.example .env.local     # API_BASE_URL defaults to http://localhost:8000
npm run dev                    # http://localhost:3000
```

`.env.local` points the app at the backend:

- `API_BASE_URL` — backend base URL used by the server-side BFF routes.
- `NEXT_PUBLIC_API_BASE_URL` — backend base URL as seen by the browser.

Both default to `http://localhost:8000` when unset.

## Demo credentials

All seeded accounts use the password **`password123`** (full list in the
[root README](../README.md)). The two you'll want most:

| Role    | Email                  | What to explore                                        |
| ------- | ---------------------- | ------------------------------------------------------ |
| Student | `maya.chen@school.edu` | Chat with Mira, then account menu → **My progress**    |
| Teacher | `teacher@school.edu`   | Roster, per-student overall-performance graphs, topics |

## Commands

```bash
npm run dev            # start the dev server
npm run build          # production build (fails on type errors)
npm run check          # typecheck + lint + format:check (run before pushing)
npm run lint           # ESLint (quality + security rules)
npm run format         # Prettier write
```

## Structure

- `src/app` — App Router entry + the BFF route handlers (`api/auth`, `api/backend`).
- `src/features/tutor` — the Mira app shell, student area (home, chat, **analytics**),
  and teacher area (roster, topics, student drill-down).
- `src/components` — reusable UI primitives (see `src/components/README.md`).
- `src/lib`, `src/hooks` — shared helpers (API client, tones, responsive, toast).
