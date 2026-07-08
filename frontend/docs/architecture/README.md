# Architecture Docs

How the frontend is organized and why. Read these before adding code so new work
fits the existing conventions.

- [`STRUCTURE.md`](./STRUCTURE.md) — file/folder layout, conventions, tooling,
  and the enforced code-quality limits (with rationale + how to tune).
- [`DIAGRAM.md`](./DIAGRAM.md) — rendering model, request/response flow, and
  where the security controls sit.

## How to use

After any change that affects **layout or flow**, update the relevant file here:

- New top-level folder, new convention, changed tooling → `STRUCTURE.md`.
- Changed request flow, rendering strategy, or where a control applies →
  `DIAGRAM.md`.

Always also append to [`../history/HISTORY.md`](../history/HISTORY.md).
