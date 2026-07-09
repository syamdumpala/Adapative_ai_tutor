# Frontend History

Append-only changelog. Newest first.

---

## 2026-07-09 — Remove demo scaffolding; make the chat fully live

Stripped the prototype affordances so the app behaves like a real product driven
entirely by the backend.

- **No role switch** — the student/teacher toggle is gone. Role is fixed by the
  signed-in account (`/auth/me`); the topbar is now brand-only.
- **No demo controls** — removed the "Restart" and "Simulate day" buttons.
- **Live chat, no script** — replaced the scripted dialogue engine with a real
  loop over `POST /tutor/ask`: `openSubject` starts a fresh chat, `sendMessage`
  sends the turn and appends the tutor's actual reply, the "Hint N of 3" badge
  reflects the graph's `hint_level`, and completed chats lock. The "Your chats"
  rail and transcripts come from `/tutor/sessions` (+ `/{id}/messages`); errors
  surface as an inline banner.
- **Deleted dummy data/components** — `data/{dialogue,dialogueGeneric,quizzes,seeds}.ts`,
  `hooks/chatActions.ts`, `api/history.ts`, `buildStudents`, and the scripted
  message cards (`QuizCard`, `DiagnosisCard`, `RevisionPlan`, `WorkedExample`,
  `VisualHint`). Trimmed `types.ts` to the live shapes.
- Verified: `npm run check` + `npm run build` green; end-to-end against the
  backend — login, subjects, chats rail, transcript load, and multi-turn
  `/tutor/ask` (new sessions appear live in the rail).

## 2026-07-09 — Wire the app to the backend via a BFF (auth + live data)

Connected the frontend to the FastAPI backend using the **Backend-for-Frontend**
pattern from `docs/security/SECURITY.md` — the browser only ever calls same-origin
`/api/*` route handlers, which attach the JWT from an **httpOnly cookie** and
forward to the backend, so the token never reaches client code (CSP `connect-src
'self'` unchanged).

- **BFF route handlers** (`src/app/api/`): `auth/login`, `auth/register`,
  `auth/logout`, `auth/me` (set/clear the `mira_session` httpOnly cookie), and a
  catch-all authenticated proxy `backend/[...path]` for all read/query endpoints.
- **Server client** `src/server/backend.ts` (cookie helpers + `backendFetch`);
  **browser client** `src/lib/api.ts` (`apiGet/apiPost/apiPatch`, `Page<T>`, `qs`).
- **Auth** (`src/features/auth/api.ts`): `signIn`/`signUp`/`signOut` now hit the BFF
  (removed the `AuthNotConnectedError` stub). `/` is now a **session-guarded** server
  component (redirects to `/login`, and takes the role + display name from `/auth/me`).
- **Student data**: subjects grid ← `GET /subjects`; profile/performance modals ←
  `/me/profile` + `/me/performance`; the "Your chats" rail + transcripts ← the
  conversation-history API (`/tutor/sessions` + `/{id}/messages`) via a non-disruptive
  `hydrate` reducer action.
- **Teacher dashboard**: roster + per-topic engagement assembled from the split
  teacher endpoints (`useTeacherStudents`); simulate-day and logout call the real APIs.
- **Env**: `API_BASE_URL` (server-only) selects the backend; falls back to
  `NEXT_PUBLIC_API_BASE_URL` then `http://localhost:8000`.
- Verified: `npm run check` + `npm run build` green; full login→cookie→proxy flow
  exercised end-to-end against the running backend (role guard 403, logout redirect).

## 2026-07-09 — Fix `next dev` "Manifest file is empty" (pin Turbopack root)

`npm run dev` 500'd with `Error: Manifest file is empty`. Cause: Next inferred
the **monorepo root** as the workspace root (it sees the root Husky
`package-lock.json` above `frontend/`), so Turbopack resolved its build manifest
in the wrong place.

- Set `turbopack: { root: process.cwd() }` in `next.config.ts` to pin the app
  root to `frontend/` (npm scripts run from there). This also silences the
  "inferred your workspace root" warning.
- Cleared the stale `.next` cache (left over from repeated `next build` runs).
- Verified: fresh `next dev` serves `/`, `/?role=teacher`, `/login` and
  `/login?mode=signup` at 200 with no manifest error; `npm run build` still green
  and the workspace-root warning is gone.

## 2026-07-09 — Turn the login screen into a real auth workflow (no API yet)

Replaced the demo login (which faked a role redirect after a timeout) with a
proper sign-in / sign-up workflow. **No backend is wired** — the network call is
an explicit, typed seam to fill in later.

- **API seam** — `src/features/auth/api.ts`: typed `signIn` / `signUp` /
  `requestPasswordReset` that currently throw `AuthNotConnectedError`. Each has a
  `TODO(api)` marker to POST to a **server-side route handler** so tokens never
  reach the client bundle (see `../security/SECURITY.md`).
- **Real validation** — `validation.ts`: email format, sign-up password policy
  (8+ chars, a letter, a number) with a live requirements checklist,
  confirm-password match, name and role checks. Per-field inline errors.
- **Form engine** — `useAuthForm.ts`: generic controlled-form hook (values,
  per-field errors, form-level error/notice, submitting state, a `field()`
  binding, real `<form onSubmit>`).
- **Forms** — `SignInForm` (+ `SignInFields`: email, password, remember-me,
  forgot-password reset request) and `SignUpForm` (+ `SignUpFields`: name,
  email, password, confirm, role) composed inside `AuthCard`; `PasswordField`
  (show/hide) and `AuthSubmit` (spinner) are shared.
- On success, `LoginPage` routes into the tutor by `user.role`
  (`/` or `/?role=teacher`) — the integration point once auth returns a user.
- **Global components**: added `Checkbox` (accessible, error-capable) and
  upgraded `TextField` with `id` / `error` / `hint` / `disabled` /
  `autoComplete` + ARIA (`aria-invalid`, `aria-describedby`). Barrel + catalog
  updated.
- Removed the old demo files (`LoginForm`, `LoginFields`, `useLoginForm`).
- `npm run check` + `npm run build` green; smoke-tested `/login` and
  `/login?mode=signup` (both 200, correct content).

## 2026-07-09 — Implement the Mira Tutor app (+ Login) from the Claude Design handoff

Built the first real product surface: the **Mira** adaptive-tutor experience,
recreated in React from the `Mira Tutor.dc.html` / `Mira Login.dc.html`
prototypes (the `<script>` DCLogic is the behavioural source of truth; the
static `<x-dc>` template is only a rough preview).

**Design system / tokens**

- Rewrote `src/app/globals.css` with the Mira palette, type scale, radii,
  shadows and keyframes as Tailwind v4 `@theme` tokens (paper/ink/green/coral/
  amber/violet families; `shadow-soft/float/pop`; `animate-fade-up` etc.).
- `src/app/layout.tsx` now self-hosts the three brand fonts (Bricolage
  Grotesque, Hanken Grotesk, Space Mono) via `next/font/google` — **no external
  font request, so the CSP `font-src 'self'` is unchanged** (see
  `../security/SECURITY.md`).

**Reusable component library** — `src/components/` (barrel + `README.md` catalog)

- 15 presentational primitives: `Logo`, `Button`, `IconButton`,
  `SegmentedControl`, `Card`, `Badge`, `Avatar`, `GlyphTile`, `SearchInput`,
  `TextField`, `Modal`, `Toast`, `ProgressBar`, `StatCard`, `EmptyState`
  (+ `icons`). Both features compose these thoroughly; Login is built almost
  entirely from them, validating reuse.
- Helpers: `src/lib/tones.ts` (tone→class maps — literal strings for Tailwind),
  `src/lib/cn.ts`, `src/lib/backdrop.ts`; hooks `src/hooks/useResponsive.ts`
  and `src/hooks/useToast.ts`.

**Features**

- `src/features/tutor/` — student home (chats rail + subject grid + profile
  menu + modals), the guided chat (data-driven dialogue engine via a
  `useReducer` handler-map, hint ladder, diagnosis / visual-hint / worked /
  quiz / revision message kinds, confidence-gated quiz), and the teacher
  dashboard (topics + students panels with search, topic & student drill-downs).
  Conversation script lives as data in `data/dialogue.ts` + `dialogueGeneric.ts`.
- `src/features/auth/` — the sign-in / sign-up screen with brand panel.
- Routes: `src/app/page.tsx` (`?role=teacher` opens the teacher view) and
  `src/app/login/page.tsx` (`?mode`/`?role` presets); both read the Next 16
  async `searchParams`. Teacher logout routes to `/login`.

**Verification**

- `npm run check` (typecheck + lint + format) and `npm run build` both green.
- Smoke-tested the running build: `/`, `/?role=teacher` and `/login` all return
  200 and render their expected content.

**Docs correction**

- Reconciled the documented `max-lines` limit with the **enforced** config: it
  is **200**, not 300 (`eslint.config.mjs`). Updated `../../RULES.md` §3 and
  `../architecture/STRUCTURE.md` accordingly.

## 2026-07-08 — Promote pre-commit hook to a root monorepo orchestrator

Moved Git-hook ownership from the frontend up to the **repo root** so a single
hook gates commits for both frontend and backend.

- Added a root `package.json` (name `adaptive-ai-tutor`) with `husky` as its
  only dependency and a `prepare` script; `npm install` at the root sets
  `core.hooksPath` → `.husky/_` and installs the hook.
- Added a root `.gitignore` (ignores the root `node_modules`).
- Removed Husky ownership from the frontend: deleted `frontend/.husky/`, removed
  the `prepare` script and the `husky` devDependency from `frontend/package.json`
  (lint-staged and its config stay in the frontend).
- New orchestrator `../.husky/pre-commit` is **path-gated**:
  - `frontend/` staged → `lint-staged` + `npm run typecheck`.
  - `backend/` staged → `backend/.venv/bin/pre-commit run` (ruff, self-scoped to
    `backend/`); PATH fallback, else warn+skip. Never edits backend code.
- Verified all four cases (frontend-only, backend-only clean/broken, both). The
  backend `ruff` check correctly blocks bad Python; backend files remain
  untouched by the setup.

**Note:** `make -C backend hooks` (`pre-commit install`) is now redundant —
pre-commit refuses to install while `core.hooksPath` is set, and the root hook
already runs the backend checks.

## 2026-07-08 — Guardrails, security & documentation baseline

Established the frontend engineering guardrails and the documentation system.
No product features yet.

**Tooling & quality**

- ESLint flat config (`eslint.config.mjs`) extended with enforced size/complexity
  limits (Balanced tier) and correctness rules — see
  [`../architecture/STRUCTURE.md`](../architecture/STRUCTURE.md).
- Added Prettier (`.prettierrc.json`, `.prettierignore`) and
  `eslint-config-prettier` so formatting and linting don't conflict.
- Tightened `tsconfig.json` with extra strictness flags (`noUncheckedIndexedAccess`,
  `noUnusedLocals`, `noUnusedParameters`, `noImplicitReturns`, etc.).
- Added scripts: `lint:fix`, `format`, `format:check`, `typecheck`, `check`.

**Security**

- Added HTTP security headers + a Content-Security-Policy to `next.config.ts`
  (applied to all routes); disabled `X-Powered-By`. See
  [`../security/SECURITY.md`](../security/SECURITY.md).
- Added security ESLint plugins: `eslint-plugin-security`,
  `eslint-plugin-no-unsanitized`.
- Added `.env.example` documenting `NEXT_PUBLIC_` vs. server-only secrets; kept
  `.env*` git-ignored except the template.

**Pre-commit automation**

- Installed Husky (`core.hooksPath` → `frontend/.husky/_`) + lint-staged.
- `.husky/pre-commit` runs lint-staged (ESLint `--fix` + Prettier on staged
  frontend files) then `tsc --noEmit`, and passes through to the shared backend
  `pre-commit` framework only if it is installed. **Backend code is never
  modified by this hook.**

**Documentation**

- Created the `docs/` system: `status/`, `architecture/`, `security/`,
  `history/`, `modules/`, each with a `README.md` + content files.
- Added `RULES.md` at the frontend root as the one-page summary + rulebook that
  references these docs.

**App changes**

- Replaced the create-next-app boilerplate `src/app/page.tsx` with a minimal,
  guardrail-compliant home page (the boilerplate `Home` exceeded the 50-line
  function limit). Updated `src/app/layout.tsx` metadata to the app name.

**Notes / decisions**

- Removed the `eslint` key from `next.config.ts`: Next.js 16 dropped the built-in
  ESLint build step (`next lint` removed). Linting runs via `npm run lint` and
  the pre-commit hook instead.
- CSP allows `'unsafe-inline'` (nonce-free strategy) to preserve static
  rendering; nonce-based hardening path documented in `security/SECURITY.md`.
