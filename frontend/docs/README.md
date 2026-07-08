# Frontend Documentation

This folder is the **living source of truth** for the frontend. It is organized
into topic folders, each with its own `README.md` (what the folder is for) and
one or more content files that must be kept up to date as the code evolves.

For the one-page summary and the golden rules, start with
[`../RULES.md`](../RULES.md).

## Folder map

| Folder                             | Purpose                                                            |
| ---------------------------------- | ----------------------------------------------------------------- |
| [`status/`](./status/README.md)       | The current state of the frontend — what exists, works, is WIP.   |
| [`architecture/`](./architecture/README.md) | File/folder layout, conventions, diagrams, tooling.         |
| [`security/`](./security/README.md)     | Security posture: headers/CSP, lint rules, secrets, checklist.    |
| [`history/`](./history/README.md)       | Append-only changelog of everything done in the frontend.         |
| [`modules/`](./modules/README.md)       | Per-module/feature documentation registry.                        |

## The update workflow (mandatory)

Whenever you change anything in the frontend:

1. **Always** append an entry to [`history/HISTORY.md`](./history/HISTORY.md).
2. **Always** update [`status/STATUS.md`](./status/STATUS.md) to reflect reality.
3. Update `architecture/`, `security/`, and/or `modules/` **if** your change
   touched those areas.

Think of it as: *code + docs land together in the same change.* A change that
updates behavior but not the docs is incomplete.

## Conventions for these docs

- One idea per file; keep files skimmable.
- Use ISO dates (`YYYY-MM-DD`) in `HISTORY.md`.
- Link between docs with relative paths so they stay clickable.
- These `.md` files are excluded from Prettier/ESLint (hand-formatted).
