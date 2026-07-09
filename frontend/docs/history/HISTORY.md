# Frontend History

Append-only changelog. Newest first.

---

## 2026-07-10 — "?" help on every analytics chart; drop the composer hint badge

- **Info affordance everywhere** — every chart on the progress page now has the
  same hover-to-explain "?" (`InfoDot`), pinned to the card's top-right via
  `ChartCard` (overflow-safe on narrow cards). Blurbs live in one place
  (`chartInfo.ts`) and cover the trend, misconception donut, subject bars, topic
  ranking, mastery-vs-confidence, effort scatter, understanding mix, and the
  review-due card.
- **Trend chart wording** — retitled to "Mastery, confidence & misconfidence over
  time"; the third series / legend label is now just **"Misconfidence"** (not
  "Misconfidence index").
- **Composer hint badge removed** — the "Hint N of 3" status chip above the chat
  input (`Composer`'s `HintBadge`) is gone per request; the tutor's actual hint
  message bubbles are unaffected. `hintRung` is no longer threaded into `Composer`
  (the chat-state field remains). Purely a frontend display change — no backend
  text drove that chip.
- **Verify** — `npm run check` + `next build` green.

## 2026-07-10 — Trend chart: Misconfidence Index line + info tooltip

Extended the "Mastery & confidence over time" chart on the student progress page.

- **Third series** — the backend now returns a signed **Misconfidence Index**
  (`misconception_index`, MI = −C·(C−Â); positive = mastery, negative =
  confidently-wrong risk) per completed session. `MasteryTrendChart` plots it as
  a third amber line on a **secondary right axis** (mastery/confidence stay on the
  left 0–100% axis), with a dashed zero reference line marking the neutral point.
  The coral "misconception detected" marker dots moved onto this MI line, and the
  tooltip formats MI as a signed decimal vs. the % series.
- **Info affordance** — new `InfoDot` ("?" circle, hover/focus reveals a
  paragraph) wired into `ChartCard` via an optional `info` prop; the trend card
  now explains what the chart shows and how the index is read.
- **API** — `AnalyticsPointDTO` gains `misconception` + `misconception_index`.
- **Verify** — `npm run check` + `next build` green.

## 2026-07-10 — Student analytics page (performance graphs)

Added a dedicated **"My progress"** page for the signed-in student that charts
their performance overall and per topic, using Recharts.

- **New surface** — `student/analytics/StudentAnalytics` renders a back-to-home
  header + a `SegmentedControl` toggle between two panels:
  - **Overall** (`OverviewPanel`) — the `/me/performance` KPI tiles, a hero
    mastery-vs-confidence trend line over every completed session (coral dots
    flag misconceptions), a misconception-by-type donut, and a mastery-vs-
    confidence-by-subject grouped bar. Data from `GET /me/analytics` +
    `GET /me/performance`.
  - **By topic** (`TopicsPanel`) — topic mastery ranking, per-topic mastery-vs-
    confidence, effort-vs-mastery bubble scatter, understanding-mix donut, and a
    "review due" rail. Data from the new `GET /me/topics`.
- **Charts** — one small file per chart under `analytics/charts/` plus a shared
  `chartTheme.ts` (design-token hex, tone/understanding/mastery → colour),
  `ChartCard` wrapper (title + empty state), and `format.ts` helpers. Grouped
  mastery/confidence bars are shared via `GroupedBars` (subject + topic reuse).
- **Data layer** — `api/student.ts` gains `AnalyticsDTO` / `TopicAnalyticsDTO`
  + `fetchAnalytics` / `fetchTopicAnalytics`; `hooks/useAnalytics.ts` exposes
  `useAnalytics` / `useTopicAnalytics` (mount-fetch, loading/error state).
- **Navigation** — `useTutorShell` now owns a `studentView` (`home | analytics`)
  with `openAnalytics` / `backToHome`; reached via a new "My progress" item in
  the account `ProfileMenu`. Threaded through `StudentArea → StudentHome →
  TopicGrid → ProfileMenu`.
- **Dependency** — added `recharts` (SVG, no `eval` → passes the CSP).
- **Verify** — `npm run check` (typecheck + lint + Prettier) and `next build`
  both green.

## 2026-07-10 — Student home: searchable topic grid

Added a search box to the student home so learners can filter the topic catalog
instead of scanning the whole grid.

- **`student/TopicGrid`** now owns a `query` state and renders the shared
  `SearchInput` between the greeting header and the card grid. Matching is
  case-insensitive over each topic's `name` + `desc` (`matchesQuery`), memoised
  over the live catalog from `useTopics`; an empty query shows the full grid.
- **No matches** → the shared `EmptyState` ("No topics match …") replaces the
  grid so the screen never goes blank mid-search.
- **Decomposition** — to stay under the file/function limits, the header and the
  results grid were extracted into `TopicGridHeader` and `TopicResults`
  sub-components, and the file is now `"use client"` (it owns state).
- **Scope** — purely client-side over the already-fetched catalog (the student
  topic list is small); the backend `/subjects` contract is untouched.
- **Verify** — `npm run check` (typecheck + lint + Prettier) and `next build`
  both green.

## 2026-07-10 — Teacher dashboard chrome: logo-home, back button, account menu

Reworked the teacher toolbar so navigation and account actions read like a real
app instead of loose buttons.

- **Mira logo = Home** — the Topbar logo now navigates the teacher to Home
  (`useTutorShell.onLogoClick` routes to `teacherNav.goHome()` for teachers);
  the standalone Home icon button was removed from the toolbar.
- **Back button** — `useTeacherNav` gained a navigation stack (`goBack`,
  `canGoBack`); the toolbar's left side is now a "‹ Teacher · …" back control
  that returns to the previous screen and is disabled at the Home root. Each
  frame snapshots the full context (`screen` + `topicId` + `studentId`), so
  walking back through the topic↔student cross-links restores the exact entity
  that was shown, not just the screen type. `goHome` clears the stack.
- **Account menu** — the direct "Log out" button became a profile **avatar**
  (`teacher/TeacherAccountMenu.tsx`) that opens a dropdown with **Profile** and
  **Log out**. Profile opens the account modal.
- **Shared profile modal** — `student/StudentModal.tsx` was generalized to
  `AccountModal` (moved to the tutor root) and is now rendered for both roles;
  the teacher's Profile action opens it via `openModal("profile")` (live from
  `/me/profile`). Its pre-load fallback is now role-neutral (no fabricated
  student surname / "Student" label).
- **Verify** — `npm run check` + `next build` green. A multi-agent adversarial
  review of the diff caught and fixed: the back-stack losing entity context, the
  student-specific profile fallback leaking to teachers, and missing menu
  a11y (`aria-haspopup`/`aria-expanded`, `role=menu`, Escape-to-close).

## 2026-07-09 — Rename "Subject" → "Topic" (UI) + teacher "Add topic" flow

Aligned the product vocabulary with what the home screen actually shows, and
gave teachers a way to grow the catalog.

- **Terminology** — the student-facing domain object is now **Topic**
  everywhere in the frontend: the `Topic` type, `data/topics.ts`
  (`TOPICS`/`topicById`), `hooks/useTopics.ts`, `student/TopicCard` +
  `student/TopicGrid`, the chat-state field `topicId`, `MiraChat.openTopic`, and
  all visible copy ("Topics", "Pick a topic to begin", "Topics available",
  "Back to topics", etc.). **The backend contract is untouched**: the catalog
  client `api/catalog.ts` is the single seam that still speaks the backend's
  `subject` vocabulary (`GET/POST /subjects`, `subject_id`, `subjects_available`).
- **Teacher "Add topic"** — new catalog screen (`teacher/TopicCatalog.tsx`,
  `TeacherScreen: "catalog"`) reachable from a "＋ Topic" button in
  `TeacherToolbar`. `teacher/TopicCreateModal.tsx` + `teacher/topicForm.ts`
  collect name/description/glyph/accent/caption, auto-slugify the id to the
  backend's `^[a-z0-9_-]+$`, validate (empty name; **duplicate by name**, since
  ids are decoupled from names — seeds use `"1".."6"`), clamp field lengths to
  the backend caps, and `createTopic()` POSTs to the teacher-gated `/subjects`.
  New topics prepend to the catalog and appear on every student's home.
- **Live topic resolution in chat** — `ChatView`/`ChatsSidebar` now resolve the
  open chat's topic from the **live** catalog (`useTopics`) with the static
  catalog as fallback, so a teacher-created (slug-id) topic no longer renders as
  "Fractions" in the chat header/sidebar.
- **Card descriptions truncate** — topic cards on the **teacher catalog and the
  student home** show only the first 5 words + "…" (full text on hover via
  `title`), via the shared `lib/text.ts#truncateWords`, so a long teacher-authored
  paragraph no longer balloons a card.
- **Verify** — `npm run check` (typecheck + lint + format) and `next build` are
  green; guardrails respected (modal logic split into `topicForm.ts` to stay
  under the 200-line/50-line limits). A multi-agent adversarial review of the
  diff surfaced these two behavioral gaps + the length-cap gap, all fixed.

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
