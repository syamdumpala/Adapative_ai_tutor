# Frontend Module Registry

_Last updated: 2026-07-08_

One row per module. Keep it current as the app grows.

| Module      | Path                    | Responsibility                              | Status |
| ----------- | ----------------------- | ------------------------------------------- | ------ |
| App shell   | `src/app/layout.tsx`    | Root HTML/body, fonts, global metadata      | 🟡 scaffold |
| Home route  | `src/app/page.tsx`      | Landing page                                | 🟡 scaffold |
| Global CSS  | `src/app/globals.css`   | Tailwind 4 base + global styles             | 🟡 scaffold |

Status legend: ✅ done · 🟡 scaffold/partial · 🚧 in progress · ⛔ deprecated.

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
