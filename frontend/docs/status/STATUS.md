# Frontend Status

_Last updated: 2026-07-09_

## Summary

The frontend is a Next.js 16 App Router app with the engineering guardrails
(linting, formatting, type safety, security headers, pre-commit hooks) and the
documentation system in place, **plus the first product surface**: the **Mira**
adaptive-tutor experience (student + teacher) and a Login screen, built from the
Claude Design handoff on top of a reusable component library.

## Tooling & guardrails — ✅ in place

| Area                  | Status | Details                                                      |
| --------------------- | ------ | ------------------------------------------------------------ |
| ESLint (quality)      | ✅     | Size/complexity limits + correctness rules                   |
| ESLint (security)     | ✅     | `eslint-plugin-security`, `eslint-plugin-no-unsanitized`     |
| Prettier              | ✅     | `.prettierrc.json` + `.prettierignore`                       |
| TypeScript strictness | ✅     | `strict` + extra strict flags in `tsconfig.json`             |
| Security headers/CSP  | ✅     | `next.config.ts` (`headers()`), applied to all routes        |
| Env/secret guardrails | ✅     | `.env.example`, `NEXT_PUBLIC_` documented, `.env*` ignored   |
| Husky + lint-staged   | ✅     | **Root** `../.husky/pre-commit`, path-gated                  |
| Docs system           | ✅     | `docs/` + `RULES.md`                                          |

## Application surface — ✅ Mira Tutor + Login

| Module              | Status | Notes                                                       |
| ------------------- | ------ | ----------------------------------------------------------- |
| Design tokens       | ✅     | `src/app/globals.css` (Tailwind `@theme`) + `next/font`     |
| Component library   | ✅     | `src/components/` — 15 primitives + `README.md` catalog     |
| Shared hooks / libs | ✅     | `useResponsive`, `useToast`, `tones`, `cn`, `backdrop`      |
| Tutor · student     | ✅     | Home (chats + subjects), guided chat, hint ladder, quiz     |
| Tutor · teacher     | ✅     | Topics + students panels, topic & student drill-downs       |
| Auth (Login)        | ✅     | Real sign-in / sign-up workflow + validation (API seam only) |
| Routes              | ✅     | `/` (`?role=`), `/login` (`?mode`/`?role`)                  |

See [`../modules/MODULES.md`](../modules/MODULES.md) for the module registry and
[`../../src/components/README.md`](../../src/components/README.md) for the
component catalog.

## In progress / next up

- Backend API integration — the tutor is currently a **self-contained demo**
  (seeded data + scripted dialogue in `src/features/tutor/data/`). Real chat,
  diagnosis and analytics should move behind a server-side route/proxy so
  backend secrets never reach the client.
- **Wire the auth API** — the sign-in / sign-up workflow, validation and states
  are complete; only the network calls in `src/features/auth/api.ts` remain
  (fill in the `TODO(api)` seams against a server-side route handler). Then add
  session persistence so the tutor resolves role from the session rather than
  the `?role=` query shim.

## Known gaps / TODO

- No test setup yet (unit/component/e2e).
- No CI pipeline wired to run `npm run check` on PRs.
- CSP still allows `'unsafe-inline'` for scripts/styles (nonce-free strategy for
  static rendering); hardening path documented in
  [`../security/SECURITY.md`](../security/SECURITY.md).
- The demo drives the guided conversation via suggested-reply buttons; the
  free-text composer echoes the message but has no scripted response.
