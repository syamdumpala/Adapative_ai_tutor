<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

# Working in this frontend

**Before writing or changing any code, read [`RULES.md`](./RULES.md)** — the
one-page summary of this codebase, its guardrails, and the mandatory workflow.
It links to the detailed docs under [`docs/`](./docs/README.md):

1. `docs/status/STATUS.md` — current state of the frontend
2. `docs/architecture/STRUCTURE.md` + `DIAGRAM.md` — layout, conventions, flow
3. `docs/security/SECURITY.md` — security controls & checklist
4. `docs/modules/MODULES.md` — the module registry
5. `docs/history/HISTORY.md` — append-only changelog

## Rules

- Enforced code-quality limits (ESLint): max **300** lines/file, **50**
  lines/function, complexity **10**, depth **4**, params **4**. Decompose rather
  than raise a limit.
- Strict TypeScript — keep `npm run typecheck` green.
- Security: never put secrets behind `NEXT_PUBLIC_`; don't widen the CSP in
  `next.config.ts` without documenting the origin in `docs/security/SECURITY.md`;
  no unsanitized DOM/`dangerouslySetInnerHTML`.
- **After any change**, append to `docs/history/HISTORY.md` and update
  `docs/status/STATUS.md`; update `architecture/`, `security/`, or `modules/`
  docs if those areas changed.
- Run `npm run check` (typecheck + lint + format) before committing. The
  **root** pre-commit hook (`../.husky/pre-commit`, installed via `npm install`
  at the repo root) enforces the frontend checks on staged frontend files.
- **Do not modify the backend** (`../backend`).

## Commands

```bash
npm run dev     # dev server
npm run build   # production build (fails on type errors)
npm run check   # typecheck + lint + format:check (pre-push gate)
npm run lint    # ESLint (quality + security)
npm run format  # Prettier write
```
