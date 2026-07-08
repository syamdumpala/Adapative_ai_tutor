# Frontend Rules & Codebase Summary

> **Read this file first.** It is the single-page summary of the frontend
> codebase, its guardrails, and the mandatory workflow. Every rule here links to
> the detailed documentation under [`docs/`](./docs/README.md).

---

## 1. What this app is

A [Next.js](https://nextjs.org) **16** App Router application (React 19,
TypeScript 5, Tailwind CSS 4) — the frontend for the Adaptive AI Tutor.

- Source lives in [`src/`](./src) (App Router under `src/app`).
- Package manager: **npm** (`package-lock.json` is the source of truth).
- The backend is a sibling folder (`../backend`) and is **out of scope** for
  frontend work — do not modify it.

> ⚠️ This is Next.js **16**, which has breaking changes vs. earlier versions
> (e.g. middleware is now `proxy.ts`, `next lint` is removed). Before writing
> framework code, read the relevant guide in
> `node_modules/next/dist/docs/`. See [`AGENTS.md`](./AGENTS.md).

## 2. The golden rule: docs are the source of truth

`docs/` is a living record. **After every change you MUST:**

1. Append an entry to [`docs/history/HISTORY.md`](./docs/history/HISTORY.md)
   (always — this is non-negotiable and append-only).
2. Update [`docs/status/STATUS.md`](./docs/status/STATUS.md) to reflect the new
   current state.
3. If the layout/flow changed → update
   [`docs/architecture/`](./docs/architecture/README.md).
4. If a security control changed → update
   [`docs/security/SECURITY.md`](./docs/security/SECURITY.md).
5. If a feature/module was added or changed → update
   [`docs/modules/MODULES.md`](./docs/modules/MODULES.md).

See the docs index: [`docs/README.md`](./docs/README.md).

## 3. Code-quality guardrails (enforced by ESLint)

Configured in [`eslint.config.mjs`](./eslint.config.mjs). Tier: **Balanced**.

| Rule                     | Limit | Meaning                                      |
| ------------------------ | ----- | -------------------------------------------- |
| `max-lines`              | 300   | Max lines per file (blanks/comments skipped) |
| `max-lines-per-function` | 50    | Max lines per function                       |
| `complexity`             | 10    | Max cyclomatic complexity                    |
| `max-depth`              | 4     | Max nested block depth                       |
| `max-params`             | 4     | Max function parameters                      |
| `max-nested-callbacks`   | 3     | Max nested callbacks                         |
| `max-statements`         | 20    | Statements per function (warning)            |

Plus correctness rules: `eqeqeq`, `no-var`, `prefer-const`, `no-eval`,
`no-implied-eval`, `no-new-func`, `no-script-url`, `no-param-reassign`,
`no-alert`, and `no-console` (warns; `console.warn`/`console.error` allowed).

**Hit a limit?** Decompose the file/function — don't raise the limit
casually. Rationale and how to tune: [`docs/architecture/STRUCTURE.md`](./docs/architecture/STRUCTURE.md).

## 4. Security guardrails

Detailed in [`docs/security/SECURITY.md`](./docs/security/SECURITY.md).

- **HTTP security headers + CSP** on every response — [`next.config.ts`](./next.config.ts).
- **Security lint**: `eslint-plugin-security` and `eslint-plugin-no-unsanitized`
  (blocks `innerHTML`/unsanitized DOM sinks).
- **Secrets**: never hardcode secrets; never put them behind `NEXT_PUBLIC_`
  (that prefix ships to the browser). Template: [`.env.example`](./.env.example).
- **Type safety**: strict TypeScript with extra strictness flags
  ([`tsconfig.json`](./tsconfig.json)).

## 5. Type safety

`tsconfig.json` runs `strict` plus `noUncheckedIndexedAccess`,
`noImplicitOverride`, `noFallthroughCasesInSwitch`, `noUnusedLocals`,
`noUnusedParameters`, `noImplicitReturns`, and `allowUnreachableCode: false`.
`npm run typecheck` must be green.

## 6. Pre-commit checks (root Husky orchestrator)

Husky lives at the **repo root** ([`../.husky/pre-commit`](../.husky/pre-commit))
and owns the single Git hook for the whole monorepo. It is **path-gated** — it
runs only the checks for the side(s) your commit touches:

- **frontend/** staged → `lint-staged` (ESLint `--fix` + Prettier) +
  `npm run typecheck`.
- **backend/** staged → the backend's own `pre-commit` framework (ruff, etc.)
  via `backend/.venv/bin/pre-commit`. This hook **never edits backend code**.

If any check fails, the commit is aborted. On a fresh clone, run `npm install`
at the **repo root** once to install the hook. Details:
[`docs/architecture/STRUCTURE.md`](./docs/architecture/STRUCTURE.md).

## 7. Commands

```bash
npm run dev           # start the dev server
npm run build         # production build (fails on type errors)
npm run lint          # ESLint (quality + security rules)
npm run lint:fix      # ESLint with autofix
npm run format        # Prettier write
npm run format:check  # Prettier check (CI-friendly)
npm run typecheck     # tsc --noEmit
npm run check         # typecheck + lint + format:check (run before pushing)
```

## 8. Definition of done for any frontend change

- [ ] `npm run check` is green (typecheck + lint + format).
- [ ] New code respects the size/complexity limits (§3).
- [ ] No secrets committed; no `NEXT_PUBLIC_` secret leakage (§4).
- [ ] `docs/history/HISTORY.md` has a new entry and `docs/status/STATUS.md` is
      updated (§2).
- [ ] Architecture / security / modules docs updated if relevant (§2).
