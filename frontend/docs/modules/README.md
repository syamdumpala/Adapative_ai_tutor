# Modules Docs

A registry of the frontend's modules/features and what each one does. This is
the map a newcomer reads to understand "what code lives where and why."

- [`MODULES.md`](./MODULES.md) — the module registry.

## What counts as a module

A cohesive unit of the app — a feature area (`features/<name>/`), a shared
subsystem (e.g. the API client in `lib/`), or the app shell. Keep entries at a
useful altitude; don't document every file.

## How to use

When you **add, rename, remove, or significantly change** a module, update
[`MODULES.md`](./MODULES.md) and append to
[`../history/HISTORY.md`](../history/HISTORY.md). Use the entry template at the
bottom of `MODULES.md`.
