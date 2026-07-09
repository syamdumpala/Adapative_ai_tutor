# Frontend Diagrams

## Rendering model (Next.js App Router)

```mermaid
flowchart TD
    Browser["Browser"] -->|HTTP request| Next["Next.js server (App Router)"]
    Next -->|"security headers + CSP (next.config.ts)"| Resp["Response"]
    Next --> RSC["Server Components (default)\nno secrets leak to client"]
    RSC -->|"serialized props"| Client["Client Components\n(\"use client\")"]
    RSC -.->|"server-side fetch"| Backend["Backend API (../backend)"]
    Resp --> Browser
    Client -->|"hydration"| Browser
```

Key points:

- **Server Components are the default.** Data fetching and secret use happen on
  the server; only serializable props cross into Client Components.
- **Security headers/CSP** are attached to every response by `next.config.ts`
  (`headers()` on `source: "/:path*"`).
- **Backend calls** should originate server-side (Server Component or Route
  Handler) so backend secrets never reach the browser bundle.

## Request → response with guardrails

```mermaid
sequenceDiagram
    participant B as Browser
    participant N as Next.js
    participant A as Backend API
    B->>N: GET /route
    N->>N: Render Server Components
    N-->>A: (optional) server-side fetch with server secret
    A-->>N: data
    N->>N: Attach CSP + security headers
    N-->>B: HTML + serialized props (+ headers)
    B->>B: Hydrate Client Components
```

## Commit-time guardrail flow (root Husky, path-gated)

```mermaid
flowchart TD
    Commit["git commit\n(from anywhere)"] --> Hook["root .husky/pre-commit"]
    Hook --> FEQ{"frontend/\nfiles staged?"}
    Hook --> BEQ{"backend/\nfiles staged?"}
    FEQ -->|yes| FE["cd frontend:\nlint-staged + tsc --noEmit"]
    FEQ -->|no| SkipFE["skip frontend"]
    BEQ -->|yes| BE["backend/.venv pre-commit run\n(ruff, self-scoped to backend/)"]
    BEQ -->|no| SkipBE["skip backend"]
    FE --> Done["commit proceeds"]
    SkipFE --> Done
    BE --> Done
    SkipBE --> Done
    FE -.->|fail| Abort["commit aborted"]
    BE -.->|fail| Abort
```

> The hook is owned by the repo root, so it gates commits from either side. Each
> side's checks run only when that side has staged files.

> Diagrams use [Mermaid](https://mermaid.js.org), which GitHub renders natively.
> Update these whenever the rendering strategy, data flow, or commit checks
> change.
