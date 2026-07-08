# Frontend Status

_Last updated: 2026-07-08_

## Summary

The frontend is a freshly-scaffolded Next.js 16 App Router app. The focus so far
has been **engineering guardrails** (linting, formatting, type safety, security,
pre-commit hooks) and the **documentation system**, not product features.

## Tooling & guardrails — ✅ in place

| Area                  | Status | Details                                                      |
| --------------------- | ------ | ------------------------------------------------------------ |
| ESLint (quality)      | ✅     | Size/complexity limits + correctness rules                   |
| ESLint (security)     | ✅     | `eslint-plugin-security`, `eslint-plugin-no-unsanitized`     |
| Prettier              | ✅     | `.prettierrc.json` + `.prettierignore`                       |
| TypeScript strictness | ✅     | `strict` + extra strict flags in `tsconfig.json`             |
| Security headers/CSP  | ✅     | `next.config.ts` (`headers()`), applied to all routes        |
| Env/secret guardrails | ✅     | `.env.example`, `NEXT_PUBLIC_` documented, `.env*` ignored   |
| Husky + lint-staged   | ✅     | **Root** `../.husky/pre-commit`, path-gated: frontend (lint-staged + typecheck) and/or backend (pre-commit framework) |
| Docs system           | ✅     | `docs/` + `RULES.md`                                          |

## Application surface — 🟡 scaffold only

| Module      | Status | Notes                                            |
| ----------- | ------ | ------------------------------------------------ |
| App shell   | 🟡     | `src/app/layout.tsx`, minimal `src/app/page.tsx` |
| Global CSS  | 🟡     | `src/app/globals.css` (Tailwind 4)               |

See [`../modules/MODULES.md`](../modules/MODULES.md) for the module registry.

## In progress / next up

- Product features (none built yet).
- Backend API integration (via `NEXT_PUBLIC_API_BASE_URL`, ideally through a
  server-side route to keep secrets off the client).

## Known gaps / TODO

- No test setup yet (unit/component/e2e).
- No CI pipeline wired to run `npm run check` on PRs.
- CSP currently allows `'unsafe-inline'` for scripts/styles (required for
  Next.js hydration without nonces). Nonce-based hardening path is documented in
  [`../security/SECURITY.md`](../security/SECURITY.md).
