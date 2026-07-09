# Frontend Module Registry

_Last updated: 2026-07-09_

One row per module. Keep it current as the app grows.

| Module               | Path                                    | Responsibility                                               | Status |
| -------------------- | --------------------------------------- | ------------------------------------------------------------ | ------ |
| App shell            | `src/app/layout.tsx`                    | Root HTML/body, brand fonts (`next/font`), metadata          | ✅     |
| Global CSS / tokens  | `src/app/globals.css`                   | Tailwind 4 `@theme` design tokens + keyframes                | ✅     |
| Tutor route          | `src/app/page.tsx`                      | Mira Tutor entry; reads `?role`                              | ✅     |
| Login route          | `src/app/login/page.tsx`                | Auth entry; reads `?mode` / `?role`                          | ✅     |
| **Component library**| `src/components/`                       | Reusable UI primitives (see `README.md`)                     | ✅     |
| Tone helpers         | `src/lib/tones.ts`                      | Tone→class maps, mastery/improvement colours                 | ✅     |
| Backdrop / cn        | `src/lib/backdrop.ts`, `src/lib/cn.ts`  | Shared page background; class-name join                      | ✅     |
| Shared hooks         | `src/hooks/`                            | `useResponsive`, `useToast`                                  | ✅     |
| **Tutor feature**    | `src/features/tutor/`                   | Mira app shell, student + teacher areas, chat engine, data   | ✅     |
| **Auth feature**     | `src/features/auth/`                    | Login / sign-up screen + brand panel                         | ✅     |

Status legend: ✅ done · 🟡 scaffold/partial · 🚧 in progress · ⛔ deprecated.

---

## Component library

- **Path:** `src/components/` (barrel `index.ts`, catalog `README.md`)
- **Responsibility:** brand-neutral presentational primitives shared by every
  feature — `Logo`, `Button`, `IconButton`, `SegmentedControl`, `Card`, `Badge`,
  `Avatar`, `GlyphTile`, `SearchInput`, `TextField`, `Modal`, `Toast`,
  `ProgressBar`, `StatCard`, `EmptyState`, `icons`.
- **Public surface:** import from `@/components`.
- **Client/Server:** Server-safe by default; only `Modal` opts into `"use client"`.
- **Rule:** new modules check here first; add a new global component only when a
  pattern is reused across features. Full details in
  [`../../src/components/README.md`](../../src/components/README.md).
- **Status:** ✅

## Tutor feature

- **Path:** `src/features/tutor/`
- **Responsibility:** the Mira adaptive-tutor experience.
  - `TutorApp.tsx` + `Topbar.tsx` + `AccountModal.tsx` + `hooks/useTutorShell.ts`
    — app shell, toast, and the shared profile/performance modal (both roles).
  - `student/` — home (`StudentHome`, `ChatsSidebar`, `TopicGrid`, `TopicCard`,
    `ProfileMenu`), chat (`ChatView`, `ChatHeader`, `Composer`, banners), and
    `messages/` (diagnosis, visual hint, worked example, quiz, revision, typing).
  - `teacher/` — `TeacherDashboard`, `TeacherHome` (`TopicPanel`,
    `StudentPanel`), `TopicDetail`, `StudentDetail`, `TeacherToolbar` (back-nav
    + `TeacherAccountMenu`), and the catalog manager `TopicCatalog` +
    `TopicCreateModal` (`topicForm.ts` hook).
  - `hooks/useMiraChat.ts` + `hooks/chatActions.ts` + `state/chatReducer.ts` +
    `state/chatHelpers.ts` — the conversation engine (reducer + async dialogue).
  - `api/catalog.ts` — the topic-catalog client (`fetchTopics`, `createTopic`);
    the single seam mapping the backend's `subject` vocabulary onto `Topic`.
  - `data/` — `topics`, `seeds`, `dialogue` (+ `dialogueGeneric`), `quizzes`,
    `teacher`, `student`; `types.ts` for shared types.
- **Dependencies:** `@/components`, `@/lib/*`, `@/hooks/*`. **No backend calls
  yet** — all data is local/seeded.
- **Client/Server:** `page.tsx` is a Server Component; `TutorApp` and its
  interactive children are `"use client"`.
- **Status:** ✅ (demo data)

## Auth feature

- **Path:** `src/features/auth/`
- **Responsibility:** a real sign-in / sign-up workflow (validation, states,
  a11y) with the network call left as a seam.
  - `LoginPage` (layout + `BrandPanel`) → `AuthCard` (brand, mode toggle) →
    `SignInForm`/`SignInFields` and `SignUpForm`/`SignUpFields`.
  - `useAuthForm` — generic controlled-form hook (values, per-field errors,
    form error/notice, submitting, `field()` binding, `<form onSubmit>`).
  - `validation.ts` — email / password-policy / confirm-match / name / role.
  - `api.ts` — **placeholder** `signIn`/`signUp`/`requestPasswordReset`
    (throw `AuthNotConnectedError`); the single spot to wire the backend.
  - `PasswordField`, `AuthSubmit`, `AuthMessage`, `RolePicker` — building blocks.
- **Dependencies:** `@/components` (incl. `TextField`, `Checkbox`),
  `@/hooks/useResponsive`, `@/lib/backdrop`. **No backend wired yet.**
- **Client/Server:** `login/page.tsx` is a Server Component; the card/forms are
  `"use client"`. On success, `LoginPage` routes into the tutor by `user.role`.
- **Status:** ✅ workflow complete · ⛔ API not connected

---

## Entry template (copy when adding a module)

### <Module name>

- **Path:** `src/features/<name>/` (or wherever it lives)
- **Responsibility:** one or two sentences.
- **Public surface:** the components/hooks/functions other code imports.
- **Dependencies:** backend endpoints, shared `lib/` modules, external origins
  (must also be reflected in CSP — see `../security/SECURITY.md`).
- **Client/Server:** Server Component by default? Which parts are `"use client"`?
- **Status:** ✅ / 🟡 / 🚧 / ⛔
