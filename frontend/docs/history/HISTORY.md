# Frontend History

Append-only changelog. Newest first.

---

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
