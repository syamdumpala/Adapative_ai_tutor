# Frontend Status

_Last updated: 2026-07-10_

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
| Tutor · student     | ✅     | Home (chats + searchable topics), guided chat, hint ladder, quiz |
| Tutor · analytics   | ✅     | "My progress" page — overall + per-topic performance graphs (Recharts) |
| Tutor · teacher     | ✅     | Topics + students panels, drill-downs, topic catalog + create |
| Auth (Login)        | ✅     | Real sign-in / sign-up workflow + validation (API seam only) |
| Routes              | ✅     | `/` (`?role=`), `/login` (`?mode`/`?role`)                  |

See [`../modules/MODULES.md`](../modules/MODULES.md) for the module registry and
[`../../src/components/README.md`](../../src/components/README.md) for the
component catalog.

## Backend integration — ✅ wired via BFF

| Surface | Status | Source |
| ------- | ------ | ------ |
| Auth (login / register / logout / session) | ✅ | `/api/auth/*` → httpOnly cookie; `/` is session-guarded and resolves role from `/auth/me` |
| Topics grid (student home) | ✅ | `GET /subjects` (per-student progress), mapped onto `Topic` in `api/catalog.ts` |
| Teacher topic catalog + create | ✅ | `GET /subjects` list + teacher-gated `POST /subjects` (`createTopic`) |
| Profile / performance modals | ✅ | `/me/profile` · `/me/performance` |
| "Your chats" rail + transcripts | ✅ | conversation-history API (`/tutor/sessions` + `/{id}/messages`) |
| Teacher dashboard (roster / student / topic) | ✅ | `/teacher/*` assembled in `useTeacherStudents` |
| Simulate-day · logout | ✅ | `/teacher/simulate-day` · `/api/auth/logout` |

The chat is now **fully live** (no scripted flow): `POST /tutor/ask` drives every
turn, and there is **no role switch / restart / simulate-day** — role comes from
the signed-in account.

## In progress / next up

- **Server-side search everywhere** — list endpoints support `q`/`sort`/filters;
  the teacher drill-down search boxes currently filter the fetched set
  client-side (fine for a class; switch to server `q` for large rosters).
- **Message pagination** — `fetchSessionMessages` loads the first 100 messages
  (the API page cap); add paging if conversations grow beyond that.

## Known gaps / TODO

- No test setup yet (unit/component/e2e).
- No CI pipeline wired to run `npm run check` on PRs.
- CSP still allows `'unsafe-inline'` for scripts/styles (nonce-free strategy for
  static rendering); hardening path documented in
  [`../security/SECURITY.md`](../security/SECURITY.md).
- The demo drives the guided conversation via suggested-reply buttons; the
  free-text composer echoes the message but has no scripted response.
