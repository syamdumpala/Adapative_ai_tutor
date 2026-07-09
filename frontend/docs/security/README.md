# Security Docs

The frontend's security posture and the guardrails that enforce it.

- [`SECURITY.md`](./SECURITY.md) — the controls in place (headers/CSP, lint
  rules, secret handling, type safety), the threat model they address, and the
  hardening roadmap.

## How to use

Whenever you add or change a security-relevant control — headers, CSP, auth,
data handling, a new third-party origin, a dependency with known CVEs — update
[`SECURITY.md`](./SECURITY.md) and append to
[`../history/HISTORY.md`](../history/HISTORY.md).

Before shipping a feature, walk the **checklist** at the bottom of
[`SECURITY.md`](./SECURITY.md).
