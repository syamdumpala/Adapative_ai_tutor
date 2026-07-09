# Frontend Structure & Conventions

## Directory layout

```
frontend/
├── src/
│   └── app/                 # Next.js App Router (routes, layouts, pages)
│       ├── layout.tsx       # Root layout (html/body, fonts, metadata)
│       ├── page.tsx         # Home route
│       └── globals.css      # Global styles (Tailwind 4)
├── public/                  # Static assets served as-is
├── docs/                    # Living documentation (source of truth)
├── RULES.md                 # One-page rules + codebase summary (read first)
├── AGENTS.md / CLAUDE.md    # Agent guidance (Next 16 caveats)
├── eslint.config.mjs        # ESLint flat config (quality + security)
├── .prettierrc.json         # Prettier config
├── .prettierignore          # Files Prettier skips
├── tsconfig.json            # TypeScript config (strict + extra flags)
├── next.config.ts           # Next config (security headers + CSP)
└── .env.example             # Env template + secret-handling rules

(the Git pre-commit hook lives at the REPO ROOT: ../.husky/pre-commit)
```

## Recommended conventions as the app grows

Keep the App Router thin and push logic into typed modules. A pragmatic layout:

```
src/
├── app/                     # routing only: layouts, pages, route handlers
├── components/              # reusable, presentational React components
├── features/<feature>/      # feature-scoped UI + hooks + logic + types
├── lib/                     # framework-agnostic helpers (api client, utils)
├── hooks/                   # shared React hooks
└── types/                   # shared TypeScript types
```

Guidelines:

- **Server Components by default.** Add `"use client"` only when you need
  interactivity/state/effects. Keep client components small and leaf-level.
- **Keep secrets server-side.** Fetch from the backend in Server Components or
  Route Handlers; never expose backend secrets to the client (see
  [`../security/SECURITY.md`](../security/SECURITY.md)).
- **Co-locate** a feature's components, hooks, and types under
  `features/<feature>/`.
- **Naming:** components `PascalCase.tsx`; hooks `useThing.ts`; utilities and
  other files `kebab-case.ts`. Path alias `@/*` maps to `src/*`.

> This is Next.js **16** — verify APIs against `node_modules/next/dist/docs/`
> before use. Notably, middleware is now `proxy.ts` and `next lint` was removed.

## Code-quality limits (enforced)

Configured in [`../../eslint.config.mjs`](../../eslint.config.mjs), applied to
`src/**`. Tier: **Balanced**.

| Rule                     | Limit | Why                                                    |
| ------------------------ | ----- | ------------------------------------------------------ |
| `max-lines`              | 200   | Files over ~200 lines usually do too much; split them. |
| `max-lines-per-function` | 50    | Long functions/components are hard to test & read.     |
| `complexity`             | 10    | Caps branching; high complexity hides bugs.            |
| `max-depth`              | 4     | Deep nesting → extract functions/early returns.        |
| `max-params`             | 4     | Many params → pass an options object.                  |
| `max-nested-callbacks`   | 3     | Prefer async/await over callback pyramids.             |
| `max-statements`         | 20    | (warning) nudge toward smaller functions.              |

Blanks and comments are **not** counted toward line limits.

### When you hit a limit

Prefer **decomposition** over raising the limit:

- Extract sub-components / helper functions / custom hooks.
- Split a large file along responsibility lines.

If a limit is genuinely wrong for this codebase, change it deliberately in
`eslint.config.mjs`, then document the change in
[`../history/HISTORY.md`](../history/HISTORY.md) with the reason.

## TypeScript strictness

`tsconfig.json` enables `strict` plus: `noUncheckedIndexedAccess`,
`noImplicitOverride`, `noFallthroughCasesInSwitch`, `noUnusedLocals`,
`noUnusedParameters`, `noImplicitReturns`, `forceConsistentCasingInFileNames`,
and `allowUnreachableCode: false`. Run `npm run typecheck`.

## Tooling & commands

| Command                | What it does                                       |
| ---------------------- | -------------------------------------------------- |
| `npm run dev`          | Dev server                                         |
| `npm run build`        | Production build (fails on type errors)            |
| `npm run lint`         | ESLint (quality + security)                        |
| `npm run lint:fix`     | ESLint autofix                                     |
| `npm run format`       | Prettier write                                     |
| `npm run format:check` | Prettier check                                     |
| `npm run typecheck`    | `tsc --noEmit`                                     |
| `npm run check`        | typecheck + lint + format:check (pre-push gate)    |

## Pre-commit hook (repo root)

Husky is installed at the **repo root** (root `package.json` + `npm install`)
and owns the single Git hook (`core.hooksPath` → `.husky/_`). The orchestrator
`../.husky/pre-commit` is **path-gated** — it inspects staged paths and runs
only the relevant side:

1. If `frontend/` files are staged → `cd frontend`, run `lint-staged` (ESLint
   `--fix` + Prettier on staged files) then `npm run typecheck`.
2. If `backend/` files are staged → run the backend's `pre-commit` framework
   (`backend/.venv/bin/pre-commit run --config .pre-commit-config.yaml`), which
   self-scopes to `backend/`. Falls back to a PATH `pre-commit`, or warns and
   skips if neither is available. **This hook never edits backend code.**

A commit touching both sides runs both blocks; either failing aborts the commit.

> **Monorepo notes**
>
> - The root owns the hook so a commit from anywhere is gated correctly,
>   regardless of which side you're working on.
> - Because Husky sets `core.hooksPath`, the backend's `make hooks`
>   (`pre-commit install`) is **no longer needed** — pre-commit would refuse to
>   install while `core.hooksPath` is set. The root hook already invokes the
>   backend checks. `make -C backend lint/format/test` still work manually.
> - Fresh clone setup: `npm install` at the repo root (installs Husky), plus the
>   usual `frontend` (`npm install`) and `backend` (`make install-dev`) setup.
